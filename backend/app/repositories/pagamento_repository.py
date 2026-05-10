import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Pagamento, dict_to_pagamento, pagamento_to_dict

logger = logging.getLogger(__name__)

def get_pagamento_by_id(pagamento_id: int):
    """Busca pagamento por ID."""
    query = """
    SELECT id_pagamento, id_os, valor, forma_pagamento, status, data_pagamento, 
           created_at, updated_at, deleted_at
    FROM pagamento 
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pagamento_id,), fetch="one")
    pagamento = dict_to_pagamento(result)
    logger.debug("get_pagamento_by_id id=%s found=%s", pagamento_id, pagamento is not None)
    return pagamento

def get_pagamentos_by_os(os_id: int):
    """Lista todos os pagamentos de uma OS."""
    query = """
    SELECT id_pagamento, id_os, valor, forma_pagamento, status, data_pagamento, 
           created_at, updated_at, deleted_at
    FROM pagamento 
    WHERE id_os = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (os_id,))
    pagamentos = [dict_to_pagamento(row) for row in results]
    logger.debug("get_pagamentos_by_os os_id=%s count=%s", os_id, len(pagamentos))
    return pagamentos

def get_all_pagamentos(limit: int = 100):
    """Lista todos os pagamentos."""
    query = """
    SELECT id_pagamento, id_os, valor, forma_pagamento, status, data_pagamento, 
           created_at, updated_at, deleted_at
    FROM pagamento 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (limit,))
    pagamentos = [dict_to_pagamento(row) for row in results]
    logger.debug("get_all_pagamentos count=%s", len(pagamentos))
    return pagamentos

def create_pagamento(pagamento: Pagamento):
    """Cria um novo pagamento."""
    query = """
    INSERT INTO pagamento (id_os, valor, forma_pagamento, status)
    VALUES (%s, %s, %s, %s)
    RETURNING id_pagamento
    """
    params = (
        pagamento.id_os, pagamento.valor, pagamento.forma_pagamento, pagamento.status
    )
    pagamento_id = execute_insert(query, params)
    pagamento.id_pagamento = pagamento_id
    pagamento.created_at = datetime.now(timezone.utc)
    logger.info("pagamento criado id=%s os=%s valor=%s forma=%s", 
                pagamento.id_pagamento, pagamento.id_os, pagamento.valor, pagamento.forma_pagamento)
    return pagamento

def update_pagamento(pagamento: Pagamento):
    """Atualiza um pagamento existente."""
    query = """
    UPDATE pagamento 
    SET valor = %s, forma_pagamento = %s, status = %s, data_pagamento = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    params = (
        pagamento.valor, pagamento.forma_pagamento, pagamento.status, 
        pagamento.data_pagamento, pagamento.id_pagamento
    )
    execute_command(query, params)
    logger.info("pagamento atualizado id=%s valor=%s status=%s", 
                pagamento.id_pagamento, pagamento.valor, pagamento.status)
    return pagamento

def update_status_pagamento(pagamento_id: int, novo_status: str):
    """Atualiza apenas o status de um pagamento."""
    data_pagamento = None
    if novo_status == "confirmado":
        data_pagamento = datetime.now(timezone.utc)
    
    query = """
    UPDATE pagamento 
    SET status = %s, data_pagamento = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    params = (novo_status, data_pagamento, pagamento_id)
    execute_command(query, params)
    logger.info("status pagamento atualizado id=%s novo_status=%s data_pagamento=%s", 
                pagamento_id, novo_status, data_pagamento)
    
    # Retorna o pagamento atualizado
    return get_pagamento_by_id(pagamento_id)

def soft_delete_pagamento(pagamento_id: int):
    """Remove um pagamento (soft delete)."""
    query = """
    UPDATE pagamento 
    SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    params = (pagamento_id,)
    execute_command(query, params)
    logger.info("pagamento removido id=%s", pagamento_id)

def check_pagamento_exists(pagamento_id: int):
    """Verifica se pagamento existe."""
    query = """
    SELECT COUNT(*) as count
    FROM pagamento 
    WHERE id_pagamento = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pagamento_id,), fetch="one")
    return result['count'] > 0 if result else False

def check_os_exists(os_id: int):
    """Verifica se OS existe."""
    query = """
    SELECT COUNT(*) as count
    FROM ordem_servico 
    WHERE id_os = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (os_id,), fetch="one")
    return result['count'] > 0 if result else False

def get_pagamentos_by_status(status: str, limit: int = 50):
    """Lista pagamentos por status."""
    query = """
    SELECT id_pagamento, id_os, valor, forma_pagamento, status, data_pagamento, 
           created_at, updated_at, deleted_at
    FROM pagamento 
    WHERE status = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT %s
    """
    results = execute_query(query, (status, limit))
    pagamentos = [dict_to_pagamento(row) for row in results]
    logger.debug("get_pagamentos_by_status status=%s count=%s", status, len(pagamentos))
    return pagamentos

def calcular_total_pagamentos_os(os_id: int):
    """Calcula valor total de pagamentos de uma OS."""
    query = """
    SELECT COALESCE(SUM(valor), 0) as valor_total
    FROM pagamento 
    WHERE id_os = %s AND status = 'confirmado' AND deleted_at IS NULL
    """
    result = execute_query(query, (os_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
