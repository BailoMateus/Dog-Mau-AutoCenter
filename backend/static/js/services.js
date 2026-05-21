// services.js — Lógica do wizard de serviços

let selectedServices = [];
let selectedVehicleId = null;
let selectedVehicleName = "";

document.addEventListener('DOMContentLoaded', () => {
    if (typeof userLoggedIn !== 'undefined' && userLoggedIn) {
        fetchUserVehicles();
    }
});

async function fetchUserVehicles() {
    try {
        const response = await fetch('/api/me/veiculos');
        if (!response.ok) throw new Error('Erro ao buscar veículos');
        
        const data = await response.json();
        const vehicles = data.items || [];
        
        document.getElementById('vehicleLoading').classList.add('d-none');
        
        if (vehicles.length === 0) {
            document.getElementById('noVehiclesAlert').classList.remove('d-none');
        } else {
            const select = document.getElementById('userVehicleSelect');
            vehicles.forEach(v => {
                const option = document.createElement('option');
                option.value = v.id_veiculo;
                option.textContent = `${v.placa} - ${v.marca} ${v.modelo}`;
                select.appendChild(option);
            });
            document.getElementById('vehicleSelectionArea').classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error fetching vehicles:', error);
        document.getElementById('vehicleLoading').classList.add('d-none');
        document.getElementById('noVehiclesAlert').classList.remove('d-none');
        document.getElementById('noVehiclesAlert').querySelector('p').textContent = "Erro ao carregar veículos. Tente recarregar a página.";
    }
}

function nextStep(step) {
    if (step === 2) {
        const select = document.getElementById('userVehicleSelect');
        if (!select.value) {
            alert("Por favor, selecione um veículo antes de continuar.");
            return;
        }
        selectedVehicleId = select.value;
        selectedVehicleName = select.options[select.selectedIndex].text;
    }

    if (step === 3 && selectedServices.length === 0) {
        alert("Por favor, selecione pelo menos um serviço antes de continuar.");
        return;
    }

    document.querySelectorAll('.card').forEach(c => c.classList.add('hidden'));
    
    const targetScreen = document.getElementById('screen' + step);
    if(targetScreen) targetScreen.classList.remove('hidden');

    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    
    for(let i = 1; i <= step; i++){
        const stepEl = document.getElementById('step' + i);
        if(stepEl) stepEl.classList.add('active');
    }

    if(step === 3){
        document.getElementById('vehicleSummary').innerText = selectedVehicleName;
        
        const list = document.getElementById('servicesSummaryList');
        list.innerHTML = '';
        let total = 0;
        selectedServices.forEach(s => {
            const li = document.createElement('li');
            li.className = "d-flex justify-content-between mb-1";
            li.innerHTML = `<span>${s.name}</span> <span class="text-secondary">R$ ${parseFloat(s.price).toFixed(2)}</span>`;
            list.appendChild(li);
            total += parseFloat(s.price);
        });
        
        document.getElementById('priceSummary').innerText = `R$ ${total.toFixed(2)}`;
    }
}

function toggleService(element, id, name, price) {
    const checkbox = element.querySelector('.service-checkbox');
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        element.style.borderColor = 'rgba(192, 37, 43)';
        element.style.backgroundColor = 'rgba(192, 37, 43, 0.1)';
        selectedServices.push({ id, name, price: parseFloat(price) });
    } else {
        element.style.borderColor = '#333';
        element.style.backgroundColor = 'transparent';
        selectedServices = selectedServices.filter(s => String(s.id) !== String(id));
    }
    
    updateTotal();
}

function updateTotal() {
    const total = selectedServices.reduce((acc, s) => acc + s.price, 0);
    document.getElementById('step2Total').innerText = `R$ ${total.toFixed(2)}`;
}

async function enviarSolicitacao() {
    const btn = document.getElementById('btnSubmit');
    const spinner = document.getElementById('submitSpinner');
    const icon = document.getElementById('submitIcon');
    const errorDiv = document.getElementById('submitError');
    const observacoes = document.getElementById('observacoes').value;
    
    errorDiv.classList.add('d-none');
    btn.disabled = true;
    spinner.classList.remove('d-none');
    icon.classList.add('d-none');
    
    const total = selectedServices.reduce((acc, s) => acc + s.price, 0);
    
    try {
        // 1. Criar Orçamento
        const orcResponse = await fetch('/orcamentos/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_usuario: userId,
                id_veiculo: parseInt(selectedVehicleId),
                valor_total: total,
                observacoes: observacoes
            })
        });
        
        if (!orcResponse.ok) throw new Error('Falha ao criar orçamento.');
        
        const orcamento = await orcResponse.json();
        const idOrcamento = orcamento.id_orcamento;
        
        // 2. Adicionar Serviços
        for (const s of selectedServices) {
            const itemResponse = await fetch(`/orcamentos/${idOrcamento}/itens/servicos`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_servico: s.id, valor_unitario: s.price })
            });
            if (!itemResponse.ok) throw new Error('Falha ao associar serviço ao orçamento.');
        }
        
        // 3. Sucesso
        const myModal = new bootstrap.Modal(document.getElementById('sucessoModal'));
        myModal.show();
        
    } catch (error) {
        console.error(error);
        errorDiv.textContent = error.message || 'Ocorreu um erro ao processar sua solicitação.';
        errorDiv.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        spinner.classList.add('d-none');
        icon.classList.remove('d-none');
    }
}

function resetForm() {
    selectedServices = [];
    selectedVehicleId = null;
    selectedVehicleName = "";
    document.getElementById('observacoes').value = "";
    
    document.querySelectorAll('.service-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('.service').forEach(el => {
        el.style.borderColor = '#333';
        el.style.backgroundColor = 'transparent';
    });
    
    updateTotal();
    nextStep(1);
}

window.nextStep = nextStep;
window.toggleService = toggleService;
window.enviarSolicitacao = enviarSolicitacao;
window.resetForm = resetForm;
