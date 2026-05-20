from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.file_storage import normalize_stored_image_url

class PecaCreate(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da peça")
    preco_unitario: float = Field(..., ge=0, description="Preço unitário da peça")
    quantidade_estoque: int = Field(0, ge=0, description="Quantidade em estoque")

class PecaUpdate(BaseModel):
    nome: str | None = Field(None, max_length=100, description="Nome da peça")
    preco_unitario: float | None = Field(None, ge=0, description="Preço unitário da peça")
    quantidade_estoque: int | None = Field(None, ge=0, description="Quantidade em estoque")

class PecaPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_peca: int
    nome: str
    preco_unitario: float
    quantidade_estoque: int
    imagem_peca: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("imagem_peca", mode="before")
    @classmethod
    def normalize_imagem_peca(cls, v: str | None) -> str | None:
        return normalize_stored_image_url(v)
