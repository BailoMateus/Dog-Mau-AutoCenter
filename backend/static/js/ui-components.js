/**
 * ui-components.js
 * Sistema centralizado de notificações, modais e componentes de UI
 * Reutilizável em todo o projeto
 */

// ==================== TOAST SYSTEM ====================

class UINotification {
  /**
   * Toast/Notificação - auto-dismiss após 4s
   * @param {string} message - Mensagem a exibir
   * @param {string} type - 'success' | 'error' | 'warning' | 'info'
   * @param {number} duration - Tempo em ms (padrão: 4000)
   */
  static toast(message, type = 'info', duration = 4000) {
    const container = this._getToastContainer();

    const toast = document.createElement('div');
    toast.className = `alert alert-${this._mapType(type)} alert-dismissible fade show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-${this._getIcon(type)}"></i>
        <span>${this._escapeHtml(message)}</span>
      </div>
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => toast.remove(), duration);
    }
  }

  /**
   * Modal de confirmação genérico
   * @param {string} title - Título do modal
   * @param {string} message - Mensagem
   * @param {string} confirmText - Texto do botão confirmar (padrão: "Confirmar")
   * @param {string} type - 'danger' | 'warning' | 'info'
   * @returns {Promise<boolean>}
   */
  static confirm(title, message, confirmText = 'Confirmar', type = 'danger') {
    return new Promise((resolve) => {
      const modal = document.createElement('div');
      modal.className = 'modal fade';
      modal.setAttribute('tabindex', '-1');
      modal.setAttribute('aria-hidden', 'true');

      const backgroundColor = type === 'danger' ? '#1a1a1a' : '#111';
      const buttonClass = type === 'danger' ? 'btn-danger' : `btn-${type}`;

      modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content" style="background-color: ${backgroundColor}; border-color: #333;">
            <div class="modal-header" style="border-color: #333;">
              <h5 class="modal-title text-white">
                <i class="bi bi-exclamation-circle me-2" style="color: #c0252b;"></i>
                ${this._escapeHtml(title)}
              </h5>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body text-white">
              ${this._escapeHtml(message)}
            </div>
            <div class="modal-footer" style="border-color: #333;">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="bi bi-x-circle me-1"></i>Cancelar
              </button>
              <button type="button" class="btn ${buttonClass}" id="confirmBtn">
                <i class="bi bi-check-circle me-1"></i>${this._escapeHtml(confirmText)}
              </button>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(modal);
      const bsModal = new bootstrap.Modal(modal);

      document.getElementById('confirmBtn').addEventListener('click', () => {
        resolve(true);
        bsModal.hide();
      });

      modal.addEventListener('hidden.bs.modal', () => {
        resolve(false);
        modal.remove();
      });

      bsModal.show();
    });
  }

  /**
   * Modal de alerta genérico
   * @param {string} title - Título
   * @param {string} message - Mensagem
   * @param {string} type - 'error' | 'warning' | 'success' | 'info'
   */
  static alert(title, message, type = 'info') {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');

    modal.innerHTML = `
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="background-color: #111; border-color: #333;">
          <div class="modal-header" style="border-color: #333;">
            <h5 class="modal-title text-white">
              <i class="bi bi-${this._getIcon(type)} me-2" style="color: ${this._getColor(type)};"></i>
              ${this._escapeHtml(title)}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-white">
            ${this._escapeHtml(message)}
          </div>
          <div class="modal-footer" style="border-color: #333;">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">OK</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    modal.addEventListener('hidden.bs.modal', () => modal.remove());
  }

  /**
   * Modal de carregamento
   * @param {string} message - Mensagem (padrão: "Carregando...")
   * @returns {Object} - {show: Function, hide: Function}
   */
  static loading(message = 'Carregando...') {
    const modal = document.createElement('div');
    modal.id = 'loadingModal';
    modal.innerHTML = `
      <div class="modal fade" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content" style="background-color: #111; border-color: #333;">
            <div class="modal-body text-center py-5">
              <div class="spinner-border" style="color: #c0252b;" role="status">
                <span class="visually-hidden">Carregando...</span>
              </div>
              <p class="text-white mt-3 mb-0">${this._escapeHtml(message)}</p>
            </div>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal.querySelector('.modal'), { backdrop: 'static' });

    return {
      show: () => bsModal.show(),
      hide: () => bsModal.hide(),
      modal: modal
    };
  }

  // ==================== PRIVATE HELPERS ====================

  static _getToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1100;
        max-width: 500px;
      `;
      document.body.appendChild(container);
    }
    return container;
  }

  static _mapType(type) {
    const map = {
      'success': 'success',
      'error': 'danger',
      'warning': 'warning',
      'info': 'info'
    };
    return map[type] || 'info';
  }

  static _getIcon(type) {
    const icons = {
      'success': 'check-circle-fill',
      'error': 'exclamation-circle-fill',
      'warning': 'exclamation-triangle-fill',
      'info': 'info-circle-fill'
    };
    return icons[type] || 'info-circle';
  }

  static _getColor(type) {
    const colors = {
      'success': '#198754',
      'error': '#dc3545',
      'warning': '#ffc107',
      'info': '#0dcaf0'
    };
    return colors[type] || '#0dcaf0';
  }

  static _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

/**
 * Modal de confirmação para exclusão
 * @param {string} entityName - Nome da entidade (ex: "usuário", "agendamento")
 * @param {Object} entity - Dados da entidade para exibição
 * @param {Function} onConfirm - Callback quando confirmar
 */
UINotification.confirmDelete = async function(entityName, entity, onConfirm) {
  const message = `
    <p class="mb-3">Tem certeza que deseja excluir este <strong>${entityName}</strong>?</p>
    <div class="alert alert-light text-dark" style="background-color: #222; border-color: #555;">
      <small><strong>ID:</strong> ${entity.id}</small><br>
      <small><strong>Nome/Info:</strong> ${this._escapeHtml(entity.name || entity.nome || entity.titulo || '-')}</small>
    </div>
    <p class="text-warning small mb-0">
      <i class="bi bi-exclamation-triangle-fill me-1"></i>
      Esta ação não pode ser desfeita.
    </p>
  `;

  return new Promise((resolve) => {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');

    modal.innerHTML = `
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="background-color: #1a1a1a; border-color: #d32f2f;">
          <div class="modal-header" style="border-color: #d32f2f;">
            <h5 class="modal-title text-danger">
              <i class="bi bi-trash-fill me-2"></i>Confirmar Exclusão
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body text-white">
            ${message}
          </div>
          <div class="modal-footer" style="border-color: #555;">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-circle me-1"></i>Cancelar
            </button>
            <button type="button" class="btn btn-danger" id="confirmDeleteBtn">
              <i class="bi bi-trash me-1"></i>Excluir Permanentemente
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);

    document.getElementById('confirmDeleteBtn').addEventListener('click', async () => {
      resolve(true);
      bsModal.hide();
      if (onConfirm) await onConfirm();
    });

    modal.addEventListener('hidden.bs.modal', () => {
      resolve(false);
      modal.remove();
    });

    bsModal.show();
  });
};

// Exportar globalmente
window.UINotification = UINotification;