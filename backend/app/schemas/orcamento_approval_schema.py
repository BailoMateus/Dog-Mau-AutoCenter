from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class OrdemServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_ordem_servico: int
    id_orcamento: int
    id_veiculo: int
    status: str
    valor_total: Decimal
    data_inicio: datetime | None = None
    data_conclusao: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
