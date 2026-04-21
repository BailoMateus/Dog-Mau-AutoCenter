import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBLY-5JOkHA6YP4viYw5SFB3H1VmoKXzNo",
    authDomain: "dog-mau-autocenter.firebaseapp.com",
    projectId: "dog-mau-autocenter",
    storageBucket: "dog-mau-autocenter.firebasestorage.app",
    messagingSenderId: "210021860949",
    appId: "1:210021860949:web:e7ce12df0e9adad49536dc",
    measurementId: "G-HMRJC0BJXL"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            // 1. OBRIGATÓRIO: Impede o form de recarregar a página
            event.preventDefault();

            // Pega os valores dos inputs definidos no login.html
            const email = document.getElementById("floatingInput").value;
            const password = document.getElementById("floatingPassword").value;
            
            // Log antes do fetch
            console.log("Enviando login...", { email });

            // 2. Prepara o formato JSON esperado pelo schema Pydantic no FastAPI
            const payload = {
                email: email,
                password: password
            };
            
            try {
                // Configurando a requisição para a rota correta do back-end
                const response = await fetch(`${window.BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });
                
                // Log do retorno do fetch
                console.log("Retorno do fetch (status):", response.status);
                
                // 3 e 4. Lida com a resposta
                if (response.ok) {
                    const data = await response.json();
                    
                    // Salva o token
                    localStorage.setItem("access_token", data.access_token);
                    console.log("Login bem-sucedido! Token salvo.");
                    
                    // Redireciona para o index para disparar o GET de perfil /me/cliente
                    window.location.href = "index.html"; 
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMsg = errorData.detail || "Usuário ou senha incorretos.";
                    
                    // Feedback Visual e Logs em caso de erro
                    console.error("Falha no login API:", errorMsg);
                    alert("Falha no login: " + errorMsg);
                }
            } catch (error) {
                // Erro de rede ou indisponibilidade
                console.error("Erro na requisição /auth/login:", error);
                alert("Erro ao tentar conectar com o servidor. Tente novamente mais tarde.");
            }
        });
    }

    const btnGoogleLogin = document.getElementById("btnGoogleLogin");
    if (btnGoogleLogin) {
        btnGoogleLogin.addEventListener("click", async () => {
            try {
                const result = await signInWithPopup(auth, provider);
                const user = result.user;
                const idToken = await user.getIdToken();
                console.log("Firebase SignIn Realizado. Token:", idToken);

                const response = await fetch(`${window.BASE_URL}/auth/google`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id_token: idToken })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Erro ao conectar com servidor");

                alert("Acesso Google efetuado com sucesso!");
                localStorage.setItem("access_token", data.access_token);
                window.location.href = "index.html";
            } catch (error) {
                console.error("Erro no fluxo do Google Login", error);
                alert("Falha no login social. Verifique o console.");
            }
        });
    }
});
