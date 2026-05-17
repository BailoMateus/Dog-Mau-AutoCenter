import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.repositories import ordem_servico_repository as os_repo
from app.repositories import os_servico_repository as os_servico_repo
from app.repositories import os_peca_repository as os_peca_repo
from app.repositories import pagamento_repository as pagamento_repo
from app.repositories import movimentacao_financeira_repository as movimentacao_financeira_repo
from app.repositories import peca_repository as peca_repo
from app.repositories import servico_repository as servico_repo
from app.schemas.relatorios_schema import RelatorioPeriodo

logger = logging.getLogger(__name__)

def validate_periodo(data: RelatorioPeriodo):
    """Valida período do relatório."""
    if data.data_inicio >= data.data_fim:
        logger.warning("período inválido inicio=%s fim=%s", data.data_inicio, data.data_fim)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de início deve ser anterior à data de fim"
        )
    
    # Validação de período máximo (1 ano)
    diferenca = data.data_fim - data.data_inicio
    if diferenca.days > 365:
        logger.warning("período muito longo dias=%s", diferenca.days)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Período não pode ser superior a 365 dias"
        )

def gerar_relatorio_faturamento(data: RelatorioPeriodo):
    """Gera relatório de faturamento por período."""
    validate_periodo(data)
    
    # Busca pagamentos confirmados no período
    query = """
    SELECT 
        DATE_TRUNC('month', p.data_pagamento) as mes,
        COUNT(*) as quantidade_pagamentos,
        COALESCE(SUM(p.valor), 0) as valor_total,
        p.forma_pagamento
    FROM pagamento p
    WHERE p.status = 'confirmado' 
    AND p.data_pagamento BETWEEN %s AND %s
    AND p.deleted_at IS NULL
    GROUP BY DATE_TRUNC('month', p.data_pagamento), p.forma_pagamento
    ORDER BY mes DESC, p.forma_pagamento
    """
    
    from app.database.db import execute_query
    results = execute_query(query, (data.data_inicio, data.data_fim))
    
    relatorio = []
    valor_total_geral = 0.0
    quantidade_total = 0
    
    for row in results:
        valor_total = float(row['valor_total'])
        relatorio.append({
            "mes": row["mes"].strftime("%Y-%m"),
            "quantidade_pagamentos": row["quantidade_pagamentos"],
            "valor_total": valor_total,
            "forma_pagamento": row["forma_pagamento"]
        })
        valor_total_geral += valor_total
        quantidade_total += row["quantidade_pagamentos"]
    
    logger.info("relatório faturamento período=%s a %s total=%.2f", 
                data.data_inicio, data.data_fim, valor_total_geral)
    
    return {
        "periodo": {
            "data_inicio": data.data_inicio,
            "data_fim": data.data_fim
        },
        "resumo": {
            "valor_total_geral": valor_total_geral,
            "quantidade_total_pagamentos": quantidade_total
        },
        "detalhes": relatorio
    }

def gerar_relatorio_servicos_realizados(data: RelatorioPeriodo):
    """Gera relatório de serviços realizados por período."""
    validate_periodo(data)
    
    # Busca OS concluídas no período
    query = """
    SELECT 
        DATE_TRUNC('month', os.data_conclusao) as mes,
        COUNT(DISTINCT os.id_os) as quantidade_os,
        COUNT(DISTINCT oss.id_servico) as servicos_diferentes,
        COUNT(oss.id_os_servico) as total_servicos,
        COALESCE(SUM(oss.quantidade * s.valor), 0) as valor_total_servicos
    FROM ordem_servico os
    JOIN os_servico oss ON os.id_os = oss.id_os
    JOIN servico s ON oss.id_servico = s.id_servico
    WHERE os.status = 'concluida'
    AND os.data_conclusao BETWEEN %s AND %s
    AND os.deleted_at IS NULL
    GROUP BY DATE_TRUNC('month', os.data_conclusao)
    ORDER BY mes DESC
    """
    
    from app.database.db import execute_query
    results = execute_query(query, (data.data_inicio, data.data_fim))
    
    relatorio = []
    valor_total_geral = 0.0
    os_total = 0
    servicos_total = 0
    
    for row in results:
        valor_total = float(row['valor_total_servicos'])
        relatorio.append({
            "mes": row["mes"].strftime("%Y-%m"),
            "quantidade_os": row["quantidade_os"],
            "servicos_diferentes": row["servicos_diferentes"],
            "total_servicos": row["total_servicos"],
            "valor_total_servicos": valor_total
        })
        valor_total_geral += valor_total
        os_total += row["quantidade_os"]
        servicos_total += row["total_servicos"]
    
    logger.info("relatório serviços realizados período=%s a %s os=%s servicos=%s", 
                data.data_inicio, data.data_fim, os_total, servicos_total)
    
    return {
        "periodo": {
            "data_inicio": data.data_inicio,
            "data_fim": data.data_fim
        },
        "resumo": {
            "valor_total_geral": valor_total_geral,
            "quantidade_total_os": os_total,
            "quantidade_total_servicos": servicos_total
        },
        "detalhes": relatorio
    }

def gerar_relatorio_estoque():
    """Gera relatório de estoque atual."""
    # Busca informações de estoque
    query = """
    SELECT 
        p.id_peca,
        p.nome,
        p.estoque_atual,
        p.valor_unitario,
        COALESCE(p.estoque_atual * p.valor_unitario, 0) as valor_total_estoque,
        CASE 
            WHEN p.estoque_atual <= 5 THEN 'baixo'
            WHEN p.estoque_atual <= 10 THEN 'medio'
            ELSE 'alto'
        END as nivel_estoque
    FROM peca p
    WHERE p.deleted_at IS NULL
    ORDER BY nivel_estoque, p.estoque_atual ASC
    """
    
    from app.database.db import execute_query
    results = execute_query(query)
    
    relatorio = []
    valor_total_geral = 0.0
    pecas_baixo_estoque = 0
    
    for row in results:
        valor_total = float(row['valor_total_estoque'])
        relatorio.append({
            "id_peca": row["id_peca"],
            "nome": row["nome"],
            "estoque_atual": row["estoque_atual"],
            "valor_unitario": float(row["valor_unitario"]),
            "valor_total_estoque": valor_total,
            "nivel_estoque": row["nivel_estoque"]
        })
        valor_total_geral += valor_total
        if row["nivel_estoque"] == "baixo":
            pecas_baixo_estoque += 1
    
    logger.info("relatório estoque total_pecas=%s valor_total=%.2f baixo_estoque=%s", 
                len(relatorio), valor_total_geral, pecas_baixo_estoque)
    
    return {
        "data_geracao": datetime.now(timezone.utc),
        "resumo": {
            "quantidade_pecas": len(relatorio),
            "valor_total_geral": valor_total_geral,
            "pecas_baixo_estoque": pecas_baixo_estoque
        },
        "detalhes": relatorio
    }

def gerar_relatorio_ordens_servico(data: RelatorioPeriodo):
    """Gera relatório de ordens de serviço por período."""
    validate_periodo(data)
    
    # Busca OS por status e período
    query = """
    SELECT 
        DATE_TRUNC('month', os.created_at) as mes,
        os.status,
        COUNT(*) as quantidade,
        COALESCE(
            (
                SELECT COALESCE(SUM(oss.quantidade * s.valor), 0)
                FROM os_servico oss
                JOIN servico s ON oss.id_servico = s.id_servico
                WHERE oss.id_os = os.id_os
            ) + 
            (
                SELECT COALESCE(SUM(osp.quantidade * p.valor_unitario), 0)
                FROM os_peca osp
                JOIN peca p ON osp.id_peca = p.id_peca
                WHERE osp.id_os = os.id_os
            ), 0
        ) as valor_total
    FROM ordem_servico os
    WHERE os.created_at BETWEEN %s AND %s
    AND os.deleted_at IS NULL
    GROUP BY DATE_TRUNC('month', os.created_at), os.status
    ORDER BY mes DESC, os.status
    """
    
    from app.database.db import execute_query
    results = execute_query(query, (data.data_inicio, data.data_fim))
    
    relatorio = []
    valor_total_geral = 0.0
    os_total = 0
    
    for row in results:
        valor_total = float(row['valor_total'])
        relatorio.append({
            "mes": row["mes"].strftime("%Y-%m"),
            "status": row["status"],
            "quantidade": row["quantidade"],
            "valor_total": valor_total
        })
        valor_total_geral += valor_total
        os_total += row["quantidade"]
    
    logger.info("relatório ordens serviço período=%s a %s os=%s valor=%.2f", 
                data.data_inicio, data.data_fim, os_total, valor_total_geral)
    
    return {
        "periodo": {
            "data_inicio": data.data_inicio,
            "data_fim": data.data_fim
        },
        "resumo": {
            "quantidade_total_os": os_total,
            "valor_total_geral": valor_total_geral
        },
        "detalhes": relatorio
    }

def gerar_relatorio_financeiro_periodo(data: RelatorioPeriodo):
    """Gera relatório financeiro completo por período."""
    validate_periodo(data)
    
    # Reutiliza função existente de movimentações financeiras
    from app.services.movimentacao_financeira_service import get_resumo_financeiro
    
    # Busca resumo financeiro
    resumo = get_resumo_financeira(data.data_inicio, data.data_fim)
    
    # Busca saldo do período
    from app.services.movimentacao_financeira_service import calcular_saldo_periodo
    saldo_info = calcular_saldo_periodo(data)
    
    # Busca resumo de pagamentos
    query = """
    SELECT 
        DATE_TRUNC('month', p.created_at) as mes,
        p.status,
        COUNT(*) as quantidade,
        COALESCE(SUM(p.valor), 0) as valor_total
    FROM pagamento p
    WHERE p.created_at BETWEEN %s AND %s
    AND p.deleted_at IS NULL
    GROUP BY DATE_TRUNC('month', p.created_at), p.status
    ORDER BY mes DESC, p.status
    """
    
    from app.database.db import execute_query
    pagamentos_results = execute_query(query, (data.data_inicio, data.data_fim))
    
    pagamentos = []
    for row in pagamentos_results:
        pagamentos.append({
            "mes": row["mes"].strftime("%Y-%m"),
            "status": row["status"],
            "quantidade": row["quantidade"],
            "valor_total": float(row["valor_total"])
        })
    
    logger.info("relatório financeiro período=%s a %s saldo=%.2f", 
                data.data_inicio, data.data_fim, saldo_info["saldo"])
    
    return {
        "periodo": {
            "data_inicio": data.data_inicio,
            "data_fim": data.data_fim
        },
        "movimentacoes_financeiras": resumo,
        "saldo_periodo": {
            "entradas": saldo_info["entradas"],
            "saidas": saldo_info["saidas"],
            "saldo": saldo_info["saldo"]
        },
        "pagamentos": pagamentos
    }

def gerar_relatorio_completo(data: RelatorioPeriodo):
    """Gera relatório completo com todos os dados."""
    validate_periodo(data)
    
    logger.info("gerando relatório completo período=%s a %s", data.data_inicio, data.data_fim)
    
    return {
        "periodo": {
            "data_inicio": data.data_inicio,
            "data_fim": data.data_fim
        },
        "faturamento": gerar_relatorio_faturamento(data)["resumo"],
        "servicos_realizados": gerar_relatorio_servicos_realizados(data)["resumo"],
        "ordens_servico": gerar_relatorio_ordens_servico(data)["resumo"],
        "financeiro": gerar_relatorio_financeiro_periodo(data)["saldo_periodo"],
        "estoque_atual": gerar_relatorio_estoque()["resumo"]
    }
