import logging

from fastapi import APIRouter, HTTPException, status, Query

from app.services import movimentacao_financeira_service
from app.schemas.movimentacao_financeira_schema import (
    MovimentacaoFinanceiraCreate, MovimentacaoFinanceiraPeriodo, 
    MovimentacaoFinanceiraPublic, SaldoPeriodo, ResumoFinanceiro
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movimentacoes-financeiras", tags=["Movimentações Financeiras"])

@router.post("/entrada", response_model=MovimentacaoFinanceiraPublic, status_code=status.HTTP_201_CREATED)
def registrar_entrada_financeira(data: MovimentacaoFinanceiraCreate):
    """Registra entrada financeira."""
    logger.info("POST /movimentacoes-financeiras/entrada valor=%s descricao=%s", data.valor, data.descricao)
    movimentacao = movimentacao_financeira_service.registrar_entrada_financeira(data)
    return MovimentacaoFinanceiraPublic(
        id_movimentacao_financeira=movimentacao.id_movimentacao_financeira,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        valor=movimentacao.valor,
        descricao=movimentacao.descricao,
        id_pagamento=movimentacao.id_pagamento,
        created_at=movimentacao.created_at
    )

@router.post("/saida", response_model=MovimentacaoFinanceiraPublic, status_code=status.HTTP_201_CREATED)
def registrar_saida_financeira(data: MovimentacaoFinanceiraCreate):
    """Registra saída financeira."""
    logger.info("POST /movimentacoes-financeiras/saida valor=%s descricao=%s", data.valor, data.descricao)
    movimentacao = movimentacao_financeira_service.registrar_saida_financeira(data)
    return MovimentacaoFinanceiraPublic(
        id_movimentacao_financeira=movimentacao.id_movimentacao_financeira,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        valor=movimentacao.valor,
        descricao=movimentacao.descricao,
        id_pagamento=movimentacao.id_pagamento,
        created_at=movimentacao.created_at
    )

@router.get("/", response_model=list[MovimentacaoFinanceiraPublic])
def list_all_movimentacoes_financeiras(limit: int = Query(default=100, le=500)):
    """Lista todas as movimentações financeiras."""
    logger.info("GET /movimentacoes-financeiras limit=%s", limit)
    movimentacoes = movimentacao_financeira_service.list_all_movimentacoes_financeiras(limit)
    return [
        MovimentacaoFinanceiraPublic(
            id_movimentacao_financeira=mov.id_movimentacao_financeira,
            tipo_movimentacao=mov.tipo_movimentacao,
            valor=mov.valor,
            descricao=mov.descricao,
            id_pagamento=mov.id_pagamento,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/tipo/{tipo}", response_model=list[MovimentacaoFinanceiraPublic])
def list_movimentacoes_by_tipo(tipo: str, limit: int = Query(default=50, le=200)):
    """Lista movimentações por tipo (entrada/saida)."""
    logger.info("GET /movimentacoes-financeiras/tipo/%s limit=%s", tipo, limit)
    movimentacoes = movimentacao_financeira_service.list_movimentacoes_by_tipo(tipo, limit)
    return [
        MovimentacaoFinanceiraPublic(
            id_movimentacao_financeira=mov.id_movimentacao_financeira,
            tipo_movimentacao=mov.tipo_movimentacao,
            valor=mov.valor,
            descricao=mov.descricao,
            id_pagamento=mov.id_pagamento,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.post("/periodo", response_model=list[MovimentacaoFinanceiraPublic])
def list_movimentacoes_by_periodo(data: MovimentacaoFinanceiraPeriodo):
    """Lista movimentações por período."""
    logger.info("POST /movimentacoes-financeiras/periodo inicio=%s fim=%s", data.data_inicio, data.data_fim)
    movimentacoes = movimentacao_financeira_service.list_movimentacoes_by_periodo(data)
    return [
        MovimentacaoFinanceiraPublic(
            id_movimentacao_financeira=mov.id_movimentacao_financeira,
            tipo_movimentacao=mov.tipo_movimentacao,
            valor=mov.valor,
            descricao=mov.descricao,
            id_pagamento=mov.id_pagamento,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/{movimentacao_id}", response_model=MovimentacaoFinanceiraPublic)
def get_movimentacao_financeira_by_id(movimentacao_id: int):
    """Busca movimentação financeira por ID."""
    logger.info("GET /movimentacoes-financeiras/%s", movimentacao_id)
    movimentacao = movimentacao_financeira_service.get_movimentacao_financeira_by_id(movimentacao_id)
    return MovimentacaoFinanceiraPublic(
        id_movimentacao_financeira=movimentacao.id_movimentacao_financeira,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        valor=movimentacao.valor,
        descricao=movimentacao.descricao,
        id_pagamento=movimentacao.id_pagamento,
        created_at=movimentacao.created_at
    )

@router.get("/pagamento/{pagamento_id}", response_model=list[MovimentacaoFinanceiraPublic])
def list_movimentacoes_by_pagamento(pagamento_id: int):
    """Lista movimentações de um pagamento."""
    logger.info("GET /movimentacoes-financeiras/pagamento/%s", pagamento_id)
    movimentacoes = movimentacao_financeira_service.get_movimentacoes_by_pagamento(pagamento_id)
    return [
        MovimentacaoFinanceiraPublic(
            id_movimentacao_financeira=mov.id_movimentacao_financeira,
            tipo_movimentacao=mov.tipo_movimentacao,
            valor=mov.valor,
            descricao=mov.descricao,
            id_pagamento=mov.id_pagamento,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.post("/periodo/saldo", response_model=SaldoPeriodo)
def calcular_saldo_periodo(data: MovimentacaoFinanceiraPeriodo):
    """Calcula saldo de entradas e saídas em um período."""
    logger.info("POST /movimentacoes-financeiras/periodo/saldo inicio=%s fim=%s", data.data_inicio, data.data_fim)
    saldo = movimentacao_financeira_service.calcular_saldo_periodo(data)
    return SaldoPeriodo(
        entradas=saldo["entradas"],
        saidas=saldo["saidas"],
        saldo=saldo["saldo"]
    )

@router.get("/resumo", response_model=list[ResumoFinanceiro])
def get_resumo_financeiro(
    data_inicio: datetime = Query(default=None),
    data_fim: datetime = Query(default=None)
):
    """Gera resumo financeiro geral ou por período."""
    logger.info("GET /movimentacoes-financeiras/resumo inicio=%s fim=%s", data_inicio, data_fim)
    resumo = movimentacao_financeira_service.get_resumo_financeiro(data_inicio, data_fim)
    return [
        ResumoFinanceiro(
            mes=item["mes"],
            tipo_movimentacao=item["tipo_movimentacao"],
            quantidade=item["quantidade"],
            valor_total=item["valor_total"]
        )
        for item in resumo
    ]
