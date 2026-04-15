from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re

class ClienteCreate(BaseModel):
    nome: str = Field(..., min_length=5, max_length=100, description="Nome completo (mínimo 5 caracteres)")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone com DDD")
    email: Optional[EmailStr] = Field(None, description="E-mail válido")
    cpf_cnpj: Optional[str] = Field(None, max_length=18, description="CPF ou CNPJ válido")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento (não pode ser menor de idade ou no futuro)")

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
        
        # Remove caracteres não numéricos
        cpf_cnpj_clean = re.sub(r'\D', '', v)
        
        if len(cpf_cnpj_clean) == 11:  # CPF
            if not cls._validate_cpf(cpf_cnpj_clean):
                raise ValueError("CPF inválido")
        elif len(cpf_cnpj_clean) == 14:  # CNPJ
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
        
        # Não pode ser no futuro
        if v > today:
            raise ValueError("Data de nascimento não pode ser no futuro")
        
        # Não pode ser menor de idade (18 anos)
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Cliente deve ter pelo menos 18 anos")
        
        return v

    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        """Valida CPF usando algoritmo de dígitos verificadores"""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Primeiro dígito
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[9]):
            return False
        
        # Segundo dígito
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[10]):
            return False
        
        return True

    @staticmethod
    def _validate_cnpj(cnpj: str) -> bool:
        """Valida CNPJ usando algoritmo de dígitos verificadores"""
        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False
        
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        # Primeiro dígito
        soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        if digito1 != int(cnpj[12]):
            return False
        
        # Segundo dígito
        soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        if digito2 != int(cnpj[13]):
            return False
        
        return True

class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=5, max_length=100, description="Nome completo (mínimo 5 caracteres)")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone com DDD")
    email: Optional[EmailStr] = Field(None, description="E-mail válido")
    cpf_cnpj: Optional[str] = Field(None, max_length=18, description="CPF ou CNPJ válido")
    data_nascimento: Optional[date] = Field(None, description="Data de nascimento (não pode ser menor de idade ou no futuro)")

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
        
        # Remove caracteres não numéricos
        cpf_cnpj_clean = re.sub(r'\D', '', v)
        
        if len(cpf_cnpj_clean) == 11:  # CPF
            if not cls._validate_cpf(cpf_cnpj_clean):
                raise ValueError("CPF inválido")
        elif len(cpf_cnpj_clean) == 14:  # CNPJ
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
        
        # Não pode ser no futuro
        if v > today:
            raise ValueError("Data de nascimento não pode ser no futuro")
        
        # Não pode ser menor de idade (18 anos)
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Cliente deve ter pelo menos 18 anos")
        
        return v

class ClientePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    nome: str
    telefone: Optional[str]
    email: Optional[str]
    cpf_cnpj: Optional[str]
    data_nascimento: Optional[date]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
