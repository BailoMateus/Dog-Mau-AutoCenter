import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.cliente_schema import ClienteCreate, ClientePublic, ClienteUpdate
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.services import cliente_service, endereco_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("", response_model=list[ClientePublic])
def list_clientes(
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes (listar)")
    return cliente_service.list_clientes(db)


@router.post("", response_model=ClientePublic, status_code=201)
def create_cliente(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /clientes nome=%s", data.nome)
    return cliente_service.create_cliente(db, data)


@router.get("/{cliente_id}", response_model=ClientePublic)
def get_cliente(
    cliente_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s", cliente_id)
    return cliente_service.get_cliente_or_404(db, cliente_id)


@router.patch("/{cliente_id}", response_model=ClientePublic)
def patch_cliente(
    cliente_id: Annotated[int, Path(ge=1)],
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /clientes/%s", cliente_id)
    return cliente_service.update_cliente(db, cliente_id, data)


@router.delete("/{cliente_id}", response_model=ClientePublic)
def remove_cliente(
    cliente_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /clientes/%s", cliente_id)
    return cliente_service.delete_cliente(db, cliente_id)


@router.post("/{cliente_id}/enderecos", response_model=EnderecoPublic, status_code=201)
def add_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    data: EnderecoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /clientes/%s/enderecos", cliente_id)
    return endereco_service.add_endereco(db, cliente_id, data)


@router.get("/{cliente_id}/enderecos", response_model=list[EnderecoPublic])
def list_enderecos(
    cliente_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/enderecos", cliente_id)
    return endereco_service.list_enderecos(db, cliente_id)


@router.patch("/{cliente_id}/enderecos/{endereco_id}", response_model=EnderecoPublic)
def patch_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.update_endereco(db, cliente_id, endereco_id, data)


@router.delete("/{cliente_id}/enderecos/{endereco_id}", response_model=EnderecoPublic)
def remove_endereco(
    cliente_id: Annotated[int, Path(ge=1)],
    endereco_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /clientes/%s/enderecos/%s", cliente_id, endereco_id)
    return endereco_service.delete_endereco(db, cliente_id, endereco_id)
