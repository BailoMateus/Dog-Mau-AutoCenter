import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.endereco import Endereco
from app.repositories import endereco_repository as repo
from app.schemas.endereco_schema import EnderecoCreate, EnderecoUpdate
from app.services import cliente_service

logger = logging.getLogger(__name__)

def add_endereco(db: Session, cliente_id: int, data: EnderecoCreate):
    cliente_service.get_cliente_or_404(db, cliente_id)
    endereco = Endereco(
        id_cliente=cliente_id,
        logradouro=data.logradouro,
        numero=data.numero,
        cep=data.cep,
        complemento=data.complemento,
        bairro=data.bairro,
        cidade=data.cidade,
        estado=data.estado,
    )
    return repo.create_endereco(db, endereco)

def list_enderecos(db: Session, cliente_id: int):
    cliente_service.get_cliente_or_404(db, cliente_id)
    return repo.list_enderecos_by_cliente(db, cliente_id)

def get_endereco_or_404(db: Session, cliente_id: int, endereco_id: int) -> Endereco:
    cliente_service.get_cliente_or_404(db, cliente_id)
    endereco = repo.get_endereco_by_id_for_cliente(db, cliente_id, endereco_id)
    if not endereco:
        logger.info(
            "endereço não encontrado cliente=%s endereco=%s",
            cliente_id,
            endereco_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endereço não encontrado")
    return endereco

def update_endereco(db: Session, cliente_id: int, endereco_id: int, data: EnderecoUpdate):
    endereco = get_endereco_or_404(db, cliente_id, endereco_id)
    if data.logradouro is not None:
        endereco.logradouro = data.logradouro
    if data.numero is not None:
        endereco.numero = data.numero
    if data.cep is not None:
        endereco.cep = data.cep
    if data.complemento is not None:
        endereco.complemento = data.complemento
    if data.bairro is not None:
        endereco.bairro = data.bairro
    if data.cidade is not None:
        endereco.cidade = data.cidade
    if data.estado is not None:
        endereco.estado = data.estado
    return repo.update_endereco(db, endereco)

def delete_endereco(db: Session, cliente_id: int, endereco_id: int):
    endereco = get_endereco_or_404(db, cliente_id, endereco_id)
    return repo.soft_delete_endereco(db, endereco)
