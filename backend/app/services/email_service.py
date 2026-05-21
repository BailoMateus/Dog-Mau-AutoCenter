import logging
import resend

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

resend.api_key = settings.resend_api_key


def send_password_reset_email(email: str, reset_token: str) -> bool:
    try:
        reset_link = (
            f"{settings.frontend_url}/reset-password.html?token={reset_token}"
        )

        params = {
            "from": "DogMau Auto Center <onboarding@resend.dev>",
            "to": [email],
            "subject": "Recuperação de Senha",
            "html": f"""
            <h2>Recuperação de Senha</h2>

            <p>Clique abaixo para redefinir sua senha:</p>

            <a href="{reset_link}">
                Redefinir Senha
            </a>

            <p>O link expira em 30 minutos.</p>
            """
        }

        resend.Emails.send(params)

        logger.info(
            "Password reset email sent to %s",
            email
        )

        return True

    except Exception as e:
        logger.error(
            "Failed to send password reset email: %s",
            str(e)
        )

        return False