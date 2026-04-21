import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.endereco import Endereco
from app.repositories import endereco_repository as repo
from app.schemas.endereco_schema import EnderecoCreate, EnderecoUpdate
from app.services import user_service

logger = logging.getLogger(__name__)

def add_endereco_to_user(db: Session, user_id: int, data: EnderecoCreate):
    user_service.get_user_or_404(db, user_id)
    endereco = Endereco(
        id_usuario=user_id,
        logradouro=data.logradouro,
        numero=data.numero,
        cep=data.cep,
        complemento=data.complemento,
    )
    return repo.create_endereco(db, endereco)

def list_enderecos_by_user(db: Session, user_id: int):
    user_service.get_user_or_404(db, user_id)
    return repo.list_enderecos_by_user(db, user_id)

def get_endereco_or_404(db: Session, user_id: int, endereco_id: int) -> Endereco:
    user_service.get_user_or_404(db, user_id)
    endereco = repo.get_endereco_by_id_for_user(db, user_id, endereco_id)
    if not endereco:
        logger.info(
            "endereço não encontrado user=%s endereco=%s",
            user_id,
            endereco_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endereço não encontrado")
    return endereco

def update_endereco_by_user(db: Session, user_id: int, endereco_id: int, data: EnderecoUpdate):
    endereco = get_endereco_or_404(db, user_id, endereco_id)
    if data.logradouro is not None:
        endereco.logradouro = data.logradouro
    if data.numero is not None:
        endereco.numero = data.numero
    if data.cep is not None:
        endereco.cep = data.cep
    if data.complemento is not None:
        endereco.complemento = data.complemento
    return repo.update_endereco(db, endereco)

def delete_endereco_by_user(db: Session, user_id: int, endereco_id: int):
    endereco = get_endereco_or_404(db, user_id, endereco_id)
    return repo.soft_delete_endereco(db, endereco)
