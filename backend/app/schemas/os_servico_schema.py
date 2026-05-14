from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class OsServicoCreate(BaseModel):
    id_servico: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)

class OsServicoUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)

class OsServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_os: int
    id_servico: int
    quantidade: int
    servico_descricao: str
    servico_preco: Decimal
    subtotal: Decimal = Field(default=0.0)
