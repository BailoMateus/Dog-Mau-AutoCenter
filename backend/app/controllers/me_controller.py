import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import CLIENTE
from app.core.security import require_role
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user_schema import UserPublic, UserUpdate
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import endereco_service, veiculo_service, user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/me", tags=["Minha Conta"])

# Middleware para garantir que é cliente
def require_cliente(current=Depends(get_current_user)):
    if current.get("role") != CLIENTE:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para clientes"
        )
    return current


def get_my_user(current: dict):
    return user_service.get_user_or_404(int(current["user_id"]))

@router.get("/profile", response_model=UserPublic)
def get_my_profile(
    current=Depends(require_cliente),
):
    """Cliente vê seus próprios dados de perfil"""
    logger.info("GET /me/profile user_id=%s", current["user_id"])
    return get_my_user(current)


@router.patch("/profile", response_model=UserPublic)
def update_my_profile(
    data: UserUpdate,
    current=Depends(require_cliente),
):
    """Cliente atualiza seus próprios dados"""
    logger.info("PATCH /me/profile user_id=%s", current["user_id"])
    user = get_my_user(current)
    return user_service.update_user(user.id_usuario, data, actor=current)


# Endereços do cliente
@router.get("/enderecos", response_model=list[EnderecoPublic])
def list_my_enderecos(
    current=Depends(require_cliente),
):
    """Cliente lista seus endereços"""
    logger.info("GET /me/enderecos user_id=%s", current["user_id"])
    return endereco_service.list_enderecos_by_user(int(current["user_id"]))

@router.post("/enderecos", response_model=EnderecoPublic, status_code=201)
def create_my_endereco(
    data: EnderecoCreate,
    current=Depends(require_cliente),
):
    """Cliente adiciona endereço"""
    logger.info("POST /me/enderecos user_id=%s", current["user_id"])
    return endereco_service.add_endereco_to_user(int(current["user_id"]), data)

@router.get("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def get_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    current=Depends(require_cliente),
):
    """Cliente vê um endereço específico"""
    logger.info("GET /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    return endereco_service.get_endereco_by_user_or_404(int(current["user_id"]), endereco_id)

@router.patch("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def update_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    current=Depends(require_cliente),
):
    """Cliente atualiza um endereço"""
    logger.info("PATCH /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    return endereco_service.update_endereco_by_user(int(current["user_id"]), endereco_id, data)


# Veículos do cliente
@router.get("/veiculos", response_model=list[VeiculoPublic])
def list_my_veiculos(
    current=Depends(require_cliente),
):
    """Cliente lista seus veículos"""
    logger.info("GET /me/veiculos user_id=%s", current["user_id"])
    return veiculo_service.list_veiculos_by_user(int(current["user_id"]))

@router.post("/veiculos", response_model=VeiculoPublic, status_code=201)
def create_my_veiculo(
    data: VeiculoCreate,
    current=Depends(require_cliente),
):
    """Cliente adiciona veículo"""
    logger.info("POST /me/veiculos user_id=%s", current["user_id"])
    return veiculo_service.create_veiculo_for_user(int(current["user_id"]), data)

@router.get("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def get_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    current=Depends(require_cliente),
):
    """Cliente vê um veículo específico"""
    logger.info("GET /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    return veiculo_service.get_veiculo_by_user_or_404(int(current["user_id"]), veiculo_id)

@router.patch("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def update_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    current=Depends(require_cliente),
):
    """Cliente atualiza um veículo"""
    logger.info("PATCH /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    return veiculo_service.update_veiculo_by_user(int(current["user_id"]), veiculo_id, data)