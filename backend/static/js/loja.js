/**
 * loja.js — busca na vitrine e adição de produtos/peças ao carrinho.
 *
 * Comportamento (Requisito 4): ao clicar em "Adicionar ao Carrinho" o item é
 * adicionado ao carrinho e o usuário PERMANECE na tela (sem redirecionar para
 * checkout/carrinho).
 */
(function () {
  const searchInput = document.getElementById('lojaSearchInput');
  const grid = document.getElementById('lojaProductGrid');
  const pecaGrid = document.getElementById('lojaPecaGrid');
  const emptyMsg = document.getElementById('lojaEmptyMsg');

  // A busca atua sobre a grade de produtos (quando existir)
  function filterProducts() {
    if (!grid) return;
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

    const el = document.createElement('div');
    el.className = `alert alert-${type || 'info'} shadow-lg mb-2`;
    el.setAttribute('role', 'alert');
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4000);
  }

  // Handler único para adicionar produto OU peça ao carrinho.
  function handleAddToCart(btn) {
    if (!btn || btn.disabled) return;

    const isDemo = btn.dataset.demo === 'true';
    if (isDemo) {
      showToast('Item demonstrativo — cadastre itens reais no painel para comprar.', 'secondary');
      return;
    }

    // Exige login antes de adicionar (mantém o fluxo de autenticação existente)
    const loggedIn = btn.dataset.loggedIn === 'true';
    if (!loggedIn) {
      const next = encodeURIComponent(window.location.pathname);
      window.location.href = `/login?next=${next}`;
      return;
    }

    // Impede no front a compra de itens sem estoque
    const estoque = parseInt(btn.dataset.estoque, 10);
    if (isNaN(estoque) || estoque <= 0) {
      showToast('Item sem estoque no momento.', 'warning');
      return;
    }

    if (!window.cart) {
      showToast('Sistema de carrinho não carregado. Recarregue a página.', 'danger');
      return;
    }

    const card = btn.closest('.loja-card') || btn.closest('[data-loja-card]');
    const nome = card ? (card.dataset.nome || 'Item') : 'Item';
    const preco = parseFloat(btn.dataset.preco) || 0;
    const imgEl = card ? card.querySelector('.loja-card-img-wrap img') : null;
    const imagem = imgEl ? imgEl.src : null;

    const tipo = btn.dataset.tipo === 'peca' ? 'peca' : 'produto';

    if (tipo === 'peca') {
      const pecaId = parseInt(btn.dataset.pecaId, 10);
      window.cart.addPeca({ id_peca: pecaId, nome: nome, preco: preco, imagem_peca: imagem });
    } else {
      const produtoId = parseInt(btn.dataset.produtoId, 10);
      window.cart.addProduct({ id_produto: produtoId, nome: nome, preco: preco, imagem_produto: imagem });
    }

    // Requisito 4: permanecer na tela atual (NÃO redirecionar para checkout/carrinho).
    showToast(`${nome} adicionado ao carrinho!`, 'success');
  }

  // Delegação de clique cobrindo as grades de produtos e de peças.
  function bindGrid(el) {
    if (!el) return;
    el.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-loja-comprar');
      if (btn) handleAddToCart(btn);
    });
  }

  bindGrid(grid);
  bindGrid(pecaGrid);
})();
