/**
 * movimentacoes_estoque.js
 * Integração com endpoints de movimentações de estoque do backend
 */

(function() {
    const API_BASE = '';
    let pecasCache = [];

    // ─── Carregamento de Peças ───
    async function carregarPecas() {
        try {
            const response = await fetch(`${API_BASE}/pecas`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            pecasCache = await response.json();
            
            // Popular selects
            const selects = ['pecaSelect', 'filtroPeca'];
            selects.forEach(id => {
                const select = document.getElementById(id);
                if (select) {
                    let html = '<option value="">Todas as Peças</option>';
                    pecasCache.forEach(peca => {
                        html += `<option value="${peca.id_peca}">${peca.nome}</option>`;
                    });
                    select.innerHTML = html;
                }
            });
        } catch (error) {
            console.error('Erro ao carregar peças:', error);
        }
    }

    // ─── Carregamento de Movimentações ───
    async function carregarMovimentacoes(filtros = {}) {
        const loader = document.getElementById('movimentacaoLoader');
        const content = document.getElementById('movimentacaoContent');
        const emptyState = document.getElementById('emptyMovimentacao');
        
        try {
            loader.classList.add('active');
            content.style.display = 'none';
            emptyState.style.display = 'none';
            
            let url = `${API_BASE}/movimentacoes-estoque/`;
            
            // Construir URL com filtros
            if (filtros.tipo) {
                url = `${API_BASE}/movimentacoes-estoque/tipo/${filtros.tipo}`;
            } else if (filtros.peca_id) {
                url = `${API_BASE}/movimentacoes-estoque/peca/${filtros.peca_id}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const movimentacoes = await response.json();
            
            if (!Array.isArray(movimentacoes) || movimentacoes.length === 0) {
                loader.classList.remove('active');
                emptyState.style.display = 'block';
                return;
            }
            
            let html = '';
            movimentacoes.forEach(mov => {
                const tipoClass = mov.tipo_movimentacao === 'entrada' ? 'tipo-entrada' : 'tipo-saida';
                const tipoLabel = mov.tipo_movimentacao === 'entrada' ? 'Entrada' : 'Saída';
                
                html += `
                    <tr>
                        <td>${mov.id_movimentacao}</td>
                        <td>${getNomePeca(mov.id_peca)}</td>
                        <td><span class="${tipoClass}">${tipoLabel}</span></td>
                        <td class="text-end">${mov.quantidade}</td>
                        <td>${mov.motivo || '—'}</td>
                        <td>${formatarData(mov.created_at)}</td>
                    </tr>
                `;
            });
            
            document.getElementById('movimentacaoBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar movimentações:', error);
            mostrarAlerta('Erro ao carregar movimentações: ' + error.message, 'danger');
            loader.classList.remove('active');
        }
    }

    // ─── Criar Nova Movimentação ───
    document.getElementById('btnSalvarMovimentacao')?.addEventListener('click', async () => {
        const tipoMovimentacao = document.getElementById('tipoMovimentacao').value;
        const pecaId = document.getElementById('pecaSelect').value;
        const quantidade = document.getElementById('quantidade').value;
        const motivo = document.getElementById('motivo').value;
        
        if (!tipoMovimentacao || !pecaId || !quantidade || !motivo) {
            mostrarAlerta('Preencha todos os campos obrigatórios', 'warning');
            return;
        }
        
        try {
            const endpoint = tipoMovimentacao === 'entrada' ? 'entrada' : 'saida';
            const response = await fetch(`${API_BASE}/movimentacoes-estoque/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    id_peca: parseInt(pecaId),
                    quantidade: parseInt(quantidade),
                    motivo: motivo
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            mostrarAlerta('Movimentação registrada com sucesso!', 'success');
            
            // Fechar modal e recarregar
            const modal = bootstrap.Modal.getInstance(document.getElementById('novaMovimentacaoModal'));
            modal.hide();
            
            document.getElementById('formNovaMovimentacao').reset();
            carregarMovimentacoes();
            
        } catch (error) {
            console.error('Erro ao criar movimentação:', error);
            mostrarAlerta('Erro ao registrar movimentação: ' + error.message, 'danger');
        }
    });

    // ─── Filtros ───
    document.getElementById('btnFiltrar')?.addEventListener('click', () => {
        const filtros = {
            tipo: document.getElementById('filtroTipo')?.value || '',
            peca_id: document.getElementById('filtroPeca')?.value || '',
            data_inicio: document.getElementById('filtroDataInicio')?.value || '',
            data_fim: document.getElementById('filtroDataFim')?.value || ''
        };
        carregarMovimentacoes(filtros);
    });

    document.getElementById('btnLimparFiltro')?.addEventListener('click', () => {
        document.getElementById('filtroTipo').value = '';
        document.getElementById('filtroPeca').value = '';
        document.getElementById('filtroDataInicio').value = '';
        document.getElementById('filtroDataFim').value = '';
        carregarMovimentacoes();
    });

    // ─── Utilitários ───
    function getNomePeca(id) {
        const peca = pecasCache.find(p => p.id_peca === id);
        return peca ? peca.nome : `Peça #${id}`;
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
        carregarPecas();
        carregarMovimentacoes();
    });
})();
