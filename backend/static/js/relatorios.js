/**
 * relatorios.js
 * Integração com endpoints de relatórios do backend
 */

(function() {
    const API_BASE = '';

    // ─── Datas Padrão ───
    function setDatasPadraoFiltros() {
        const hoje = new Date();
        const treintaDiasAtras = new Date(hoje.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        const formatoData = (data) => data.toISOString().split('T')[0];
        
        ['faturamento', 'servicos', 'financeiro', 'ordens'].forEach(prefixo => {
            const dataInicio = document.getElementById(`${prefixo}DataInicio`);
            const dataFim = document.getElementById(`${prefixo}DataFim`);
            if (dataInicio) dataInicio.value = formatoData(treintaDiasAtras);
            if (dataFim) dataFim.value = formatoData(hoje);
        });
    }

    // ─── Dashboard ───
    async function carregarDashboard() {
        const loader = document.getElementById('dashboardLoader');
        const content = document.getElementById('dashboardContent');
        
        try {
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/dashboard`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            exibirDashboard(data);
            
            loader.classList.remove('active');
            content.style.display = 'block';
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
            mostrarAlerta('Erro ao carregar dashboard: ' + error.message, 'danger');
            loader.classList.remove('active');
        }
    }

    function exibirDashboard(data) {
        const metricsHtml = `
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Faturamento Total</div>
                    <div class="metric-value">R$ ${formatarMoeda(data.faturamento_total || 0)}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Serviços Realizados</div>
                    <div class="metric-value">${data.servicos_realizados || 0}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Ordens de Serviço</div>
                    <div class="metric-value">${data.total_ordem_servico || 0}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Lucro Total</div>
                    <div class="metric-value" style="color: #28a745;">R$ ${formatarMoeda(data.lucro_total || 0)}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Prejuízo Total</div>
                    <div class="metric-value" style="color: #f44336;">R$ ${formatarMoeda(data.prejuizo_total || 0)}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card">
                    <div class="metric-label">Quantidade em Estoque</div>
                    <div class="metric-value">${data.quantidade_estoque || 0}</div>
                </div>
            </div>
        `;
        
        document.getElementById('dashboardMetrics').innerHTML = metricsHtml;
    }

    // ─── Faturamento ───
    document.getElementById('btnFaturamento')?.addEventListener('click', async () => {
        const dataInicio = document.getElementById('faturamentoDataInicio').value;
        const dataFim = document.getElementById('faturamentoDataFim').value;
        
        if (!dataInicio || !dataFim) {
            mostrarAlerta('Selecione as datas de início e fim', 'warning');
            return;
        }
        
        try {
            const loader = document.getElementById('faturamentoLoader');
            const content = document.getElementById('faturamentoContent');
            
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/faturamento`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    data_abertura: dataInicio,
                    data_fim: dataFim
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            let html = '';
            if (data.detalhes && data.detalhes.length > 0) {
                data.detalhes.forEach(item => {
                    html += `
                        <tr>
                            <td>${formatarData(item.data || item.periodo)}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.total_faturado || 0)}</td>
                            <td class="text-end">${item.qtd_pedidos || 0}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.ticket_medio || 0)}</td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="4" class="text-center text-muted">Nenhum dado disponível</td></tr>';
            }
            
            document.getElementById('faturamentoBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar faturamento:', error);
            mostrarAlerta('Erro ao carregar relatório: ' + error.message, 'danger');
            document.getElementById('faturamentoLoader')?.classList.remove('active');
        }
    });

    // ─── Serviços Realizados ───
    document.getElementById('btnServicos')?.addEventListener('click', async () => {
        const dataInicio = document.getElementById('servicosDataInicio').value;
        const dataFim = document.getElementById('servicosDataFim').value;
        
        if (!dataInicio || !dataFim) {
            mostrarAlerta('Selecione as datas de início e fim', 'warning');
            return;
        }
        
        try {
            const loader = document.getElementById('servicosLoader');
            const content = document.getElementById('servicosContent');
            
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/servicos-realizados`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    data_abertura: dataInicio,
                    data_fim: dataFim
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            let html = '';
            if (data.detalhes && data.detalhes.length > 0) {
                data.detalhes.forEach(item => {
                    html += `
                        <tr>
                            <td>${item.nome_servico || item.servico || 'N/A'}</td>
                            <td class="text-end">${item.qtd_realizadas || 0}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.receita_total || 0)}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.receita_media || 0)}</td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="4" class="text-center text-muted">Nenhum dado disponível</td></tr>';
            }
            
            document.getElementById('servicosBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar serviços:', error);
            mostrarAlerta('Erro ao carregar relatório: ' + error.message, 'danger');
        }
    });

    // ─── Estoque ───
    document.getElementById('btnEstoque')?.addEventListener('click', async () => {
        try {
            const loader = document.getElementById('estoqueLoader');
            const content = document.getElementById('estoqueContent');
            
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/estoque`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            let html = '';
            if (data.detalhes && data.detalhes.length > 0) {
                data.detalhes.forEach(item => {
                    html += `
                        <tr>
                            <td>${item.nome_peca || item.peca || 'N/A'}</td>
                            <td class="text-end">${item.quantidade || 0}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.valor_total || 0)}</td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="3" class="text-center text-muted">Nenhuma peça em estoque</td></tr>';
            }
            
            document.getElementById('estoqueBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar estoque:', error);
            mostrarAlerta('Erro ao carregar relatório: ' + error.message, 'danger');
        }
    });

    // ─── Financeiro ───
    document.getElementById('btnFinanceiro')?.addEventListener('click', async () => {
        const dataInicio = document.getElementById('financeiroDataInicio').value;
        const dataFim = document.getElementById('financeiroDataFim').value;
        
        if (!dataInicio || !dataFim) {
            mostrarAlerta('Selecione as datas de início e fim', 'warning');
            return;
        }
        
        try {
            const loader = document.getElementById('financeiroLoader');
            const content = document.getElementById('financeiroContent');
            
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/financeiro-periodo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    data_abertura: dataInicio,
                    data_fim: dataFim
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            let html = '';
            if (data.movimentacoes_financeiras && data.movimentacoes_financeiras.length > 0) {
                data.movimentacoes_financeiras.forEach(item => {
                    const labelTipo = item.tipo_movimentacao === 'entrada' ? 'Entrada' : 'Saída';
                    html += `
                        <tr>
                            <td>${item.mes || 'N/A'}</td>
                            <td>${labelTipo}</td>
                            <td class="text-end">${item.quantidade || 0}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.valor_total || 0)}</td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="4" class="text-center text-muted">Nenhum dado financeiro</td></tr>';
            }
            
            document.getElementById('financeiroBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar financeiro:', error);
            mostrarAlerta('Erro ao carregar relatório: ' + error.message, 'danger');
        }
    });

    // ─── Ordens de Serviço ───
    document.getElementById('btnOrdens')?.addEventListener('click', async () => {
        const dataInicio = document.getElementById('ordensDataInicio').value;
        const dataFim = document.getElementById('ordensDataFim').value;
        
        if (!dataInicio || !dataFim) {
            mostrarAlerta('Selecione as datas de início e fim', 'warning');
            return;
        }
        
        try {
            const loader = document.getElementById('ordensLoader');
            const content = document.getElementById('ordensContent');
            
            loader.classList.add('active');
            content.style.display = 'none';
            
            const response = await fetch(`${API_BASE}/relatorios/ordens-servico`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    data_abertura: dataInicio,
                    data_fim: dataFim
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            let html = '';
            if (data.detalhes && data.detalhes.length > 0) {
                data.detalhes.forEach(item => {
                    html += `
                        <tr>
                            <td>${item.status || 'N/A'}</td>
                            <td class="text-end">${item.qtd_ordens || 0}</td>
                            <td class="text-end">R$ ${formatarMoeda(item.receita_total || 0)}</td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="3" class="text-center text-muted">Nenhuma ordem de serviço</td></tr>';
            }
            
            document.getElementById('ordensBody').innerHTML = html;
            loader.classList.remove('active');
            content.style.display = 'block';
            
        } catch (error) {
            console.error('Erro ao carregar ordens:', error);
            mostrarAlerta('Erro ao carregar relatório: ' + error.message, 'danger');
        }
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
        setDatasPadraoFiltros();
        carregarDashboard();
    });
})();
