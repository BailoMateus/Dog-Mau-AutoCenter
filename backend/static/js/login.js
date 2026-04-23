// login.js — Lógica do formulário de login (versão SSR)
// O cookie HttpOnly é setado pelo servidor na resposta do POST /auth/login.
// O JS só precisa redirecionar após sucesso.

document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. Login por formulário (email + senha)
    // ==========================================
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

    // ==========================================
    // 2. Login com Google (Firebase Auth)
    // ==========================================
    const btnGoogle = document.getElementById("btnGoogleLogin");

    if (btnGoogle) {
        btnGoogle.addEventListener("click", async () => {
            console.log("Botão Google clicado");

            // Verifica se o Firebase Auth está carregado
            if (typeof firebase === "undefined" || !firebase.auth) {
                alert("Serviço Google indisponível. Tente novamente mais tarde.");
                console.error("Firebase Auth SDK não carregado");
                return;
            }

            const provider = new firebase.auth.GoogleAuthProvider();

            try {
                // Abre o popup de login do Google
                const result = await firebase.auth().signInWithPopup(provider);
                const idToken = await result.user.getIdToken();

                console.log("Google Auth OK, enviando token ao backend...");

                // Envia o token do Google para nosso backend validar
                const response = await fetch("/auth/google", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "same-origin",
                    body: JSON.stringify({ id_token: idToken })
                });

                if (response.ok) {
                    console.log("Login Google OK — redirecionando...");
                    window.location.href = "/";
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    alert("Falha no login Google: " + (errorData.detail || "Erro desconhecido"));
                }
            } catch (error) {
                // Usuário cancelou o popup ou erro de rede
                if (error.code === "auth/popup-closed-by-user") {
                    console.log("Popup Google fechado pelo usuário");
                    return;
                }
                console.error("Erro no login Google:", error);
                alert("Erro no login com Google: " + error.message);
            }
        });
    }
});
