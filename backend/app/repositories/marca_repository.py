import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.marca import Marca

logger = logging.getLogger(__name__)

def get_marca_by_id(db: Session, marca_id: int):
    row = (
        db.query(Marca)
        .filter(Marca.id_marca == marca_id, Marca.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_marca_by_id id=%s found=%s", marca_id, row is not None)
    return row

def get_all_marcas(db: Session):
    rows = db.query(Marca).filter(Marca.deleted_at.is_(None)).all()
    logger.debug("get_all_marcas count=%s", len(rows))
    return rows

def create_marca(db: Session, marca: Marca):
    db.add(marca)
    db.commit()
    db.refresh(marca)
    logger.info("marca criada id=%s", marca.id_marca)
    return marca

def update_marca(db: Session, marca: Marca):
    db.commit()
    db.refresh(marca)
    logger.info("marca atualizada id=%s", marca.id_marca)
    return marca

def soft_delete_marca(db: Session, marca: Marca):
    marca.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(marca)
    logger.info("marca soft-delete id=%s", marca.id_marca)
    return marca