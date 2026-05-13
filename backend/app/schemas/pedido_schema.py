from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class PedidoCreate(BaseModel):
    id_cliente: int = Field(..., gt=0)
    valor_total: Decimal = Field(..., ge=0)
    status: str = Field("processando", max_length=30)

class PedidoUpdate(BaseModel):
    id_cliente: int | None = Field(None, gt=0)
    valor_total: Decimal | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=30)

class PedidoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    id_cliente: int
    valor_total: Decimal
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
