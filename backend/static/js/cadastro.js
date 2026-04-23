// cadastro.js — Lógica do formulário de cadastro (versão SSR)
// O cookie HttpOnly é setado pelo servidor na resposta do POST /auth/register.
// O JS apenas valida client-side e redireciona após sucesso.

document.addEventListener("DOMContentLoaded", () => {

    // 1. Trava de Idade: data máxima 18 anos atrás
    const inputDate = document.getElementById("floatingNascimento");
    if (inputDate) {
        const today = new Date();
        const past18Years = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
        const maxDateString = past18Years.toISOString().split("T")[0];
        inputDate.setAttribute("max", maxDateString);
    }

    // 2. Olhinho - Mostrar/Esconder Senhas
    const togglePassword = document.getElementById("togglePassword");
    const inputPassword = document.getElementById("floatingPassword");
    const toggleConfirm = document.getElementById("toggleConfirmPassword");
    const inputConfirm = document.getElementById("floatingConfirmPassword");

    const setupToggle = (btnToggle, input) => {
        if (btnToggle && input) {
            btnToggle.addEventListener("click", () => {
                const type = input.getAttribute("type") === "password" ? "text" : "password";
                input.setAttribute("type", type);
                btnToggle.classList.toggle("bi-eye");
                btnToggle.classList.toggle("bi-eye-slash");
            });
        }
    };
    setupToggle(togglePassword, inputPassword);
    setupToggle(toggleConfirm, inputConfirm);

    // 3. Integração ViaCEP
    const inputCep = document.getElementById("floatingCep");
    if (inputCep) {
        inputCep.addEventListener("blur", async (e) => {
            let cepValue = e.target.value.replace(/\D/g, "");
            if (cepValue.length === 8) {
                try {
                    const res = await fetch(`https://viacep.com.br/ws/${cepValue}/json/`);
                    const data = await res.json();
                    if (!data.erro) {
                        document.getElementById("floatingRua").value = data.logradouro;
                        document.getElementById("floatingBairro").value = data.bairro;
                        document.getElementById("floatingCidade").value = data.localidade;
                        document.getElementById("floatingEstado").value = data.uf;
                        document.getElementById("floatingNumero").focus();
                    }
                } catch (err) {
                    console.error("ViaCEP falhou", err);
                }
            }
        });
    }

    // 4. Validação Matemática de CPF e CNPJ (Módulo 11)
    function validarCpfCnpj(doc) {
        doc = doc.replace(/\D/g, "");
        if (doc.length === 11) {
            if (/^(\d)\1+$/.test(doc)) return false;
            let soma = 0;
            let resto;
            for (let i = 1; i <= 9; i++) soma = soma + parseInt(doc.substring(i - 1, i)) * (11 - i);
            resto = (soma * 10) % 11 % 10;
            if (resto !== parseInt(doc.substring(9, 10))) return false;

            soma = 0;
            for (let i = 1; i <= 10; i++) soma = soma + parseInt(doc.substring(i - 1, i)) * (12 - i);
            resto = (soma * 10) % 11 % 10;
            if (resto !== parseInt(doc.substring(10, 11))) return false;
            return true;
        } else if (doc.length === 14) {
            if (/^(\d)\1+$/.test(doc)) return false;
            let tamanho = doc.length - 2;
            let numeros = doc.substring(0, tamanho);
            let digitos = doc.substring(tamanho);
            let soma = 0;
            let pos = tamanho - 7;
            for (let i = tamanho; i >= 1; i--) {
                soma += numeros.charAt(tamanho - i) * pos--;
                if (pos < 2) pos = 9;
            }
            let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
            if (resultado !== parseInt(digitos.charAt(0))) return false;

            tamanho = tamanho + 1;
            numeros = doc.substring(0, tamanho);
            soma = 0;
            pos = tamanho - 7;
            for (let i = tamanho; i >= 1; i--) {
                soma += numeros.charAt(tamanho - i) * pos--;
                if (pos < 2) pos = 9;
            }
            resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
            if (resultado !== parseInt(digitos.charAt(1))) return false;
            return true;
        }
        return false;
    }

    // 5. Submit do Formulário de Cadastro
    const form = document.getElementById("cadastroForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            console.log("Iniciando submissão do formulário...");
            e.preventDefault();
            
            let isValid = true;
            
            // Dispara validação visual nativa dos campos com 'required', 'minlength', 'max' no HTML
            if (!form.checkValidity()) {
                isValid = false;
                console.warn("Validação nativa falhou (campos vazios ou curtos).");
            }
            form.classList.add("was-validated");

            // Validação de CPF/CNPJ Manualmente
            const cpfCnpjInput = document.getElementById("floatingCpf");
            const cpfCnpjValue = cpfCnpjInput ? cpfCnpjInput.value : "";
            const feedbackCpf = document.getElementById("feedbackCpf");
            
            if (cpfCnpjValue && !validarCpfCnpj(cpfCnpjValue)) {
                cpfCnpjInput.classList.remove("is-valid");
                cpfCnpjInput.classList.add("is-invalid");
                if (feedbackCpf) feedbackCpf.textContent = "Dígitos verificadores do CPF/CNPJ inválidos.";
                isValid = false;
                console.warn("CPF/CNPJ inválido.");
            } else if (cpfCnpjInput) {
                // Remove custom is-invalid forces if valid (rely on native was-validated)
                cpfCnpjInput.classList.remove("is-invalid");
            }

            if (!inputPassword || !inputConfirm) {
                console.error("Inputs de senha não encontrados no DOM!");
                return;
            }

            const password = inputPassword.value;
            const confirm = inputConfirm.value;
            const feedbackPassword = document.getElementById("feedbackPassword");
            const feedbackConfirm = document.getElementById("feedbackConfirmPassword");

            // Validação de Confirmação de Senha
            if (password !== confirm) {
                inputConfirm.classList.remove("is-valid");
                inputConfirm.classList.add("is-invalid");
                if (feedbackConfirm) feedbackConfirm.textContent = "As senhas não coincidem.";
                isValid = false;
                console.warn("Validação falhou: senhas não coincidem.");
            } else {
                inputConfirm.classList.remove("is-invalid");
            }

            // Validar senha forte
            const strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\\$%\\^&\\*])(?=.{8,})");
            if (password && !strongRegex.test(password)) {
                inputPassword.classList.remove("is-valid");
                inputPassword.classList.add("is-invalid");
                if (feedbackPassword) feedbackPassword.innerHTML = "Senha fraca. Deve ter mínimo 8 caracteres com uma <b>letra maiúscula</b>, <b>minúscula</b>, <b>número</b> e <b>caractere especial (!@#$%)</b>.";
                isValid = false;
                console.warn("Validação falhou: senha fraca.");
            } else {
                inputPassword.classList.remove("is-invalid");
            }

            if (!isValid) {
                console.warn("Formulário bloqueado por erros validacao em tela.");
                return; // Bloqueia submissão silenciosamente mostrando erros na interface
            }

            console.log("Validações concluídas com sucesso.");

            try {
                // Limpar máscara dos campos CPF/CNPJ e CEP antes do envio nativo
                cpfCnpjInput.value = cpfCnpjValue.replace(/\D/g, '');
                const cepInput = document.getElementById("floatingCep");
                if (cepInput) {
                    cepInput.value = cepInput.value.replace(/\D/g, '');
                }
                console.log("Máscaras removidas. CPF e CEP limpos.");
            } catch (err) {
                console.error("Erro ao limpar máscaras:", err);
            }

            console.log("Acionando envio nativo (form.submit())...");
            try {
                // Envia o formulário nativamente bypassing interceptors
                form.submit();
                console.log("form.submit() disparado com sucesso!");
            } catch (err) {
                console.error("Erro fatal ao tentar enviar via form.submit():", err);
            }
        });
    }

    // ==========================================
    // 6. Login com Google (Firebase Auth)
    // ==========================================
    const btnGoogle = document.getElementById("btnGoogleLogin");

    if (btnGoogle) {
        btnGoogle.addEventListener("click", async () => {
            console.log("Botão Google clicado (cadastro)");

            if (typeof firebase === "undefined" || !firebase.auth) {
                alert("Serviço Google indisponível. Tente novamente mais tarde.");
                console.error("Firebase Auth SDK não carregado");
                return;
            }

            const provider = new firebase.auth.GoogleAuthProvider();

            try {
                const result = await firebase.auth().signInWithPopup(provider);
                const idToken = await result.user.getIdToken();

                console.log("Google Auth OK, enviando token ao backend...");

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
