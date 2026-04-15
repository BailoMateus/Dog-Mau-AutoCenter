import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.cliente import Cliente

logger = logging.getLogger(__name__)

def get_cliente_by_id(db: Session, cliente_id: int):
    row = (
        db.query(Cliente)
        .filter(Cliente.id_cliente == cliente_id, Cliente.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_cliente_by_id id=%s found=%s", cliente_id, row is not None)
    return row

def create_cliente(db: Session, cliente: Cliente):
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    logger.info("cliente criado id=%s", cliente.id_cliente)
    return cliente

def get_all_clientes(db: Session):
    rows = db.query(Cliente).filter(Cliente.deleted_at.is_(None)).all()
    logger.debug("get_all_clientes count=%s", len(rows))
    return rows

def update_cliente(db: Session, cliente: Cliente):
    db.commit()
    db.refresh(cliente)
    logger.info("cliente atualizado id=%s", cliente.id_cliente)
    return cliente

def soft_delete_cliente(db: Session, cliente: Cliente):
    cliente.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cliente)
    logger.info("cliente soft-delete id=%s", cliente.id_cliente)
    return cliente

def get_cliente_by_email(db: Session, email: str):
    row = (
        db.query(Cliente)
        .filter(Cliente.email == email, Cliente.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_cliente_by_email email=%s found=%s", email, row is not None)
    return row