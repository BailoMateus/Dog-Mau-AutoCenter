// services.js — Lógica do wizard de serviços (extraído do inline de services.html)

let selectedService = "";
let selectedPrice = "";

function nextStep(step) {
    document.querySelectorAll('.card').forEach(c => c.classList.add('hidden'));
    document.getElementById('screen' + step).classList.remove('hidden');

    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.getElementById('step' + step).classList.add('active');

    if (step === 3) {
        document.getElementById('serviceName').innerText = selectedService;
        document.getElementById('price').innerText = selectedPrice;
    }
}

function selectService(name, price) {
    selectedService = name;
    selectedPrice = price;
}
