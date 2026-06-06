/**
 * profile-edit.js
 * * Gerencia a edição do perfil do usuário com confirmação via modal
 * para cada campo alterado, e também o upload de foto de perfil.
 */

let originalData = {};
let confirmationModal = null;
let currentFieldChanges = {};
let currentUserData = null;

// Mapa de labels amigáveis para exibição nos modais de confirmação
const fieldLabels = {
    nome: 'Nome',
    email: 'E-mail',
    telefone: 'Telefone',
    cpf_cnpj: 'CPF/CNPJ',
    data_nascimento: 'Data de Nascimento'
};

document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    const saveBtn = document.getElementById('saveBtn');

    if (!profileForm) return;

    // Carrega dados do usuário primeiro
    loadUserProfile().then(() => {
        captureOriginalData();
    });

    // Cria modal de confirmação dinamicamente no DOM
    createConfirmationModal();

    // Listener para o botão de salvar perfil
    if (saveBtn) {
        saveBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleSaveProfile();
        });
    }

    // Listener para reset form (Restaurar valores originais da sessão)
    const resetBtn = profileForm.querySelector('button[type="reset"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            restoreOriginalValues();
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
        });
    }

    // Ouvinte para renderizar os dados por extenso do endereço principal ao mudar a seleção
    const selectEndereco = document.getElementById('endereco_principal');
    if (selectEndereco) {
        selectEndereco.addEventListener('change', function() {
            renderActiveAddressCard(this);
        });
    }
});

/**
 * Captura o estado atual dos inputs para controle de histórico/mudanças
 */
function captureOriginalData() {
    originalData = {
        nome: document.getElementById('nome')?.value || '',
        email: document.getElementById('email')?.value || '',
        telefone: document.getElementById('telefone')?.value || '',
        cpf_cnpj: document.getElementById('cpf_cnpj')?.value || '',
        data_nascimento: document.getElementById('data_nascimento')?.value || ''
    };
}

/**
 * Restaura o formulário para os valores coletados no último carregamento bem-sucedido
 */
function restoreOriginalValues() {
    for (const key in originalData) {
        const input = document.getElementById(key);
        if (input) {
            input.value = originalData[key];
        }
    }
    // Re-sincroniza o card de endereço se aplicável
    const selectEndereco = document.getElementById('endereco_principal');
    if (selectEndereco) {
        renderActiveAddressCard(selectEndereco);
    }
}

/**
 * Carrega dados do perfil do usuário através de /api/me/profile
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
        
        if (document.getElementById('nome')) document.getElementById('nome').value = currentUserData.nome || '';
        if (document.getElementById('email')) document.getElementById('email').value = currentUserData.email || '';
        if (document.getElementById('telefone')) document.getElementById('telefone').value = currentUserData.telefone || '';
        if (document.getElementById('cpf_cnpj')) document.getElementById('cpf_cnpj').value = currentUserData.cpf_cnpj || '';
        if (document.getElementById('data_nascimento')) document.getElementById('data_nascimento').value = currentUserData.data_nascimento || '';

        // Carrega foto de perfil se existir na resposta
        const fotoPreview = document.getElementById('fotoPreview');
        if (fotoPreview) {
            if (currentUserData.foto_perfil) {
                fotoPreview.src = currentUserData.foto_perfil;
            } else {
                fotoPreview.src = '/static/images/default-avatar.png'; // Fallback visual limpo
            }
        }

        // Carrega e renderiza a seção de endereços do usuário
        await loadUserEnderecos();

        // Altera visibilidade do esqueleto da página
        const form = document.getElementById('profileForm');
        const loader = document.getElementById('perfilLoader');
        if (form) form.style.display = 'block';
        if (loader) loader.style.display = 'none';

    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        const loader = document.getElementById('perfilLoader');
        if (loader) loader.style.display = 'none';
        showAlert('danger', 'Erro ao carregar dados do perfil');
    }
}

/**
 * Configura o upload de foto de perfil de ponta a ponta
 */
function setupProfilePhotoUpload() {
    const fotoPerfil = document.getElementById('fotoPerfil');
    const uploadFotoBtn = document.getElementById('uploadFotoBtn');
    const fotoPreview = document.getElementById('fotoPreview');

    if (!fotoPerfil || !uploadFotoBtn) return;

    // Listener para seleção de arquivo e validação de preview temporário
    fotoPerfil.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        try {
            // Valida o arquivo se o UploadManager global estiver ativo
            if (typeof UploadManager !== 'undefined' && UploadManager.validarImagem) {
                UploadManager.validarImagem(file, {
                    maxSize: 2 * 1024 * 1024, // 2MB
                    types: ['image/jpeg', 'image/jpg', 'image/png']
                });
            } else {
                // Fallback de validação inline nativa
                if (file.size > 2 * 1024 * 1024) throw new Error("A imagem não deve exceder 2MB.");
                if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
                    throw new Error("Formato de arquivo inválido. Use JPG, JPEG ou PNG.");
                }
            }

            // Exibe o preview local imediatamente para o usuário
            if (typeof UploadManager !== 'undefined' && UploadManager.gerarPreview) {
                fotoPreview.src = await UploadManager.gerarPreview(file);
            } else {
                fotoPreview.src = URL.createObjectURL(file);
            }

            // Mostra botão de upload definitivo
            uploadFotoBtn.style.display = 'inline-block';

        } catch (error) {
            console.error('Erro ao processar imagem:', error);
            showAlert('danger', 'Erro: ' + error.message);
            fotoPerfil.value = ''; // Limpa o input
        }
    });

    // Listener para envio via requisição multipart para /api/me/foto-perfil
    uploadFotoBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        const file = fotoPerfil.files[0];

        if (!file) {
            showAlert('danger', 'Selecione uma imagem primeiro');
            return;
        }

        try {
            uploadFotoBtn.disabled = true;
            uploadFotoBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Enviando...';

            let responseData;
            // Verifica se possui gerenciador externo ou injeta chamada direta assíncrona
            if (typeof UploadManager !== 'undefined' && UploadManager.uploadFotoPerfil) {
                responseData = await UploadManager.uploadFotoPerfil(file);
            } else {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/me/foto-perfil', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Falha no upload com o servidor.');
                responseData = await response.json();
            }

            // Atualiza o preview e o payload de sessão global com o caminho retornado
            if (responseData && responseData.foto_perfil) {
                fotoPreview.src = responseData.foto_perfil;
                if (currentUserData) currentUserData.foto_perfil = responseData.foto_perfil;
                showAlert('success', 'Foto de perfil atualizada com sucesso!');
            }

            fotoPerfil.value = '';
            uploadFotoBtn.style.display = 'none';
            uploadFotoBtn.disabled = false;
            uploadFotoBtn.innerHTML = '<i class="bi bi-cloud-upload me-1"></i>Enviar Foto';

        } catch (error) {
            console.error('Erro ao fazer upload de foto:', error);
            showAlert('danger', 'Erro ao enviar foto: ' + error.message);
            uploadFotoBtn.disabled = false;
            uploadFotoBtn.innerHTML = '<i class="bi bi-cloud-upload me-1"></i>Enviar Foto';
        }
    });
}

/**
 * Cria a estrutura HTML do modal de confirmação
 */
function createConfirmationModal() {
    if (document.getElementById('confirmationModal')) return;

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

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
}

/**
 * Compara modificações e gerencia o fluxo de confirmação unitário ou sequencial
 */
function handleSaveProfile() {
    const currentData = {
        nome: document.getElementById('nome')?.value || '',
        email: document.getElementById('email')?.value || '',
        telefone: document.getElementById('telefone')?.value || '',
        cpf_cnpj: document.getElementById('cpf_cnpj')?.value || '',
        data_nascimento: document.getElementById('data_nascimento')?.value || ''
    };

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

    if (Object.keys(changes).length === 1) {
        const field = Object.keys(changes)[0];
        confirmFieldChange(field, originalData[field], changes[field]);
    } else {
        confirmMultipleChanges(changes);
    }
}

/**
 * Abre modal vinculando alteração de um único campo
 */
function confirmFieldChange(field, oldValue, newValue) {
    currentFieldChanges = { [field]: newValue };

    document.getElementById('fieldName').textContent = fieldLabels[field] || field;
    document.getElementById('oldValue').textContent = oldValue || '(vazio)';
    document.getElementById('newValue').textContent = newValue || '(vazio)';

    const oldBtn = document.getElementById('confirmBtn');
    const newBtn = oldBtn.cloneNode(true);
    oldBtn.parentNode.replaceChild(newBtn, oldBtn);

    document.getElementById('confirmBtn').addEventListener('click', async () => {
        await submitProfileChanges(currentFieldChanges);
        confirmationModal.hide();
    });

    confirmationModal.show();
}

/**
 * Controla pilha de múltiplos campos alterados iterando confirmações sequenciais
 */
function confirmMultipleChanges(changes) {
    const fields = Object.keys(changes);
    let currentIndex = 0;

    async function confirmNextField() {
        if (currentIndex < fields.length) {
            const field = fields[currentIndex];
            currentFieldChanges = { [field]: changes[field] };
            currentIndex++;
            confirmFieldChange(field, originalData[field], changes[field]);
            
            // Re-vincula botão para a próxima chamada recursiva controlada por temporizador
            const oldBtn = document.getElementById('confirmBtn');
            const newBtn = oldBtn.cloneNode(true);
            oldBtn.parentNode.replaceChild(newBtn, oldBtn);
            
            document.getElementById('confirmBtn').addEventListener('click', async () => {
                await submitProfileChanges(currentFieldChanges);
                confirmationModal.hide();
                setTimeout(confirmNextField, 400);
            });
        } else {
            showAlert('success', 'Todas as alterações foram salvas com sucesso!');
            captureOriginalData();
        }
    }

    confirmNextField();
}

/**
 * Transmite alterações consolidadas via PATCH para /api/me/profile
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

        // Atualiza a memória de dados locais para evitar alertas duplicados
        for (let key in changes) {
            originalData[key] = changes[key];
            const input = document.getElementById(key);
            if (input) input.value = changes[key];
        }

        showAlert('success', 'Informações atualizadas com sucesso!');
    } catch (error) {
        console.error('Erro:', error);
        showAlert('danger', 'Erro ao salvar alterações. Tente novamente.');
    }
}

/**
 * Carrega a lista de endereços do usuário e gerencia exibição textual expandida
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

        // Limpa opções voláteis mantendo o placeholder inicial
        while (select.options.length > 1) {
            select.remove(1);
        }

        if (Array.isArray(enderecos) && enderecos.length > 0) {
            enderecos.forEach(endereco => {
                const option = document.createElement('option');
                option.value = endereco.id_endereco;
                
                const rua = endereco.rua || '';
                const numero = endereco.numero || '';
                const cidade = endereco.cidade || '';
                const estado = endereco.estado || '';
                const label = `${rua}, ${numero} - ${cidade}/${estado}`.replace(/\s+/g, ' ').trim();
                
                option.textContent = label || `Endereço #${endereco.id_endereco}`;
                
                // Vincula o payload completo como string no dataset da tag option
                option.dataset.full = JSON.stringify(endereco);
                
                // Se for marcado explicitamente como principal pelo back, define como selecionado por padrão
                if (endereco.principal || endereco.is_main) {
                    option.selected = true;
                }
                
                select.appendChild(option);
            });
        }

        // Renderiza o endereço por extenso na tela baseado na opção ativa
        renderActiveAddressCard(select);

    } catch (error) {
        console.error('Erro ao carregar endereços:', error);
    }
}

/**
 * REQUISITO 4: Renderiza textualmente os dados detalhados do endereço ativo
 */
function renderActiveAddressCard(selectElement) {
    let containerVisual = document.getElementById('endereco_detalhado_container');
    
    // Se não existir o container na tela, cria dinamicamente abaixo do select para evitar quebras de UI
    if (!containerVisual) {
        containerVisual = document.createElement('div');
        containerVisual.id = 'endereco_detalhado_container';
        containerVisual.className = 'mt-3 p-3 rounded text-white border border-secondary';
        containerVisual.style.backgroundColor = '#151515';
        selectElement.parentNode.appendChild(containerVisual);
    }

    const selectedOption = selectElement.options[selectElement.selectedIndex];
    
    if (!selectedOption || !selectedOption.value || selectedOption.value === "") {
        containerVisual.innerHTML = `
            <div class="text-muted text-center py-2">
                <i class="bi bi-geo-alt me-1"></i> Nenhum endereço cadastrado ou selecionado como principal.
            </div>`;
        return;
    }

    try {
        const data = JSON.parse(selectedOption.dataset.full);
        containerVisual.innerHTML = `
            <div class="d-flex align-items-start gap-2">
                <i class="bi bi-geo-alt-fill text-danger mt-1" style="font-size: 1.2rem;"></i>
                <div>
                    <h6 class="mb-1 text-white fw-bold">Endereço de Entrega Principal</h6>
                    <p class="mb-0 text-muted small" style="line-height: 1.5;">
                        <strong>Logradouro:</strong> ${data.rua || ''}, Nº ${data.numero || 'S/N'}<br>
                        ${data.complemento ? `<strong>Complemento:</strong> ${data.complemento}<br>` : ''}
                        <strong>Bairro:</strong> ${data.bairro || ''} | <strong>CEP:</strong> ${data.cep || ''}<br>
                        <strong>Cidade/Estado:</strong> ${data.cidade || ''} - ${data.estado || ''}
                    </p>
                </div>
            </div>
        `;
    } catch (e) {
        containerVisual.innerHTML = `<div class="text-muted small">${selectedOption.textContent}</div>`;
    }
}

/**
 * Exibe alertas flutuantes associados ao formulário
 */
function showAlert(type, message) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show text-white border-0`;
    alertContainer.setAttribute('role', 'alert');
    alertContainer.style.backgroundColor = type === 'success' ? '#198754' : type === 'danger' ? '#dc3545' : '#0dcaf0';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;

    const form = document.getElementById('profileForm');
    if (form) {
        form.parentNode.insertBefore(alertContainer, form);
    }

    setTimeout(() => {
        alertContainer.remove();
    }, 5000);
}

// Escopo global para funções injetadas via manipuladores em linha (onclick)
window.handleSaveProfile = handleSaveProfile;
window.confirmFieldChange = confirmFieldChange;
window.submitProfileChanges = submitProfileChanges;
window.loadUserProfile = loadUserProfile;
window.setupProfilePhotoUpload = setupProfilePhotoUpload;
window.loadUserEnderecos = loadUserEnderecos;