from sqlalchemy import Boolean, Column, DateTime, Identity, Integer, String, text
from sqlalchemy.sql import func

from app.database.database import Base
class User(Base):
    __tablename__ = "usuario"

    id_usuario = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    senha_hash = Column(String(255), nullable=False)

    # coluna reservada: nome físico "role"
    role = Column("role", String(20), nullable=True, server_default=text("'mecanico'"))

    ativo = Column(Boolean, nullable=True, server_default=text("true"))

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
