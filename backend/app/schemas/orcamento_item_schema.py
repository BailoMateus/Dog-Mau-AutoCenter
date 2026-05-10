from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class OrcamentoPecaCreate(BaseModel):
    id_peca: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)

class OrcamentoPecaUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)

class OrcamentoPecaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_orcamento: int
    id_peca: int
    quantidade: int
    peca_nome: str
    peca_preco: Decimal
    subtotal: Decimal = Field(default=0.0)

    def model_post_init(self, __context):
        """Calcula subtotal após inicialização."""
        self.subtotal = self.peca_preco * self.quantidade

class OrcamentoServicoCreate(BaseModel):
    id_servico: int = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)

class OrcamentoServicoUpdate(BaseModel):
    quantidade: int = Field(..., gt=0)

class OrcamentoServicoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_orcamento: int
    id_servico: int
    quantidade: int
    servico_descricao: str
    servico_preco: Decimal
    subtotal: Decimal = Field(default=0.0)

    def model_post_init(self, __context):
        """Calcula subtotal após inicialização."""
        self.subtotal = self.servico_preco * self.quantidade
