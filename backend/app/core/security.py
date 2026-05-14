import logging
from datetime import datetime, timedelta
import os

from fastapi import Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.middlewares.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash de senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verificar senha
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# gerar token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug("access token emitido sub=%s", to_encode.get("sub"))
    return encoded_jwt

def validate_file(file, allowed_types, max_size):
    """Valida tipo e tamanho do arquivo."""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de arquivo não permitido."
        )

    if len(file.file.read()) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo excede o tamanho máximo permitido."
        )
    file.file.seek(0)  # Resetar ponteiro do arquivo

def require_role(allowed_roles: list):
    def role_checker(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            logger.warning(
                "autorização negada user_id=%s role=%s allowed=%s",
                user.get("user_id"),
                user.get("role"),
                allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado",
            )

        logger.debug(
            "autorização ok user_id=%s role=%s",
            user.get("user_id"),
            user.get("role"),
        )
        return user

    return role_checker
