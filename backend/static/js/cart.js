/**
 * Sistema de Carrinho - Dog Mau Auto Center
 * Gerencia carrinho local (produtos e peças) e integra com a API de pedidos.
 *
 * Cada item do carrinho tem o formato:
 *   { tipo: 'produto'|'peca', id: <int>, nome, preco, quantidade, imagem }
 * A chave única do item é `${tipo}:${id}` — assim produtos e peças com o mesmo
 * número de ID não colidem.
 */

class ShoppingCart {
  constructor() {
    this.cartKey = 'dogmau_cart';
    this.ownerKey = 'dogmau_cart_owner';
    this.checkCartOwner();
    this.cart = this.loadCart();
    this.init();
  }

  checkCartOwner() {
    const metaTag = document.querySelector('meta[name="current-user-id"]');
    const currentUserId = metaTag ? metaTag.content : '';
    const savedOwner = localStorage.getItem(this.ownerKey);

    // Se mudamos de um usuário logado para OUTRO usuário logado, limpa.
    // Se o usuário apenas deslogou (currentUserId == ''), NÃO limpa o carrinho.
    if (savedOwner && currentUserId && savedOwner !== currentUserId) {
        localStorage.removeItem(this.cartKey);
    }

    // Atualiza quem é o dono atual do carrinho na sessão local, apenas se estiver logado
    if (currentUserId) {
        localStorage.setItem(this.ownerKey, currentUserId);
    }
  }

  // === GERENCIAMENTO LOCAL (LocalStorage) ===

  loadCart() {
    try {
      const saved = localStorage.getItem(this.cartKey);
      const raw = saved ? JSON.parse(saved) : [];
      // Normaliza itens (compatibilidade com formatos antigos baseados em id_produto)
      return raw.map((it) => this.normalizeItem(it)).filter(Boolean);
    } catch (e) {
      console.error('Erro ao carregar carrinho:', e);
      return [];
    }
  }

  normalizeItem(it) {
    if (!it) return null;
    const tipo = it.tipo || (it.id_peca ? 'peca' : 'produto');
    const id = it.id != null ? it.id : (tipo === 'peca' ? it.id_peca : it.id_produto);
    if (id == null) return null;
    const preco = Number(it.preco != null ? it.preco : it.price);
    return {
      tipo,
      id: parseInt(id, 10),
      nome: it.nome || it.name || (tipo === 'peca' ? 'Peça' : 'Produto'),
      preco: isNaN(preco) ? 0 : preco,
      quantidade: parseInt(it.quantidade || it.quantity || 1, 10),
      imagem: it.imagem || it.imagem_produto || it.imagem_peca || null,
    };
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

  itemKey(item) {
    return `${item.tipo}:${item.id}`;
  }

  addItem(data) {
    const item = this.normalizeItem(data);
    if (!item) {
      console.error('Item inválido para o carrinho:', data);
      return;
    }
    const key = this.itemKey(item);
    const existing = this.cart.find((i) => this.itemKey(i) === key);
    if (existing) {
      existing.quantidade += item.quantidade || 1;
    } else {
      this.cart.push(item);
    }
    this.saveCart();
    this.showNotification(`${item.nome} adicionado ao carrinho!`);
  }

  // Compatibilidade: adicionar produto
  addProduct(produto) {
    this.addItem({
      tipo: 'produto',
      id: produto.id_produto != null ? produto.id_produto : produto.id,
      nome: produto.nome,
      preco: produto.preco,
      imagem: produto.imagem_produto || produto.imagem || null,
      quantidade: produto.quantidade || 1,
    });
  }

  // Adicionar peça
  addPeca(peca) {
    this.addItem({
      tipo: 'peca',
      id: peca.id_peca != null ? peca.id_peca : peca.id,
      nome: peca.nome,
      preco: peca.preco != null ? peca.preco : peca.preco_unitario,
      imagem: peca.imagem_peca || peca.imagem || null,
      quantidade: peca.quantidade || 1,
    });
  }

  removeItem(key) {
    this.cart = this.cart.filter((item) => this.itemKey(item) !== key);
    this.saveCart();
  }

  updateQuantity(key, quantidade) {
    if (quantidade <= 0) {
      this.removeItem(key);
    } else {
      const item = this.cart.find((i) => this.itemKey(i) === key);
      if (item) {
        item.quantidade = quantidade;
        this.saveCart();
      }
    }
  }

  getTotal() {
    return this.cart.reduce((total, item) => total + (Number(item.preco) * item.quantidade), 0);
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
    const key = this.itemKey(item);
    const tipoLabel = item.tipo === 'peca' ? 'Peça' : 'Produto';
    return `
      <div class="cart-item" data-key="${key}">
        <div class="cart-item-info">
          ${item.imagem ? `<img src="${item.imagem}" alt="${item.nome}" class="cart-item-image">` : ''}
          <div class="cart-item-details">
            <h6 class="cart-item-name">${item.nome} <small class="text-muted">(${tipoLabel})</small></h6>
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
              data-key="${key}"
            >
            <button type="button" class="qty-btn qty-plus" data-action="plus">+</button>
          </div>

          <button
            type="button"
            class="btn-remove"
            data-key="${key}"
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
        const key = input.dataset.key;
        let qty = parseInt(input.value);

        if (action === 'plus') qty++;
        else if (action === 'minus' && qty > 1) qty--;

        this.updateQuantity(key, qty);
      });
    });

    // Input de quantidade
    document.querySelectorAll('.qty-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const key = e.target.dataset.key;
        let qty = parseInt(e.target.value) || 0;
        if (qty < 1) qty = 1;
        this.updateQuantity(key, qty);
      });
    });

    // Botões de remover
    document.querySelectorAll('.btn-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const key = e.target.closest('.btn-remove').dataset.key;
        this.removeItem(key);
      });
    });
  }

  // === CHECKOUT ===

  async proceedToCheckout() {
    if (this.isEmpty()) {
      this.showAlert('Carrinho vazio!', 'warning');
      return;
    }

    // Redireciona para checkout (o backend fará o redirecionamento de login se necessário)
    window.location.href = '/checkout';
  }

  // === UTILITÁRIOS ===

  formatPrice(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
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
