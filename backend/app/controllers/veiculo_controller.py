import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.database.database import get_db
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import veiculo_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/clientes/{cliente_id}/veiculos", tags=["Veiculos"])


@router.get("", response_model=list[VeiculoPublic])
def list_veiculos(
    cliente_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/veiculos", cliente_id)
    return veiculo_service.list_veiculos(db, cliente_id)


@router.post("", response_model=VeiculoPublic, status_code=201)
def create_veiculo(
    cliente_id: Annotated[int, Path(ge=1)],
    data: VeiculoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /clientes/%s/veiculos placa=%s", cliente_id, data.placa)
    return veiculo_service.create_veiculo(db, cliente_id, data)


@router.get("/{veiculo_id}", response_model=VeiculoPublic)
def get_veiculo(
    cliente_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /clientes/%s/veiculos/%s", cliente_id, veiculo_id)
    return veiculo_service.get_veiculo_or_404(db, cliente_id, veiculo_id)


@router.patch("/{veiculo_id}", response_model=VeiculoPublic)
def patch_veiculo(
    cliente_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /clientes/%s/veiculos/%s", cliente_id, veiculo_id)
    return veiculo_service.update_veiculo(db, cliente_id, veiculo_id, data)


@router.delete("/{veiculo_id}", response_model=VeiculoPublic)
def remove_veiculo(
    cliente_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /clientes/%s/veiculos/%s", cliente_id, veiculo_id)
    return veiculo_service.delete_veiculo(db, cliente_id, veiculo_id)