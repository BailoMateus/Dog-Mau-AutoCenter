import logging

from app.core.roles import MECANICO
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import get_user_by_email

logger = logging.getLogger(__name__)

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)

    if not user:
        logger.info("login falhou: usuário não encontrado email=%s", email)
        return None

    if user.ativo is False:
        logger.info("login falhou: usuário inativo email=%s", email)
        return None

    is_valid = verify_password(password, user.senha_hash)
    logger.warning("DEBUG LOGIN: verify_password=%s | plain='%s' | hash='%s' | type_hash='%s'", is_valid, password, user.senha_hash, type(user.senha_hash))
    
    if not is_valid:
        logger.info("login falhou: senha incorreta email=%s", email)
        return None

    return user

def login(email: str, password: str):
    user = authenticate_user(email, password)

    if not user:
        return None

    role = user.role if user.role else MECANICO
    token = create_access_token({"sub": str(user.id_usuario), "role": role})
    logger.info("login ok: user_id=%s role=%s", user.id_usuario, role)

    return token
