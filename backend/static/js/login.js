// login.js — Lógica do formulário de login (versão SSR)
// O cookie HttpOnly é setado pelo servidor na resposta do POST /auth/login.
// O JS só precisa redirecionar após sucesso.

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
                    credentials: "same-origin",
                    body: JSON.stringify(payload)
                });

                console.log("Retorno do fetch (status):", response.status);

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                if (response.ok) {
                    // Cookie HttpOnly já foi setado pelo servidor no response
                    console.log("Login bem-sucedido! Cookie HttpOnly setado pelo servidor.");
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
