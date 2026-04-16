from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MarcaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50)
    pais_origem: str | None = Field(None, max_length=50)
    site_oficial: str | None = Field(None, max_length=150)

class MarcaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=50)
    pais_origem: str | None = Field(None, max_length=50)
    site_oficial: str | None = Field(None, max_length=150)

class MarcaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_marca: int
    nome: str
    pais_origem: str | None
    site_oficial: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None