"""
Entidades de dados simples (sem ORM).
Substitui os models SQLAlchemy por classes básicas e dicionários.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id_usuario: Optional[int] = None
    nome: str = ""
    email: str = ""
    senha_hash: str = ""
    role: str = "CLIENTE"
    ativo: bool = True
    telefone: str = ""
    cpf_cnpj: str = ""
    data_nascimento: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Endereco:
    id_endereco: Optional[int] = None
    id_cliente: int = 0
    logradouro: str = ""
    numero: Optional[str] = None
    cep: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Marca:
    id_marca: Optional[int] = None
    nome: str = ""
    pais_origem: Optional[str] = None
    site_oficial: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Modelo:
    id_modelo: Optional[int] = None
    id_marca: int = 0
    nome_modelo: str = ""
    ano_lancamento: Optional[int] = None
    tipo_combustivel: Optional[str] = None
    categoria: Optional[str] = None
    num_portas: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Veiculo:
    id_veiculo: Optional[int] = None
    placa: str = ""
    ano_fabricacao: Optional[int] = None
    cor: Optional[str] = None
    id_cliente: int = 0
    id_modelo: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Servico:
    id_servico: Optional[int] = None
    descricao: str = ""
    preco: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

# Funções auxiliares para converter dicionários do banco para entidades
def dict_to_user(data: dict) -> User:
    """Converte dicionário do banco para entidade User."""
    if not data:
        return None
    return User(**data)

def dict_to_endereco(data: dict) -> Endereco:
    """Converte dicionário do banco para entidade Endereco."""
    if not data:
        return None
    return Endereco(**data)

def dict_to_marca(data: dict) -> Marca:
    """Converte dicionário do banco para entidade Marca."""
    if not data:
        return None
    return Marca(**data)

def dict_to_modelo(data: dict) -> Modelo:
    """Converte dicionário do banco para entidade Modelo."""
    if not data:
        return None
    return Modelo(**data)

def dict_to_veiculo(data: dict) -> Veiculo:
    """Converte dicionário do banco para entidade Veiculo."""
    if not data:
        return None
    return Veiculo(**data)

def dict_to_servico(data: dict) -> Servico:
    """Converte dicionário do banco para entidade Servico."""
    if not data:
        return None
    return Servico(**data)

# Funções para converter entidades para dicionários (para INSERT/UPDATE)
def user_to_dict(user: User, exclude_password: bool = False) -> dict:
    """Converte entidade User para dicionário."""
    data = {
        'nome': user.nome,
        'email': user.email,
        'role': user.role,
        'ativo': user.ativo,
        'telefone': user.telefone,
        'cpf_cnpj': user.cpf_cnpj,
        'data_nascimento': user.data_nascimento
    }
    if not exclude_password and user.senha_hash:
        data['senha_hash'] = user.senha_hash
    return data

def endereco_to_dict(endereco: Endereco) -> dict:
    """Converte entidade Endereco para dicionário."""
    return {
        'id_cliente': endereco.id_cliente,
        'logradouro': endereco.logradouro,
        'numero': endereco.numero,
        'cep': endereco.cep,
        'complemento': endereco.complemento,
        'bairro': endereco.bairro,
        'cidade': endereco.cidade,
        'estado': endereco.estado
    }

def marca_to_dict(marca: Marca) -> dict:
    """Converte entidade Marca para dicionário."""
    return {
        'nome': marca.nome,
        'pais_origem': marca.pais_origem,
        'site_oficial': marca.site_oficial
    }

def modelo_to_dict(modelo: Modelo) -> dict:
    """Converte entidade Modelo para dicionário."""
    return {
        'id_marca': modelo.id_marca,
        'nome_modelo': modelo.nome_modelo,
        'ano_lancamento': modelo.ano_lancamento,
        'tipo_combustivel': modelo.tipo_combustivel,
        'categoria': modelo.categoria,
        'num_portas': modelo.num_portas
    }

def veiculo_to_dict(veiculo: Veiculo) -> dict:
    """Converte entidade Veiculo para dicionário."""
    return {
        'placa': veiculo.placa,
        'ano_fabricacao': veiculo.ano_fabricacao,
        'cor': veiculo.cor,
        'id_cliente': veiculo.id_cliente,
        'id_modelo': veiculo.id_modelo
    }

def servico_to_dict(servico: Servico) -> dict:
    """Converte entidade Servico para dicionário."""
    return {
        'descricao': servico.descricao,
        'preco': servico.preco
    }
