"""
Entidades de dados simples (sem ORM).
Substitui os models SQLAlchemy por classes básicas e dicionários.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal
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
    foto_perfil: Optional[str] = None
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
    id_usuario: int = 0
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
    produto_nome: Optional[str] = None
    produto_preco: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Peca:
    id_peca: Optional[int] = None
    nome: str = ""
    preco_unitario: float = 0.0
    quantidade_estoque: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class Agendamento:
    id_agendamento: Optional[int] = None
    id_usuario: int = 0
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
    id_usuario: int = 0
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

@dataclass
class OrdemServico:
    id_os: Optional[int] = None
    id_orcamento: Optional[int] = None
    id_veiculo: int = 0
    id_usuario: int = 0
    descricao_problema: str = ""
    valor_total: float = 0.0
    status: str = "aberta"
    data_abertura: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def id_ordem_servico(self) -> Optional[int]:
        return self.id_os

    @property
    def data_inicio(self) -> Optional[datetime]:
        return self.data_abertura

@dataclass
class OrdemServicoPeca:
    id_os: int = 0
    id_peca: int = 0
    quantidade: int = 1

@dataclass
class OrdemServicoServico:
    id_os: int = 0
    id_servico: int = 0
    quantidade: int = 1

@dataclass
class Mecanico:
    id_usuario: Optional[int] = None
    nome: str = ""
    especialidade: str = ""
    telefone: str = ""
    email: str = ""
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class MovimentacaoEstoque:
    id_movimentacao: Optional[int] = None
    id_peca: int = 0
    tipo_movimentacao: str = ""  # 'saida' ou 'entrada'
    quantidade: int = 0
    motivo: str = ""
    created_at: Optional[datetime] = None

@dataclass
class Pagamento:
    id_pagamento: Optional[int] = None
    id_os: int = 0
    valor: float = 0.0
    forma_pagamento: str = ""
    status: str = "pendente"
    data_pagamento: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

@dataclass
class MovimentacaoFinanceira:
    id_movimentacao_financeira: Optional[int] = None
    tipo_movimentacao: str = ""  # 'entrada' ou 'saida'
    valor: float = 0.0
    descricao: str = ""
    id_pagamento: Optional[int] = None
    created_at: Optional[datetime] = None

# Response DTOs com dados enriquecidos de JOINs
@dataclass
class OrcamentoPecaResponse:
    """DTO Response para peça do orçamento - contém dados enriquecidos."""
    id_orcamento: int
    id_peca: int
    quantidade: int
    peca_nome: str
    peca_preco: Decimal
    subtotal: Decimal = 0.0

    def __post_init__(self):
        if self.subtotal == 0.0:
            self.subtotal = Decimal(self.peca_preco) * Decimal(self.quantidade)

@dataclass
class OrcamentoServicoResponse:
    """DTO Response para serviço do orçamento - contém dados enriquecidos."""
    id_orcamento: int
    id_servico: int
    quantidade: int
    servico_descricao: str
    servico_preco: Decimal
    subtotal: Decimal = 0.0

    def __post_init__(self):
        if self.subtotal == 0.0:
            self.subtotal = Decimal(self.servico_preco) * Decimal(self.quantidade)

@dataclass
class OrdemServicoPecaResponse:
    """DTO Response para peça da OS - contém dados enriquecidos."""
    id_os: int
    id_peca: int
    quantidade: int
    peca_nome: str
    peca_preco: Decimal
    peca_estoque: int
    subtotal: Decimal = 0.0

    def __post_init__(self):
        if self.subtotal == 0.0:
            self.subtotal = Decimal(self.peca_preco) * Decimal(self.quantidade)

@dataclass
class OrdemServicoServicoResponse:
    """DTO Response para serviço da OS - contém dados enriquecidos."""
    id_os: int
    id_servico: int
    quantidade: int
    servico_descricao: str
    servico_preco: Decimal
    subtotal: Decimal = 0.0

    def __post_init__(self):
        if self.subtotal == 0.0:
            self.subtotal = Decimal(self.servico_preco) * Decimal(self.quantidade)

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

def dict_to_peca(data: dict) -> Peca:
    """Converte dicionário do banco para entidade Peca."""
    if not data:
        return None
    return Peca(**data)

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
    """Converte dicionário do banco para entidade OrcamentoPeca.

    Ignora colunas extras (ex: peca_nome, peca_preco) retornadas por JOINs.
    """
    if not data:
        return None
    return OrcamentoPeca(
        id_orcamento=data.get('id_orcamento'),
        id_peca=data.get('id_peca'),
        quantidade=data.get('quantidade')
    )

def dict_to_orcamento_servico(data: dict) -> OrcamentoServico:
    """Converte dicionário do banco para entidade OrcamentoServico.

    Ignora colunas extras (ex: servico_descricao, servico_preco) retornadas por JOINs.
    """
    if not data:
        return None
    return OrcamentoServico(
        id_orcamento=data.get('id_orcamento'),
        id_servico=data.get('id_servico'),
        quantidade=data.get('quantidade')
    )

def dict_to_ordem_servico(data: dict) -> OrdemServico:
    """Converte dicionário do banco para entidade OrdemServico."""
    if not data:
        return None
    return OrdemServico(**data)

def dict_to_ordem_servico_peca(data: dict) -> OrdemServicoPeca:
    """Converte dicionário do banco para entidade OrdemServicoPeca."""
    if not data:
        return None
    return OrdemServicoPeca(**data)

def dict_to_ordem_servico_servico(data: dict) -> OrdemServicoServico:
    """Converte dicionário do banco para entidade OrdemServicoServico."""
    if not data:
        return None
    return OrdemServicoServico(**data)

def dict_to_mecanico(data: dict) -> Mecanico:
    """Converte dicionário do banco para entidade Mecanico."""
    if not data:
        return None
    return Mecanico(**data)

def dict_to_movimentacao_estoque(data: dict) -> MovimentacaoEstoque:
    """Converte dicionário do banco para entidade MovimentacaoEstoque."""
    if not data:
        return None
    return MovimentacaoEstoque(**data)

def dict_to_pagamento(data: dict) -> Pagamento:
    """Converte dicionário do banco para entidade Pagamento."""
    if not data:
        return None
    return Pagamento(**data)

def dict_to_movimentacao_financeira(data: dict) -> MovimentacaoFinanceira:
    """Converte dicionário do banco para entidade MovimentacaoFinanceira."""
    if not data:
        return None
    return MovimentacaoFinanceira(**data)

# Funções auxiliares para converter entidades para dicionários
def user_to_dict(user: User) -> dict:
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

def endereco_to_dict(endereco: Endereco) -> dict:
    """Converte entidade Endereco para dicionário."""
    if not endereco:
        return None
    return {
        'id_endereco': endereco.id_endereco,
        'id_usuario': endereco.id_usuario,
        'logradouro': endereco.logradouro,
        'numero': endereco.numero,
        'cep': endereco.cep,
        'complemento': endereco.complemento,
        'bairro': endereco.bairro,
        'cidade': endereco.cidade,
        'estado': endereco.estado,
        'created_at': endereco.created_at,
        'updated_at': endereco.updated_at,
        'deleted_at': endereco.deleted_at
    }

def marca_to_dict(marca: Marca) -> dict:
    """Converte entidade Marca para dicionário."""
    if not marca:
        return None
    return {
        'id_marca': marca.id_marca,
        'nome': marca.nome,
        'pais_origem': marca.pais_origem,
        'site_oficial': marca.site_oficial,
        'created_at': marca.created_at,
        'updated_at': marca.updated_at,
        'deleted_at': marca.deleted_at
    }

def modelo_to_dict(modelo: Modelo) -> dict:
    """Converte entidade Modelo para dicionário."""
    if not modelo:
        return None
    return {
        'id_modelo': modelo.id_modelo,
        'id_marca': modelo.id_marca,
        'nome_modelo': modelo.nome_modelo,
        'ano_lancamento': modelo.ano_lancamento,
        'tipo_combustivel': modelo.tipo_combustivel,
        'categoria': modelo.categoria,
        'num_portas': modelo.num_portas,
        'created_at': modelo.created_at,
        'updated_at': modelo.updated_at,
        'deleted_at': modelo.deleted_at
    }

def veiculo_to_dict(veiculo: Veiculo) -> dict:
    """Converte entidade Veiculo para dicionário."""
    if not veiculo:
        return None
    return {
        'id_veiculo': veiculo.id_veiculo,
        'placa': veiculo.placa,
        'ano_fabricacao': veiculo.ano_fabricacao,
        'cor': veiculo.cor,
        'id_usuario': veiculo.id_usuario,
        'id_modelo': veiculo.id_modelo,
        'created_at': veiculo.created_at,
        'updated_at': veiculo.updated_at,
        'deleted_at': veiculo.deleted_at
    }

def servico_to_dict(servico: Servico) -> dict:
    """Converte entidade Servico para dicionário."""
    if not servico:
        return None
    return {
        'id_servico': servico.id_servico,
        'descricao': servico.descricao,
        'preco': servico.preco,
        'created_at': servico.created_at,
        'updated_at': servico.updated_at,
        'deleted_at': servico.deleted_at
    }

def produto_to_dict(produto: Produto) -> dict:
    """Converte entidade Produto para dicionário."""
    if not produto:
        return None
    return {
        'id_produto': produto.id_produto,
        'nome': produto.nome,
        'descricao': produto.descricao,
        'preco': produto.preco,
        'quantidade_estoque': produto.quantidade_estoque,
        'created_at': produto.created_at,
        'updated_at': produto.updated_at,
        'deleted_at': produto.deleted_at
    }

def pedido_to_dict(pedido: Pedido) -> dict:
    """Converte entidade Pedido para dicionário."""
    if not pedido:
        return None
    return {
        'id_pedido': pedido.id_pedido,
        'id_usuario': pedido.id_usuario,
        'valor_total': pedido.valor_total,
        'status': pedido.status,
        'created_at': pedido.created_at,
        'updated_at': pedido.updated_at,
        'deleted_at': pedido.deleted_at
    }

def pedido_produto_to_dict(pedido_produto: PedidoProduto) -> dict:
    """Converte entidade PedidoProduto para dicionário."""
    if not pedido_produto:
        return None

    return {
        'id_pedido': pedido_produto.id_pedido,
        'id_produto': pedido_produto.id_produto,
        'quantidade': pedido_produto.quantidade,
        'created_at': pedido_produto.created_at,
        'updated_at': pedido_produto.updated_at,
        'deleted_at': pedido_produto.deleted_at
    }

def peca_to_dict(peca: Peca) -> dict:
    """Converte entidade Peca para dicionário."""
    if not peca:
        return None
    return {
        'id_peca': peca.id_peca,
        'nome': peca.nome,
        'preco_unitario': peca.preco_unitario,
        'quantidade_estoque': peca.quantidade_estoque,
        'created_at': peca.created_at,
        'updated_at': peca.updated_at,
        'deleted_at': peca.deleted_at
    }

def agendamento_to_dict(agendamento: Agendamento) -> dict:
    """Converte entidade Agendamento para dicionário."""
    if not agendamento:
        return None
    return {
        'id_agendamento': agendamento.id_agendamento,
        'id_usuario': agendamento.id_usuario,
        'id_veiculo': agendamento.id_veiculo,
        'data_agendamento': agendamento.data_agendamento,
        'descricao': agendamento.descricao,
        'status': agendamento.status,
        'created_at': agendamento.created_at,
        'updated_at': agendamento.updated_at,
        'deleted_at': agendamento.deleted_at
    }

def orcamento_to_dict(orcamento: Orcamento) -> dict:
    """Converte entidade Orcamento para dicionário."""
    if not orcamento:
        return None
    return {
        'id_orcamento': orcamento.id_orcamento,
        'id_usuario': orcamento.id_usuario,
        'id_veiculo': orcamento.id_veiculo,
        'status': orcamento.status,
        'valor_total': orcamento.valor_total,
        'created_at': orcamento.created_at,
        'updated_at': orcamento.updated_at,
        'deleted_at': orcamento.deleted_at
    }

def orcamento_peca_to_dict(orcamento_peca: OrcamentoPeca) -> dict:
    """Converte entidade OrcamentoPeca para dicionário."""
    if not orcamento_peca:
        return None
    return {
        'id_orcamento': orcamento_peca.id_orcamento,
        'id_peca': orcamento_peca.id_peca,
        'quantidade': orcamento_peca.quantidade
    }

def orcamento_servico_to_dict(orcamento_servico: OrcamentoServico) -> dict:
    """Converte entidade OrcamentoServico para dicionário."""
    if not orcamento_servico:
        return None
    return {
        'id_orcamento': orcamento_servico.id_orcamento,
        'id_servico': orcamento_servico.id_servico,
        'quantidade': orcamento_servico.quantidade
    }

def ordem_servico_to_dict(ordem_servico: OrdemServico) -> dict:
    """Converte entidade OrdemServico para dicionário."""
    if not ordem_servico:
        return None
    return {
        'id_os': ordem_servico.id_os,
        'id_orcamento': ordem_servico.id_orcamento,
        'id_veiculo': ordem_servico.id_veiculo,
        'id_usuario': ordem_servico.id_usuario,
        'descricao_problema': ordem_servico.descricao_problema,
        'valor_total': ordem_servico.valor_total,
        'status': ordem_servico.status,
        'data_abertura': ordem_servico.data_abertura,
        'data_conclusao': ordem_servico.data_conclusao,
        'created_at': ordem_servico.created_at,
        'updated_at': ordem_servico.updated_at,
        'deleted_at': ordem_servico.deleted_at
    }

def ordem_servico_peca_to_dict(ordem_servico_peca: OrdemServicoPeca) -> dict:
    """Converte entidade OrdemServicoPeca para dicionário."""
    if not ordem_servico_peca:
        return None
    return {
        'id_os': ordem_servico_peca.id_os,
        'id_peca': ordem_servico_peca.id_peca,
        'quantidade': ordem_servico_peca.quantidade
    }

def ordem_servico_servico_to_dict(ordem_servico_servico: OrdemServicoServico) -> dict:
    """Converte entidade OrdemServicoServico para dicionário."""
    if not ordem_servico_servico:
        return None
    return {
        'id_os': ordem_servico_servico.id_os,
        'id_servico': ordem_servico_servico.id_servico,
        'quantidade': ordem_servico_servico.quantidade
    }

def mecanico_to_dict(mecanico: Mecanico) -> dict:
    """Converte entidade Mecanico para dicionário."""
    if not mecanico:
        return None
    return {
        'id_usuario': mecanico.id_usuario,
        'nome': mecanico.nome,
        'especialidade': mecanico.especialidade,
        'telefone': mecanico.telefone,
        'email': mecanico.email,
        'ativo': mecanico.ativo,
        'created_at': mecanico.created_at,
        'updated_at': mecanico.updated_at,
        'deleted_at': mecanico.deleted_at
    }

def movimentacao_estoque_to_dict(movimentacao: MovimentacaoEstoque) -> dict:
    """Converte entidade MovimentacaoEstoque para dicionário."""
    if not movimentacao:
        return None
    return {
        'id_movimentacao': movimentacao.id_movimentacao,
        'id_peca': movimentacao.id_peca,
        'tipo_movimentacao': movimentacao.tipo_movimentacao,
        'quantidade': movimentacao.quantidade,
        'motivo': movimentacao.motivo,
        'created_at': movimentacao.created_at
    }

def pagamento_to_dict(pagamento: Pagamento) -> dict:
    """Converte entidade Pagamento para dicionário."""
    if not pagamento:
        return None
    return {
        'id_pagamento': pagamento.id_pagamento,
        'id_os': pagamento.id_os,
        'valor': pagamento.valor,
        'forma_pagamento': pagamento.forma_pagamento,
        'status': pagamento.status,
        'data_pagamento': pagamento.data_pagamento,
        'created_at': pagamento.created_at,
        'updated_at': pagamento.updated_at,
        'deleted_at': pagamento.deleted_at
    }

def movimentacao_financeira_to_dict(movimentacao: MovimentacaoFinanceira) -> dict:
    """Converte entidade MovimentacaoFinanceira para dicionário."""
    if not movimentacao:
        return None
    return {
        'id_movimentacao_financeira': movimentacao.id_movimentacao_financeira,
        'tipo_movimentacao': movimentacao.tipo_movimentacao,
        'valor': movimentacao.valor,
        'descricao': movimentacao.descricao,
        'id_pagamento': movimentacao.id_pagamento,
        'created_at': movimentacao.created_at
    }

# Funções para criar Response DTOs a partir de dicionários com dados enriquecidos
def dict_to_orcamento_peca_response(data: dict) -> OrcamentoPecaResponse:
    """Converte dicionário do banco (com JOIN) para OrcamentoPecaResponse."""
    if not data:
        return None
    return OrcamentoPecaResponse(
        id_orcamento=data.get('id_orcamento'),
        id_peca=data.get('id_peca'),
        quantidade=data.get('quantidade'),
        peca_nome=data.get('peca_nome'),
        peca_preco=Decimal(str(data.get('peca_preco', 0)))
    )

def dict_to_orcamento_servico_response(data: dict) -> OrcamentoServicoResponse:
    """Converte dicionário do banco (com JOIN) para OrcamentoServicoResponse."""
    if not data:
        return None
    return OrcamentoServicoResponse(
        id_orcamento=data.get('id_orcamento'),
        id_servico=data.get('id_servico'),
        quantidade=data.get('quantidade'),
        servico_descricao=data.get('servico_descricao'),
        servico_preco=Decimal(str(data.get('servico_preco', 0)))
    )

def dict_to_ordem_servico_peca_response(data: dict) -> OrdemServicoPecaResponse:
    """Converte dicionário do banco (com JOIN) para OrdemServicoPecaResponse."""
    if not data:
        return None
    return OrdemServicoPecaResponse(
        id_os=data.get('id_os'),
        id_peca=data.get('id_peca'),
        quantidade=data.get('quantidade'),
        peca_nome=data.get('peca_nome'),
        peca_preco=Decimal(str(data.get('peca_preco', 0))),
        peca_estoque=data.get('peca_estoque', 0)
    )

def dict_to_ordem_servico_servico_response(data: dict) -> OrdemServicoServicoResponse:
    """Converte dicionário do banco (com JOIN) para OrdemServicoServicoResponse."""
    if not data:
        return None
    return OrdemServicoServicoResponse(
        id_os=data.get('id_os'),
        id_servico=data.get('id_servico'),
        quantidade=data.get('quantidade'),
        servico_descricao=data.get('servico_descricao'),
        servico_preco=Decimal(str(data.get('servico_preco', 0)))
    )
