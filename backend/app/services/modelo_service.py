import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.entities import Modelo
from app.repositories import modelo_repository as repo
from app.schemas.modelo_schema import ModeloCreate, ModeloUpdate

logger = logging.getLogger(__name__)

def list_modelos(db: Session):
    return repo.get_all_modelos(db)

def list_modelos_by_marca(db: Session, marca_id: int):
    return repo.get_modelos_by_marca(db, marca_id)

def create_modelo(db: Session, data: ModeloCreate):
    modelo = Modelo(
        id_marca=data.id_marca,
        nome_modelo=data.nome_modelo,
        ano_lancamento=data.ano_lancamento,
        tipo_combustivel=data.tipo_combustivel,
        categoria=data.categoria,
        num_portas=data.num_portas,
    )
    return repo.create_modelo(db, modelo)

def get_modelo_or_404(db: Session, modelo_id: int) -> Modelo:
    modelo = repo.get_modelo_by_id(db, modelo_id)
    if not modelo:
        logger.info("modelo não encontrado id=%s", modelo_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado")
    return modelo

def update_modelo(db: Session, modelo_id: int, data: ModeloUpdate):
    modelo = get_modelo_or_404(db, modelo_id)

    if data.nome_modelo is not None:
        modelo.nome_modelo = data.nome_modelo
    if data.ano_lancamento is not None:
        modelo.ano_lancamento = data.ano_lancamento
    if data.tipo_combustivel is not None:
        modelo.tipo_combustivel = data.tipo_combustivel
    if data.categoria is not None:
        modelo.categoria = data.categoria
    if data.num_portas is not None:
        modelo.num_portas = data.num_portas

    return repo.update_modelo(db, modelo)

def delete_modelo(db: Session, modelo_id: int):
    modelo = get_modelo_or_404(db, modelo_id)
    return repo.soft_delete_modelo(db, modelo)