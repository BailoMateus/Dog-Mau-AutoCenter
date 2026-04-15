import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.mecanico_schema import MecanicoCreate, MecanicoPublic, MecanicoUpdate
from app.services import mecanico_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/mecanicos", tags=["Mecanicos"])

@router.get("", response_model=list[MecanicoPublic])
def list_mecanicos(
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /mecanicos")
    return mecanico_service.list_mecanicos(db)


@router.post("", response_model=MecanicoPublic, status_code=201)
def create_mecanico(
    data: MecanicoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /mecanicos nome=%s", data.nome)
    return mecanico_service.create_mecanico(db, data)


@router.get("/{mecanico_id}", response_model=MecanicoPublic)
def get_mecanico(
    mecanico_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /mecanicos/%s", mecanico_id)
    return mecanico_service.get_mecanico_or_404(db, mecanico_id)


@router.patch("/{mecanico_id}", response_model=MecanicoPublic)
def patch_mecanico(
    mecanico_id: Annotated[int, Path(ge=1)],
    data: MecanicoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /mecanicos/%s", mecanico_id)
    return mecanico_service.update_mecanico(db, mecanico_id, data)


@router.delete("/{mecanico_id}", response_model=MecanicoPublic)
def remove_mecanico(
    mecanico_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /mecanicos/%s", mecanico_id)
    return mecanico_service.delete_mecanico(db, mecanico_id)