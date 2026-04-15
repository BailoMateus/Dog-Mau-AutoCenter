from sqlalchemy import Column, DateTime, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class Modelo(Base):
    __tablename__ = "modelo"

    id_modelo = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    id_marca = Column(Integer, ForeignKey("marca.id_marca"), nullable=False)

    nome_modelo = Column(String(50), nullable=False)
    ano_lancamento = Column(Integer, nullable=True)
    tipo_combustivel = Column(String(30), nullable=True)
    categoria = Column(String(30), nullable=True)
    num_portas = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    marca = relationship("Marca", back_populates="modelos")