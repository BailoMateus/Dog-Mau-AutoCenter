import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo

logger = logging.getLogger(__name__)

def get_veiculo_by_id_for_user(db: Session, user_id: int, veiculo_id: int):
    row = (
        db.query(Veiculo)
        .filter(
            Veiculo.id_veiculo == veiculo_id,
            Veiculo.id_usuario == user_id,
            Veiculo.deleted_at.is_(None),
        )
        .first()
    )
    logger.debug(
        "get_veiculo_by_id_for_user user=%s veiculo=%s found=%s",
        user_id,
        veiculo_id,
        row is not None,
    )
    return row

def create_veiculo(db: Session, veiculo: Veiculo):
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    logger.info("veiculo criado id=%s user=%s", veiculo.id_veiculo, veiculo.id_usuario)
    return veiculo

def list_veiculos_by_user(db: Session, user_id: int):
    rows = (
        db.query(Veiculo)
        .filter(Veiculo.id_usuario == user_id, Veiculo.deleted_at.is_(None))
        .all()
    )
    logger.debug("list_veiculos_by_user user=%s count=%s", user_id, len(rows))
    return rows

def update_veiculo(db: Session, veiculo: Veiculo):
    db.commit()
    db.refresh(veiculo)
    logger.info("veiculo atualizado id=%s", veiculo.id_veiculo)
    return veiculo

def soft_delete_veiculo(db: Session, veiculo: Veiculo):
    veiculo.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(veiculo)
    logger.info("veiculo soft-delete id=%s", veiculo.id_veiculo)
    return veiculo
