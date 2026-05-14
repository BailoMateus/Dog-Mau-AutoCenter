import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Orcamento, dict_to_orcamento, orcamento_to_dict

logger = logging.getLogger(__name__)

def get_orcamento_by_id(orcamento_id: int):
    """Busca orçamento por ID."""
    query = """
    SELECT id_orcamento, id_usuario, id_veiculo, status, valor_total,
           created_at, updated_at, deleted_at
    FROM orcamento 
    WHERE id_orcamento = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (orcamento_id,), fetch="one")
    orcamento = dict_to_orcamento(result)
    logger.debug("get_orcamento_by_id id=%s found=%s", orcamento_id, orcamento is not None)
    return orcamento

def get_all_orcamentos():
    """Lista todos os orçamentos."""
    query = """
    SELECT id_orcamento, id_usuario, id_veiculo, status, valor_total,
           created_at, updated_at, deleted_at
    FROM orcamento 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query)
    orcamentos = [dict_to_orcamento(row) for row in results]
    logger.debug("get_all_orcamentos count=%s", len(orcamentos))
    return orcamentos

def get_orcamentos_by_usuario(usuario_id: int):
    """Lista orçamentos de um usuario."""
    query = """
    SELECT id_orcamento, id_usuario, id_veiculo, status, valor_total,
           created_at, updated_at, deleted_at
    FROM orcamento 
    WHERE id_usuario = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (usuario_id,))
    orcamentos = [dict_to_orcamento(row) for row in results]
    logger.debug("get_orcamentos_by_usuario usuario_id=%s count=%s", usuario_id, len(orcamentos))
    return orcamentos

def get_orcamentos_by_veiculo(veiculo_id: int):
    """Lista orçamentos de um veículo."""
    query = """
    SELECT id_orcamento, id_usuario, id_veiculo, status, valor_total,
           created_at, updated_at, deleted_at
    FROM orcamento 
    WHERE id_veiculo = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (veiculo_id,))
    orcamentos = [dict_to_orcamento(row) for row in results]
    logger.debug("get_orcamentos_by_veiculo veiculo_id=%s count=%s", veiculo_id, len(orcamentos))
    return orcamentos

def create_orcamento(orcamento: Orcamento):
    """Cria um novo orçamento."""
    query = """
    INSERT INTO orcamento (id_usuario, id_veiculo, status, valor_total)
    VALUES (%s, %s, %s, %s)
    RETURNING id_orcamento
    """
    params = (
        orcamento.id_usuario, orcamento.id_veiculo, 
        orcamento.status, orcamento.valor_total
    )
    orcamento_id = execute_insert(query, params)
    orcamento.id_orcamento = orcamento_id
    logger.info("orcamento criado id=%s usuario=%s veiculo=%s", 
                orcamento.id_orcamento, orcamento.id_usuario, orcamento.id_veiculo)
    return orcamento

def update_orcamento(orcamento: Orcamento):
    """Atualiza um orçamento."""
    query = """
    UPDATE orcamento 
    SET id_usuario = %s, id_veiculo = %s, status = %s, valor_total = %s, 
        updated_at = CURRENT_TIMESTAMP
    WHERE id_orcamento = %s AND deleted_at IS NULL
    """
    params = (
        orcamento.id_usuario, orcamento.id_veiculo, orcamento.status, 
        orcamento.valor_total, orcamento.id_orcamento
    )
    execute_command(query, params)
    logger.info("orcamento atualizado id=%s", orcamento.id_orcamento)
    return orcamento

def update_status_orcamento(orcamento_id: int, novo_status: str):
    """Atualiza apenas o status do orçamento."""
    query = """
    UPDATE orcamento 
    SET status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_orcamento = %s AND deleted_at IS NULL
    """
    params = (novo_status, orcamento_id)
    execute_command(query, params)
    logger.info("status do orçamento atualizado id=%s novo_status=%s", orcamento_id, novo_status)

def update_valor_total_orcamento(orcamento_id: int, novo_valor_total: float):
    """Atualiza apenas o valor total do orçamento."""
    query = """
    UPDATE orcamento 
    SET valor_total = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_orcamento = %s AND deleted_at IS NULL
    """
    params = (novo_valor_total, orcamento_id)
    execute_command(query, params)
    logger.info("valor total do orçamento atualizado id=%s novo_valor=%s", orcamento_id, novo_valor_total)

def soft_delete_orcamento(orcamento: Orcamento):
    """Soft delete de orçamento."""
    query = """
    UPDATE orcamento 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_orcamento = %s
    """
    params = (datetime.now(timezone.utc), orcamento.id_orcamento)
    execute_command(query, params)
    orcamento.deleted_at = datetime.now(timezone.utc)
    logger.info("orcamento soft-delete id=%s", orcamento.id_orcamento)
    return orcamento

def check_usuario_exists(usuario_id: int):
    """Verifica se usuario existe."""
    query = """
    SELECT COUNT(*) as count
    FROM usuario 
    WHERE id_usuario = %s AND deleted_at IS NULL AND ativo = TRUE
    """
    result = execute_query(query, (usuario_id,), fetch="one")
    return result['count'] > 0 if result else False

def check_veiculo_exists(veiculo_id: int):
    """Verifica se veículo existe."""
    query = """
    SELECT COUNT(*) as count
    FROM veiculo 
    WHERE id_veiculo = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (veiculo_id,), fetch="one")
    return result['count'] > 0 if result else False

def check_veiculo_pertence_usuario(veiculo_id: int, usuario_id: int):
    """Verifica se veículo pertence ao usuario."""
    query = """
    SELECT COUNT(*) as count
    FROM veiculo 
    WHERE id_veiculo = %s AND id_usuario = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (veiculo_id, usuario_id), fetch="one")
    return result['count'] > 0 if result else False
