import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.repositories import cliente_repository as repo
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate

logger = logging.getLogger(__name__)

def list_clientes(db: Session):
    return repo.get_all_clientes(db)

def create_cliente(db: Session, data: ClienteCreate):
    cliente = Cliente(
        nome=data.nome,
        telefone=data.telefone,
        email=data.email,
    )
    return repo.create_cliente(db, cliente)

def get_cliente_or_404(db: Session, cliente_id: int) -> Cliente:
    cliente = repo.get_cliente_by_id(db, cliente_id)
    if not cliente:
        logger.info("cliente não encontrado id=%s", cliente_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente

def update_cliente(db: Session, cliente_id: int, data: ClienteUpdate):
    cliente = get_cliente_or_404(db, cliente_id)
    if data.nome is not None:
        cliente.nome = data.nome
    if data.telefone is not None:
        cliente.telefone = data.telefone
    if data.email is not None:
        cliente.email = data.email
    return repo.update_cliente(db, cliente)

def delete_cliente(db: Session, cliente_id: int):
    cliente = get_cliente_or_404(db, cliente_id)
    return repo.soft_delete_cliente(db, cliente)
