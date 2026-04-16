from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class EnderecoCreate(BaseModel):
    logradouro: str = Field(..., min_length=1, max_length=150)
    numero: str | None = Field(None, max_length=10)
    cep: str | None = Field(None, max_length=9)
    complemento: str | None = Field(None, max_length=100)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=2)

class EnderecoUpdate(BaseModel):
    logradouro: str | None = Field(None, min_length=1, max_length=150)
    numero: str | None = Field(None, max_length=10)
    cep: str | None = Field(None, max_length=9)
    complemento: str | None = Field(None, max_length=100)
    bairro: str | None = Field(None, max_length=100)
    cidade: str | None = Field(None, max_length=100)
    estado: str | None = Field(None, max_length=2)

class EnderecoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_endereco: int
    id_cliente: int
    logradouro: str
    numero: str | None
    cep: str | None
    complemento: str | None
    bairro: str | None
    cidade: str | None
    estado: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
