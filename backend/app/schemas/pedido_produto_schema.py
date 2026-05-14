from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class PedidoProdutoCreate(BaseModel):
    id_produto: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)

class PedidoProdutoUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)

class PedidoProdutoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: int
    id_produto: int
    quantidade: int
    produto_nome: str
    produto_preco: Decimal
    subtotal: Decimal = Field(default=0.0)
    created_at: str | None = None
    updated_at: str | None = None

    def model_post_init(self, __context):
        """Calcula subtotal após inicialização."""
        self.subtotal = self.produto_preco * self.quantidade
