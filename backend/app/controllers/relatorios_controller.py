import logging

from fastapi import APIRouter, HTTPException, status

from app.services import relatorios_service
from app.schemas.relatorios_schema import (
    RelatorioPeriodo, FaturamentoRelatorio, ServicosRealizadosRelatorio,
    EstoqueRelatorio, OrdensServicoRelatorio, FinanceiroPeriodoRelatorio,
    RelatorioCompleto
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.post("/faturamento", response_model=FaturamentoRelatorio)
def gerar_relatorio_faturamento(data: RelatorioPeriodo):
    """Gera relatório de faturamento por período."""
    logger.info("POST /relatorios/faturamento periodo=%s a %s", data.data_inicio, data.data_fim)
    relatorio = relatorios_service.gerar_relatorio_faturamento(data)
    return FaturamentoRelatorio(
        periodo=relatorio["periodo"],
        resumo=relatorio["resumo"],
        detalhes=relatorio["detalhes"]
    )

@router.post("/servicos-realizados", response_model=ServicosRealizadosRelatorio)
def gerar_relatorio_servicos_realizados(data: RelatorioPeriodo):
    """Gera relatório de serviços realizados por período."""
    logger.info("POST /relatorios/servicos-realizados periodo=%s a %s", data.data_inicio, data.data_fim)
    relatorio = relatorios_service.gerar_relatorio_servicos_realizados(data)
    return ServicosRealizadosRelatorio(
        periodo=relatorio["periodo"],
        resumo=relatorio["resumo"],
        detalhes=relatorio["detalhes"]
    )

@router.get("/estoque", response_model=EstoqueRelatorio)
def gerar_relatorio_estoque():
    """Gera relatório de estoque atual."""
    logger.info("GET /relatorios/estoque")
    relatorio = relatorios_service.gerar_relatorio_estoque()
    return EstoqueRelatorio(
        data_geracao=relatorio["data_geracao"],
        resumo=relatorio["resumo"],
        detalhes=relatorio["detalhes"]
    )

@router.post("/ordens-servico", response_model=OrdensServicoRelatorio)
def gerar_relatorio_ordens_servico(data: RelatorioPeriodo):
    """Gera relatório de ordens de serviço por período."""
    logger.info("POST /relatorios/ordens-servico periodo=%s a %s", data.data_inicio, data.data_fim)
    relatorio = relatorios_service.gerar_relatorio_ordens_servico(data)
    return OrdensServicoRelatorio(
        periodo=relatorio["periodo"],
        resumo=relatorio["resumo"],
        detalhes=relatorio["detalhes"]
    )

@router.post("/financeiro-periodo", response_model=FinanceiroPeriodoRelatorio)
def gerar_relatorio_financeiro_periodo(data: RelatorioPeriodo):
    """Gera relatório financeiro completo por período."""
    logger.info("POST /relatorios/financeiro-periodo periodo=%s a %s", data.data_inicio, data.data_fim)
    relatorio = relatorios_service.gerar_relatorio_financeiro_periodo(data)
    return FinanceiroPeriodoRelatorio(
        periodo=relatorio["periodo"],
        movimentacoes_financeiras=[
            {
                "mes": item["mes"],
                "tipo_movimentacao": item["tipo_movimentacao"],
                "quantidade": item["quantidade"],
                "valor_total": item["valor_total"]
            }
            for item in relatorio["movimentacoes_financeiras"]
        ],
        saldo_periodo=relatorio["saldo_periodo"],
        pagamentos=relatorio["pagamentos"]
    )

@router.post("/completo", response_model=RelatorioCompleto)
def gerar_relatorio_completo(data: RelatorioPeriodo):
    """Gera relatório completo com todos os dados."""
    logger.info("POST /relatorios/completo periodo=%s a %s", data.data_inicio, data.data_fim)
    relatorio = relatorios_service.gerar_relatorio_completo(data)
    return RelatorioCompleto(
        periodo=relatorio["periodo"],
        faturamento=relatorio["faturamento"],
        servicos_realizados=relatorio["servicos_realizados"],
        ordens_servico=relatorio["ordens_servico"],
        financeiro=relatorio["financeiro"],
        estoque_atual=relatorio["estoque_atual"]
    )
