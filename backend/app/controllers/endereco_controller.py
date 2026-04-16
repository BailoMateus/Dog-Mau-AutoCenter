import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.services import endereco_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/clientes/{cliente_id}/enderecos", tags=["Enderecos"])


@router.get("", response_model=list[EnderecoPublic])
def list_enderecos(
    cliente_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/enderecos", cliente_id)
    return endereco_service.list_enderecos(db, cliente_id)


@router.post("", response_model=EnderecoPublic, status_code=201)
def create_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    data: EnderecoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /clientes/%s/enderecos", cliente_id)
    return endereco_service.add_endereco(db, cliente_id, data)


@router.get("/{endereco_id}", response_model=EnderecoPublic)
def get_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.get_endereco_or_404(db, cliente_id, endereco_id)


@router.patch("/{endereco_id}", response_model=EnderecoPublic)
def patch_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.update_endereco(db, cliente_id, endereco_id, data)


@router.delete("/{endereco_id}", response_model=EnderecoPublic)
def remove_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.delete_endereco(db, cliente_id, endereco_id)