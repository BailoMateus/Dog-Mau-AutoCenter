import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import veiculo_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/api/usuarios/{usuario_id}/veiculos", tags=["Veiculos"])


@router.get("", response_model=list[VeiculoPublic])
def list_veiculos(
    usuario_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /api/usuarios/%s/veiculos", usuario_id)
    return veiculo_service.list_veiculos_by_user(usuario_id)


@router.post("", response_model=VeiculoPublic, status_code=201)
def create_veiculo(
    usuario_id: Annotated[int, Path(ge=1)],
    data: VeiculoCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /api/usuarios/%s/veiculos", usuario_id)
    return veiculo_service.create_veiculo_for_user(usuario_id, data)


@router.get("/{veiculo_id}", response_model=VeiculoPublic)
def get_veiculo(
    usuario_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /api/usuarios/%s/veiculos/%s", usuario_id, veiculo_id)
    return veiculo_service.get_veiculo_by_user_or_404(usuario_id, veiculo_id)


@router.patch("/{veiculo_id}", response_model=VeiculoPublic)
def update_veiculo(
    usuario_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /api/usuarios/%s/veiculos/%s", usuario_id, veiculo_id)
    return veiculo_service.update_veiculo_by_user(usuario_id, veiculo_id, data)


@router.delete("/{veiculo_id}", response_model=VeiculoPublic)
def delete_veiculo(
    usuario_id: Annotated[int, Path(ge=1)],
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /api/usuarios/%s/veiculos/%s", usuario_id, veiculo_id)
    return veiculo_service.delete_veiculo_by_user(usuario_id, veiculo_id)
