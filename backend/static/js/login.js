// login.js — Lógica do formulário de login (versão SSR)
// O cookie HttpOnly é setado pelo servidor na resposta do POST /auth/login.
// O JS só precisa redirecionar após sucesso.

document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // 1. Login por formulário (email + senha)
    // ==========================================
    // Agora o login é feito via POST nativo (action="/auth/login") no HTML.
    // O JS só lida com o Google Auth.
    
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
