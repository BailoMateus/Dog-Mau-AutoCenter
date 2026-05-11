import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.marca_schema import MarcaCreate, MarcaPublic, MarcaUpdate
from app.services import marca_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/marcas", tags=["Marcas"])

@router.get("", response_model=list[MarcaPublic])
def list_marcas(
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /marcas")
    return marca_service.list_marcas()

@router.post("", response_model=MarcaPublic, status_code=201)
def create_marca(
    data: MarcaCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /marcas")
    return marca_service.create_marca(data)

@router.get("/{marca_id}", response_model=MarcaPublic)
def get_marca(
    marca_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /marcas/%s", marca_id)
    return marca_service.get_marca_or_404(marca_id)

@router.patch("/{marca_id}", response_model=MarcaPublic)
def update_marca(
    marca_id: Annotated[int, Path(ge=1)],
    data: MarcaUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /marcas/%s", marca_id)
    return marca_service.update_marca(marca_id, data)

@router.delete("/{marca_id}", response_model=MarcaPublic)
def delete_marca(
    marca_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /marcas/%s", marca_id)
    return marca_service.delete_marca(marca_id)