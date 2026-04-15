from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class ServicoCreate(BaseModel):
    descricao: str = Field(..., min_length=1)
    preco: Decimal = Field(..., gt=0)

class ServicoUpdate(BaseModel):
    descricao: str | None = Field(None, min_length=1)
    preco: Decimal | None = Field(None, gt=0)

class ServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_servico: int
    descricao: str
    preco: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None