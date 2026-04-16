// Arquivo: frontend/cadastro.js
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


// Inicializa o Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

document.addEventListener("DOMContentLoaded", () => {

    // 1. Lógica do botão Google Auth com Firebase
    const btnGoogleLogin = document.getElementById("btnGoogleLogin");
    if (btnGoogleLogin) {
        btnGoogleLogin.addEventListener("click", async () => {
            try {
                const result = await signInWithPopup(auth, provider);
                const credential = GoogleAuthProvider.credentialFromResult(result);
                const token = credential.accessToken;
                const user = result.user;

                // Obtém o JWT Token retornado pelo Firebase para validar no backend
                const idToken = await user.getIdToken();
                console.log("Firebase SignIn Realizado. Token:", idToken);

                // Envia token ao backend centralizado
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

    // 2. Trava de Idade: Setar data máxima no HTML para 18 anos atrás
    const inputDate = document.getElementById("floatingNascimento");
    if (inputDate) {
        const today = new Date();
        const past18Years = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
        const maxDateString = past18Years.toISOString().split("T")[0];
        inputDate.setAttribute("max", maxDateString);
    }

    // 3. Olhinho - Mostrar/Esconder Senhas
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

    // 4. Integração ViaCEP
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

    // Função de Validação Matemática de CPF e CNPJ (Módulo 11)
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
            let tamanho = doc.length - 2
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

    // 5. Submit do Formulário de Cadastro Normal
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Validação de CPF/CNPJ
            const cpfCnpjInput = document.getElementById("floatingCpf");
            const cpfCnpjValue = cpfCnpjInput.value;

            if (!validarCpfCnpj(cpfCnpjValue)) {
                cpfCnpjInput.classList.add("is-invalid");
                alert("O CPF ou CNPJ digitado é inválido. Verifique os números.");
                return false;
            } else {
                cpfCnpjInput.classList.remove("is-invalid");
            }

            const password = inputPassword.value;
            const confirm = inputConfirm.value;

            // Validação local de Confirmação de Senha
            if (password !== confirm) {
                alert("As senhas não coincidem!");
                return;
            }

            // Validar senha forte no front preventivamente
            const strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})");
            if (!strongRegex.test(password)) {
                alert("Sua senha é fraca. Ela precisa ter ao menos:\n- 8 Caracteres\n- 1 Letra Maiúscula\n- 1 Letra Minúscula\n- 1 Número\n- 1 Caractere Especial (!@#$%)");
                return;
            }

            const payload = {
                nome: document.getElementById("floatingNome").value,
                email: document.getElementById("floatingInput").value,
                cpf_cnpj: document.getElementById("floatingCpf").value.replace(/\D/g, ''),
                data_nascimento: document.getElementById("floatingNascimento").value,
                password: password,
                cep: document.getElementById("floatingCep").value.replace(/\D/g, ''),
                logradouro: document.getElementById("floatingRua").value,
                numero: document.getElementById("floatingNumero").value,
                bairro: document.getElementById("floatingBairro").value,
                cidade: document.getElementById("floatingCidade").value,
                estado: document.getElementById("floatingEstado").value,
                telefone: null
            };

            try {
                const response = await fetch(`${window.BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Erro genérico no cadastro");
                }

                alert("Cadastro realizado com sucesso!");
                localStorage.setItem("access_token", data.access_token);
                window.location.href = "index.html"; // Redireciona
            } catch (err) {
                console.error(err);
                alert("Ops! " + err.message);
            }
        });
    }
});
