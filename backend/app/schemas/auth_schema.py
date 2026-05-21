import re
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator

class LoginRequest(BaseModel):
    email: str
    password: str

class FirebaseLoginRequest(BaseModel):
    id_token: str

class RegisterRequest(BaseModel):
    nome: str = Field(..., min_length=5)
    email: EmailStr
    password: str
    telefone: str | None = None
    cpf_cnpj: str | None = None
    data_nascimento: date | None = None
    
    cep: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: str | None = None

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_cpf_cnpj(cls, v: str | None) -> str | None:
        if not v:
            return v
            
        doc = re.sub(r"\D", "", v)
        if len(doc) == 11:
            if doc == doc[0] * 11:
                raise ValueError("CPF inválido: números repetidos")
            # CPF Modulo 11
            soma = sum(int(doc[i]) * (10 - i) for i in range(9))
            resto = (soma * 10) % 11 % 10
            if resto != int(doc[9]):
                raise ValueError("CPF inválido: dígito verificador 1 incorreto")
                
            soma = sum(int(doc[i]) * (11 - i) for i in range(10))
            resto = (soma * 10) % 11 % 10
            if resto != int(doc[10]):
                raise ValueError("CPF inválido: dígito verificador 2 incorreto")
                
        elif len(doc) == 14:
            if doc == doc[0] * 14:
                raise ValueError("CNPJ inválido: números repetidos")
            # CNPJ Modulo 11
            pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            soma = sum(int(doc[i]) * pesos1[i] for i in range(12))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            if digito1 != int(doc[12]):
                raise ValueError("CNPJ inválido: dígito verificador 1 incorreto")
                
            pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            soma = sum(int(doc[i]) * pesos2[i] for i in range(13))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            if digito2 != int(doc[13]):
                raise ValueError("CNPJ inválido: dígito verificador 2 incorreto")
        else:
            raise ValueError("O documento deve ter 11 (CPF) ou 14 (CNPJ) números")
            
        return doc

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter pelo menos um número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter pelo menos um caractere especial")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=8)
    
    @field_validator("nova_senha")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter pelo menos um número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter pelo menos um caractere especial")
        return v
