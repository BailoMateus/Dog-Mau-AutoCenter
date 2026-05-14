from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class RelatorioPeriodo(BaseModel):
    data_inicio: datetime
    data_fim: datetime

class FaturamentoDetalhe(BaseModel):
    mes: str
    quantidade_pagamentos: int
    valor_total: float
    forma_pagamento: str

class FaturamentoResumo(BaseModel):
    valor_total_geral: float
    quantidade_total_pagamentos: int

class FaturamentoRelatorio(BaseModel):
    periodo: dict
    resumo: FaturamentoResumo
    detalhes: list[FaturamentoDetalhe]

class ServicosRealizadosDetalhe(BaseModel):
    mes: str
    quantidade_os: int
    servicos_diferentes: int
    total_servicos: int
    valor_total_servicos: float

class ServicosRealizadosResumo(BaseModel):
    valor_total_geral: float
    quantidade_total_os: int
    quantidade_total_servicos: int

class ServicosRealizadosRelatorio(BaseModel):
    periodo: dict
    resumo: ServicosRealizadosResumo
    detalhes: list[ServicosRealizadosDetalhe]

class EstoqueDetalhe(BaseModel):
    id_peca: int
    nome: str
    estoque_atual: int
    valor_unitario: float
    valor_total_estoque: float
    nivel_estoque: str

class EstoqueResumo(BaseModel):
    quantidade_pecas: int
    valor_total_geral: float
    pecas_baixo_estoque: int

class EstoqueRelatorio(BaseModel):
    data_geracao: datetime
    resumo: EstoqueResumo
    detalhes: list[EstoqueDetalhe]

class OrdensServicoDetalhe(BaseModel):
    mes: str
    status: str
    quantidade: int
    valor_total: float

class OrdensServicoResumo(BaseModel):
    quantidade_total_os: int
    valor_total_geral: float

class OrdensServicoRelatorio(BaseModel):
    periodo: dict
    resumo: OrdensServicoResumo
    detalhes: list[OrdensServicoDetalhe]

class FinanceiroPeriodoDetalhe(BaseModel):
    mes: str
    tipo_movimentacao: str
    quantidade: int
    valor_total: float

class FinanceiroPeriodoSaldo(BaseModel):
    entradas: float
    saidas: float
    saldo: float

class FinanceiroPeriodoPagamento(BaseModel):
    mes: str
    status: str
    quantidade: int
    valor_total: float

class FinanceiroPeriodoRelatorio(BaseModel):
    periodo: dict
    movimentacoes_financeiras: list[FinanceiroPeriodoDetalhe]
    saldo_periodo: FinanceiroPeriodoSaldo
    pagamentos: list[FinanceiroPeriodoPagamento]

class RelatorioCompleto(BaseModel):
    periodo: dict
    faturamento: FaturamentoResumo
    servicos_realizados: ServicosRealizadosResumo
    ordens_servico: OrdensServicoResumo
    financeiro: FinanceiroPeriodoSaldo
    estoque_atual: EstoqueResumo
