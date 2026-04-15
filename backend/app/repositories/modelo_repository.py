import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.modelo import Modelo

logger = logging.getLogger(__name__)

def get_modelo_by_id(db: Session, modelo_id: int):
    row = (
        db.query(Modelo)
        .filter(Modelo.id_modelo == modelo_id, Modelo.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_modelo_by_id id=%s found=%s", modelo_id, row is not None)
    return row

def get_modelos_by_marca(db: Session, marca_id: int):
    rows = (
        db.query(Modelo)
        .filter(Modelo.id_marca == marca_id, Modelo.deleted_at.is_(None))
        .all()
    )
    logger.debug("get_modelos_by_marca marca_id=%s count=%s", marca_id, len(rows))
    return rows

def get_all_modelos(db: Session):
    rows = db.query(Modelo).filter(Modelo.deleted_at.is_(None)).all()
    logger.debug("get_all_modelos count=%s", len(rows))
    return rows

def create_modelo(db: Session, modelo: Modelo):
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    logger.info("modelo criado id=%s", modelo.id_modelo)
    return modelo

def update_modelo(db: Session, modelo: Modelo):
    db.commit()
    db.refresh(modelo)
    logger.info("modelo atualizado id=%s", modelo.id_modelo)
    return modelo

def soft_delete_modelo(db: Session, modelo: Modelo):
    modelo.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(modelo)
    logger.info("modelo soft-delete id=%s", modelo.id_modelo)
    return modelo