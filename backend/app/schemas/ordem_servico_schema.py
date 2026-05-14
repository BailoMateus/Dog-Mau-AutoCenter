from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class OrdemServicoCreate(BaseModel):
    id_veiculo: int = Field(..., gt=0)
    id_mecanico: int = Field(..., gt=0)
    descricao_problema: str = Field(..., min_length=1, max_length=1000)

class OrdemServicoUpdate(BaseModel):
    id_veiculo: int | None = Field(None, gt=0)
    id_mecanico: int | None = Field(None, gt=0)
    descricao_problema: str | None = Field(None, min_length=1, max_length=1000)

class OrdemServicoStatusUpdate(BaseModel):
    status: str = Field(..., max_length=30)

class OrdemServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_os: int
    id_veiculo: int
    id_mecanico: int
    descricao_problema: str
    status: str
    data_abertura: datetime | None = None
    data_conclusao: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
