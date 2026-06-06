/**
 * loja.js — busca na vitrine e fluxo transacional do botão Comprar
 */
(function () {
  const searchInput = document.getElementById('lojaSearchInput');
  const grid = document.getElementById('lojaProductGrid');
  const emptyMsg = document.getElementById('lojaEmptyMsg');

  if (!grid) return;

  function filterProducts() {
    const term = (searchInput?.value || '').trim().toLowerCase();
    const cards = grid.querySelectorAll('[data-loja-card]');
    let visible = 0;

    cards.forEach((card) => {
      const nome = (card.dataset.nome || '').toLowerCase();
      const desc = (card.dataset.desc || '').toLowerCase();
      const match = !term || nome.includes(term) || desc.includes(term);
      card.closest('.col').style.display = match ? '' : 'none';
      if (match) visible += 1;
    });

    if (emptyMsg) {
      emptyMsg.style.display = visible === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterProducts);
    const searchBtn = searchInput.closest('.input-group')?.querySelector('.btn-loja-search');
    if (searchBtn) {
      searchBtn.addEventListener('click', filterProducts);
    }
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {
      searchInput.value = q;
      filterProducts();
    }
  }

  function showToast(message, type) {
    let container = document.querySelector('.loja-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'loja-toast-container';
      document.body.appendChild(container);
    }
    container = document.querySelector('.loja-toast-container') || container;

    const el = document.createElement('div');
    el.className = `alert alert-${type || 'info'} shadow-lg mb-2`;
    el.setAttribute('role', 'alert');
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }

  // Captura o evento de clique nos cards da vitrine pública de produtos
  grid.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-loja-comprar');
    if (!btn || btn.disabled) return;

    const isDemo = btn.dataset.demo === 'true';
    if (isDemo) {
      showToast('Produto demonstrativo — cadastre itens reais no painel para comprar.', 'secondary');
      return;
    }

    // Item 17: Validar login antes de checkout / compra
    const loggedIn = btn.dataset.loggedIn === 'true';
    if (!loggedIn) {
      const next = encodeURIComponent(window.location.pathname);
      window.location.href = `/login?next=${next}`;
      return;
    }

    // Item 5: Impedir no front a compra de itens sem estoque
    const estoque = parseInt(btn.dataset.estoque, 10);
    if (isNaN(estoque) || estoque <= 0) {
      showToast('Produto sem estoque no momento.', 'warning');
      return;
    }

    // Extrair dados do produto a partir do card HTML
    const card = btn.closest('.loja-card') || btn.closest('[data-loja-card]');
    const produtoId = parseInt(btn.dataset.produtoId, 10);
    const preco = parseFloat(btn.dataset.preco) || 0;
    const nome = card ? (card.dataset.nome || 'Produto') : 'Produto';
    const imgEl = card ? card.querySelector('.loja-card-img-wrap img, .produto-imagem img') : null;
    const imagem = imgEl ? imgEl.src : null;

    if (!window.cart) {
      showToast('Sistema de carrinho não carregado. Recarregue a página.', 'danger');
      return;
    }

    // CORREÇÃO: Alinhamento de chaves com o estado interno global (name/price)
    window.cart.addProduct({
      id_produto: produtoId,
      name: nome,
      price: preco,
      imagem_produto: imagem,
      quantity: 1
    });

    // CORREÇÃO (Item 2): Encaminha o cliente diretamente para a página do Checkout Real
    window.location.href = '/checkout';
  });

})();