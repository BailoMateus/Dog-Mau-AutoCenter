from sqlalchemy import Column, DateTime, Identity, Integer, String
from sqlalchemy.sql import func

from app.database.database import Base

class Mecanico(Base):
    __tablename__ = "mecanico"

    id_mecanico = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    nome = Column(String(100), nullable=False)
    especialidade = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)