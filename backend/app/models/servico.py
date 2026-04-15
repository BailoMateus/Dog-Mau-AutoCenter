from sqlalchemy import Column, DateTime, Identity, Integer, Numeric, Text
from sqlalchemy.sql import func

from app.database.database import Base

class Servico(Base):
    __tablename__ = "servico"

    id_servico = Column(
        Integer,
        Identity(start=1, increment=1),
        primary_key=True,
    )

    descricao = Column(Text, nullable=False)
    preco = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)