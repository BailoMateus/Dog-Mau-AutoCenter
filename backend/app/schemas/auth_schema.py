from datetime import date
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    password: str
    telefone: str | None = None
    cpf_cnpj: str | None = None
    data_nascimento: date | None = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
