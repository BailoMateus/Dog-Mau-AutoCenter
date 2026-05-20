from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class ServicoCreate(BaseModel):
    nome_servico: str = Field(..., min_length=1, max_length=150)
    descricao: str = Field(..., min_length=1)
    tempo_estimado: str | None = Field(None, max_length=50)
    preco: Decimal = Field(..., gt=0)

class ServicoUpdate(BaseModel):
    nome_servico: str | None = Field(None, min_length=1, max_length=150)
    descricao: str | None = Field(None, min_length=1)
    tempo_estimado: str | None = Field(None, max_length=50)
    preco: Decimal | None = Field(None, gt=0)

class ServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servico: int
    nome_servico: str
    descricao: str
    tempo_estimado: str | None = None
    preco: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None