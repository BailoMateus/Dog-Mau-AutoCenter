// services.js — Lógica do wizard de serviços

let selectedService = "";
let selectedPrice = "";

function updateModels() {
    const brandId = document.getElementById('brandSelect').value;
    const modelSelect = document.getElementById('modelSelect');
    
    modelSelect.innerHTML = '<option value="" disabled selected>Selecione um modelo...</option>';
    
    // modelosPorMarca is defined globally in services.html
    if(typeof modelosPorMarca !== 'undefined' && modelosPorMarca[brandId]) {
        modelosPorMarca[brandId].forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.nome;
            modelSelect.appendChild(option);
        });
    }
}

function nextStep(step) {
    if (step === 3 && !selectedService) {
        alert("Por favor, selecione um serviço na lista antes de continuar.");
        return;
    }

    document.querySelectorAll('.card').forEach(c => c.classList.add('hidden'));
    document.getElementById('screen' + step).classList.remove('hidden');

    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    
    for(let i = 1; i <= step; i++){
        document.getElementById('step' + i).classList.add('active');
    }

    if(step === 3){
        const brandSelect = document.getElementById('brandSelect');
        const modelSelect = document.getElementById('modelSelect');
        const brandName = brandSelect.options[brandSelect.selectedIndex].text;
        const modelName = modelSelect.options[modelSelect.selectedIndex].text;

        document.getElementById('vehicle').innerText = `${brandName} ${modelName}`;
        document.getElementById('serviceName').innerText = selectedService;
        document.getElementById('price').innerText = selectedPrice;
    }
}

function selectService(element, name, price){
    selectedService = name;
    selectedPrice = price;
    
    document.querySelectorAll('.service').forEach(el => {
        el.style.borderColor = '#333';
        el.style.backgroundColor = 'transparent';
    });
    
    element.style.borderColor = 'rgba(192, 37, 43)';
    element.style.backgroundColor = 'rgba(192, 37, 43, 0.1)';
}

function enviarSolicitacao() {
    // Exibe modal do Bootstrap
    const myModal = new bootstrap.Modal(document.getElementById('sucessoModal'));
    myModal.show();
}

function resetForm() {
    selectedService = "";
    selectedPrice = "";
    document.getElementById('observacoes').value = "";
    document.querySelectorAll('.service').forEach(el => {
        el.style.borderColor = '#333';
        el.style.backgroundColor = 'transparent';
    });
    nextStep(1);
}

window.updateModels = updateModels;
window.nextStep = nextStep;
window.selectService = selectService;
window.enviarSolicitacao = enviarSolicitacao;
window.resetForm = resetForm;
