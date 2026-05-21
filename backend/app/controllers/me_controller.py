import logging
from typing import Annotated

from app.schemas.password_schema import PasswordChangeRequest
from fastapi import APIRouter, Depends, File, Path, UploadFile

from app.core.roles import CLIENTE
from app.core.security import require_role
from app.middlewares.auth_middleware import get_current_user
from app.schemas.user_schema import UserPublic, UserUpdate
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import endereco_service, veiculo_service, user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/me", tags=["Minha Conta"])


def get_my_user(current: dict):
    return user_service.get_user_or_404(int(current["user_id"]))

@router.get("/profile", response_model=UserPublic)
def get_my_profile(
    current=Depends(get_current_user),
):
    """Qualquer usuário logado vê seus próprios dados de perfil"""
    logger.info("GET /me/profile user_id=%s", current["user_id"])
    return get_my_user(current)


@router.patch("/profile", response_model=UserPublic)
def update_my_profile(
    data: UserUpdate,
    current=Depends(get_current_user),
):
    """Qualquer usuário logado atualiza seus próprios dados"""
    logger.info("PATCH /me/profile user_id=%s", current["user_id"])
    user = get_my_user(current)
    return user_service.update_user(user.id_usuario, data, actor=current)


@router.post("/foto-perfil", response_model=UserPublic)
def upload_my_profile_photo(
    file: UploadFile = File(...),
    current=Depends(get_current_user),
):
    """Qualquer usuário logado atualiza a foto de perfil (multipart/form-data)."""
    logger.info("POST /me/foto-perfil user_id=%s", current["user_id"])
    return user_service.upload_user_photo(int(current["user_id"]), file, actor=current)

@router.get("/enderecos", response_model=list[EnderecoPublic])
def list_my_enderecos(
    current=Depends(get_current_user),
):
    """Usuário lista seus próprios endereços"""
    logger.info("GET /me/enderecos user_id=%s", current["user_id"])
    return endereco_service.list_enderecos_by_user(int(current["user_id"]))


@router.post("/enderecos", response_model=EnderecoPublic, status_code=201)
def create_my_endereco(
    data: EnderecoCreate,
    current=Depends(get_current_user),
):
    """Usuário adiciona um endereço para si mesmo"""
    logger.info("POST /me/enderecos user_id=%s", current["user_id"])
    return endereco_service.add_endereco_to_user(int(current["user_id"]), data)


@router.get("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def get_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    """Usuário vê um endereço específico dele"""
    logger.info("GET /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    return endereco_service.get_endereco_by_user_or_404(int(current["user_id"]), endereco_id)


@router.patch("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def update_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    current=Depends(get_current_user),
):
    """Usuário atualiza um endereço dele"""
    logger.info("PATCH /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    return endereco_service.update_endereco_by_user(int(current["user_id"]), endereco_id, data)

@router.get("/veiculos", response_model=list[VeiculoPublic])
def list_my_veiculos(
    current=Depends(get_current_user),
):
    """Usuário lista seus próprios veículos"""
    logger.info("GET /me/veiculos user_id=%s", current["user_id"])
    return veiculo_service.list_veiculos_by_user(int(current["user_id"]))


@router.post("/veiculos", response_model=VeiculoPublic, status_code=201)
def create_my_veiculo(
    data: VeiculoCreate,
    current=Depends(get_current_user),
):
    """Usuário adiciona um veículo para si mesmo"""
    logger.info("POST /me/veiculos user_id=%s", current["user_id"])
    return veiculo_service.create_veiculo_for_user(int(current["user_id"]), data)


@router.get("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def get_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    current=Depends(get_current_user),
):
    """Usuário vê um veículo específico dele"""
    logger.info("GET /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    return veiculo_service.get_veiculo_by_user_or_404(int(current["user_id"]), veiculo_id)


@router.patch("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def update_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    current=Depends(get_current_user),
):
    """Usuário atualiza um veículo dele"""
    logger.info("PATCH /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    return veiculo_service.update_veiculo_by_user(int(current["user_id"]), veiculo_id, data)


@router.post("/password-change")
def change_my_password(
    data: PasswordChangeRequest,
    current=Depends(get_current_user),
):
    """Usuário logado altera sua própria senha após verificar senha atual."""
    logger.info("POST /me/password-change user_id=%s", current["user_id"])
    return user_service.change_user_password(
        int(current["user_id"]), 
        data, 
        actor=current
    )