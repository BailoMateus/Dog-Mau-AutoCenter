/**
 * global-search.js — busca global com autocomplete (produtos + serviços)
 */
(function () {
  const form = document.getElementById('globalSearchForm');
  const input = document.getElementById('globalSearchInput');
  if (!form || !input) return;

  const wrap = form.closest('.search-box-wrap') || form.parentElement;
  let dropdown = document.getElementById('globalSearchDropdown');
  if (!dropdown) {
    dropdown = document.createElement('div');
    dropdown.id = 'globalSearchDropdown';
    dropdown.className = 'global-search-dropdown';
    dropdown.setAttribute('role', 'listbox');
    if (wrap) {
      wrap.classList.add('search-box-wrap');
      wrap.appendChild(dropdown);
    } else {
      form.appendChild(dropdown);
    }
  }

  let debounceTimer = null;
  let cache = { produtos: [], servicos: [] };

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

  function runLocalSearch(term) {
    const q = (term || '').trim().toLowerCase();
    const lojaGrid = document.getElementById('lojaProductGrid');
    const homeGrid = document.getElementById('homeProductGrid');

    if (lojaGrid) {
      const visible = filterGrid(lojaGrid, q);
      showEmptyMessage('lojaEmptyMsg', visible === 0 && q.length > 0);
      return true;
    }
    if (homeGrid) {
      const visible = filterGrid(homeGrid, q);
      showEmptyMessage('homeEmptyMsg', visible === 0 && q.length > 0);
      return true;
    }
    return false;
  }

  function hideDropdown() {
    dropdown.style.display = 'none';
    dropdown.innerHTML = '';
  }

  function renderDropdown(data, term) {
    const produtos = data.produtos || [];
    const servicos = data.servicos || [];
    if (!term || (produtos.length === 0 && servicos.length === 0)) {
      hideDropdown();
      return;
    }

    let html = '';
    if (produtos.length) {
      html += '<div class="global-search-section">Produtos</div>';
      produtos.forEach((p) => {
        html += `<a href="/loja?q=${encodeURIComponent(p.nome)}" class="global-search-item" role="option">
          <i class="bi bi-box-seam text-danger me-2"></i>
          <span>${escapeHtml(p.nome)}</span>
          <small class="ms-auto text-muted">R$ ${Number(p.preco).toFixed(2)}</small>
        </a>`;
      });
    }
    if (servicos.length) {
      html += '<div class="global-search-section">Serviços</div>';
      servicos.forEach((s) => {
        html += `<a href="/servicos" class="global-search-item" role="option">
          <i class="bi bi-tools text-danger me-2"></i>
          <span>${escapeHtml(s.nome)}</span>
          <small class="ms-auto text-muted">R$ ${Number(s.preco).toFixed(2)}</small>
        </a>`;
      });
    }
    if (!html) {
      html = '<div class="global-search-empty">Nenhum resultado encontrado</div>';
    }
    dropdown.innerHTML = html;
    dropdown.style.display = 'block';
  }

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
  }

  async function fetchAutocomplete(term) {
    try {
      const res = await fetch(`/api/busca?q=${encodeURIComponent(term)}`);
      if (!res.ok) return { produtos: [], servicos: [] };
      return await res.json();
    } catch {
      return { produtos: [], servicos: [] };
    }
  }

  function onInput() {
    const term = input.value.trim();
    runLocalSearch(term.toLowerCase());

    clearTimeout(debounceTimer);
    if (term.length < 1) {
      hideDropdown();
      return;
    }
    debounceTimer = setTimeout(async () => {
      cache = await fetchAutocomplete(term);
      renderDropdown(cache, term);
    }, 250);
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const term = input.value.trim();
    hideDropdown();
    if (!runLocalSearch(term.toLowerCase())) {
      const url = term ? `/loja?q=${encodeURIComponent(term)}` : '/loja';
      window.location.href = url;
    }
  });

  input.addEventListener('input', onInput);
  input.addEventListener('focus', onInput);

  document.addEventListener('click', (e) => {
    if (!form.contains(e.target) && !dropdown.contains(e.target)) {
      hideDropdown();
    }
  });

  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    input.value = q;
    runLocalSearch(q.toLowerCase());
  }
})();
