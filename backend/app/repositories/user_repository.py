import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str):
    user = (
        db.query(User)
        .filter(User.email == email, User.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_user_by_email email=%s found=%s", email, user is not None)
    return user

def get_user_by_id(db: Session, user_id: int):
    user = (
        db.query(User)
        .filter(User.id_usuario == user_id, User.deleted_at.is_(None))
        .first()
    )
    logger.debug("get_user_by_id id=%s found=%s", user_id, user is not None)
    return user

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("usuário criado id=%s email=%s", user.id_usuario, user.email)
    return user

def get_all_users(db: Session):
    rows = db.query(User).filter(User.deleted_at.is_(None)).all()
    logger.debug("get_all_users count=%s", len(rows))
    return rows

def update_user(db: Session, user: User):
    db.commit()
    db.refresh(user)
    logger.info("usuário atualizado id=%s", user.id_usuario)
    return user

def soft_delete_user(db: Session, user: User):
    user.deleted_at = datetime.now(timezone.utc)
    user.ativo = False
    db.commit()
    db.refresh(user)
    logger.info("usuário soft-delete id=%s", user.id_usuario)
    return user
