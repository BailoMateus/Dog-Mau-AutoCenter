from pydantic import BaseModel, Field, validator

class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=6, description="Senha atual")
    new_password: str = Field(..., min_length=6, description="Nova senha")
    confirm_password: str = Field(..., min_length=6, description="Confirmação")

    @validator("new_password")
    def new_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("Nova senha não pode estar vazia")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if values.get("new_password") and v != values.get("new_password"):
            raise ValueError("Senhas não coincidem")
        return v