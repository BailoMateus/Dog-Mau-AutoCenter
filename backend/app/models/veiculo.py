from sqlalchemy import Column, DateTime, ForeignKey, Identity, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class Veiculo(Base):
    __tablename__ = "veiculo"
    __table_args__ = (UniqueConstraint("placa", name="veiculo_placa_key"),)

    id_veiculo = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    placa = Column(String(10), nullable=False)
    ano_fabricacao = Column(Integer, nullable=True)
    cor = Column(String(30), nullable=True)

    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario", name="fk_veiculo_usuario"),
        nullable=False,
    )
    id_modelo = Column(
        Integer,
        ForeignKey("modelo.id_modelo", name="fk_veiculo_modelo"),
        nullable=False,
    )

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship("User", back_populates="veiculos")
    modelo = relationship("Modelo", back_populates="veiculos")
