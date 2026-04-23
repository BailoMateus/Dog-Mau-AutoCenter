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

            // Validação de Confirmação de Senha
            if (password !== confirm) {
                alert("As senhas não coincidem!");
                return;
            }

            // Validar senha forte
            const strongRegex = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\\$%\\^&\\*])(?=.{8,})");
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
                const response = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "same-origin",
                    body: JSON.stringify(payload)
                });

                // IMPORTANTE: checar response.ok ANTES de .json()
                // Se o servidor retorna 500 com corpo HTML, .json() estouraria
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                if (!response.ok) {
                    // Tentar ler JSON de erro, mas proteger contra corpo não-JSON
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || "Erro no cadastro (status " + response.status + ")");
                }

                // Sucesso — cookie HttpOnly já foi setado pelo servidor
                console.log("Cadastro bem-sucedido! Cookie HttpOnly setado pelo servidor.");
                alert("Cadastro realizado com sucesso!");
                window.location.href = "/";

            } catch (err) {
                console.error(err);
                alert("Ops! " + err.message);
            }
        });
    }
});
