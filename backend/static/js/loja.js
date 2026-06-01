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

    // Extrair dados do produto a partir do card HTML
    const card = btn.closest('.loja-card');
    const produtoId = parseInt(btn.dataset.produtoId, 10);
    const preco = parseFloat(btn.dataset.preco) || 0;
    const nome = card ? (card.dataset.nome || 'Produto') : 'Produto';
    const imgEl = card ? card.querySelector('.loja-card-img-wrap img') : null;
    const imagem = imgEl ? imgEl.src : null;

    // Verificar se o carrinho está disponível
    if (!window.cart) {
      showToast('Sistema de carrinho não carregado. Recarregue a página.', 'danger');
      return;
    }

    // Adicionar ao carrinho local
    window.cart.addProduct({
      id_produto: produtoId,
      nome: nome,
      preco: preco,
      imagem_produto: imagem
    });

    // Abrir a barra lateral do carrinho automaticamente
    const dropdown = document.getElementById('cart-dropdown');
    const overlay = document.getElementById('cart-overlay');
    if (dropdown && !dropdown.classList.contains('active')) {
      dropdown.classList.add('active');
    }
    if (overlay && !overlay.classList.contains('active')) {
      overlay.classList.add('active');
    }
  });

  // Change Status in Pedido Card
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-save-status');
    if (btn) {
      const pedidoId = btn.dataset.pedId;
      const select = document.getElementById(`status-select-${pedidoId}`);
      if (!select) return;
      
      const newStatus = select.value;
      const originalValue = select.dataset.originalValue || select.querySelector('option[selected]')?.value || 'pendente';
      
      btn.disabled = true;
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
          
          // Se o status for concluído, recarregar a página após um breve delay para refletir no estoque
          if (newStatus === 'concluido') {
            setTimeout(() => window.location.reload(), 1500);
          }
        } else {
          const data = await res.json();
          showToast(data.detail || 'Erro ao atualizar status.', 'danger');
          select.value = originalValue;
        }
      } catch (err) {
        showToast('Erro de rede ao atualizar status.', 'danger');
        select.value = originalValue;
      } finally {
        btn.disabled = false;
        select.disabled = false;
      }
    }
  });

  // Delete Pedido via AJAX
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-delete-pedido');
    if (!btn) return;
    
    const id = btn.dataset.pedId;
    if (confirm(`Tem certeza que deseja excluir o pedido #${id}?`)) {
      btn.disabled = true;
      try {
        const response = await fetch(`/api/pedidos/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.ok) {
          showToast(`Pedido #${id} excluído com sucesso.`, 'success');
          // Remove o card da grid
          const cardCol = btn.closest('.col');
          if (cardCol) {
            cardCol.remove();
          }
        } else {
          const data = await response.json();
          showToast(data.detail || 'Não foi possível excluir o pedido.', 'danger');
          btn.disabled = false;
        }
      } catch (error) {
        showToast('Erro de rede ao se comunicar com o servidor.', 'danger');
        btn.disabled = false;
      }
    }
  });

})();
