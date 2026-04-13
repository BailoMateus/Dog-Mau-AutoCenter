import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.servico import Servico

logger = logging.getLogger(__name__)

def get_servico_by_id(db: Session, servico_id: int):
    row = (
        db.query(Servico)
        .filter(Servico.id_servico == servico_id, Servico.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_servico_by_id id=%s found=%s", servico_id, row is not None)
    return row

def get_all_servicos(db: Session):
    rows = db.query(Servico).filter(Servico.deleted_at.is_(None)).all()
    logger.debug("get_all_servicos count=%s", len(rows))
    return rows

def create_servico(db: Session, servico: Servico):
    db.add(servico)
    db.commit()
    db.refresh(servico)
    logger.info("servico criado id=%s", servico.id_servico)
    return servico

def update_servico(db: Session, servico: Servico):
    db.commit()
    db.refresh(servico)
    logger.info("servico atualizado id=%s", servico.id_servico)
    return servico

def soft_delete_servico(db: Session, servico: Servico):
    servico.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(servico)
    logger.info("servico soft-delete id=%s", servico.id_servico)
    return servico