from pydantic import BaseModel, Field

class PecaCreateSchema(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da peça")
    preco_unitario: float = Field(..., ge=0, description="Preço unitário da peça")
    quantidade_estoque: int = Field(0, ge=0, description="Quantidade em estoque")

class PecaUpdateSchema(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da peça")
    preco_unitario: float = Field(..., ge=0, description="Preço unitário da peça")
    quantidade_estoque: int = Field(..., ge=0, description="Quantidade em estoque")

class PecaResponseSchema(BaseModel):
    id_peca: int
    nome: str
    preco_unitario: float
    quantidade_estoque: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True