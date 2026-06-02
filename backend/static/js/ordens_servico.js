/**
 * ordens_servico.js — Gerenciamento de OS (admin / mecânico)
 */
(function () {
    const API_BASE = '/ordens-servico';
    const root = document.getElementById('osPainelRoot');
    if (!root) return;

    const currentUserId = parseInt(root.dataset.currentUserId, 10);
    const currentUserRole = root.dataset.currentUserRole || '';

    let ordensCache = [];
    let responsaveisCache = [];
    let osAtribuirId = null;
    let osStatusId = null;

    const STATUS_LABELS = {
        aberta: { text: 'Aberta', class: 'bg-info text-dark' },
        em_andamento: { text: 'Em andamento', class: 'bg-primary' },
        aguardando_peca: { text: 'Aguardando peça', class: 'bg-warning text-dark' },
        concluida: { text: 'Concluída', class: 'bg-success' },
        cancelada: { text: 'Cancelada', class: 'bg-danger' },
    };

    function fetchOpts(method, body) {
        const opts = { method, credentials: 'include', headers: {} };
        if (body !== undefined) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return opts;
    }

    async function api(path, method = 'GET', body) {
        const response = await fetch(`${API_BASE}${path}`, fetchOpts(method, body));
        let data = null;
        try {
            data = await response.json();
        } catch (_) {
            data = null;
        }
        if (!response.ok) {
            const msg = (data && data.detail) ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : `HTTP ${response.status}`;
            throw new Error(msg);
        }
        return data;
    }

    function mostrarAlerta(msg, tipo) {
        const container = document.getElementById('osAlertContainer');
        if (!container) return;
        container.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show small" role="alert">
                ${msg}
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
            </div>`;
        setTimeout(() => { container.innerHTML = ''; }, 5000);
    }

    function formatarData(iso) {
        if (!iso) return '—';
        const d = new Date(iso);
        if (Number.isNaN(d.getTime())) return '—';
        return d.toLocaleDateString('pt-BR');
    }

    function formatarMoeda(v) {
        const n = parseFloat(v);
        if (Number.isNaN(n)) return 'R$ 0,00';
        return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function badgeStatus(status) {
        const cfg = STATUS_LABELS[status] || { text: status, class: 'bg-secondary' };
        return `<span class="badge ${cfg.class}">${cfg.text}</span>`;
    }

    function veiculoLabel(os) {
        const placa = os.veiculo_placa || '—';
        const modelo = os.veiculo_modelo ? ` (${os.veiculo_modelo})` : '';
        return `${placa}${modelo}`;
    }

    function responsavelLabel(os) {
        if (!os.id_usuario) {
            return '<span class="badge bg-secondary">Sem responsável</span>';
        }
        return os.responsavel_nome || `ID ${os.id_usuario}`;
    }

    function setLoading(on) {
        document.getElementById('osLoader').style.display = on ? 'block' : 'none';
        if (on) {
            document.getElementById('osTableWrap').style.display = 'none';
            document.getElementById('osEmpty').style.display = 'none';
            document.getElementById('osError').style.display = 'none';
        }
    }

    function buildQuery() {
        const params = new URLSearchParams();
        const status = document.getElementById('osFiltroStatus').value;
        const resp = document.getElementById('osFiltroResponsavel').value;
        const cliente = document.getElementById('osFiltroCliente').value;
        const di = document.getElementById('osFiltroDataInicio').value;
        const df = document.getElementById('osFiltroDataFim').value;
        const busca = document.getElementById('osFiltroBusca').value.trim();

        if (status) params.set('status', status);
        if (resp !== '') params.set('id_responsavel', resp);
        if (cliente) params.set('id_cliente', cliente);
        if (di) params.set('data_inicio', di);
        if (df) params.set('data_fim', df);
        if (busca) params.set('busca', busca);

        const qs = params.toString();
        return qs ? `/?${qs}` : '/';
    }

    async function carregarResponsaveis() {
        responsaveisCache = await api('/responsaveis-elegiveis');
        const filtro = document.getElementById('osFiltroResponsavel');
        const atribuir = document.getElementById('osAtribuirSelect');
        responsaveisCache.forEach((u) => {
            const label = `${u.nome} (${u.role})`;
            if (filtro) {
                const opt = document.createElement('option');
                opt.value = u.id_usuario;
                opt.textContent = label;
                filtro.appendChild(opt);
            }
            if (atribuir) {
                const opt2 = document.createElement('option');
                opt2.value = u.id_usuario;
                opt2.textContent = label;
                atribuir.appendChild(opt2);
            }
        });
    }

    async function carregarOrdens() {
        setLoading(true);
        try {
            ordensCache = await api(buildQuery());
            renderTabela(ordensCache);
        } catch (err) {
            setLoading(false);
            const errEl = document.getElementById('osError');
            errEl.textContent = 'Erro ao carregar ordens: ' + err.message;
            errEl.style.display = 'block';
        }
    }

    function renderTabela(ordens) {
        setLoading(false);
        const tbody = document.getElementById('osTableBody');
        const wrap = document.getElementById('osTableWrap');
        const empty = document.getElementById('osEmpty');

        if (!ordens || ordens.length === 0) {
            wrap.style.display = 'none';
            empty.style.display = 'block';
            tbody.innerHTML = '';
            return;
        }

        empty.style.display = 'none';
        wrap.style.display = 'block';

        tbody.innerHTML = ordens.map((os) => {
            const acoes = botoesAcao(os);
            return `
                <tr data-os-id="${os.id_os}">
                    <td><a href="/ordem-servico/${os.id_os}" class="text-decoration-none" style="color: rgba(192,37,43);">#${os.id_os}</a></td>
                    <td>${veiculoLabel(os)}</td>
                    <td class="d-none d-lg-table-cell">${os.cliente_nome || '—'}</td>
                    <td>${responsavelLabel(os)}</td>
                    <td>${badgeStatus(os.status)}</td>
                    <td class="d-none d-md-table-cell">${formatarData(os.data_abertura)}</td>
                    <td>${formatarMoeda(os.valor_total)}</td>
                    <td class="text-center text-nowrap">${acoes}</td>
                </tr>`;
        }).join('');
    }

    function botoesAcao(os) {
        const parts = [];
        const st = os.status;

        if (st !== 'concluida' && st !== 'cancelada') {
            if (!os.id_usuario || os.id_usuario === currentUserId || currentUserRole === 'admin') {
                parts.push(`<button type="button" class="btn btn-sm btn-outline-success me-1 os-btn-aceitar" data-id="${os.id_os}" title="Aceitar / assumir"><i class="bi bi-hand-thumbs-up"></i></button>`);
            }
            parts.push(`<button type="button" class="btn btn-sm btn-outline-info me-1 os-btn-atribuir" data-id="${os.id_os}" title="Atribuir"><i class="bi bi-person-plus"></i></button>`);
        }

        if (st === 'aberta') {
            parts.push(`<button type="button" class="btn btn-sm btn-outline-primary me-1 os-btn-iniciar" data-id="${os.id_os}" title="Iniciar"><i class="bi bi-play-fill"></i></button>`);
        }
        if (st !== 'concluida' && st !== 'cancelada') {
            parts.push(`<button type="button" class="btn btn-sm btn-outline-warning me-1 os-btn-status" data-id="${os.id_os}" title="Alterar status"><i class="bi bi-arrow-repeat"></i></button>`);
        }
        if (st === 'em_andamento' || st === 'aguardando_peca') {
            parts.push(`<button type="button" class="btn btn-sm btn-outline-success me-1 os-btn-concluir" data-id="${os.id_os}" title="Concluir"><i class="bi bi-check-lg"></i></button>`);
        }

        return parts.join('') || '<span class="text-muted small">—</span>';
    }

    async function atualizarLinha(idOs) {
        const os = await api(`/${idOs}`);
        const idx = ordensCache.findIndex((o) => o.id_os === idOs);
        if (idx >= 0) {
            ordensCache[idx] = os;
        } else {
            ordensCache.unshift(os);
        }
        renderTabela(ordensCache);
        mostrarAlerta(`OS #${idOs} atualizada com sucesso.`, 'success');
    }

    function abrirStatus(idOs) {
        const os = ordensCache.find((o) => o.id_os === idOs);
        osStatusId = idOs;
        document.getElementById('osStatusIdLabel').textContent = idOs;
        const sel = document.getElementById('osStatusSelect');
        sel.value = os ? os.status : 'aberta';
        document.getElementById('osStatusErro').classList.add('d-none');
        document.getElementById('osStatusModal').classList.remove('d-none');
    }

    function abrirAtribuir(idOs) {
        osAtribuirId = idOs;
        document.getElementById('osAtribuirIdLabel').textContent = idOs;
        document.getElementById('osAtribuirSelect').value = '';
        document.getElementById('osAtribuirErro').classList.add('d-none');
        document.getElementById('osAtribuirModal').classList.remove('d-none');
    }

    function fecharModal(id) {
        document.getElementById(id).classList.add('d-none');
    }

    document.getElementById('osBtnFiltrar')?.addEventListener('click', carregarOrdens);
    document.getElementById('osBtnRecarregar')?.addEventListener('click', carregarOrdens);
    document.getElementById('osFiltroBusca')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') carregarOrdens();
    });

    document.getElementById('osBtnConfirmarStatus')?.addEventListener('click', async () => {
        const novo = document.getElementById('osStatusSelect').value;
        const erro = document.getElementById('osStatusErro');
        const os = ordensCache.find((o) => o.id_os === osStatusId);
        if (os && novo === os.status) {
            fecharModal('osStatusModal');
            return;
        }
        try {
            if (novo === 'concluida') {
                await api(`/${osStatusId}/concluir`, 'POST');
            } else {
                await api(`/${osStatusId}/status`, 'PATCH', { status: novo });
            }
            fecharModal('osStatusModal');
            await atualizarLinha(osStatusId);
        } catch (err) {
            erro.textContent = err.message;
            erro.classList.remove('d-none');
        }
    });

    document.getElementById('osBtnConfirmarAtribuir')?.addEventListener('click', async () => {
        const idUsuario = document.getElementById('osAtribuirSelect').value;
        const erro = document.getElementById('osAtribuirErro');
        if (!idUsuario) {
            erro.textContent = 'Selecione um responsável.';
            erro.classList.remove('d-none');
            return;
        }
        try {
            await api(`/${osAtribuirId}/atribuir-mecanico`, 'PATCH', { id_usuario: parseInt(idUsuario, 10) });
            fecharModal('osAtribuirModal');
            await atualizarLinha(osAtribuirId);
        } catch (err) {
            erro.textContent = err.message;
            erro.classList.remove('d-none');
        }
    });

    document.getElementById('osTableBody')?.addEventListener('click', async (e) => {
        const btn = e.target.closest('button[data-id]');
        if (!btn) return;
        const idOs = parseInt(btn.dataset.id, 10);

        try {
            if (btn.classList.contains('os-btn-aceitar')) {
                await api(`/${idOs}/aceitar`, 'POST');
                await atualizarLinha(idOs);
            } else if (btn.classList.contains('os-btn-atribuir')) {
                abrirAtribuir(idOs);
            } else if (btn.classList.contains('os-btn-iniciar')) {
                await api(`/${idOs}/iniciar`, 'POST');
                await atualizarLinha(idOs);
            } else if (btn.classList.contains('os-btn-concluir')) {
                if (!confirm(`Concluir a OS #${idOs}?`)) return;
                await api(`/${idOs}/concluir`, 'POST');
                await atualizarLinha(idOs);
            } else if (btn.classList.contains('os-btn-status')) {
                abrirStatus(idOs);
            }
        } catch (err) {
            mostrarAlerta(err.message, 'danger');
        }
    });

    window.OsGerenciamento = { fecharModal, carregarOrdens };

    (async function init() {
        try {
            await carregarResponsaveis();
            await carregarOrdens();
        } catch (err) {
            setLoading(false);
            document.getElementById('osError').textContent = err.message;
            document.getElementById('osError').style.display = 'block';
        }
    })();
})();
