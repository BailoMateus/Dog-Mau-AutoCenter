from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PedidoPecaCreate(BaseModel):
    id_peca: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)


class PedidoPecaUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)


class PedidoPecaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    id_peca: int
    quantidade: int
    peca_nome: str
    peca_preco: Decimal
    subtotal: Decimal = Field(default=0.0)
    created_at: str | None = None
    updated_at: str | None = None

    def model_post_init(self, __context):
        """Calcula subtotal após inicialização."""
        self.subtotal = self.peca_preco * self.quantidade
