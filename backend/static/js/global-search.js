/**
 * global-search.js — busca de produtos no header e na loja
 */
(function () {
  const form = document.getElementById('globalSearchForm');
  const input = document.getElementById('globalSearchInput');
  if (!form || !input) return;

  function filterGrid(grid, term) {
    if (!grid) return 0;
    const cards = grid.querySelectorAll('[data-loja-card]');
    let visible = 0;
    cards.forEach((card) => {
      const nome = (card.dataset.nome || '').toLowerCase();
      const desc = (card.dataset.desc || '').toLowerCase();
      const match = !term || nome.includes(term) || desc.includes(term);
      const col = card.closest('.col');
      if (col) col.style.display = match ? '' : 'none';
      if (match) visible += 1;
    });
    return visible;
  }

  function showEmptyMessage(id, show) {
    const el = document.getElementById(id);
    if (el) el.style.display = show ? 'block' : 'none';
  }

  function runSearch(term) {
    const q = (term || '').trim().toLowerCase();
    const lojaGrid = document.getElementById('lojaProductGrid');
    const homeGrid = document.getElementById('homeProductGrid');

    if (lojaGrid) {
      const visible = filterGrid(lojaGrid, q);
      showEmptyMessage('lojaEmptyMsg', visible === 0);
      return true;
    }

    if (homeGrid) {
      const visible = filterGrid(homeGrid, q);
      showEmptyMessage('homeEmptyMsg', visible === 0);
      return true;
    }

    return false;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const term = input.value.trim();
    if (!runSearch(term)) {
      const url = term ? `/loja?q=${encodeURIComponent(term)}` : '/loja';
      window.location.href = url;
    }
  });

  input.addEventListener('input', () => {
    runSearch(input.value);
  });

  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    input.value = q;
    runSearch(q);
  }
})();
