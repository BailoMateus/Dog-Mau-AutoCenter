from sqlalchemy import Column, DateTime, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class Endereco(Base):
    __tablename__ = "endereco"

    id_endereco = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario", name="fk_endereco_usuario"),
        nullable=False,
    )

    logradouro = Column(String(150), nullable=False)
    numero = Column(String(10), nullable=True)
    cep = Column(String(9), nullable=True)
    complemento = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship("User", back_populates="enderecos")
