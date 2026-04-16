import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.mecanico import Mecanico

logger = logging.getLogger(__name__)

def get_mecanico_by_id(db: Session, mecanico_id: int):
    row = (
        db.query(Mecanico)
        .filter(Mecanico.id_mecanico == mecanico_id, Mecanico.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_mecanico_by_id id=%s found=%s", mecanico_id, row is not None)
    return row

def get_all_mecanicos(db: Session):
    rows = db.query(Mecanico).filter(Mecanico.deleted_at.is_(None)).all()
    logger.debug("get_all_mecanicos count=%s", len(rows))
    return rows

def create_mecanico(db: Session, mecanico: Mecanico):
    db.add(mecanico)
    db.commit()
    db.refresh(mecanico)
    logger.info("mecanico criado id=%s", mecanico.id_mecanico)
    return mecanico

def update_mecanico(db: Session, mecanico: Mecanico):
    db.commit()
    db.refresh(mecanico)
    logger.info("mecanico atualizado id=%s", mecanico.id_mecanico)
    return mecanico

def soft_delete_mecanico(db: Session, mecanico: Mecanico):
    mecanico.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mecanico)
    logger.info("mecanico soft-delete id=%s", mecanico.id_mecanico)
    return mecanico