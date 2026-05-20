/**
 * ordem_servico_detail.js
 * Integração com endpoints de Ordem de Serviço do backend
 */

(function() {
    const API_BASE = '/api';
    const osId = document.querySelector('body').getAttribute('data-os-id') || 
                 (new URLSearchParams(window.location.search).get('id')) ||
                 window.location.pathname.split('/').pop();

    // ─── Carregamento de Dados ───
    async function carregarOrdemServico() {
        const loader = document.getElementById('osLoader');
        const content = document.getElementById('osContent');
        const error = document.getElementById('osError');
        
        try {
            loader.classList.add('active');
            content.style.display = 'none';
            error.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/ordens-servico/${osId}`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const os = await response.json();
            exibirOrdemServico(os);
            
            // Carregar dados relacionados
            await Promise.all([
                carregarServicos(),
                carregarPecas(),
                carregarMovimentacoes()
            ]);
            
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar OS:', error);
            loader.classList.remove('active');
            error.style.display = 'block';
        }
    }

    function exibirOrdemServico(os) {
        document.getElementById('osId').textContent = os.id_os || osId;
        document.getElementById('osVeiculo').textContent = `Veículo #${os.id_veiculo}`;
        document.getElementById('osMecanico').textContent = `Mecânico #${os.id_usuario}`;
        document.getElementById('osDescricao').textContent = os.descricao_problema || '—';
        
        // Datas
        if (os.data_abertura) {
            document.getElementById('osDataAbertura').textContent = formatarData(os.data_abertura);
        }
        if (os.data_conclusao) {
            document.getElementById('osDataConclusao').textContent = formatarData(os.data_conclusao);
        } else {
            document.getElementById('osDataConclusao').textContent = 'Não concluída';
        }
        
        // Status
        const statusBadge = document.getElementById('osStatusBadge');
        statusBadge.textContent = (os.status || 'aberta').toUpperCase();
        statusBadge.className = `os-status status-${os.status || 'aberta'}`;
    }

    // ─── Carregamento de Serviços ───
    async function carregarServicos() {
        const loader = document.getElementById('servicosLoader');
        const content = document.getElementById('servicosContent');
        const empty = document.getElementById('emptyServicos');
        
        try {
            loader.style.display = 'block';
            content.style.display = 'none';
            empty.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/servicos`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const servicos = await response.json();
            
            if (!Array.isArray(servicos) || servicos.length === 0) {
                loader.style.display = 'none';
                empty.style.display = 'block';
                return;
            }
            
            let html = '';
            let totalServicos = 0;
            
            servicos.forEach(servico => {
                const subtotal = (servico.servico_preco || 0) * (servico.quantidade || 0);
                totalServicos += subtotal;
                
                html += `
                    <tr>
                        <td>${servico.servico_descricao || 'Serviço #' + servico.id_servico}</td>
                        <td class="text-end">${servico.quantidade || 0}</td>
                        <td class="text-end">R$ ${formatarMoeda(servico.servico_preco || 0)}</td>
                        <td class="text-end">R$ ${formatarMoeda(subtotal)}</td>
                    </tr>
                `;
            });
            
            document.getElementById('servicosBody').innerHTML = html;
            document.getElementById('totalServicos').textContent = `R$ ${formatarMoeda(totalServicos)}`;
            
            loader.style.display = 'none';
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar serviços:', error);
            loader.style.display = 'none';
            empty.style.display = 'block';
        }
    }

    // ─── Carregamento de Peças ───
    async function carregarPecas() {
        const loader = document.getElementById('pecasLoader');
        const content = document.getElementById('pecasContent');
        const empty = document.getElementById('emptyPecas');
        
        try {
            loader.style.display = 'block';
            content.style.display = 'none';
            empty.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/pecas`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const pecas = await response.json();
            
            if (!Array.isArray(pecas) || pecas.length === 0) {
                loader.style.display = 'none';
                empty.style.display = 'block';
                return;
            }
            
            let html = '';
            let totalPecas = 0;
            
            pecas.forEach(peca => {
                const subtotal = (peca.peca_preco || 0) * (peca.quantidade || 0);
                totalPecas += subtotal;
                
                html += `
                    <tr>
                        <td>${peca.peca_nome || 'Peça #' + peca.id_peca}</td>
                        <td class="text-end">${peca.quantidade || 0}</td>
                        <td class="text-end">R$ ${formatarMoeda(peca.peca_preco || 0)}</td>
                        <td class="text-end">${peca.peca_estoque || 0}</td>
                        <td class="text-end">R$ ${formatarMoeda(subtotal)}</td>
                    </tr>
                `;
            });
            
            document.getElementById('pecasBody').innerHTML = html;
            document.getElementById('totalPecas').textContent = `R$ ${formatarMoeda(totalPecas)}`;
            
            // Calcular total da OS
            const totalServicos = parseFloat(document.getElementById('totalServicos').textContent.replace('R$ ', '').replace(',', '.')) || 0;
            const totalOS = totalServicos + totalPecas;
            document.getElementById('totalOS').textContent = `R$ ${formatarMoeda(totalOS)}`;
            
            loader.style.display = 'none';
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar peças:', error);
            loader.style.display = 'none';
            empty.style.display = 'block';
        }
    }

    // ─── Carregamento de Movimentações ───
    async function carregarMovimentacoes() {
        const loader = document.getElementById('movimentacoesLoader');
        const content = document.getElementById('movimentacoesContent');
        const empty = document.getElementById('emptyMovimentacoes');
        
        try {
            loader.style.display = 'block';
            content.style.display = 'none';
            empty.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/pecas/movimentacoes`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const movimentacoes = await response.json();
            
            if (!Array.isArray(movimentacoes) || movimentacoes.length === 0) {
                loader.style.display = 'none';
                empty.style.display = 'block';
                return;
            }
            
            let html = '';
            movimentacoes.forEach(mov => {
                const tipoClass = mov.tipo_movimentacao === 'entrada' ? 'tipo-entrada' : 'tipo-saida';
                const tipoLabel = mov.tipo_movimentacao === 'entrada' ? 'Entrada' : 'Saída';
                
                html += `
                    <tr>
                        <td>${mov.id_movimentacao}</td>
                        <td>Peça #${mov.id_peca}</td>
                        <td><span class="${tipoClass}">${tipoLabel}</span></td>
                        <td class="text-end">${mov.quantidade || 0}</td>
                        <td>${formatarData(mov.created_at)}</td>
                    </tr>
                `;
            });
            
            document.getElementById('movimentacoesBody').innerHTML = html;
            loader.style.display = 'none';
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar movimentações:', error);
            loader.style.display = 'none';
            empty.style.display = 'block';
        }
    }

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

    // ─── Inicialização ───
    document.addEventListener('DOMContentLoaded', () => {
        if (osId) {
            carregarOrdemServico();
        } else {
            console.error('OS ID não encontrado na URL');
            document.getElementById('osLoader').style.display = 'none';
            document.getElementById('osError').style.display = 'block';
        }
    });
})();
