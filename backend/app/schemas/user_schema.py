from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.roles import ALL_ROLES, CLIENTE

class UserCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = CLIENTE
    ativo: bool = True
    telefone: str | None = Field(None, max_length=20)
    cpf_cnpj: str | None = Field(None, max_length=18)
    data_nascimento: date | None = Field(None)
    foto_perfil: str | None = None

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str) -> str:
        if len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

    @model_validator(mode="after")
    def role_must_be_valid(self):
        if self.role not in ALL_ROLES:
            raise ValueError(f"role deve ser um de: {', '.join(ALL_ROLES)}")
        if len(self.role) > 20:
            raise ValueError("role deve ter no máximo 20 caracteres")
        return self

class UserUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6)
    role: str | None = None
    ativo: bool | None = None
    telefone: str | None = Field(None, max_length=20)
    cpf_cnpj: str | None = Field(None, max_length=18)
    data_nascimento: date | None = None
    foto_perfil: str | None = None

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

    @model_validator(mode="after")
    def role_must_be_valid_when_set(self):
        if self.role is not None:
            if self.role not in ALL_ROLES:
                raise ValueError(f"role deve ser um de: {', '.join(ALL_ROLES)}")
            if len(self.role) > 20:
                raise ValueError("role deve ter no máximo 20 caracteres")
        return self

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nome: str
    email: str
    role: str | None
    ativo: bool | None
    telefone: str
    cpf_cnpj: str
    data_nascimento: date
    foto_perfil: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
