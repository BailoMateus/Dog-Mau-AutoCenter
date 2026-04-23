import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.core.roles import ADMIN, MECANICO
from app.core.security import require_role
from app.schemas.servico_schema import ServicoCreate, ServicoPublic, ServicoUpdate
from app.services import servico_service

logger = logging.getLogger(__name__)

_STAFF = [ADMIN, MECANICO]

router = APIRouter(prefix="/servicos", tags=["Servicos"])

@router.get("", response_model=list[ServicoPublic])
def list_servicos(
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /servicos")
    return servico_service.list_servicos()


@router.post("", response_model=ServicoPublic, status_code=201)
def create_servico(
    data: ServicoCreate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("POST /servicos")
    return servico_service.create_servico(data)


@router.get("/{servico_id}", response_model=ServicoPublic)
def get_servico(
    servico_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("GET /servicos/%s", servico_id)
    return servico_service.get_servico_or_404(servico_id)


@router.patch("/{servico_id}", response_model=ServicoPublic)
def patch_servico(
    servico_id: Annotated[int, Path(ge=1)],
    data: ServicoUpdate,
    _=Depends(require_role(_STAFF)),
):
    logger.info("PATCH /servicos/%s", servico_id)
    return servico_service.update_servico(servico_id, data)


@router.delete("/{servico_id}", response_model=ServicoPublic)
def remove_servico(
    servico_id: Annotated[int, Path(ge=1)],
    _=Depends(require_role(_STAFF)),
):
    logger.info("DELETE /servicos/%s", servico_id)
    return servico_service.delete_servico(servico_id)