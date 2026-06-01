/**
 * ordem_servico_detail.js
 * Integração com endpoints de Ordem de Serviço do backend
 */

(function() {
    const API_BASE = '';
    const osId = document.body.getAttribute('data-os-id') ||
                 (new URLSearchParams(window.location.search).get('id')) ||
                 window.location.pathname.split('/').filter(Boolean).pop();

    let osData = null;

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

            osData = await response.json();
            await exibirOrdemServico(osData);

            await Promise.all([
                carregarServicos(),
                carregarPecas(),
                carregarMovimentacoes()
            ]);

            if (loader) loader.classList.remove('active');
            if (content) content.style.display = 'block';

        } catch (err) {
            console.error('Erro ao carregar OS:', err);
            if (loader) loader.classList.remove('active');
            if (errorEl) errorEl.style.display = 'block';
        }
    }

    async function exibirOrdemServico(os) {
        document.getElementById('osId').textContent = os.id_os || osId;

        let veiculoLabel = `Veículo #${os.id_veiculo}`;
        try {
            const vRes = await fetch(`${API_BASE}/api/veiculos/${os.id_veiculo}`, { credentials: 'include' });
            if (vRes.ok) {
                const v = await vRes.json();
                veiculoLabel = `${v.placa || ''} — ${v.cor || ''} (${v.ano_fabricacao || ''})`.trim();
            }
        } catch (_) { /* mantém fallback */ }

        let mecanicoLabel = os.mecanico_nome || `Mecânico #${os.id_usuario}`;
        if (!os.mecanico_nome && os.id_usuario) {
            try {
                const uRes = await fetch(`${API_BASE}/api/users/${os.id_usuario}`, { credentials: 'include' });
                if (uRes.ok) {
                    const u = await uRes.json();
                    mecanicoLabel = u.nome || mecanicoLabel;
                }
            } catch (_) { /* mantém fallback */ }
        }

        document.getElementById('osVeiculo').textContent = veiculoLabel;
        document.getElementById('osMecanico').textContent = mecanicoLabel;
        document.getElementById('osDescricao').textContent = os.descricao_problema || '—';

        if (os.data_abertura) {
            document.getElementById('osDataAbertura').textContent = formatarData(os.data_abertura);
        }
        if (os.data_conclusao) {
            document.getElementById('osDataConclusao').textContent = formatarData(os.data_conclusao);
        } else {
            document.getElementById('osDataConclusao').textContent = 'Não concluída';
        }

        const statusBadge = document.getElementById('osStatusBadge');
        statusBadge.textContent = (os.status || 'aberta').toUpperCase();
        statusBadge.className = `os-status status-${os.status || 'aberta'}`;

        setupStatusControl(os);
    }

    function setupStatusControl(os) {
        const wrap = document.getElementById('osStatusControl');
        if (!wrap) return;

        const canChange = !os.id_orcamento || os.orcamento_status === 'aprovado';
        wrap.innerHTML = '';

        if (!canChange) {
            wrap.innerHTML = '<p class="text-warning small mb-0">Alteração de status disponível após aprovação do orçamento.</p>';
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
        btn.className = 'btn btn-sm btn-danger ms-2';
        btn.textContent = 'Atualizar';
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
                if (window.UINotification) {
                    UINotification.toast('Status atualizado com sucesso.', 'success');
                }
                carregarOrdemServico();
            } catch (e) {
                if (window.UINotification) {
                    UINotification.toast(e.message, 'error');
                } else {
                    alert(e.message);
                }
            }
        });

        wrap.appendChild(select);
        wrap.appendChild(btn);
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

            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';

        } catch (err) {
            console.error('Erro ao carregar serviços:', err);
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

            const totalServicos = parseFloat(document.getElementById('totalServicos').textContent.replace('R$ ', '').replace(',', '.')) || 0;
            const totalOS = totalServicos + totalPecas;
            document.getElementById('totalOS').textContent = `R$ ${formatarMoeda(totalOS)}`;

            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';

        } catch (err) {
            console.error('Erro ao carregar peças:', err);
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
            if (loader) loader.style.display = 'none';
            if (content) content.style.display = 'block';

        } catch (err) {
            console.error('Erro ao carregar movimentações:', err);
            if (loader) loader.style.display = 'none';
            if (empty) empty.style.display = 'block';
        }
    }

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

    document.addEventListener('DOMContentLoaded', () => {
        if (osId && !isNaN(parseInt(osId, 10))) {
            carregarOrdemServico();
        } else {
            console.error('OS ID não encontrado na URL');
            const loader = document.getElementById('osLoader');
            const errorEl = document.getElementById('osError');
            if (loader) loader.style.display = 'none';
            if (errorEl) errorEl.style.display = 'block';
        }
    });
})();
