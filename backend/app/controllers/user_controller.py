import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.roles import ADMIN
from app.core.security import require_role
from app.database.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user_schema import UserCreate, UserPublic, UserUpdate
from app.services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.get("", response_model=list[UserPublic])
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_role([ADMIN])),
):
    logger.info("GET /users (listar)")
    users = user_service.list_users(db)
    return users

@router.post("", response_model=UserPublic, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    existing_users = user_service.list_users(db)
    if not existing_users:
        if data.role != ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primeiro usuário deve ser ADMIN"
            )
        logger.info("POST /users (primeiro usuário - sem autenticação) email=%s role=%s", data.email, data.role)
    else:
        user_service.assert_can_modify(current, None, admin_only=True)
        logger.info("POST /users email=%s role=%s", data.email, data.role)
    
    user = user_service.create_user(db, data)
    return user

@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    logger.info("GET /users/%s actor=%s", user_id, current.get("user_id"))
    user_service.assert_can_read(current, user_id)
    return user_service.get_user_or_404(db, user_id)

@router.patch("/{user_id}", response_model=UserPublic)
def patch_user(
    user_id: Annotated[int, Path(ge=1)],
    data: UserUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    logger.info("PATCH /users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.update_user(db, user_id, data, actor=current)

@router.delete("/{user_id}", response_model=UserPublic)
def remove_user(
    user_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    logger.info("DELETE /users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.delete_user(db, user_id, actor=current)
