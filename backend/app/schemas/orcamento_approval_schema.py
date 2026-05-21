from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class OrdemServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_os: int
    id_orcamento: int
    id_veiculo: int
    status: str
    valor_total: Decimal
    data_abertura: datetime | None = None
    data_conclusao: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
