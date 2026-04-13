const userLogado = `
  <a href="#" class="d-flex align-items-center text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
    <img src="assets/perfil.png" width="32" height="32" class="rounded-circle me-2"/>
    <span class="fw-semibold">User</span>
  </a>
  <ul class="dropdown-menu dropdown-menu-end">
    <li><a class="dropdown-item" href="#">Veículo</a></li>
    <li><a class="dropdown-item" href="#">Perfil</a></li>
    <li><hr class="dropdown-divider"></li>
    <li><a class="dropdown-item" href="#">Sair</a></li>
  </ul>
`;

const userDeslogado = `
  <a href="#" class="d-flex align-items-center text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
    <i class="bi bi-person-circle fs-4 me-2"></i>
    <span>Login</span>
  </a>
  <ul class="dropdown-menu dropdown-menu-end">
    <li><a class="dropdown-item" href="#">Entrar</a></li>
    <li><a class="dropdown-item" href="#">Cadastrar</a></li>
  </ul>
`;

const header = `
<header class="py-3 border-bottom">
  <div class="container">
    <div class="d-flex align-items-center justify-content-between">
      <a href="index.html" class="d-flex align-items-center text-decoration-none">
        <img src="assets/logo.png" width="70" class="me-2">
      </a>

      <ul class="nav mx-auto">
        <li><a href="#" class="nav-link px-4 fs-5 link-secondary">Home</a></li>
        <li><a href="#" class="nav-link px-4 fs-5 link-body-emphasis">Produtos</a></li>
        <li><a href="#" class="nav-link px-4 fs-5 link-body-emphasis">Serviços</a></li>
        <li><a href="#" class="nav-link px-4 fs-5 link-body-emphasis">Sobre</a></li>
      </ul>

      <div class="d-flex align-items-center gap-3">
        <input type="search" class="form-control" placeholder="Buscar..." style="width: 180px;"/>
        <div class="dropdown">
          <div id="user-area"></div>
        </div>
      </div>
    </div>
  </div>
</header>
`;
document.getElementById("header").innerHTML = header;

let logado = true;

if (logado) {
  document.getElementById("user-area").innerHTML = userLogado;
} else {
  document.getElementById("user-area").innerHTML = userDeslogado;
}
