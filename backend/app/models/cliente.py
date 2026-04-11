from sqlalchemy import Column, DateTime, Identity, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    enderecos = relationship("Endereco", back_populates="cliente")
