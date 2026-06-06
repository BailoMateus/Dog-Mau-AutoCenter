/**
 * profile-edit.js
 * 
 * Gerencia a edição do perfil do usuário com confirmação via modal
 * para cada campo alterado, e também o upload de foto de perfil.
 */

let originalData = {};
let confirmationModal = null;
let currentFieldChanges = {};
let currentUserData = null;

document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    const saveBtn = document.getElementById('saveBtn');

    if (!profileForm) return;

    // Carrega dados do usuário primeiro
    loadUserProfile().then(() => {
        originalData = {
            nome: document.getElementById('nome')?.value || '',
            email: document.getElementById('email')?.value || '',
            telefone: document.getElementById('telefone')?.value || '',
            cpf_cnpj: document.getElementById('cpf_cnpj')?.value || '',
            data_nascimento: document.getElementById('data_nascimento')?.value || ''
        };
    });

    // Cria modal de confirmação
    createConfirmationModal();

    // Listener para o botão de salvar perfil
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

    // Configurar upload de foto de perfil
    setupProfilePhotoUpload();

    // Listener para botão de gerenciar endereços
    const gerenciarEnderecoBtn = document.getElementById('gerenciarEnderecoBtn');
    if (gerenciarEnderecoBtn) {
        gerenciarEnderecoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Redireciona para a aba de endereços dentro do painel
            window.location.href = '/painel?tab=meu_usuario#endereco-management';
            // TODO: Criar modal ou seção para gerenciar endereços
        });
    }
});

/**
 * Carrega dados do perfil do usuário
 */
async function loadUserProfile() {
    try {
        const response = await fetch('/api/me/profile', {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            console.error('Erro ao carregar perfil');
            const loader = document.getElementById('perfilLoader');
            if (loader) loader.style.display = 'none';
            showAlert('danger', 'Não foi possível carregar os dados do perfil. Tente novamente.');
            return;
        }

        currentUserData = await response.json();
        
        // Preenche os campos
        document.getElementById('nome').value = currentUserData.nome || '';
        document.getElementById('email').value = currentUserData.email || '';
        document.getElementById('telefone').value = currentUserData.telefone || '';
        document.getElementById('cpf_cnpj').value = currentUserData.cpf_cnpj || '';
        document.getElementById('data_nascimento').value = currentUserData.data_nascimento || '';

        // Carrega foto de perfil se existir
        if (currentUserData.foto_perfil) {
            const fotoPreview = document.getElementById('fotoPreview');
            if (fotoPreview) {
                fotoPreview.src = currentUserData.foto_perfil;
            }
        }

        // Carrega endereços do usuário
        await loadUserEnderecos();

        // Mostra o formulário
        document.getElementById('profileForm').style.display = 'block';
        document.getElementById('perfilLoader').style.display = 'none';

    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        const loader = document.getElementById('perfilLoader');
        if (loader) loader.style.display = 'none';
        showAlert('danger', 'Erro ao carregar dados do perfil');
    }
}

/**
 * Configura o upload de foto de perfil
 */
function setupProfilePhotoUpload() {
    const fotoPerfil = document.getElementById('fotoPerfil');
    const uploadFotoBtn = document.getElementById('uploadFotoBtn');
    const fotoPreview = document.getElementById('fotoPreview');

    if (!fotoPerfil || !uploadFotoBtn) return;

    // Listener para seleção de arquivo
    fotoPerfil.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        try {
            // Valida o arquivo
            UploadManager.validarImagem(file, {
                maxSize: 2 * 1024 * 1024, // 2MB
                types: ['image/jpeg', 'image/jpg', 'image/png']
            });

            // Gera preview
            const preview = await UploadManager.gerarPreview(file);
            fotoPreview.src = preview;

            // Mostra botão de upload
            uploadFotoBtn.style.display = 'inline-block';

        } catch (error) {
            console.error('Erro ao processar imagem:', error);
            showAlert('danger', 'Erro: ' + error.message);
            fotoPerfil.value = ''; // Limpa o input
        }
    });

    // Listener para botão de upload
    uploadFotoBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        const file = fotoPerfil.files[0];

        if (!file) {
            showAlert('danger', 'Selecione uma imagem primeiro');
            return;
        }

        try {
            // Desabilita o botão durante o upload
            uploadFotoBtn.disabled = true;
            uploadFotoBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Enviando...';

            // Faz o upload
            const response = await UploadManager.uploadFotoPerfil(file);

            // Atualiza a foto de perfil com a resposta
            if (response.foto_perfil) {
                fotoPreview.src = response.foto_perfil;
                currentUserData.foto_perfil = response.foto_perfil;
            }

            // Limpa o input e oculta o botão
            fotoPerfil.value = '';
            uploadFotoBtn.style.display = 'none';
            uploadFotoBtn.disabled = false;
            uploadFotoBtn.innerHTML = '<i class="bi bi-cloud-upload me-1"></i>Enviar Foto';

            showAlert('success', 'Foto de perfil atualizada com sucesso!');

        } catch (error) {
            console.error('Erro ao fazer upload de foto:', error);
            showAlert('danger', 'Erro ao enviar foto: ' + error.message);
            uploadFotoBtn.disabled = false;
            uploadFotoBtn.innerHTML = '<i class="bi bi-cloud-upload me-1"></i>Enviar Foto';
        }
    });
}

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
                        <div class="alert alert-secondary" style="background-color: #111; border-color: #333;">
                            <small>
                                <strong>Valor anterior:</strong> <span id="oldValue" class="text-muted"></span><br>
                                <strong>Novo valor:</strong> <span id="newValue" style="color: #c0252b;"></span>
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
 * Carrega endereços do usuário
 */
async function loadUserEnderecos() {
    try {
        const response = await fetch('/api/me/enderecos', {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            console.warn('Erro ao carregar endereços:', response.status);
            return;
        }

        const enderecos = await response.json();
        const select = document.getElementById('endereco_principal');
        
        if (!select) return;

        // Limpa as opções existentes (exceto a primeira)
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Adiciona os endereços carregados
        if (Array.isArray(enderecos) && enderecos.length > 0) {
            enderecos.forEach(endereco => {
                const option = document.createElement('option');
                option.value = endereco.id_endereco;
                
                // Formata o endereço para exibição
                const rua = endereco.rua || '';
                const numero = endereco.numero || '';
                const cidade = endereco.cidade || '';
                const estado = endereco.estado || '';
                const label = `${rua} ${numero} - ${cidade}, ${estado}`.replace(/\s+/g, ' ').trim();
                
                option.textContent = label || `Endereço #${endereco.id_endereco}`;
                option.dataset.full = JSON.stringify(endereco);
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar endereços:', error);
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
window.loadUserProfile = loadUserProfile;
window.setupProfilePhotoUpload = setupProfilePhotoUpload;
window.loadUserEnderecos = loadUserEnderecos;
