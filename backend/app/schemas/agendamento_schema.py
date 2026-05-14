from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class AgendamentoCreate(BaseModel):
    id_usuario: int = Field(..., gt=0)
    id_veiculo: int = Field(..., gt=0)
    data_agendamento: datetime = Field(...)
    descricao: str | None = Field(None, max_length=500)
    status: str = Field("agendado", max_length=30)

class AgendamentoUpdate(BaseModel):
    id_usuario: int | None = Field(None, gt=0)
    id_veiculo: int | None = Field(None, gt=0)
    data_agendamento: datetime | None = None
    descricao: str | None = Field(None, max_length=500)
    status: str | None = Field(None, max_length=30)

class AgendamentoUpdateData(BaseModel):
    data_agendamento: datetime = Field(...)

class AgendamentoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_agendamento: int
    id_usuario: int
    id_veiculo: int
    data_agendamento: datetime
    descricao: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
