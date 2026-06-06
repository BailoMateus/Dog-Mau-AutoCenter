import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status, Header, File, UploadFile

from app.core.roles import ADMIN, CLIENTE, MECANICO
from app.core.security import require_role
from app.database.db import get_db
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user_schema import UserCreate, UserPublic, UserUpdate
from app.services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Usuários"])

# ==========================================
# ROTAS DO USUÁRIO LOGADO (/api/me)
# ==========================================

@router.get("/api/me/profile", response_model=UserPublic)
def get_my_profile(
    current=Depends(get_current_user)
):
    """
    REQUISITO 1 e 2: Retorna o perfil completo do usuário logado, 
    incluindo a URL da foto de perfil (foto_perfil) e dados estendidos.
    """
    user_id = current.get("user_id")
    logger.info("GET /api/me/profile associado ao user_id=%s", user_id)
    return user_service.get_user_or_404(user_id)


@router.patch("/api/me/profile", response_model=UserPublic)
def update_my_profile(
    data: UserUpdate,
    current=Depends(get_current_user)
):
    """
    Permite que o usuário atualize seus próprios dados cadastrais de forma segura.
    """
    user_id = current.get("user_id")
    logger.info("PATCH /api/me/profile executado pelo user_id=%s", user_id)
    return user_service.update_user(user_id, data, actor=current)


@router.post("/api/me/foto-perfil", response_model=UserPublic)
def upload_my_photo(
    file: UploadFile = File(...),
    current=Depends(get_current_user)
):
    """
    REQUISITO 1: Endpoint dedicado para upload da própria foto de perfil 
    apenas com base no token de sessão ativo.
    """
    user_id = current.get("user_id")
    logger.info("POST /api/me/foto-perfil executado pelo user_id=%s", user_id)
    return user_service.upload_user_photo(user_id, file, actor=current)


# ==========================================
# ROTAS ADMINISTRATIVAS (/api/users)
# ==========================================

@router.get("/api/users", response_model=list[UserPublic])
def list_users(
    _=Depends(require_role([ADMIN])),
):
    logger.info("GET /api/users (listar)")
    users = user_service.list_users()
    return users


@router.post("/api/users", response_model=UserPublic, status_code=201)
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
        logger.info("POST /api/users (primeiro usuário - sem autenticação) email=%s role=%s", data.email, data.role)
        user = user_service.create_user(data)
        return user
    else:
        if data.role == CLIENTE:
            logger.info("POST /api/users (cliente - sem autenticação) email=%s", data.email)
            user = user_service.create_user(data)
            return user
        
        # Correção do Fallback de segurança removendo objetos soltos/fantasmas (request)
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token não fornecido ou cabeçalho de autorização ausente"
            )

        current_user = get_current_user(authorization)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        if current_user["role"] not in [ADMIN, MECANICO]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Apenas funcionários podem cadastrar este tipo de conta."
            )
        
        logger.info("POST /api/users (admin/mecanico) email=%s", data.email)
        user = user_service.create_user(data)
        return user


@router.get("/api/users/{user_id}", response_model=UserPublic)
def get_user(
    user_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    logger.info("GET /api/users/%s actor=%s", user_id, current.get("user_id"))
    user_service.assert_can_read(current, user_id)
    return user_service.get_user_or_404(user_id)


@router.patch("/api/users/{user_id}", response_model=UserPublic)
def patch_user(
    user_id: Annotated[int, Path(ge=1)],
    data: UserUpdate,
    current=Depends(get_current_user),
):
    logger.info("PATCH /api/users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.update_user(user_id, data, actor=current)


@router.delete("/api/users/{user_id}", response_model=UserPublic)
def remove_user(
    user_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    logger.info("DELETE /api/users/%s actor=%s", user_id, current.get("user_id"))
    return user_service.delete_user(user_id, actor=current)


@router.post("/api/users/{user_id}/foto-perfil", response_model=UserPublic)
@router.post("/api/users/{user_id}/upload-photo", response_model=UserPublic, include_in_schema=False)
def upload_user_photo(
    user_id: Annotated[int, Path(ge=1)],
    file: UploadFile = File(...),
    current=Depends(get_current_user),
):
    logger.info("POST /api/users/%s/foto-perfil actor=%s", user_id, current.get("user_id"))
    return user_service.upload_user_photo(user_id, file, actor=current)