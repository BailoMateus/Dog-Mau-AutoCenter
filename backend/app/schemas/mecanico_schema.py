from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MecanicoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    especialidade: str | None = Field(None, max_length=100)

class MecanicoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    especialidade: str | None = Field(None, max_length=100)

class MecanicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mecanico: int
    nome: str
    especialidade: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None