from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150)
    descricao: str | None = Field(None, max_length=1000)
    preco: Decimal = Field(..., ge=0)
    quantidade_estoque: int = Field(0, ge=0)

class ProdutoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=150)
    descricao: str | None = Field(None, max_length=1000)
    preco: Decimal | None = Field(None, ge=0)
    quantidade_estoque: int | None = Field(None, ge=0)

class ProdutoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto: int
    nome: str
    descricao: str | None = None
    preco: Decimal
    quantidade_estoque: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
