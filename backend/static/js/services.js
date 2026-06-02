// services.js — fluxo público de contratação de serviços

let selectedServices = [];

function showInlineMessage(el, message, type) {
    if (!el) return;
    el.className = `alert alert-${type || 'warning'} mt-3`;
    el.textContent = message;
    el.classList.remove('d-none');
}

function showStep1Error(message) {
    showInlineMessage(document.getElementById('step1Error'), message, 'warning');
}

function hideInlineMessage(el) {
    if (el) el.classList.add('d-none');
}

function nextStep(step) {
    if (step === 2 && selectedServices.length === 0) {
        showStep1Error('Selecione pelo menos um serviço para continuar.');
        return;
    }
    hideInlineMessage(document.getElementById('step1Error'));
    hideInlineMessage(document.getElementById('submitError'));

    document.querySelectorAll('#screen1, #screen2, #screen3').forEach((c) => c.classList.add('hidden'));

    const targetScreen = document.getElementById('screen' + step);
    if (targetScreen) targetScreen.classList.remove('hidden');

    document.querySelectorAll('.step').forEach((s) => s.classList.remove('active'));
    for (let i = 1; i <= step; i++) {
        const stepEl = document.getElementById('step' + i);
        if (stepEl) stepEl.classList.add('active');
    }

    if (step === 2) {
        renderServicesReview();
    }
}

function toggleService(element, id, name, price) {
    const checkbox = element.querySelector('.service-checkbox');
    checkbox.checked = !checkbox.checked;

    if (checkbox.checked) {
        element.style.borderColor = 'rgba(192, 37, 43)';
        element.style.backgroundColor = 'rgba(192, 37, 43, 0.1)';
        if (!selectedServices.find((s) => String(s.id) === String(id))) {
            selectedServices.push({ id: String(id), name, price: parseFloat(price) });
        }
    } else {
        element.style.borderColor = '#333';
        element.style.backgroundColor = 'transparent';
        selectedServices = selectedServices.filter((s) => String(s.id) !== String(id));
    }

    updateTotal();
    hideInlineMessage(document.getElementById('step1Error'));
}

function updateTotal() {
    const total = selectedServices.reduce((acc, s) => acc + s.price, 0);
    const el = document.getElementById('step1Total');
    if (el) el.innerText = `R$ ${total.toFixed(2)}`;
}

function renderServicesReview() {
    const list = document.getElementById('selectedServicesReview');
    if (!list) return;
    list.innerHTML = '';
    selectedServices.forEach((s) => {
        const li = document.createElement('li');
        li.className = 'd-flex justify-content-between mb-2 border-bottom border-secondary pb-2';
        li.innerHTML = `<span>${s.name}</span><span class="text-danger fw-bold">R$ ${s.price.toFixed(2)}</span>`;
        list.appendChild(li);
    });
}

function prosseguirVeiculo() {
    if (selectedServices.length === 0) {
        showInlineMessage(document.getElementById('submitError'), 'Selecione pelo menos um serviço.', 'warning');
        return;
    }
    if (!userLoggedIn) {
        sessionStorage.setItem('dogmau_pending_services', JSON.stringify(selectedServices));
        window.location.href = '/login?next=' + encodeURIComponent('/servicos');
        return;
    }
    nextStep(3);
}

function populateModelos() {
    const marcaId = document.getElementById('marcaSelect')?.value;
    const modeloSelect = document.getElementById('modeloSelect');
    if (!modeloSelect) return;

    modeloSelect.innerHTML = '<option value="" disabled selected>Selecione o modelo...</option>';
    modeloSelect.disabled = !marcaId;

    if (!marcaId || !modelosPorMarca[marcaId]) return;

    modelosPorMarca[marcaId].forEach((mod) => {
        const opt = document.createElement('option');
        opt.value = mod.id;
        opt.textContent = mod.nome;
        modeloSelect.appendChild(opt);
    });
    modeloSelect.disabled = false;
}

async function enviarSolicitacao() {
    const btn = document.getElementById('btnSubmit');
    const spinner = document.getElementById('submitSpinner');
    const icon = document.getElementById('submitIcon');
    const errorDiv = document.getElementById('submitError');

    const idModelo = document.getElementById('modeloSelect')?.value;
    const cor = document.getElementById('veiculoCor')?.value?.trim();
    const ano = document.getElementById('veiculoAno')?.value;
    const placa = document.getElementById('veiculoPlaca')?.value?.trim().toUpperCase();
    const observacoes = document.getElementById('observacoes')?.value || '';

    hideInlineMessage(errorDiv);

    if (!idModelo || !cor || !ano || !placa) {
        showInlineMessage(errorDiv, 'Preencha marca, modelo, cor, ano e placa do veículo.', 'warning');
        return;
    }

    if (!userLoggedIn || !userId) {
        window.location.href = '/login?next=' + encodeURIComponent('/servicos');
        return;
    }

    btn.disabled = true;
    spinner.classList.remove('d-none');
    icon.classList.add('d-none');

    const total = selectedServices.reduce((acc, s) => acc + s.price, 0);

    try {
        const veiculoRes = await fetch('/api/me/veiculos/resolver', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                id_modelo: parseInt(idModelo, 10),
                placa,
                ano_fabricacao: parseInt(ano, 10),
                cor
            })
        });
        if (!veiculoRes.ok) {
            const err = await veiculoRes.json().catch(() => ({}));
            throw new Error(err.detail || 'Não foi possível registrar o veículo.');
        }
        const veiculo = await veiculoRes.json();

        const orcResponse = await fetch('/orcamentos/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                id_usuario: userId,
                id_veiculo: veiculo.id_veiculo,
                valor_total: total,
                observacoes
            })
        });
        if (!orcResponse.ok) throw new Error('Falha ao criar orçamento.');

        const orcamento = await orcResponse.json();
        const idOrcamento = orcamento.id_orcamento;

        for (const s of selectedServices) {
            const itemResponse = await fetch(`/orcamentos/${idOrcamento}/itens/servicos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ id_servico: parseInt(s.id, 10), valor_unitario: s.price })
            });
            if (!itemResponse.ok) throw new Error('Falha ao associar serviço ao orçamento.');
        }

        sessionStorage.removeItem('dogmau_pending_services');
        const myModal = new bootstrap.Modal(document.getElementById('sucessoModal'));
        myModal.show();
    } catch (error) {
        console.error(error);
        showInlineMessage(errorDiv, error.message || 'Ocorreu um erro ao processar sua solicitação.', 'danger');
    } finally {
        btn.disabled = false;
        spinner.classList.add('d-none');
        icon.classList.remove('d-none');
    }
}

function resetForm() {
    selectedServices = [];
    document.getElementById('observacoes').value = '';
    document.querySelectorAll('.service-checkbox').forEach((cb) => { cb.checked = false; });
    document.querySelectorAll('.service').forEach((el) => {
        el.style.borderColor = '#333';
        el.style.backgroundColor = 'transparent';
    });
    updateTotal();
    nextStep(1);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('marcaSelect')?.addEventListener('change', populateModelos);

    const pending = sessionStorage.getItem('dogmau_pending_services');
    if (pending && userLoggedIn) {
        try {
            selectedServices = JSON.parse(pending);
            if (selectedServices.length > 0) {
                nextStep(3);
            }
        } catch (_) {
            sessionStorage.removeItem('dogmau_pending_services');
        }
    }
});

window.nextStep = nextStep;
window.toggleService = toggleService;
window.prosseguirVeiculo = prosseguirVeiculo;
window.enviarSolicitacao = enviarSolicitacao;
window.resetForm = resetForm;
