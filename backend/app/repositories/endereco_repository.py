import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.endereco import Endereco

logger = logging.getLogger(__name__)

def get_endereco_by_id_for_cliente(db: Session, cliente_id: int, endereco_id: int):
    row = (
        db.query(Endereco)
        .filter(
            Endereco.id_endereco == endereco_id,
            Endereco.id_cliente == cliente_id,
            Endereco.deleted_at.is_(None),
        )
        .first()
    )
    logger.debug(
        "get_endereco_by_id_for_cliente cliente=%s endereco=%s found=%s",
        cliente_id,
        endereco_id,
        row is not None,
    )
    return row

def create_endereco(db: Session, endereco: Endereco):
    db.add(endereco)
    db.commit()
    db.refresh(endereco)
    logger.info("endereco criado id=%s cliente=%s", endereco.id_endereco, endereco.id_cliente)
    return endereco

def list_enderecos_by_cliente(db: Session, cliente_id: int):
    rows = (
        db.query(Endereco)
        .filter(Endereco.id_cliente == cliente_id, Endereco.deleted_at.is_(None))
        .all()
    )
    logger.debug("list_enderecos_by_cliente cliente=%s count=%s", cliente_id, len(rows))
    return rows

def update_endereco(db: Session, endereco: Endereco):
    db.commit()
    db.refresh(endereco)
    logger.info("endereco atualizado id=%s", endereco.id_endereco)
    return endereco

def soft_delete_endereco(db: Session, endereco: Endereco):
    endereco.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(endereco)
    logger.info("endereco soft-delete id=%s", endereco.id_endereco)
    return endereco
