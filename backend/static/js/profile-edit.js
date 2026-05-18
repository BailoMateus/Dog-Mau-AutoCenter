/**
 * profile-edit.js
 * 
 * Gerencia a edição do perfil do usuário com confirmação via modal
 * para cada campo alterado.
 */

let originalData = {};
let confirmationModal = null;
let currentFieldChanges = {};

document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    const saveBtn = document.getElementById('saveBtn');

    if (!profileForm) return;

    // Armazena valores originais
    originalData = {
        nome: document.getElementById('nome')?.value || '',
        email: document.getElementById('email')?.value || '',
        telefone: document.getElementById('telefone')?.value || '',
        cpf_cnpj: document.getElementById('cpf_cnpj')?.value || '',
        data_nascimento: document.getElementById('data_nascimento')?.value || ''
    };

    // Cria modal de confirmação
    createConfirmationModal();

    // Listener para o botão de salvar
    if (saveBtn) {
        saveBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleSaveProfile();
        });
    }

    // Listener para reset form
    const resetBtn = profileForm.querySelector('button[type="reset"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Recarrega os valores originais
            document.getElementById('nome').value = originalData.nome;
            document.getElementById('email').value = originalData.email;
            document.getElementById('telefone').value = originalData.telefone;
            document.getElementById('cpf_cnpj').value = originalData.cpf_cnpj;
            document.getElementById('data_nascimento').value = originalData.data_nascimento;
        });
    }
});

/**
 * Cria o modal de confirmação
 */
function createConfirmationModal() {
    const modalHtml = `
        <div class="modal fade" id="confirmationModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark border-secondary">
                    <div class="modal-header border-secondary">
                        <h5 class="modal-title text-white">
                            <i class="bi bi-exclamation-circle me-2" style="color: #c0252b;"></i>
                            Confirmar Alteração
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-white">
                        <p class="mb-3">Deseja realmente alterar <strong id="fieldName"></strong>?</p>
                        <div class="alert alert-info" style="background-color: #1a3a3a; border-color: #555;">
                            <small>
                                <strong>Valor anterior:</strong> <span id="oldValue" class="text-muted"></span><br>
                                <strong>Novo valor:</strong> <span id="newValue" style="color: #4fc3f7;"></span>
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer border-secondary">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle me-1"></i>Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" id="confirmBtn">
                            <i class="bi bi-check-circle me-1"></i>Confirmar Alteração
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Injeta modal no DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
}

/**
 * Detecta mudanças e pede confirmação
 */
function handleSaveProfile() {
    const currentData = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        telefone: document.getElementById('telefone').value,
        cpf_cnpj: document.getElementById('cpf_cnpj').value,
        data_nascimento: document.getElementById('data_nascimento').value
    };

    // Encontra mudanças
    const changes = {};
    for (let key in currentData) {
        if (currentData[key] !== originalData[key]) {
            changes[key] = currentData[key];
        }
    }

    if (Object.keys(changes).length === 0) {
        showAlert('info', 'Nenhuma alteração detectada.');
        return;
    }

    // Se houver apenas uma mudança, pede confirmação direto
    if (Object.keys(changes).length === 1) {
        const field = Object.keys(changes)[0];
        confirmFieldChange(field, originalData[field], changes[field]);
    } else {
        // Se houver múltiplas mudanças, pede confirmação para cada uma
        confirmMultipleChanges(changes);
    }
}

/**
 * Confirma uma mudança individual
 */
function confirmFieldChange(field, oldValue, newValue) {
    currentFieldChanges = { [field]: newValue };

    const fieldLabels = {
        nome: 'Nome',
        email: 'E-mail',
        telefone: 'Telefone',
        cpf_cnpj: 'CPF/CNPJ',
        data_nascimento: 'Data de Nascimento'
    };

    document.getElementById('fieldName').textContent = fieldLabels[field] || field;
    document.getElementById('oldValue').textContent = oldValue || '(vazio)';
    document.getElementById('newValue').textContent = newValue || '(vazio)';

    // Remove listener anterior
    const oldBtn = document.getElementById('confirmBtn');
    const newBtn = oldBtn.cloneNode(true);
    oldBtn.parentNode.replaceChild(newBtn, oldBtn);

    // Novo listener
    document.getElementById('confirmBtn').addEventListener('click', () => {
        submitProfileChanges(currentFieldChanges);
        confirmationModal.hide();
    });

    confirmationModal.show();
}

/**
 * Confirma múltiplas mudanças uma por uma
 */
function confirmMultipleChanges(changes) {
    const fields = Object.keys(changes);
    let currentIndex = 0;

    function confirmNextField() {
        if (currentIndex < fields.length) {
            const field = fields[currentIndex];
            currentFieldChanges = { [field]: changes[field] };
            confirmFieldChange(field, originalData[field], changes[field]);
            currentIndex++;
        } else {
            // Todas as confirmações feitas
            showAlert('success', 'Todas as alterações foram salvas com sucesso!');
            location.reload(); // Recarrega a página
        }
    }

    // Inicia a confirmação da primeira alteração
    const fieldLabels = {
        nome: 'Nome',
        email: 'E-mail',
        telefone: 'Telefone',
        cpf_cnpj: 'CPF/CNPJ',
        data_nascimento: 'Data de Nascimento'
    };

    const field = fields[0];
    document.getElementById('fieldName').textContent = fieldLabels[field] || field;
    document.getElementById('oldValue').textContent = originalData[field] || '(vazio)';
    document.getElementById('newValue').textContent = changes[field] || '(vazio)';

    const oldBtn = document.getElementById('confirmBtn');
    const newBtn = oldBtn.cloneNode(true);
    oldBtn.parentNode.replaceChild(newBtn, oldBtn);

    document.getElementById('confirmBtn').addEventListener('click', () => {
        submitProfileChanges(currentFieldChanges);
        confirmationModal.hide();
        // Aguarda um pouco e confirma o próximo
        setTimeout(confirmNextField, 800);
    });

    confirmationModal.show();
}

/**
 * Submete as alterações para o servidor
 */
async function submitProfileChanges(changes) {
    try {
        const response = await fetch('/api/me/profile', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(changes)
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Erro ao atualizar perfil:', error);
            showAlert('danger', error.detail || 'Erro ao salvar alterações');
            return;
        }

        const updatedUser = await response.json();
        
        // Atualiza os valores originais
        for (let key in changes) {
            originalData[key] = changes[key];
            if (document.getElementById(key)) {
                document.getElementById(key).value = changes[key];
            }
        }

        showAlert('success', 'Campo alterado com sucesso!');
    } catch (error) {
        console.error('Erro:', error);
        showAlert('danger', 'Erro ao salvar alterações. Tente novamente.');
    }
}

/**
 * Mostra alertas para o usuário
 */
function showAlert(type, message) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Injeta o alerta no topo do formulário
    const form = document.getElementById('profileForm');
    if (form) {
        form.parentNode.insertBefore(alertContainer, form);
    }

    // Remove o alerta após 5 segundos
    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}

window.handleSaveProfile = handleSaveProfile;
window.confirmFieldChange = confirmFieldChange;
window.submitProfileChanges = submitProfileChanges;
