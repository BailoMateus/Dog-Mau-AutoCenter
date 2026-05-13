from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class OrcamentoCreate(BaseModel):
    id_cliente: int = Field(..., gt=0)
    id_veiculo: int = Field(..., gt=0)
    status: str = Field("pendente", max_length=30)
    valor_total: Decimal = Field(0, ge=0)

class OrcamentoUpdate(BaseModel):
    id_cliente: int | None = Field(None, gt=0)
    id_veiculo: int | None = Field(None, gt=0)
    status: str | None = Field(None, max_length=30)
    valor_total: Decimal | None = Field(None, ge=0)

class OrcamentoUpdateStatus(BaseModel):
    status: str = Field(..., max_length=30)

class OrcamentoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_orcamento: int
    id_cliente: int
    id_veiculo: int
    status: str
    valor_total: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None
