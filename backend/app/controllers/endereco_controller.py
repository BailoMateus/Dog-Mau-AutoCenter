import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException, status

from app.core.roles import ADMIN, MECANICO
# Adaptado com a sua dependência de usuário logado
from app.core.security import get_current_user 
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.services import endereco_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enderecos", tags=["Enderecos"])


@router.get("", response_model=list[EnderecoPublic])
def list_enderecos(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    logger.info("GET /enderecos por usuario %s", current_user.id_usuario)
    
    # STAFF vê tudo, Cliente vê apenas os dele
    if current_user.role in [ADMIN, MECANICO]:
        return endereco_service.list_enderecos()
        
    # Ajustado para usar o nome exato do seu service: list_enderecos_by_user
    return endereco_service.list_enderecos_by_user(current_user.id_usuario)


@router.post("", response_model=EnderecoPublic, status_code=201)
def create_endereco(
    data: EnderecoCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    logger.info("POST /enderecos")
    
    # Se for cliente, ignoramos o id_usuario enviado no JSON e injetamos o dele
    if current_user.role not in [ADMIN, MECANICO]:
        data.id_usuario = current_user.id_usuario
        
    return endereco_service.create_endereco(data)


@router.get("/{endereco_id}", response_model=EnderecoPublic)
def get_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    logger.info("GET /enderecos/%s", endereco_id)
    
    # Se for cliente comum, usamos a busca do service com a trava do id_usuario
    if current_user.role not in [ADMIN, MECANICO]:
        return endereco_service.get_endereco_by_user_or_404(current_user.id_usuario, endereco_id)
        
    return endereco_service.get_endereco_or_404(endereco_id)


@router.patch("/{endereco_id}", response_model=EnderecoPublic)
def update_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    logger.info("PATCH /enderecos/%s", endereco_id)
    
    # Se for cliente comum, atualiza garantindo a posse do endereço
    if current_user.role not in [ADMIN, MECANICO]:
        return endereco_service.update_endereco_by_user(current_user.id_usuario, endereco_id, data)
        
    return endereco_service.update_endereco(endereco_id, data)


@router.delete("/{endereco_id}", response_model=EnderecoPublic)
def delete_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    logger.info("DELETE /enderecos/%s", endereco_id)
    
    # Se for cliente comum, deleta garantindo a posse
    if current_user.role not in [ADMIN, MECANICO]:
        return endereco_service.delete_endereco_by_user(current_user.id_usuario, endereco_id)
        
    return endereco_service.delete_endereco(endereco_id)