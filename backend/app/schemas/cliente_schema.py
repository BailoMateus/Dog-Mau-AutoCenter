from datetime import date, datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=5, max_length=100, description="Nome completo do cliente")
    telefone: str | None = Field(None, max_length=20, description="Telefone do cliente")
    email: EmailStr | None = Field(None, description="E-mail válido do cliente")
    cpf_cnpj: str | None = Field(None, max_length=18, description="CPF ou CNPJ do cliente")
    data_nascimento: date | None = Field(None, description="Data de nascimento do cliente")

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cpf_cnpj_clean = re.sub(r"\D", "", v)
        if len(cpf_cnpj_clean) == 11:
            if not cls._validate_cpf(cpf_cnpj_clean):
                raise ValueError("CPF inválido")
        elif len(cpf_cnpj_clean) == 14:
            if not cls._validate_cnpj(cpf_cnpj_clean):
                raise ValueError("CNPJ inválido")
        else:
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        return v

    @field_validator("data_nascimento")
    @classmethod
    def validate_data_nascimento(cls, v: date | None) -> date | None:
        if v is None:
            return v
        today = date.today()
        if v > today:
            raise ValueError("Data de nascimento não pode ser no futuro")
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Cliente deve ter pelo menos 18 anos")
        return v

    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[9]):
            return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[10]):
            return False
        return True

    @staticmethod
    def _validate_cnpj(cnpj: str) -> bool:
        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        if digito1 != int(cnpj[12]):
            return False
        soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        if digito2 != int(cnpj[13]):
            return False
        return True

class ClienteUpdate(BaseModel):
    nome: str | None = Field(None, min_length=5, max_length=100, description="Nome completo do cliente")
    telefone: str | None = Field(None, max_length=20, description="Telefone do cliente")
    email: EmailStr | None = Field(None, description="E-mail válido do cliente")
    cpf_cnpj: str | None = Field(None, max_length=18, description="CPF ou CNPJ do cliente")
    data_nascimento: date | None = Field(None, description="Data de nascimento do cliente")

    @field_validator("email")
    @classmethod
    def email_max_len(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 100:
            raise ValueError("email deve ter no máximo 100 caracteres")
        return v

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cpf_cnpj_clean = re.sub(r"\D", "", v)
        if len(cpf_cnpj_clean) == 11:
            if not cls._validate_cpf(cpf_cnpj_clean):
                raise ValueError("CPF inválido")
        elif len(cpf_cnpj_clean) == 14:
            if not cls._validate_cnpj(cpf_cnpj_clean):
                raise ValueError("CNPJ inválido")
        else:
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        return v

    @field_validator("data_nascimento")
    @classmethod
    def validate_data_nascimento(cls, v: date | None) -> date | None:
        if v is None:
            return v
        today = date.today()
        if v > today:
            raise ValueError("Data de nascimento não pode ser no futuro")
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Cliente deve ter pelo menos 18 anos")
        return v

class ClientePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    nome: str
    telefone: str | None
    email: str | None
    cpf_cnpj: str | None
    data_nascimento: date | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
