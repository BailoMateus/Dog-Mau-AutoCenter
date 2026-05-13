import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.services import endereco_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/enderecos", tags=["Enderecos"])


@router.get("", response_model=list[EnderecoPublic])
def list_enderecos(
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /enderecos")
    return endereco_service.list_enderecos()


@router.post("", response_model=EnderecoPublic, status_code=201)
def create_endereco(
    data: EnderecoCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /enderecos")
    return endereco_service.create_endereco(data)


@router.get("/{endereco_id}", response_model=EnderecoPublic)
def get_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /enderecos/%s", endereco_id)
    return endereco_service.get_endereco_or_404(endereco_id)


@router.patch("/{endereco_id}", response_model=EnderecoPublic)
def update_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /enderecos/%s", endereco_id)
    return endereco_service.update_endereco(endereco_id, data)


@router.delete("/{endereco_id}", response_model=EnderecoPublic)
def delete_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /enderecos/%s", endereco_id)
    return endereco_service.delete_endereco(endereco_id)
