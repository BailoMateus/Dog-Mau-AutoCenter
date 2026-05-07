import logging

from fastapi import HTTPException, status
from app.models.entities import Servico
from app.repositories import servico_repository as repo
from app.schemas.servico_schema import ServicoCreate, ServicoUpdate

logger = logging.getLogger(__name__)

def list_servicos():
    return repo.get_all_servicos()

def create_servico(data: ServicoCreate):
    servico = Servico(
        descricao=data.descricao,
        preco=data.preco,
    )
    return repo.create_servico(servico)

def get_servico_or_404(servico_id: int) -> Servico:
    servico = repo.get_servico_by_id(servico_id)
    if not servico:
        logger.info("servico não encontrado id=%s", servico_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
    return servico

def update_servico(servico_id: int, data: ServicoUpdate):
    servico = get_servico_or_404(servico_id)

    if data.descricao is not None:
        servico.descricao = data.descricao
    if data.preco is not None:
        servico.preco = data.preco

    return repo.update_servico(servico)

def delete_servico(servico_id: int):
    servico = get_servico_or_404(servico_id)
    return repo.soft_delete_servico(servico)