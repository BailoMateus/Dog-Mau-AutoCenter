import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.services import endereco_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/clientes/{cliente_id}/enderecos", tags=["Enderecos"])


@router.get("", response_model=list[EnderecoPublic])
def list_enderecos(
    cliente_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/enderecos", cliente_id)
    return endereco_service.list_enderecos_by_user(cliente_id)


@router.post("", response_model=EnderecoPublic, status_code=201)
def create_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    data: EnderecoCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /clientes/%s/enderecos", cliente_id)
    return endereco_service.add_endereco_to_user(cliente_id, data)


@router.get("/{endereco_id}", response_model=EnderecoPublic)
def get_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.get_endereco_or_404(cliente_id, endereco_id)


@router.patch("/{endereco_id}", response_model=EnderecoPublic)
def patch_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.update_endereco_by_user(cliente_id, endereco_id, data)


@router.delete("/{endereco_id}", response_model=EnderecoPublic)
def remove_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.delete_endereco_by_user(cliente_id, endereco_id)