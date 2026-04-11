from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    telefone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

class ClienteUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    telefone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

class ClientePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    nome: str
    telefone: str | None
    email: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
