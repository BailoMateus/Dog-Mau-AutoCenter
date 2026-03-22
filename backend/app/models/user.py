from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.database.database import Base

class User(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nome = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    senha_hash = Column(String, nullable=False)

    role = Column(String, nullable=False)  # admin, mecanico, cliente

    ativo = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    deleted_at = Column(DateTime, nullable=True)
