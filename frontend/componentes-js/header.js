export const userDeslogado = `
  <a href="#" class="d-flex align-items-center text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
    <i class="bi bi-person-circle fs-4 me-2"> <span class="fw-semibold">Login</span></i>
  </a>
  <ul class="dropdown-menu dropdown-menu-end">
    <li><a class="dropdown-item" href="login.html">Entrar</a></li>
    <li><a class="dropdown-item" href="cadastro.html">Cadastrar</a></li>
  </ul>
`;

export const header = `
<header class="py-3">
  <div class="container">
    <div class="d-flex align-items-center justify-content-between">
      <a href="index.html" class="d-flex align-items-center text-decoration-none">
        <img src="assets/logo.png" class="me-2" id="logo" alt="Dog Mau logo"style="border-radius: 50%; width: 50px; height: 50px;" />
      </a>

      <ul class="nav mx-auto mb-0">
        <li><a href="#" class="nav-link px-4 fs-4 active">Home</a></li>
        <li><a href="#" class="nav-link px-4 fs-4">Produtos</a></li>
        <li><a href="#" class="nav-link px-4 fs-4">Serviços</a></li>
        <li><a href="#" class="nav-link px-4 fs-4">Sobre</a></li>
      </ul>

      <div class="d-flex align-items-center gap-3">
        <form class="search-box d-flex align-items-center">
            <input type="search" class="form-control search-input" placeholder="Buscar..." />
            <button class="btn btn-danger ms-2">
                <i class="bi bi-search"></i>
            </button>
        </form>
        <div class="dropdown">
          <div id="user-area"></div>
        </div>
      </div>
    </div>
  </div>
</header>
`;

export function initNavLinks() {
  const navLinks = document.querySelectorAll('.nav .nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      navLinks.forEach(l => l.classList.remove('active'));
      
      link.classList.add('active');
    });
  });
}


