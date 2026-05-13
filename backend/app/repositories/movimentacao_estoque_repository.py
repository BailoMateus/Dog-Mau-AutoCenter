import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import MovimentacaoEstoque, dict_to_movimentacao_estoque, movimentacao_estoque_to_dict

logger = logging.getLogger(__name__)

def create_movimentacao_estoque(movimentacao: MovimentacaoEstoque):
    """Cria uma nova movimentação de estoque."""
    query = """
    INSERT INTO movimentacao_estoque (id_peca, tipo_movimentacao, quantidade, motivo)
    VALUES (%s, %s, %s, %s)
    RETURNING id_movimentacao
    """
    params = (
        movimentacao.id_peca, movimentacao.tipo_movimentacao, 
        movimentacao.quantidade, movimentacao.motivo
    )
    movimentacao_id = execute_insert(query, params)
    movimentacao.id_movimentacao = movimentacao_id
    movimentacao.created_at = datetime.now(timezone.utc)
    logger.info("movimentação de estoque criada id=%s peca=%s tipo=%s quantidade=%s", 
                movimentacao.id_movimentacao, movimentacao.id_peca, 
                movimentacao.tipo_movimentacao, movimentacao.quantidade)
    return movimentacao

def get_movimentacoes_by_peca(peca_id: int, limit: int = 50):
    """Lista movimentações de uma peça."""
    query = """
    SELECT id_movimentacao, id_peca, tipo_movimentacao, quantidade, motivo, created_at
    FROM movimentacao_estoque 
    WHERE id_peca = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (peca_id, limit))
    movimentacoes = [dict_to_movimentacao_estoque(row) for row in results]
    logger.debug("get_movimentacoes_by_peca peca_id=%s count=%s", peca_id, len(movimentacoes))
    return movimentacoes

def get_all_movimentacoes(limit: int = 100):
    """Lista todas as movimentações de estoque."""
    query = """
    SELECT id_movimentacao, id_peca, tipo_movimentacao, quantidade, motivo, created_at
    FROM movimentacao_estoque 
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (limit,))
    movimentacoes = [dict_to_movimentacao_estoque(row) for row in results]
    logger.debug("get_all_movimentacoes count=%s", len(movimentacoes))
    return movimentacoes

def get_movimentacoes_by_tipo(tipo: str, limit: int = 50):
    """Lista movimentações por tipo (entrada/saida)."""
    query = """
    SELECT id_movimentacao, id_peca, tipo_movimentacao, quantidade, motivo, created_at
    FROM movimentacao_estoque 
    WHERE tipo_movimentacao = %s
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (tipo, limit))
    movimentacoes = [dict_to_movimentacao_estoque(row) for row in results]
    logger.debug("get_movimentacoes_by_tipo tipo=%s count=%s", tipo, len(movimentacoes))
    return movimentacoes

def get_ultima_movimentacao_peca(peca_id: int):
    """Busca última movimentação de uma peça."""
    query = """
    SELECT id_movimentacao, id_peca, tipo_movimentacao, quantidade, motivo, created_at
    FROM movimentacao_estoque 
    WHERE id_peca = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    result = execute_query(query, (peca_id,), fetch="one")
    return dict_to_movimentacao_estoque(result) if result else None

def registrar_saida_estoque(peca_id: int, quantidade: int, motivo: str = ""):
    """Registra saída de estoque."""
    # Buscar estoque atual
    from app.repositories.os_peca_repository import get_peca_estoque
    estoque_anterior = get_peca_estoque(peca_id)
    
    # Validar estoque suficiente
    if estoque_anterior < quantidade:
        logger.error("estoque insuficiente peca=%s estoque=%s saida=%s", 
                    peca_id, estoque_anterior, quantidade)
        raise ValueError(f"Estoque insuficiente. Disponível: {estoque_anterior}, Solicitado: {quantidade}")
    
    # Calcular novo estoque
    estoque_posterior = estoque_anterior - quantidade
    
    # Criar movimentação
    movimentacao = MovimentacaoEstoque(
        id_peca=peca_id,
        tipo_movimentacao="saida",
        quantidade=quantidade,
        motivo=motivo or "Saída manual"
    )
    
    # Atualizar estoque da peça
    from app.repositories.os_peca_repository import update_peca_estoque
    update_peca_estoque(peca_id, estoque_posterior)
    
    # Criar registro de movimentação
    return create_movimentacao_estoque(movimentacao)

def registrar_entrada_estoque(peca_id: int, quantidade: int, motivo: str = ""):
    """Registra entrada de estoque."""
    # Buscar estoque atual
    from app.repositories.os_peca_repository import get_peca_estoque
    estoque_anterior = get_peca_estoque(peca_id)
    
    # Calcular novo estoque
    estoque_posterior = estoque_anterior + quantidade
    
    # Criar movimentação
    movimentacao = MovimentacaoEstoque(
        id_peca=peca_id,
        tipo_movimentacao="entrada",
        quantidade=quantidade,
        motivo=motivo or "Entrada manual"
    )
    
    # Atualizar estoque da peça
    from app.repositories.os_peca_repository import update_peca_estoque
    update_peca_estoque(peca_id, estoque_posterior)
    
    # Criar registro de movimentação
    return create_movimentacao_estoque(movimentacao)

def get_historico_estoque(peca_id: int, dias: int = 30):
    """Busca histórico de estoque de uma peça nos últimos dias."""
    query = """
    SELECT id_movimentacao, id_peca, tipo_movimentacao, quantidade, motivo, created_at
    FROM movimentacao_estoque 
    WHERE id_peca = %s AND created_at >= CURRENT_DATE - INTERVAL '%s days'
    ORDER BY created_at DESC
    """
    results = execute_query(query, (peca_id, dias))
    movimentacoes = [dict_to_movimentacao_estoque(row) for row in results]
    logger.debug("get_historico_estoque peca_id=%s dias=%s count=%s", peca_id, dias, len(movimentacoes))
    return movimentacoes
