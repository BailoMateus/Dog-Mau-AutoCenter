import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.modelo_schema import ModeloCreate, ModeloPublic, ModeloUpdate
from app.services import modelo_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/modelos", tags=["Modelos"])

@router.get("", response_model=list[ModeloPublic])
def list_modelos(
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /modelos")
    return modelo_service.list_modelos(db)


@router.post("", response_model=ModeloPublic, status_code=201)
def create_modelo(
    data: ModeloCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /modelos nome=%s", data.nome_modelo)
    return modelo_service.create_modelo(db, data)


@router.get("/{modelo_id}", response_model=ModeloPublic)
def get_modelo(
    modelo_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /modelos/%s", modelo_id)
    return modelo_service.get_modelo_or_404(db, modelo_id)


@router.get("/marca/{marca_id}", response_model=list[ModeloPublic])
def list_modelos_by_marca(
    marca_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /modelos/marca/%s", marca_id)
    return modelo_service.list_modelos_by_marca(db, marca_id)


@router.patch("/{modelo_id}", response_model=ModeloPublic)
def patch_modelo(
    modelo_id: Annotated[int, Path(ge=1)],
    data: ModeloUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /modelos/%s", modelo_id)
    return modelo_service.update_modelo(db, modelo_id, data)


@router.delete("/{modelo_id}", response_model=ModeloPublic)
def remove_modelo(
    modelo_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /modelos/%s", modelo_id)
    return modelo_service.delete_modelo(db, modelo_id)