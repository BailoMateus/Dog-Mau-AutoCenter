/**
 * upload-utils.js
 * Utilitários para upload de imagens para produtos, peças e perfil
 */

class UploadManager {
    /**
     * Upload de imagem de produto
     * @param {File} file - Arquivo a enviar
     * @param {Object} produtoData - Dados do produto {nome, descricao, preco, quantidade_estoque}
     * @returns {Promise<Object>} - Resposta da API
     */
    static async uploadProdutoComImagem(file, produtoData) {
        const formData = new FormData();
        formData.append('nome', produtoData.nome);
        formData.append('descricao', produtoData.descricao || '');
        formData.append('preco', produtoData.preco);
        formData.append('quantidade_estoque', produtoData.quantidade_estoque || 0);
        formData.append('imagem_produto', file);

        try {
            const response = await fetch('/api/produtos', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao fazer upload de produto:', error);
            throw error;
        }
    }

    /**
     * Upload de imagem de peça
     * @param {File} file - Arquivo a enviar
     * @param {Object} pecaData - Dados da peça {nome, descricao, preco, quantidade_estoque}
     * @returns {Promise<Object>} - Resposta da API
     */
    static async uploadPecaComImagem(file, pecaData) {
        const formData = new FormData();
        formData.append('nome', pecaData.nome);
        formData.append('descricao', pecaData.descricao || '');
        formData.append('preco', pecaData.preco);
        formData.append('quantidade_estoque', pecaData.quantidade_estoque || 0);
        formData.append('imagem_peca', file);

        try {
            const response = await fetch('/api/pecas', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao fazer upload de peça:', error);
            throw error;
        }
    }

    /**
     * Upload de foto de perfil baseado na sessão do usuário logado (/api/me)
     * @param {File} file - Arquivo a enviar
     * @returns {Promise<Object>} - Resposta da API
     */
    static async uploadFotoPerfil(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/me/foto-perfil', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao fazer upload de foto de perfil:', error);
            throw error;
        }
    }

    /**
     * Validar arquivo de imagem de acordo com as travas do backend
     * @param {File} file - Arquivo a validar
     * @param {Object} opcoes - {maxSize: bytes, types: [mime types]}
     * @returns {boolean} - Válido ou não
     */
    static validarImagem(file, opcoes = {}) {
        // Alinhado com o backend: Máximo 2MB e apenas JPEG/PNG
        const maxSize = opcoes.maxSize || 2 * 1024 * 1024; 
        const tipos = opcoes.types || ['image/jpeg', 'image/jpg', 'image/png'];

        if (file.size > maxSize) {
            throw new Error(`Arquivo excede o tamanho máximo permitido de ${maxSize / 1024 / 1024} MB.`);
        }

        if (!tipos.includes(file.type.toLowerCase())) {
            throw new Error('Formato de imagem inválido. Use apenas JPG, JPEG ou PNG.');
        }

        return true;
    }

    /**
     * Gerar preview de imagem (Data URL)
     * @param {File} file - Arquivo da imagem
     * @returns {Promise<string>} - Data URL da imagem
     */
    static gerarPreview(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    }

    /**
     * Configurar input de arquivo com preview e tratamento de erros
     * @param {string} inputId - ID do input file
     * @param {string} previewId - ID do elemento de preview
     * @param {Function} onFileSelected - Callback quando arquivo é selecionado
     */
    static setupImagePreview(inputId, previewId, onFileSelected = null) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        if (!input) return;

        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                this.validarImagem(file);
                
                if (preview) {
                    const dataUrl = await this.gerarPreview(file);
                    if (preview.tagName === 'IMG') {
                        preview.src = dataUrl;
                    } else {
                        preview.style.backgroundImage = `url(${dataUrl})`;
                    }
                    preview.style.display = 'block';
                }

                if (onFileSelected) {
                    onFileSelected(file);
                }
            } catch (error) {
                console.error('Erro ao processar imagem:', error);
                // Limpa o input para permitir nova tentativa
                input.value = '';
                if (window.UINotification) {
                    window.UINotification.toast(error.message, 'error');
                } else {
                    alert(error.message);
                }
            }
        });
    }
}

// Exportar para uso global ou modular
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UploadManager;
} else {
    window.UploadManager = UploadManager;
}