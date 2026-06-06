from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MovimentacaoEstoqueCreate(BaseModel):
    id_peca: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)
    motivo: str = Field(max_length=255)


class MovimentacaoEstoqueFiltro(BaseModel):
    data_inicio: date | None = None
    data_fim: date | None = None
    tipo_movimentacao: str | None = None
    id_peca: int | None = Field(default=None, ge=1)
    id_produto: int | None = Field(default=None, ge=1)
    limit: int = Field(default=500, le=1000)


class MovimentacaoEstoquePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimentacao: int
    id_peca: int | None = None
    id_produto: int | None = None
    id_os: int | None = None
    tipo_movimentacao: str
    quantidade: int
    motivo: str
    created_at: datetime
