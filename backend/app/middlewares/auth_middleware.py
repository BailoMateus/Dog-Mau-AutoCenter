import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.config import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

# OAuth2PasswordBearer para documentação OpenAPI (usa header Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _decode_token(token: str) -> dict:
    """Decodifica e valida um JWT. Retorna payload ou levanta JWTError."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None:
        raise JWTError("payload sem 'sub'")
    return {"user_id": user_id, "role": role}


def _extract_token_from_request(request: Request) -> str:
    """
    Extrai o token JWT do request.
    Tenta em ordem de prioridade:
    1. Cookie '__session' (HttpOnly, preferencial para browser/fetch com credentials)
    2. Cookie 'access_token' (compatibilidade)
    3. Header Authorization: Bearer <token> (para clientes API/Swagger)
    """
    # 1. Tenta cookie __session (HttpOnly)
    token = request.cookies.get("__session")
    if token:
        logger.debug("Token lido do cookie __session")
        return token
    
    # 2. Fallback: cookie access_token
    token = request.cookies.get("access_token")
    if token:
        logger.debug("Token lido do cookie access_token")
        return token
    
    # 3. Fallback: Header Authorization
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        logger.debug("Token lido do header Authorization")
        return token
    
    return None


def get_current_user(request: Request):
    """
    Extrai o usuário autenticado do token JWT.
    
    Estratégia de leitura do token (em ordem de prioridade):
    1. Cookie '__session' (HttpOnly - preferencial para fetch com credentials)
    2. Cookie 'access_token' (compatibilidade)
    3. Header Authorization: Bearer <token> (para clientes API / Swagger)
    
    Se nenhum token for encontrado ou se for inválido, levanta 401.
    """
    token = _extract_token_from_request(request)
    
    if not token:
        logger.warning("Acesso negado: sem token (header ou cookie)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        user_data = _decode_token(token)
        logger.debug("JWT ok user_id=%s role=%s", user_data["user_id"], user_data["role"])
        return user_data
    except JWTError as e:
        logger.warning("JWT inválido ou expirado: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
