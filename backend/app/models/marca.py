from sqlalchemy import Column, DateTime, Identity, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base

class Marca(Base):
    __tablename__ = "marca"

    id_marca = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    nome = Column(String(50), nullable=False)
    pais_origem = Column(String(50), nullable=True)
    site_oficial = Column(String(150), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    modelos = relationship("Modelo", back_populates="marca")