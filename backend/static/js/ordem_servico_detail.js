/**
 * ordem_servico_detail.js
 */
(function() {
    const API_BASE = '';
    const osId = document.body.getAttribute('data-os-id') ||
                 window.location.pathname.split('/').filter(Boolean).pop();

    async function carregarOrdemServico() {
        const loader = document.getElementById('osLoader');
        const content = document.getElementById('osContent');
        const errorEl = document.getElementById('osError');

        try {
            if (loader) loader.classList.add('active');
            if (content) content.style.display = 'none';
            if (errorEl) errorEl.style.display = 'none';

            const response = await fetch(`${API_BASE}/ordens-servico/${osId}`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const os = await response.json();
            exibirOrdemServico(os);

            await Promise.all([carregarServicos(), carregarPecas(), carregarMovimentacoes()]);

            if (loader) loader.classList.remove('active');
            if (content) content.style.display = 'block';
        } catch (err) {
            console.error('Erro ao carregar OS:', err);
            if (loader) loader.classList.remove('active');
            if (errorEl) errorEl.style.display = 'block';
        }
    }

    function exibirOrdemServico(os) {
        document.getElementById('osId').textContent = os.id_os || osId;

        const veiculoLabel = os.placa
            ? `${os.placa} — ${os.nome_modelo || ''} ${os.cor || ''} (${os.ano_fabricacao || ''})`.replace(/\s+/g, ' ').trim()
            : `Veículo #${os.id_veiculo}`;

        document.getElementById('osVeiculo').textContent = veiculoLabel;
        document.getElementById('osProprietario').textContent = os.proprietario_nome || '—';
        document.getElementById('osMecanico').textContent = os.mecanico_nome || 'Não atribuído';
        document.getElementById('osDescricao').textContent = os.descricao_problema || '—';

        if (os.data_abertura) {
            document.getElementById('osDataAbertura').textContent = formatarData(os.data_abertura);
        }
        document.getElementById('osDataConclusao').textContent = os.data_conclusao
            ? formatarData(os.data_conclusao) : 'Não concluída';

        const statusBadge = document.getElementById('osStatusBadge');
        statusBadge.textContent = (os.status || 'aberta').toUpperCase().replace('_', ' ');
        statusBadge.className = `os-status status-${os.status || 'aberta'}`;

        const valorTotal = parseFloat(os.valor_total || 0);
        document.getElementById('totalOS').textContent = `R$ ${formatarMoeda(valorTotal)}`;

        setupStatusControl(os);
    }

    function setupStatusControl(os) {
        const wrap = document.getElementById('osStatusControl');
        if (!wrap) return;

        const canChange = !os.id_orcamento || os.orcamento_status === 'aprovado';
        wrap.innerHTML = '';

        if (!canChange) {
            wrap.innerHTML = '<p class="text-warning small mb-0 text-center">Alteração de status disponível após aprovação do orçamento.</p>';
            return;
        }

        const select = document.createElement('select');
        select.className = 'form-select form-select-sm bg-dark text-white border-secondary';
        ['aberta', 'em_andamento', 'concluida', 'cancelada'].forEach((s) => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s.replace('_', ' ');
            if (s === os.status) opt.selected = true;
            select.appendChild(opt);
        });

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-danger btn-dogmau';
        btn.textContent = 'Atualizar status';
        btn.addEventListener('click', async () => {
            try {
                const res = await fetch(`${API_BASE}/ordens-servico/${osId}/status`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ status: select.value })
                });
                if (!res.ok) {
                    const data = await res.json().catch(() => ({}));
                    throw new Error(data.detail || 'Não foi possível atualizar o status.');
                }
                notify('Status atualizado com sucesso.', 'success');
                carregarOrdemServico();
            } catch (e) {
                notify(e.message, 'error');
            }
        });

        wrap.appendChild(select);
        wrap.appendChild(btn);
    }

    function notify(msg, type) {
        if (window.UINotification) UINotification.toast(msg, type);
        else if (window.showToast) showToast(msg, type);
    }

    async function carregarServicos() {
        const loader = document.getElementById('servicosLoader');
        const content = document.getElementById('servicosContent');
        const empty = document.getElementById('emptyServicos');

        try {
            if (loader) loader.style.display = 'block';
            if (content) content.style.display = 'none';
            if (empty) empty.style.display = 'none';

            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/servicos`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const servicos = await response.json();
            if (!Array.isArray(servicos) || servicos.length === 0) {
                if (loader) loader.style.display = 'none';
                if (empty) empty.style.display = 'block';
                document.getElementById('totalServicos').textContent = 'R$ 0,00';
                return;
            }

            let html = '';
            let totalServicos = 0;
            servicos.forEach((s) => {
                const subtotal = (s.servico_preco || 0) * (s.quantidade || 1);
                totalServicos += subtotal;
                html += `<tr>
                    <td>${s.servico_descricao || 'Serviço #' + s.id_servico}</td>
                    <td class="text-end">${s.quantidade || 1}</td>
                    <td class="text-end">R$ ${formatarMoeda(s.servico_preco || 0)}</td>
                    <td class="text-end">R$ ${formatarMoeda(subtotal)}</td>
                </tr>`;
            });

            document.getElementById('servicosBody').innerHTML = html;
            document.getElementById('totalServicos').textContent = `R$ ${formatarMoeda(totalServicos)}`;
            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';
        } catch (err) {
            console.error(err);
            if (loader) loader.style.display = 'none';
            if (empty) empty.style.display = 'block';
        }
    }

    async function carregarPecas() {
        const loader = document.getElementById('pecasLoader');
        const content = document.getElementById('pecasContent');
        const empty = document.getElementById('emptyPecas');

        try {
            if (loader) loader.style.display = 'block';
            if (content) content.style.display = 'none';
            if (empty) empty.style.display = 'none';

            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/pecas`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const pecas = await response.json();
            if (!Array.isArray(pecas) || pecas.length === 0) {
                if (loader) loader.style.display = 'none';
                if (empty) empty.style.display = 'block';
                document.getElementById('totalPecas').textContent = 'R$ 0,00';
                return;
            }

            let html = '';
            let totalPecas = 0;
            pecas.forEach((p) => {
                const subtotal = (p.peca_preco || 0) * (p.quantidade || 0);
                totalPecas += subtotal;
                html += `<tr>
                    <td>${p.peca_nome || 'Peça #' + p.id_peca}</td>
                    <td class="text-end">${p.quantidade || 0}</td>
                    <td class="text-end">R$ ${formatarMoeda(p.peca_preco || 0)}</td>
                    <td class="text-end">${p.peca_estoque ?? '—'}</td>
                    <td class="text-end">R$ ${formatarMoeda(subtotal)}</td>
                </tr>`;
            });

            document.getElementById('pecasBody').innerHTML = html;
            document.getElementById('totalPecas').textContent = `R$ ${formatarMoeda(totalPecas)}`;
            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';
        } catch (err) {
            console.error(err);
            if (loader) loader.style.display = 'none';
            if (empty) empty.style.display = 'block';
        }
    }

    async function carregarMovimentacoes() {
        const loader = document.getElementById('movimentacoesLoader');
        const content = document.getElementById('movimentacoesContent');
        const empty = document.getElementById('emptyMovimentacoes');

        try {
            if (loader) loader.style.display = 'block';
            if (content) content.style.display = 'none';
            if (empty) empty.style.display = 'none';

            const response = await fetch(`${API_BASE}/ordens-servico/${osId}/pecas/movimentacoes`, { credentials: 'include' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const movimentacoes = await response.json();
            if (!Array.isArray(movimentacoes) || movimentacoes.length === 0) {
                if (loader) loader.style.display = 'none';
                if (empty) empty.style.display = 'block';
                return;
            }

            let html = '';
            movimentacoes.forEach((mov) => {
                const tipoClass = mov.tipo_movimentacao === 'entrada' ? 'tipo-entrada' : 'tipo-saida';
                html += `<tr>
                    <td>${mov.id_movimentacao}</td>
                    <td>Peça #${mov.id_peca}</td>
                    <td><span class="${tipoClass}">${mov.tipo_movimentacao === 'entrada' ? 'Entrada' : 'Saída'}</span></td>
                    <td class="text-end">${mov.quantidade || 0}</td>
                    <td>${formatarData(mov.created_at)}</td>
                </tr>`;
            });

            document.getElementById('movimentacoesBody').innerHTML = html;
            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';
        } catch (err) {
            console.error(err);
            if (loader) loader.style.display = 'none';
            if (empty) empty.style.display = 'block';
        }
    }

    function formatarMoeda(v) { return parseFloat(v || 0).toFixed(2).replace('.', ','); }
    function formatarData(d) {
        if (!d) return 'N/A';
        try { return new Date(d).toLocaleDateString('pt-BR'); } catch { return d; }
    }

    document.addEventListener('DOMContentLoaded', () => {
        if (osId && !isNaN(parseInt(osId, 10))) carregarOrdemServico();
        else {
            document.getElementById('osLoader').classList.remove('active');
            document.getElementById('osError').style.display = 'block';
        }
    });
})();
