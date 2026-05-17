const form = document.getElementById("resetPasswordForm");

//vcs arrumam isso dps tb, eu so quero que funcione

form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const token =
        document.getElementById("token").value;

    const novaSenha =
        document.getElementById("novaSenha").value;

    const confirmarSenha =
        document.getElementById("confirmarSenha").value;

    const errorBox =
        document.getElementById("errorBox");

    const successBox =
        document.getElementById("successBox");

    const submitButton =
        document.getElementById("submitButton");

    errorBox.classList.add("d-none");
    successBox.classList.add("d-none");

    if (novaSenha !== confirmarSenha) {
        errorBox.textContent =
            "As senhas não coincidem.";

        errorBox.classList.remove("d-none");

        return;
    }

    submitButton.disabled = true;

    submitButton.innerHTML = `
        <span
            class="spinner-border spinner-border-sm me-2"
            role="status"
            aria-hidden="true"
        ></span>

        Salvando...
    `;

    try {

        const response = await fetch(
            "/auth/reset-password",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                credentials: "include",

                body: JSON.stringify({
                    token: token,
                    nova_senha: novaSenha
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            errorBox.textContent =
                data.detail ||
                "Erro ao redefinir senha.";

            errorBox.classList.remove("d-none");

            return;
        }

        successBox.textContent =
            "Senha redefinida com sucesso. Redirecionando...";

        successBox.classList.remove("d-none");

        setTimeout(() => {
            window.location.href = "/";
        }, 2000);

    } catch (error) {

        console.error(error);

        errorBox.textContent =
            "Erro de rede ao redefinir senha.";

        errorBox.classList.remove("d-none");

    } finally {

        submitButton.disabled = false;

        submitButton.innerHTML =
            "Redefinir senha";
    }
});