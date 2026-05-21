/**
 * Sistema de Carrinho - Dog Mau Auto Center
 * Gerencia carrinho local e integra com API de pedidos
 */

class ShoppingCart {
  constructor() {
    this.cartKey = 'dogmau_cart';
    this.cart = this.loadCart();
    this.init();
  }

  // === GERENCIAMENTO LOCAL (LocalStorage) ===

  loadCart() {
    try {
      const saved = localStorage.getItem(this.cartKey);
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      console.error('Erro ao carregar carrinho:', e);
      return [];
    }
  }

  saveCart() {
    try {
      localStorage.setItem(this.cartKey, JSON.stringify(this.cart));
      this.updateCartUI();
    } catch (e) {
      console.error('Erro ao salvar carrinho:', e);
    }
  }

  // === OPERAÇÕES DO CARRINHO ===

  addProduct(produto) {
    // Verifica se já existe no carrinho
    const existing = this.cart.find(item => item.id_produto === produto.id_produto);

    if (existing) {
      existing.quantidade++;
    } else {
      this.cart.push({
        id_produto: produto.id_produto,
        nome: produto.nome,
        preco: produto.preco,
        quantidade: 1,
        imagem_produto: produto.imagem_produto || null
      });
    }

    this.saveCart();
    this.showNotification(`${produto.nome} adicionado ao carrinho!`);
  }

  removeProduct(id_produto) {
    this.cart = this.cart.filter(item => item.id_produto !== id_produto);
    this.saveCart();
  }

  updateQuantity(id_produto, quantidade) {
    if (quantidade <= 0) {
      this.removeProduct(id_produto);
    } else {
      const item = this.cart.find(item => item.id_produto === id_produto);
      if (item) {
        item.quantidade = quantidade;
        this.saveCart();
      }
    }
  }

  getTotal() {
    return this.cart.reduce((total, item) => total + (item.preco * item.quantidade), 0);
  }

  getItemCount() {
    return this.cart.reduce((count, item) => count + item.quantidade, 0);
  }

  clear() {
    this.cart = [];
    this.saveCart();
  }

  isEmpty() {
    return this.cart.length === 0;
  }

  // === UI UPDATES ===

  init() {
    this.createCartUI();
    this.attachEventListeners();
    this.updateCartUI();
  }

  createCartUI() {
    // Cria o HTML do dropdown do carrinho se não existir
    if (!document.getElementById('cart-dropdown')) {
      const cartHTML = `
        <div id="cart-dropdown" class="cart-dropdown">
          <div class="cart-header">
            <h5>Carrinho de Compras</h5>
            <button type="button" class="btn-close btn-close-white" id="close-cart"></button>
          </div>
          
          <div class="cart-items" id="cart-items">
            <div class="empty-cart">Carrinho vazio</div>
          </div>
          
          <div class="cart-footer">
            <div class="cart-total">
              <strong>Total:</strong>
              <span id="cart-total-price">R$ 0,00</span>
            </div>
            <button 
              type="button" 
              id="checkout-btn" 
              class="btn btn-danger w-100"
              style="display: none;"
            >
              Prosseguir para Pagamento
            </button>
          </div>
        </div>
        
        <!-- Overlay para fechar o carrinho -->
        <div id="cart-overlay" class="cart-overlay"></div>
      `;

      document.body.insertAdjacentHTML('beforeend', cartHTML);
    }
  }

  attachEventListeners() {
    // Botão para abrir/fechar carrinho
    const cartToggle = document.getElementById('cart-toggle');
    if (cartToggle) {
      cartToggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleCart();
      });
    }

    // Botão de fechar carrinho
    const closeBtn = document.getElementById('close-cart');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeCart());
    }

    // Overlay para fechar ao clicar fora
    const overlay = document.getElementById('cart-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this.closeCart());
    }

    // Botão de checkout
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
      checkoutBtn.addEventListener('click', () => this.proceedToCheckout());
    }
  }

  toggleCart() {
    const dropdown = document.getElementById('cart-dropdown');
    if (dropdown) {
      dropdown.classList.toggle('active');
      const overlay = document.getElementById('cart-overlay');
      if (overlay) {
        overlay.classList.toggle('active');
      }
    }
  }

  closeCart() {
    const dropdown = document.getElementById('cart-dropdown');
    if (dropdown) {
      dropdown.classList.remove('active');
    }
    const overlay = document.getElementById('cart-overlay');
    if (overlay) {
      overlay.classList.remove('active');
    }
  }

  updateCartUI() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartToggle = document.getElementById('cart-toggle');
    const checkoutBtn = document.getElementById('checkout-btn');
    const cartTotalPrice = document.getElementById('cart-total-price');

    if (!cartItemsContainer) return;

    // Atualiza badge de itens no ícone
    if (cartToggle) {
      const badge = cartToggle.querySelector('.cart-badge');
      const itemCount = this.getItemCount();
      if (badge) {
        badge.textContent = itemCount;
        badge.style.display = itemCount > 0 ? 'block' : 'none';
      }
    }

    // Atualiza preço total
    if (cartTotalPrice) {
      cartTotalPrice.textContent = this.formatPrice(this.getTotal());
    }

    // Mostra/esconde botão de checkout
    if (checkoutBtn) {
      checkoutBtn.style.display = this.isEmpty() ? 'none' : 'block';
    }

    // Renderiza itens
    if (this.isEmpty()) {
      cartItemsContainer.innerHTML = '<div class="empty-cart">Carrinho vazio</div>';
    } else {
      cartItemsContainer.innerHTML = this.cart.map(item => this.renderCartItem(item)).join('');
      this.attachCartItemListeners();
    }
  }

  renderCartItem(item) {
    return `
      <div class="cart-item" data-produto-id="${item.id_produto}">
        <div class="cart-item-info">
          ${item.imagem_produto ? `<img src="${item.imagem_produto}" alt="${item.nome}" class="cart-item-image">` : ''}
          <div class="cart-item-details">
            <h6 class="cart-item-name">${item.nome}</h6>
            <p class="cart-item-price">${this.formatPrice(item.preco)}</p>
          </div>
        </div>
        
        <div class="cart-item-controls">
          <div class="quantity-control">
            <button type="button" class="qty-btn qty-minus" data-action="minus">−</button>
            <input 
              type="number" 
              class="qty-input" 
              value="${item.quantidade}" 
              min="1"
              data-produto-id="${item.id_produto}"
            >
            <button type="button" class="qty-btn qty-plus" data-action="plus">+</button>
          </div>
          
          <button 
            type="button" 
            class="btn-remove" 
            data-produto-id="${item.id_produto}"
            title="Remover do carrinho"
          >
            <i class="bi bi-trash"></i>
          </button>
        </div>
        
        <div class="cart-item-subtotal">
          <small>Subtotal:</small>
          <strong>${this.formatPrice(item.preco * item.quantidade)}</strong>
        </div>
      </div>
    `;
  }

  attachCartItemListeners() {
    // Botões de quantidade
    document.querySelectorAll('.qty-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.target.closest('.qty-btn').dataset.action;
        const input = e.target.closest('.quantity-control').querySelector('.qty-input');
        const id_produto = parseInt(input.dataset.produtoId);
        let qty = parseInt(input.value);

        if (action === 'plus') qty++;
        else if (action === 'minus' && qty > 1) qty--;

        this.updateQuantity(id_produto, qty);
      });
    });

    // Input de quantidade
    document.querySelectorAll('.qty-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const id_produto = parseInt(e.target.dataset.produtoId);
        let qty = parseInt(e.target.value) || 0;
        if (qty < 1) qty = 1;
        this.updateQuantity(id_produto, qty);
      });
    });

    // Botões de remover
    document.querySelectorAll('.btn-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id_produto = parseInt(e.target.closest('.btn-remove').dataset.produtoId);
        this.removeProduct(id_produto);
      });
    });
  }

  // === CHECKOUT ===

  async proceedToCheckout() {
    // Verifica se usuário está autenticado
    const token = this.getAuthToken();
    if (!token) {
      this.showAlert('Você precisa estar logado para fazer uma compra. Redirecionando...', 'warning');
      setTimeout(() => {
        window.location.href = '/cadastro';
      }, 1500);
      return;
    }

    if (this.isEmpty()) {
      this.showAlert('Carrinho vazio!', 'warning');
      return;
    }

    // Redireciona para checkout
    window.location.href = '/checkout';
  }

  // === UTILITÁRIOS ===

  formatPrice(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  }

  getAuthToken() {
    // Tenta obter token do localStorage (pode ser adicionado no login)
    return localStorage.getItem('auth_token') || document.querySelector('meta[name="auth-token"]')?.content;
  }

  showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertAdjacentElement('afterbegin', alert);
    setTimeout(() => alert.remove(), 4000);
  }
}

// Inicializa carrinho quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
  window.cart = new ShoppingCart();
});

// Função helper para adicionar produto ao carrinho (chamada do botão)
function addToCart(produtoData) {
  if (window.cart) {
    window.cart.addProduct(produtoData);
  }
}
