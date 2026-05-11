import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

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
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /veiculos")
    return veiculo_service.list_veiculos()


@router.post("", response_model=VeiculoPublic, status_code=201)
def create_veiculo(
    data: VeiculoCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /veiculos")
    return veiculo_service.create_veiculo(data)


@router.get("/{veiculo_id}", response_model=VeiculoPublic)
def get_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /veiculos/%s", veiculo_id)
    return veiculo_service.get_veiculo_or_404(veiculo_id)


@router.patch("/{veiculo_id}", response_model=VeiculoPublic)
def update_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /veiculos/%s", veiculo_id)
    return veiculo_service.update_veiculo(veiculo_id, data)


@router.delete("/{veiculo_id}", response_model=VeiculoPublic)
def delete_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /veiculos/%s", veiculo_id)
    return veiculo_service.delete_veiculo(veiculo_id)