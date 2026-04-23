// login.js — Lógica do formulário de login (versão Jinja2)
// O token JWT é salvo como cookie para que o servidor possa ler nas próximas requests.

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("floatingInput").value;
            const password = document.getElementById("floatingPassword").value;

            console.log("Enviando login...", { email });

            const payload = {
                email: email,
                password: password
            };

            try {
                const response = await fetch("/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                console.log("Retorno do fetch (status):", response.status);

                if (response.ok) {
                    const data = await response.json();

                    // Salva o token como cookie para o servidor ler (controle de acesso Jinja2)
                    document.cookie = `access_token=${data.access_token}; path=/; SameSite=Lax`;
                    console.log("Login bem-sucedido! Cookie setado.");

                    // Redireciona para a home
                    window.location.href = "/";
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMsg = errorData.detail || "Usuário ou senha incorretos.";

                    console.error("Falha no login API:", errorMsg);
                    alert("Falha no login: " + errorMsg);
                }
            } catch (error) {
                console.error("Erro na requisição /auth/login:", error);
                alert("Erro ao tentar conectar com o servidor. Tente novamente mais tarde.");
            }
        });
    }
});
