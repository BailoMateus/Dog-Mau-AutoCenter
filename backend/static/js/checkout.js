/**
 * Lógica de Checkout - Dog Mau Auto Center
 */

class CheckoutManager {
  constructor() {
    this.form = document.getElementById('checkout-form');
    this.cart = window.cart;
    this.init();
  }

  init() {
    if (!this.cart || this.cart.isEmpty()) {
      this.showEmptyCart();
      return;
    }

    this.loadCartItems();
    this.loadUserData();
    this.attachFormListener();
  }

  loadCartItems() {
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total');

    if (!container) return;

    if (this.cart.isEmpty()) {
      this.showEmptyCart();
      return;
    }

    // Renderiza itens
    container.innerHTML = this.cart.cart
      .map(item => `
        <div class="checkout-item">
          <div class="checkout-item-image">
            ${item.imagem_produto ?
              `<img src="${item.imagem_produto}" alt="${item.nome}">` :
              '<i class="bi bi-box" style="font-size: 2em; color: #555;"></i>'
            }
          </div>
          <div class="checkout-item-info">
            <div class="checkout-item-name">${item.nome}</div>
            <div class="checkout-item-details">
              <span>${item.quantidade}x ${this.formatPrice(item.preco)}</span>
              <strong>${this.formatPrice(item.quantidade * item.preco)}</strong>
            </div>
          </div>
        </div>
      `)
      .join('');

    // Atualiza totais
    const subtotal = this.cart.getTotal();
    const frete = 15.00; // Valor fixo de frete para exemplo
    const total = subtotal + frete;

    subtotalEl.textContent = this.formatPrice(subtotal);
    document.getElementById('frete').textContent = this.formatPrice(frete);
    totalEl.textContent = this.formatPrice(total);
  }

  loadUserData() {
    // Tenta preencher com dados do usuário logado
    const metaUser = document.querySelector('meta[name="user-name"]');
    const metaEmail = document.querySelector('meta[name="user-email"]');
    const metaPhone = document.querySelector('meta[name="user-phone"]');

    if (metaUser && metaUser.content) {
      document.getElementById('destinatario').value = metaUser.content;
    }

    if (metaEmail && metaEmail.content) {
      document.getElementById('email').value = metaEmail.content;
    }

    if (metaPhone && metaPhone.content) {
      document.getElementById('telefone').value = metaPhone.content;
    }
  }

  attachFormListener() {
    if (this.form) {
      this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    // Valida campos
    if (!this.form.checkValidity()) {
      if (window.UINotification) UINotification.toast('Por favor, preencha todos os campos obrigatórios', 'warning');
      return;
    }

    // Coleta dados do formulário
    const formData = new FormData(this.form);
    const endereco = {
      rua: formData.get('rua'),
      numero: formData.get('numero'),
      complemento: formData.get('complemento'),
      bairro: formData.get('bairro'),
      cidade: formData.get('cidade'),
      estado: formData.get('estado'),
      cep: formData.get('cep'),
      tipo: 'entrega'
    };

    // Mostra loading
    this.showLoading(true);

    try {
      // 1. Cria pedido
      const pedidoData = {
        valor_total: this.cart.getTotal()
      };

      const pedidoResponse = await fetch('/api/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',  // Envia cookies HttpOnly (autenticação)
        body: JSON.stringify(pedidoData)
      });

      if (!pedidoResponse.ok) {
        const error = await pedidoResponse.json();
        throw new Error(error.detail || 'Erro ao criar pedido');
      }

      const pedido = await pedidoResponse.json();
      const pedidoId = pedido.id_pedido || pedido.id;

      if (!pedidoId) {
        throw new Error('ID do pedido não retornado');
      }

      // 2. Adiciona itens ao pedido
      for (const item of this.cart.cart) {
        const itemResponse = await fetch(`/api/pedidos/${pedidoId}/itens`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',  // Envia cookies HttpOnly (autenticação)
          body: JSON.stringify({
            id_produto: item.id_produto,
            quantidade: item.quantidade
          })
        });

        if (!itemResponse.ok) {
          throw new Error('Erro ao adicionar item ao pedido');
        }
      }

      // 4. Limpa carrinho
      this.cart.clear();
      localStorage.removeItem('dogmau_cart');

      // 5. Mostra sucesso
      this.showSuccess();

      // 6. Redireciona após 2 segundos
      setTimeout(() => {
        window.location.href = '/painel?tab=pedidos';
      }, 2000);

    } catch (error) {
      console.error('Erro no checkout:', error);
      this.showError(error.message || 'Erro ao processar pedido. Tente novamente.');
    } finally {
      this.showLoading(false);
    }
  }

  showEmptyCart() {
    const container = document.querySelector('.checkout-content');
    if (container) {
      container.innerHTML = `
        <div style="grid-column: 1/-1;" class="empty-cart-message">
          <i class="bi bi-bag-slash"></i>
          <p>Seu carrinho está vazio!</p>
          <a href="/produtos" class="btn-continue-shopping">
            <i class="bi bi-arrow-left me-2"></i>
            Voltar aos Produtos
          </a>
        </div>
      `;
    }
  }

  showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    const submitBtn = document.getElementById('submit-btn');

    if (overlay) {
      overlay.classList.toggle('active', show);
    }

    if (submitBtn) {
      submitBtn.disabled = show;
      if (show) {
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';
      } else {
        submitBtn.innerHTML = '<i class="bi bi-lock-fill"></i> Confirmar Pedido e Pagar';
      }
    }
  }

  showError(message) {
    const alertEl = document.getElementById('error-alert');
    const messageEl = document.getElementById('error-message');

    if (alertEl && messageEl) {
      messageEl.textContent = message;
      alertEl.classList.add('show');

      setTimeout(() => {
        alertEl.classList.remove('show');
      }, 5000);
    }
  }

  showSuccess() {
    const successEl = document.getElementById('success-message');
    if (successEl) {
      successEl.classList.add('show');
    }
  }

  formatPrice(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }

  getAuthToken() {
    // Tenta obter token do localStorage
    const token = localStorage.getItem('auth_token');
    if (token) return token;

    // Tenta obter do meta tag
    const metaToken = document.querySelector('meta[name="auth-token"]');
    if (metaToken) return metaToken.content;

    // Verifica cookie se houver acesso via fetch
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === '__session' || name === 'auth_token') {
        return decodeURIComponent(value);
      }
    }

    return null;
  }
}

// Inicializa checkout quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
  new CheckoutManager();
});
