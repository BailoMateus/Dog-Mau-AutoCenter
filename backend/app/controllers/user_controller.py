import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status, Header

from app.core.roles import ADMIN, CLIENTE
from app.core.security import require_role
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user_schema import UserCreate, UserPublic, UserUpdate
from app.services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.get("", response_model=list[UserPublic])
def list_users(
    _=Depends(require_role([ADMIN])),
):
    logger.info("GET /users (listar)")
    users = user_service.list_users()
    return users

@router.post("", response_model=UserPublic, status_code=201)
def create_user(
    data: UserCreate,
    authorization: Annotated[str | None, Header()] = None,
):
    existing_admin = user_service.get_user_by_role(ADMIN)
    if not existing_admin:
        if data.role != ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primeiro usuário deve ser ADMIN"
            )
        logger.info("POST /users (primeiro usuário - sem autenticação) email=%s role=%s", data.email, data.role)
        user = user_service.create_user(data)
        return user
    else:
        if data.role == CLIENTE:
            logger.info("POST /users (cliente - sem autenticação) email=%s", data.email)
            user = user_service.create_user(data)
            return user
        
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Validação do token
        token = authorization.replace("Bearer ", "")
        try:
            from app.core.config import SECRET_KEY, ALGORITHM
            from jose import jwt
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            
            if role != ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acesso não autorizado"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        logger.info("POST /users email=%s role=%s", data.email, data.role)
        user = user_service.create_user(data)
        return user

@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    logger.info("GET /users/%s actor=%s", user_id, current.get("user_id"))
    user_service.assert_can_read(current, user_id)
    return user_service.get_user_or_404(user_id)

@router.patch("/{user_id}", response_model=UserPublic)
def patch_user(
    user_id: Annotated[int, Path(ge=1)],
    data: UserUpdate,
    current=Depends(get_current_user),
):
    logger.info("PATCH /users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.update_user(user_id, data, actor=current)

@router.delete("/{user_id}", response_model=UserPublic)
def remove_user(
    user_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    logger.info("DELETE /users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.delete_user(user_id, actor=current)
