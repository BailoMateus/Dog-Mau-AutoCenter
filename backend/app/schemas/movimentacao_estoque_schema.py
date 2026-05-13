from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MovimentacaoEstoqueCreate(BaseModel):
    id_peca: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)
    motivo: str = Field(max_length=255)

class MovimentacaoEstoquePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimentacao: int
    id_peca: int
    tipo_movimentacao: str
    quantidade: int
    motivo: str
    created_at: datetime
