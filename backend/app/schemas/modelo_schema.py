from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class ModeloCreate(BaseModel):
    id_marca: int
    nome_modelo: str = Field(..., min_length=1, max_length=50)
    ano_lancamento: int | None = None
    tipo_combustivel: str | None = Field(None, max_length=30)
    categoria: str | None = Field(None, max_length=30)
    num_portas: int | None = None

class ModeloUpdate(BaseModel):
    nome_modelo: str | None = Field(None, min_length=1, max_length=50)
    ano_lancamento: int | None = None
    tipo_combustivel: str | None = Field(None, max_length=30)
    categoria: str | None = Field(None, max_length=30)
    num_portas: int | None = None

class ModeloPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_modelo: int
    id_marca: int
    nome_modelo: str
    ano_lancamento: int | None
    tipo_combustivel: str | None
    categoria: str | None
    num_portas: int | None
    created_at: datetime | None = None
    updated_at: datetime | None = None