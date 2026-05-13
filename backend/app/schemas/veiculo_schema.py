from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

class VeiculoCreate(BaseModel):
    placa: str = Field(..., min_length=1, max_length=10)
    ano_fabricacao: int | None = Field(None, ge=1886, le=2100)
    cor: str | None = Field(None, max_length=30)
    id_modelo: int = Field(..., ge=1)

    @field_validator("placa")
    @classmethod
    def placa_strip(cls, v: str) -> str:
        return v.strip()

class VeiculoUpdate(BaseModel):
    placa: str | None = Field(None, min_length=1, max_length=10)
    ano_fabricacao: int | None = Field(None, ge=1886, le=2100)
    cor: str | None = Field(None, max_length=30)
    id_modelo: int | None = Field(None, ge=1)

    @field_validator("placa")
    @classmethod
    def placa_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip()

class VeiculoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_veiculo: int
    placa: str
    ano_fabricacao: int | None
    cor: str | None
    id_usuario: int
    id_modelo: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
