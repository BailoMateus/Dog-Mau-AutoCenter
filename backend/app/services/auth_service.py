import logging

from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_email
from app.core.security import verify_password, create_access_token

logger = logging.getLogger(__name__)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.senha_hash):
        return None

    return user


def login(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if not user:
        logger.info("login falhou: usuário não encontrado email=%s", email)
        return None

    if not verify_password(password, user.senha_hash):
        logger.info("login falhou: senha incorreta email=%s", email)
        return None

    token = create_access_token(
        {"sub": str(user.id_usuario), "role": user.role}
    )
    logger.info(
        "login ok: user_id=%s role=%s",
        user.id_usuario,
        user.role,
    )

    return token
