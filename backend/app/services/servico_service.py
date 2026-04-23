import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.entities import Servico
from app.repositories import servico_repository as repo
from app.schemas.servico_schema import ServicoCreate, ServicoUpdate

logger = logging.getLogger(__name__)

def list_servicos(db: Session):
    return repo.get_all_servicos(db)

def create_servico(db: Session, data: ServicoCreate):
    servico = Servico(
        descricao=data.descricao,
        preco=data.preco,
    )
    return repo.create_servico(db, servico)

def get_servico_or_404(db: Session, servico_id: int) -> Servico:
    servico = repo.get_servico_by_id(db, servico_id)
    if not servico:
        logger.info("servico não encontrado id=%s", servico_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
    return servico

def update_servico(db: Session, servico_id: int, data: ServicoUpdate):
    servico = get_servico_or_404(db, servico_id)

    if data.descricao is not None:
        servico.descricao = data.descricao
    if data.preco is not None:
        servico.preco = data.preco

    return repo.update_servico(db, servico)

def delete_servico(db: Session, servico_id: int):
    servico = get_servico_or_404(db, servico_id)
    return repo.soft_delete_servico(db, servico)