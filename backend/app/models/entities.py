from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date

@dataclass
class User:
    id_usuario: Optional[int] = None
    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    role: str = "CLIENTE"
    ativo: bool = True
    telefone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    data_nascimento: Optional[date] = None  
    foto_perfil: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


# Funções auxiliares para converter dicionários do banco para entidades
def dict_to_user(data: dict) -> Optional[User]:
    """Converte dicionário do banco para entidade User."""
    if not data:
        return None
    return User(**data)

# Funções auxiliares para converter entidades para dicionários
def user_to_dict(user: User) -> Optional[dict]:
    """Converte entidade User para dicionário."""
    if not user:
        return None
    return {
        'id_usuario': user.id_usuario,
        'nome': user.nome,
        'email': user.email,
        'senha_hash': user.senha_hash,
        'role': user.role,
        'ativo': user.ativo,
        'telefone': user.telefone,
        'cpf_cnpj': user.cpf_cnpj,
        'data_nascimento': user.data_nascimento,
        'foto_perfil': user.foto_perfil,
        'created_at': user.created_at,
        'updated_at': user.updated_at,
        'deleted_at': user.deleted_at
    }