/**
 * loja.js — busca na vitrine e ação do botão Comprar
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

  grid.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-loja-comprar');
    if (!btn || btn.disabled) return;

    const isDemo = btn.dataset.demo === 'true';
    if (isDemo) {
      showToast('Produto demonstrativo — cadastre itens reais no painel para comprar.', 'secondary');
      return;
    }

    const loggedIn = btn.dataset.loggedIn === 'true';
    if (!loggedIn) {
      const next = encodeURIComponent(window.location.pathname);
      window.location.href = `/login?next=${next}`;
      return;
    }

    const estoque = parseInt(btn.dataset.estoque, 10);
    if (estoque <= 0) {
      showToast('Produto sem estoque no momento.', 'warning');
      return;
    }

    const produtoId = parseInt(btn.dataset.produtoId, 10);
    const preco = parseFloat(btn.dataset.preco) || 0;
    const userId = parseInt(btn.dataset.userId, 10);

    btn.disabled = true;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processando...';

    try {
      if (typeof criarPedido !== 'function' || typeof adicionarProdutoAoPedido !== 'function') {
        throw new Error('Módulo de compra não carregado.');
      }

      const pedido = await criarPedido(userId, preco);
      await adicionarProdutoAoPedido(pedido.id_pedido, produtoId, 1);
      showToast('Produto adicionado ao pedido! Acesse Minha Área para acompanhar.', 'success');
    } catch (err) {
      showToast(err.message || 'Não foi possível concluir a compra.', 'danger');
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalHtml;
    }
  });

  // Change Status in Pedido Card
  document.addEventListener('change', async (e) => {
    if (e.target.classList.contains('pedido-status-select')) {
      const select = e.target;
      const pedidoId = select.dataset.pedId;
      const newStatus = select.value;
      const originalValue = select.dataset.originalValue || select.value;
      
      select.disabled = true;
      try {
        const res = await fetch(`/api/pedidos/${pedidoId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus }),
          credentials: 'include'
        });
        if (res.ok) {
          showToast(`Status do pedido #${pedidoId} atualizado para ${newStatus}.`, 'success');
          select.dataset.originalValue = newStatus;
        } else {
          const data = await res.json();
          showToast(data.detail || 'Erro ao atualizar status.', 'danger');
          select.value = originalValue;
        }
      } catch (err) {
        showToast('Erro de rede ao atualizar status.', 'danger');
        select.value = originalValue;
      } finally {
        select.disabled = false;
      }
    }
  });

  // Track original value on focus to allow revert
  document.addEventListener('focusin', (e) => {
    if (e.target.classList.contains('pedido-status-select')) {
        if (!e.target.dataset.originalValue) {
            e.target.dataset.originalValue = e.target.value;
        }
    }
  });

})();
