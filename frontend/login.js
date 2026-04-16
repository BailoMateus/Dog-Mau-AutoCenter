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
});
