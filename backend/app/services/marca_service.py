import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.entities import Marca
from app.repositories import marca_repository as repo
from app.schemas.marca_schema import MarcaCreate, MarcaUpdate

logger = logging.getLogger(__name__)

def list_marcas(db: Session):
    return repo.get_all_marcas(db)

def create_marca(db: Session, data: MarcaCreate):
    marca = Marca(
        nome=data.nome,
        pais_origem=data.pais_origem,
        site_oficial=data.site_oficial,
    )
    return repo.create_marca(db, marca)

def get_marca_or_404(db: Session, marca_id: int) -> Marca:
    marca = repo.get_marca_by_id(db, marca_id)
    if not marca:
        logger.info("marca não encontrada id=%s", marca_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca não encontrada")
    return marca

def update_marca(db: Session, marca_id: int, data: MarcaUpdate):
    marca = get_marca_or_404(db, marca_id)

    if data.nome is not None:
        marca.nome = data.nome
    if data.pais_origem is not None:
        marca.pais_origem = data.pais_origem
    if data.site_oficial is not None:
        marca.site_oficial = data.site_oficial

    return repo.update_marca(db, marca)

def delete_marca(db: Session, marca_id: int):
    marca = get_marca_or_404(db, marca_id)
    return repo.soft_delete_marca(db, marca)