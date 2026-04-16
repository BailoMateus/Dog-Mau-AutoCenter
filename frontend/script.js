import {header, userDeslogado} from './componentes-js/header.js'
import {carrossel} from './componentes-js/carrossel.js'
import {footer} from './componentes-js/footer.js'
import {features} from './componentes-js/features.js'

// Script geral pra ter as integrações entre o front e o back
document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("header").innerHTML = header;

    const token = localStorage.getItem("access_token");
    const userArea = document.getElementById("user-area");

    if (token) {
        try {
            // PROVA DO SELECT: Buscando os dados do cliente
            const response = await fetch(`${window.BASE_URL}/me/cliente`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                const clienteData = await response.json();
                const primeiroNome = clienteData.nome.split(" ")[0]; // Pega apenas o primeiro nome

                // Renderiza o Estado Logado com o nome do usuário vindo da API
                userArea.innerHTML = `
                  <a href="#" class="d-flex align-items-center text-decoration-none dropdown-toggle" data-bs-toggle="dropdown">
                    <img src="assets/perfil.png" width="32" height="32" class="rounded-circle me-2" alt="Perfil"/>
                    <span class="fw-semibold">Olá, ${primeiroNome}</span>
                  </a>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="#">Veículo</a></li>
                    <li><a class="dropdown-item" href="#">Perfil</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="#" id="btnSair">Sair</a></li>
                  </ul>
                `;

                // Ação de Logout
                document.getElementById("btnSair").addEventListener("click", (e) => {
                    e.preventDefault();
                    localStorage.removeItem("access_token");
                    window.location.reload(); // Recarrega a página deslogando o usuário
                });
            } else {
                // Token expirado ou inválido
                localStorage.removeItem("access_token");
                userArea.innerHTML = userDeslogado;
            }
        } catch (error) {
            console.error("Erro na requisição /me/cliente", error);
            userArea.innerHTML = userDeslogado;
        }
    } else {
        userArea.innerHTML = userDeslogado;
    }

    document.getElementById("carrossel").innerHTML = carrossel;
    document.getElementById("features").innerHTML = features;
    document.getElementById("footer").innerHTML = footer;

    document.getElementById("carrosselItem1").src = "assets/navbar.png"
    document.getElementById("carrosselItem2").src = "assets/navbar.png"
    document.getElementById("carrosselItem3").src = "assets/navbar.png"
})
