import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.mecanico import Mecanico
from app.repositories import mecanico_repository as repo
from app.schemas.mecanico_schema import MecanicoCreate, MecanicoUpdate

logger = logging.getLogger(__name__)

def list_mecanicos(db: Session):
    return repo.get_all_mecanicos(db)

def create_mecanico(db: Session, data: MecanicoCreate):
    mecanico = Mecanico(
        nome=data.nome,
        especialidade=data.especialidade,
    )
    return repo.create_mecanico(db, mecanico)

def get_mecanico_or_404(db: Session, mecanico_id: int) -> Mecanico:
    mecanico = repo.get_mecanico_by_id(db, mecanico_id)
    if not mecanico:
        logger.info("mecanico não encontrado id=%s", mecanico_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mecânico não encontrado")
    return mecanico

def update_mecanico(db: Session, mecanico_id: int, data: MecanicoUpdate):
    mecanico = get_mecanico_or_404(db, mecanico_id)

    if data.nome is not None:
        mecanico.nome = data.nome
    if data.especialidade is not None:
        mecanico.especialidade = data.especialidade

    return repo.update_mecanico(db, mecanico)

def delete_mecanico(db: Session, mecanico_id: int):
    mecanico = get_mecanico_or_404(db, mecanico_id)
    return repo.soft_delete_mecanico(db, mecanico)