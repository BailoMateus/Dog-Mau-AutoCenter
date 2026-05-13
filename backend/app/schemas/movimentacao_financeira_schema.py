from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MovimentacaoFinanceiraCreate(BaseModel):
    valor: float = Field(..., gt=0)
    descricao: str = Field(min_length=1, max_length=255)
    id_pagamento: int | None = Field(default=None, ge=1)

class MovimentacaoFinanceiraPeriodo(BaseModel):
    data_inicio: datetime
    data_fim: datetime
    limit: int = Field(default=100, le=500)

class MovimentacaoFinanceiraPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimentacao_financeira: int
    tipo_movimentacao: str
    valor: float
    descricao: str
    id_pagamento: int | None = None
    created_at: datetime

class SaldoPeriodo(BaseModel):
    entradas: float
    saidas: float
    saldo: float

class ResumoFinanceiro(BaseModel):
    mes: str
    tipo_movimentacao: str
    quantidade: int
    valor_total: float
