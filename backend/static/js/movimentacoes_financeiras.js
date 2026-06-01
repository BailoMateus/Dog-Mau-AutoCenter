/**
 * movimentacoes_financeiras.js
 * Integração com endpoints de movimentações financeiras do backend
 */

(function() {
    const API_BASE = '';

    // ─── Carregamento de Movimentações ───
    async function carregarMovimentacoes(filtros = {}) {
        const loader = document.getElementById('movimentacaoLoader');
        const content = document.getElementById('movimentacaoContent');
        const emptyState = document.getElementById('emptyMovimentacao');
        
        try {
            loader.classList.add('active');
            content.style.display = 'none';
            emptyState.style.display = 'none';
            
            let url = `${API_BASE}/movimentacoes-financeiras/`;
            
            // Se houver período definido, usar endpoint de período
            if (filtros.data_inicio && filtros.data_fim) {
                url = `${API_BASE}/movimentacoes-financeiras/periodo`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        data_abertura: filtros.data_inicio,
                        data_fim: filtros.data_fim
                    })
                });
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const movimentacoes = await response.json();
                renderizarMovimentacoes(movimentacoes);
            } else {
                const response = await fetch(url, { credentials: 'include' });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const movimentacoes = await response.json();
                renderizarMovimentacoes(movimentacoes);
            }
            
            // Carregar resumo
            await carregarResumo();
            
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar movimentações:', error);
            mostrarAlerta('Erro ao carregar movimentações: ' + error.message, 'danger');
            loader.classList.remove('active');
            emptyState.style.display = 'block';
        }
    }

    function renderizarMovimentacoes(movimentacoes) {
        const emptyState = document.getElementById('emptyMovimentacao');
        
        if (!Array.isArray(movimentacoes) || movimentacoes.length === 0) {
            emptyState.style.display = 'block';
            return;
        }
        
        let html = '';
        movimentacoes.forEach(mov => {
            const tipoClass = mov.tipo_movimentacao === 'entrada' ? 'tipo-entrada' : 'tipo-saida';
            const tipoLabel = mov.tipo_movimentacao === 'entrada' ? 'Entrada' : 'Saída';
            
            html += `
                <tr>
                    <td>${mov.id_movimentacao_financeira || mov.id_movimentacao || 'N/A'}</td>
                    <td><span class="${tipoClass}">${tipoLabel}</span></td>
                    <td>${mov.descricao || '—'}</td>
                    <td class="text-end">R$ ${formatarMoeda(mov.valor || 0)}</td>
                    <td>${mov.id_pagamento || '—'}</td>
                    <td>${formatarData(mov.created_at)}</td>
                </tr>
            `;
        });
        
        document.getElementById('movimentacaoBody').innerHTML = html;
    }

    // ─── Carregamento de Resumo ───
    async function carregarResumo() {
        try {
            const dataInicio = document.getElementById('filtroDataInicio').value;
            const dataFim = document.getElementById('filtroDataFim').value;
            
            let url = `${API_BASE}/movimentacoes-financeiras/resumo`;
            if (dataInicio && dataFim) {
                url += `?data_abertura=${dataInicio}&data_fim=${dataFim}`;
            }
            
            const response = await fetch(url, { credentials: 'include' });
            if (!response.ok) return;
            
            const resumo = await response.json();
            
            // Calcular totais por tipo
            let totalEntradas = 0, totalSaidas = 0;
            let qtdEntradas = 0, qtdSaidas = 0;
            
            if (Array.isArray(resumo)) {
                resumo.forEach(item => {
                    if (item.tipo_movimentacao === 'entrada') {
                        totalEntradas += parseFloat(item.valor_total || 0);
                        qtdEntradas += item.quantidade || 0;
                    } else {
                        totalSaidas += parseFloat(item.valor_total || 0);
                        qtdSaidas += item.quantidade || 0;
                    }
                });
            }
            
            // Atualizar cards
            document.getElementById('resumoEntradas').textContent = `R$ ${formatarMoeda(totalEntradas)}`;
            document.getElementById('resumoQtdEntradas').textContent = `${qtdEntradas} movimentações`;
            
            document.getElementById('resumoSaidas').textContent = `R$ ${formatarMoeda(totalSaidas)}`;
            document.getElementById('resumoQtdSaidas').textContent = `${qtdSaidas} movimentações`;
            
            const saldo = totalEntradas - totalSaidas;
            const saldoElement = document.getElementById('resumoSaldo');
            saldoElement.textContent = `R$ ${formatarMoeda(saldo)}`;
            saldoElement.style.color = saldo >= 0 ? '#28a745' : '#f44336';
            
        } catch (error) {
            console.error('Erro ao carregar resumo:', error);
        }
    }

    // ─── Criar Nova Movimentação Financeira ───
    document.getElementById('btnSalvarMovimentacao')?.addEventListener('click', async () => {
        const tipoMovimentacao = document.getElementById('tipoMovimentacao').value;
        const valor = document.getElementById('valor').value;
        const descricao = document.getElementById('descricao').value;
        const idPagamento = document.getElementById('idPagamento').value;
        
        if (!tipoMovimentacao || !valor || !descricao) {
            mostrarAlerta('Preencha todos os campos obrigatórios', 'warning');
            return;
        }
        
        try {
            const endpoint = tipoMovimentacao === 'entrada' ? 'entrada' : 'saida';
            const payload = {
                valor: parseFloat(valor),
                descricao: descricao
            };
            
            if (idPagamento) {
                payload.id_pagamento = parseInt(idPagamento);
            }
            
            const response = await fetch(`${API_BASE}/movimentacoes-financeiras/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            mostrarAlerta('Movimentação financeira registrada com sucesso!', 'success');
            
            // Fechar modal e recarregar
            const modal = bootstrap.Modal.getInstance(document.getElementById('novaMovimentacaoFinanceiraModal'));
            modal.hide();
            
            document.getElementById('formNovaMovimentacaoFinanceira').reset();
            carregarMovimentacoes();
            
        } catch (error) {
            console.error('Erro ao criar movimentação:', error);
            mostrarAlerta('Erro ao registrar movimentação: ' + error.message, 'danger');
        }
    });

    // ─── Filtros ───
    document.getElementById('btnFiltrar')?.addEventListener('click', () => {
        const filtros = {
            data_inicio: document.getElementById('filtroDataInicio')?.value || '',
            data_fim: document.getElementById('filtroDataFim')?.value || ''
        };
        carregarMovimentacoes(filtros);
    });

    document.getElementById('btnLimparFiltro')?.addEventListener('click', () => {
        document.getElementById('filtroDataInicio').value = '';
        document.getElementById('filtroDataFim').value = '';
        carregarMovimentacoes();
    });

    // ─── Utilitários ───
    function formatarMoeda(valor) {
        return parseFloat(valor).toFixed(2).replace('.', ',');
    }

    function formatarData(data) {
        if (!data) return 'N/A';
        try {
            return new Date(data).toLocaleDateString('pt-BR');
        } catch (e) {
            return data;
        }
    }

    function mostrarAlerta(mensagem, tipo = 'info') {
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.setAttribute('role', 'alert');
        alerta.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('main').insertBefore(alerta, document.querySelector('.container'));
        setTimeout(() => alerta.remove(), 5000);
    }

    // ─── Inicialização ───
    document.addEventListener('DOMContentLoaded', () => {
        // Definir período padrão (últimos 30 dias)
        const hoje = new Date();
        const treintaDiasAtras = new Date(hoje.getTime() - 30 * 24 * 60 * 60 * 1000);
        const formatoData = (data) => data.toISOString().split('T')[0];
        
        document.getElementById('filtroDataInicio').value = formatoData(treintaDiasAtras);
        document.getElementById('filtroDataFim').value = formatoData(hoje);
        
        carregarMovimentacoes();
    });
})();
