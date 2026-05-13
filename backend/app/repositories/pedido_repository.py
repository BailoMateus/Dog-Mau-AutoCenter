import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Pedido, dict_to_pedido, pedido_to_dict

logger = logging.getLogger(__name__)

def get_pedido_by_id(pedido_id: int):
    """Busca pedido por ID."""
    query = """
    SELECT id_pedido, id_cliente, valor_total, status, 
           created_at, updated_at, deleted_at
    FROM pedido 
    WHERE id_pedido = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id,), fetch="one")
    pedido = dict_to_pedido(result)
    logger.debug("get_pedido_by_id id=%s found=%s", pedido_id, pedido is not None)
    return pedido

def get_all_pedidos():
    """Lista todos os pedidos."""
    query = """
    SELECT id_pedido, id_cliente, valor_total, status, 
           created_at, updated_at, deleted_at
    FROM pedido 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query)
    pedidos = [dict_to_pedido(row) for row in results]
    logger.debug("get_all_pedidos count=%s", len(pedidos))
    return pedidos

def get_pedidos_by_cliente(cliente_id: int):
    """Lista pedidos de um cliente."""
    query = """
    SELECT id_pedido, id_cliente, valor_total, status, 
           created_at, updated_at, deleted_at
    FROM pedido 
    WHERE id_cliente = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (cliente_id,))
    pedidos = [dict_to_pedido(row) for row in results]
    logger.debug("get_pedidos_by_cliente cliente_id=%s count=%s", cliente_id, len(pedidos))
    return pedidos

def create_pedido(pedido: Pedido):
    """Cria um novo pedido."""
    query = """
    INSERT INTO pedido (id_cliente, valor_total, status)
    VALUES (%s, %s, %s)
    RETURNING id_pedido
    """
    params = (
        pedido.id_cliente, pedido.valor_total, pedido.status
    )
    pedido_id = execute_insert(query, params)
    pedido.id_pedido = pedido_id
    logger.info("pedido criado id=%s cliente=%s valor=%s", pedido.id_pedido, pedido.id_cliente, pedido.valor_total)
    return pedido

def update_pedido(pedido: Pedido):
    """Atualiza um pedido."""
    query = """
    UPDATE pedido 
    SET id_cliente = %s, valor_total = %s, status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pedido = %s AND deleted_at IS NULL
    """
    params = (
        pedido.id_cliente, pedido.valor_total, pedido.status, pedido.id_pedido
    )
    execute_command(query, params)
    logger.info("pedido atualizado id=%s", pedido.id_pedido)
    return pedido

def soft_delete_pedido(pedido: Pedido):
    """Soft delete de pedido."""
    query = """
    UPDATE pedido 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pedido = %s
    """
    params = (datetime.now(timezone.utc), pedido.id_pedido)
    execute_command(query, params)
    pedido.deleted_at = datetime.now(timezone.utc)
    logger.info("pedido soft-delete id=%s", pedido.id_pedido)
    return pedido

def check_cliente_exists(cliente_id: int):
    """Verifica se cliente existe."""
    query = """
    SELECT COUNT(*) as count
    FROM usuario 
    WHERE id_usuario = %s AND deleted_at IS NULL AND ativo = TRUE
    """
    result = execute_query(query, (cliente_id,), fetch="one")
    return result['count'] > 0 if result else False
