import logging

from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    logger.debug("get_user_by_email email=%s found=%s", email, user is not None)
    return user

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id_usuario == user_id).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).filter(User.deleted_at == None).all()

def update_user(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User):
    user.deleted_at = None  # depois você troca por datetime.utcnow()
    db.commit()
    return user