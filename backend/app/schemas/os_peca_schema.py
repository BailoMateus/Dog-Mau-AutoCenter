from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class OsPecaCreate(BaseModel):
    id_peca: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)

class OsPecaUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)

class OsPecaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_os: int
    id_peca: int
    quantidade: int
    peca_nome: str
    peca_preco: Decimal
    peca_estoque: int
    subtotal: Decimal = Field(default=0.0)

class MovimentacaoEstoquePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimentacao: int
    id_peca: int
    id_os: int | None = None
    id_pedido: int | None = None
    tipo_movimentacao: str
    quantidade: int
    estoque_anterior: int
    estoque_posterior: int
    motivo: str
    created_at: str
