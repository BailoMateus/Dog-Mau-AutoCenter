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
    id_usuario: int = 0
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
    id_usuario: int = 0
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

@dataclass
class Produto:
    id_produto: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    preco: float = 0.0
    quantidade_estoque: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Pedido:
    id_pedido: Optional[int] = None
    id_cliente: int = 0
    valor_total: float = 0.0
    status: str = "processando"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class PedidoProduto:
    id_pedido: int = 0
    id_produto: int = 0
    quantidade: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Agendamento:
    id_agendamento: Optional[int] = None
    id_cliente: int = 0
    id_veiculo: int = 0
    data_agendamento: Optional[datetime] = None
    descricao: str = ""
    status: str = "agendado"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Orcamento:
    id_orcamento: Optional[int] = None
    id_cliente: int = 0
    id_veiculo: int = 0
    status: str = "pendente"
    valor_total: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class OrcamentoPeca:
    id_orcamento: int = 0
    id_peca: int = 0
    quantidade: int = 1

@dataclass
class OrcamentoServico:
    id_orcamento: int = 0
    id_servico: int = 0
    quantidade: int = 1

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

def dict_to_produto(data: dict) -> Produto:
    """Converte dicionário do banco para entidade Produto."""
    if not data:
        return None
    return Produto(**data)

def dict_to_pedido(data: dict) -> Pedido:
    """Converte dicionário do banco para entidade Pedido."""
    if not data:
        return None
    return Pedido(**data)

def dict_to_pedido_produto(data: dict) -> PedidoProduto:
    """Converte dicionário do banco para entidade PedidoProduto."""
    if not data:
        return None
    return PedidoProduto(**data)

def dict_to_agendamento(data: dict) -> Agendamento:
    """Converte dicionário do banco para entidade Agendamento."""
    if not data:
        return None
    return Agendamento(**data)

def dict_to_orcamento(data: dict) -> Orcamento:
    """Converte dicionário do banco para entidade Orcamento."""
    if not data:
        return None
    return Orcamento(**data)

def dict_to_orcamento_peca(data: dict) -> OrcamentoPeca:
    """Converte dicionário do banco para entidade OrcamentoPeca."""
    if not data:
        return None
    return OrcamentoPeca(**data)

def dict_to_orcamento_servico(data: dict) -> OrcamentoServico:
    """Converte dicionário do banco para entidade OrcamentoServico."""
    if not data:
        return None
    return OrcamentoServico(**data)

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
        'id_usuario': endereco.id_usuario,
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
        'id_usuario': veiculo.id_usuario,
        'id_modelo': veiculo.id_modelo
    }

def servico_to_dict(servico: Servico) -> dict:
    """Converte entidade Servico para dicionário."""
    return {
        'descricao': servico.descricao,
        'preco': servico.preco
    }

def produto_to_dict(produto: Produto) -> dict:
    """Converte entidade Produto para dicionário."""
    return {
        'nome': produto.nome,
        'descricao': produto.descricao,
        'preco': produto.preco,
        'quantidade_estoque': produto.quantidade_estoque
    }

def pedido_to_dict(pedido: Pedido) -> dict:
    """Converte entidade Pedido para dicionário."""
    return {
        'id_cliente': pedido.id_cliente,
        'valor_total': pedido.valor_total,
        'status': pedido.status
    }

def pedido_produto_to_dict(pedido_produto: PedidoProduto) -> dict:
    """Converte entidade PedidoProduto para dicionário."""
    return {
        'id_pedido': pedido_produto.id_pedido,
        'id_produto': pedido_produto.id_produto,
        'quantidade': pedido_produto.quantidade
    }

def agendamento_to_dict(agendamento: Agendamento) -> dict:
    """Converte entidade Agendamento para dicionário."""
    return {
        'id_cliente': agendamento.id_cliente,
        'id_veiculo': agendamento.id_veiculo,
        'data_agendamento': agendamento.data_agendamento,
        'descricao': agendamento.descricao,
        'status': agendamento.status
    }

def orcamento_to_dict(orcamento: Orcamento) -> dict:
    """Converte entidade Orcamento para dicionário."""
    return {
        'id_cliente': orcamento.id_cliente,
        'id_veiculo': orcamento.id_veiculo,
        'status': orcamento.status,
        'valor_total': orcamento.valor_total
    }

def orcamento_peca_to_dict(orcamento_peca: OrcamentoPeca) -> dict:
    """Converte entidade OrcamentoPeca para dicionário."""
    return {
        'id_orcamento': orcamento_peca.id_orcamento,
        'id_peca': orcamento_peca.id_peca,
        'quantidade': orcamento_peca.quantidade
    }

def orcamento_servico_to_dict(orcamento_servico: OrcamentoServico) -> dict:
    """Converte entidade OrcamentoServico para dicionário."""
    return {
        'id_orcamento': orcamento_servico.id_orcamento,
        'id_servico': orcamento_servico.id_servico,
        'quantidade': orcamento_servico.quantidade
    }
