import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import veiculo_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/api/veiculos", tags=["Veiculos"])


@router.get("", response_model=list[VeiculoPublic])
def list_all_veiculos(_=Depends(require_role(_STAFF))):
    return veiculo_service.list_all_veiculos()


@router.get("/user/{usuario_id}", response_model=list[VeiculoPublic])
def list_veiculos_by_user(
    usuario_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    return veiculo_service.list_veiculos_by_user(usuario_id)


@router.post("/user/{usuario_id}", response_model=VeiculoPublic, status_code=201)
def create_veiculo(
    usuario_id: Annotated[int, Path(ge=1)],
    data: VeiculoCreate,
    _=Depends(require_role(_STAFF)),
):
    return veiculo_service.create_veiculo_for_user(usuario_id, data)


@router.get("/{veiculo_id}", response_model=VeiculoPublic)
def get_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    return veiculo_service.get_veiculo_by_id_or_404(veiculo_id)


@router.patch("/{veiculo_id}", response_model=VeiculoPublic)
def update_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    _=Depends(require_role(_STAFF)),
):
    return veiculo_service.update_veiculo(veiculo_id, data)


@router.delete("/{veiculo_id}", response_model=VeiculoPublic)
def delete_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    return veiculo_service.delete_veiculo(veiculo_id)