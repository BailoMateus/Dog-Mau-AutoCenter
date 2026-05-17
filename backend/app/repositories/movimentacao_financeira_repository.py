import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import MovimentacaoFinanceira, dict_to_movimentacao_financeira, movimentacao_financeira_to_dict

logger = logging.getLogger(__name__)

def get_movimentacao_financeira_by_id(movimentacao_id: int):
    """Busca movimentação financeira por ID."""
    query = """
    SELECT id_movimentacao_financeira, tipo_movimentacao, valor, descricao, id_pagamento, created_at
    FROM movimentacao_financeira 
    WHERE id_movimentacao_financeira = %s
    """
    result = execute_query(query, (movimentacao_id,), fetch="one")
    movimentacao = dict_to_movimentacao_financeira(result)
    logger.debug("get_movimentacao_financeira_by_id id=%s found=%s", movimentacao_id, movimentacao is not None)
    return movimentacao

def get_all_movimentacoes_financeiras(limit: int = 100):
    """Lista todas as movimentações financeiras."""
    query = """
    SELECT id_movimentacao_financeira, tipo_movimentacao, valor, descricao, id_pagamento, created_at
    FROM movimentacao_financeira 
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (limit,))
    movimentacoes = [dict_to_movimentacao_financeira(row) for row in results]
    logger.debug("get_all_movimentacoes_financeiras count=%s", len(movimentacoes))
    return movimentacoes

def get_movimentacoes_by_tipo(tipo: str, limit: int = 50):
    """Lista movimentações por tipo (entrada/saida)."""
    query = """
    SELECT id_movimentacao_financeira, tipo_movimentacao, valor, descricao, id_pagamento, created_at
    FROM movimentacao_financeira 
    WHERE tipo_movimentacao = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (tipo, limit))
    movimentacoes = [dict_to_movimentacao_financeira(row) for row in results]
    logger.debug("get_movimentacoes_by_tipo tipo=%s count=%s", tipo, len(movimentacoes))
    return movimentacoes

def get_movimentacoes_by_periodo(data_inicio: datetime, data_fim: datetime, limit: int = 100):
    """Lista movimentações por período."""
    query = """
    SELECT id_movimentacao_financeira, tipo_movimentacao, valor, descricao, id_pagamento, created_at
    FROM movimentacao_financeira 
    WHERE created_at BETWEEN %s AND %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (data_inicio, data_fim, limit))
    movimentacoes = [dict_to_movimentacao_financeira(row) for row in results]
    logger.debug("get_movimentacoes_by_periodo periodo=%s a %s count=%s", data_inicio, data_fim, len(movimentacoes))
    return movimentacoes

def get_movimentacoes_by_pagamento(pagamento_id: int):
    """Lista movimentações de um pagamento."""
    query = """
    SELECT id_movimentacao_financeira, tipo_movimentacao, valor, descricao, id_pagamento, created_at
    FROM movimentacao_financeira 
    WHERE id_pagamento = %s
    ORDER BY created_at DESC
    """
    results = execute_query(query, (pagamento_id,))
    movimentacoes = [dict_to_movimentacao_financeira(row) for row in results]
    logger.debug("get_movimentacoes_by_pagamento pagamento_id=%s count=%s", pagamento_id, len(movimentacoes))
    return movimentacoes

def create_movimentacao_financeira(movimentacao: MovimentacaoFinanceira):
    """Cria uma nova movimentação financeira."""
    query = """
    INSERT INTO movimentacao_financeira (tipo_movimentacao, valor, descricao, id_pagamento)
    VALUES (%s, %s, %s, %s)
    RETURNING id_movimentacao_financeira
    """
    params = (
        movimentacao.tipo_movimentacao, movimentacao.valor, 
        movimentacao.descricao, movimentacao.id_pagamento
    )
    movimentacao_id = execute_insert(query, params)
    movimentacao.id_movimentacao_financeira = movimentacao_id
    movimentacao.created_at = datetime.now(timezone.utc)
    logger.info("movimentação financeira criada id=%s tipo=%s valor=%s", 
                movimentacao.id_movimentacao_financeira, movimentacao.tipo_movimentacao, movimentacao.valor)
    return movimentacao

def check_pagamento_exists(pagamento_id: int):
    """Verifica se pagamento existe."""
    query = """
    SELECT COUNT(*) as count
    FROM pagamento 
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pagamento_id,), fetch="one")
    return result['count'] > 0 if result else False

def registrar_entrada_financeira(valor: float, descricao: str, pagamento_id: int = None):
    """Registra entrada financeira."""
    # Valida pagamento se fornecido
    if pagamento_id and not check_pagamento_exists(pagamento_id):
        logger.warning("pagamento não encontrado pagamento_id=%s", pagamento_id)
        raise ValueError("Pagamento não encontrado")
    
    movimentacao = MovimentacaoFinanceira(
        tipo_movimentacao="entrada",
        valor=valor,
        descricao=descricao,
        id_pagamento=pagamento_id
    )
    
    return create_movimentacao_financeira(movimentacao)

def registrar_saida_financeira(valor: float, descricao: str, pagamento_id: int = None):
    """Registra saída financeira."""
    # Valida pagamento se fornecido
    if pagamento_id and not check_pagamento_exists(pagamento_id):
        logger.warning("pagamento não encontrado pagamento_id=%s", pagamento_id)
        raise ValueError("Pagamento não encontrado")
    
    movimentacao = MovimentacaoFinanceira(
        tipo_movimentacao="saida",
        valor=valor,
        descricao=descricao,
        id_pagamento=pagamento_id
    )
    
    return create_movimentacao_financeira(movimentacao)

def calcular_saldo_periodo(data_inicio: datetime, data_fim: datetime):
    """Calcula saldo de entradas e saídas em um período."""
    query = """
    SELECT 
        tipo_movimentacao,
        COALESCE(SUM(valor), 0) as valor_total
    FROM movimentacao_financeira 
    WHERE created_at BETWEEN %s AND %s
    GROUP BY tipo_movimentacao
    """
    results = execute_query(query, (data_inicio, data_fim))
    
    saldo = {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0}
    
    for row in results:
        if row['tipo_movimentacao'] == 'entrada':
            saldo["entradas"] = float(row['valor_total'])
        elif row['tipo_movimentacao'] == 'saida':
            saldo["saidas"] = float(row['valor_total'])
    
    saldo["saldo"] = saldo["entradas"] - saldo["saidas"]
    
    logger.debug("calcular_saldo_periodo periodo=%s a %s entradas=%s saidas=%s saldo=%s", 
                data_inicio, data_fim, saldo["entradas"], saldo["saidas"], saldo["saldo"])
    
    return saldo

def get_resumo_financeiro(data_inicio: datetime = None, data_fim: datetime = None):
    """Gera resumo financeiro geral ou por período."""
    if not data_inicio:
        data_inicio = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not data_fim:
        data_fim = datetime.now(timezone.utc)
    
    query = """
    SELECT 
        tipo_movimentacao,
        COUNT(*) as quantidade,
        COALESCE(SUM(valor), 0) as valor_total,
        DATE_TRUNC('month', created_at) as mes
    FROM movimentacao_financeira 
    WHERE created_at BETWEEN %s AND %s
    GROUP BY tipo_movimentacao, DATE_TRUNC('month', created_at)
    ORDER BY mes DESC, tipo_movimentacao
    """
    results = execute_query(query, (data_inicio, data_fim))
    
    resumo = []
    for row in results:
        resumo.append({
            "mes": row["mes"].strftime("%Y-%m"),
            "tipo_movimentacao": row["tipo_movimentacao"],
            "quantidade": row["quantidade"],
            "valor_total": float(row["valor_total"])
        })
    
    logger.debug("get_resumo_financeiro periodo=%s a %s resumo_count=%s", 
                data_inicio, data_fim, len(resumo))
    
    return resumo
