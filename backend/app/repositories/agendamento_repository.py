import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Agendamento, dict_to_agendamento, agendamento_to_dict

logger = logging.getLogger(__name__)

def get_agendamento_by_id(agendamento_id: int):
    """Busca agendamento por ID."""
    query = """
    SELECT id_agendamento, id_usuario, id_veiculo, data_agendamento, descricao, status,
           created_at, updated_at, deleted_at
    FROM agendamento 
    WHERE id_agendamento = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (agendamento_id,), fetch="one")
    agendamento = dict_to_agendamento(result)
    logger.debug("get_agendamento_by_id id=%s found=%s", agendamento_id, agendamento is not None)
    return agendamento

def get_all_agendamentos():
    """Lista todos os agendamentos."""
    query = """
    SELECT id_agendamento, id_usuario, id_veiculo, data_agendamento, descricao, status,
           created_at, updated_at, deleted_at
    FROM agendamento 
    WHERE deleted_at IS NULL
    ORDER BY data_agendamento ASC
    """
    results = execute_query(query)
    agendamentos = [dict_to_agendamento(row) for row in results]
    logger.debug("get_all_agendamentos count=%s", len(agendamentos))
    return agendamentos



def get_agendamentos_by_veiculo(veiculo_id: int):
    """Lista agendamentos de um veículo."""
    query = """
    SELECT id_agendamento, id_usuario, id_veiculo, data_agendamento, descricao, status,
           created_at, updated_at, deleted_at
    FROM agendamento 
    WHERE id_veiculo = %s AND deleted_at IS NULL
    ORDER BY data_agendamento ASC
    """
    results = execute_query(query, (veiculo_id,))
    agendamentos = [dict_to_agendamento(row) for row in results]
    logger.debug("get_agendamentos_by_veiculo veiculo_id=%s count=%s", veiculo_id, len(agendamentos))
    return agendamentos

def create_agendamento(agendamento: Agendamento):
    """Cria um novo agendamento."""
    query = """
    INSERT INTO agendamento (id_usuario, id_veiculo, data_agendamento, descricao, status)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_agendamento
    """
    params = (
        agendamento.id_usuario, agendamento.id_veiculo, 
        agendamento.data_agendamento, agendamento.descricao, agendamento.status
    )
    agendamento_id = execute_insert(query, params)
    agendamento.id_agendamento = agendamento_id
    logger.info("agendamento criado id=%s usuario=%s veiculo=%s", 
                agendamento.id_agendamento, agendamento.id_usuario, agendamento.id_veiculo)
    return agendamento

def update_agendamento(agendamento: Agendamento):
    """Atualiza um agendamento."""
    query = """
    UPDATE agendamento 
    SET id_usuario = %s, id_veiculo = %s, data_agendamento = %s, descricao = %s, 
        status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_agendamento = %s AND deleted_at IS NULL
    """
    params = (
        agendamento.id_usuario, agendamento.id_veiculo, agendamento.data_agendamento,
        agendamento.descricao, agendamento.status, agendamento.id_agendamento
    )
    execute_command(query, params)
    logger.info("agendamento atualizado id=%s", agendamento.id_agendamento)
    return agendamento

def update_data_agendamento(agendamento_id: int, nova_data: datetime):
    """Atualiza apenas a data do agendamento."""
    query = """
    UPDATE agendamento 
    SET data_agendamento = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_agendamento = %s AND deleted_at IS NULL
    """
    params = (nova_data, agendamento_id)
    execute_command(query, params)
    logger.info("data do agendamento atualizada id=%s nova_data=%s", agendamento_id, nova_data)

def update_status_agendamento(agendamento_id: int, novo_status: str):
    """Atualiza apenas o status do agendamento."""
    query = """
    UPDATE agendamento 
    SET status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_agendamento = %s AND deleted_at IS NULL
    """
    params = (novo_status, agendamento_id)
    execute_command(query, params)
    logger.info("status do agendamento atualizado id=%s novo_status=%s", agendamento_id, novo_status)

def soft_delete_agendamento(agendamento: Agendamento):
    """Soft delete de agendamento."""
    query = """
    UPDATE agendamento 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_agendamento = %s
    """
    params = (datetime.now(timezone.utc), agendamento.id_agendamento)
    execute_command(query, params)
    agendamento.deleted_at = datetime.now(timezone.utc)
    logger.info("agendamento soft-delete id=%s", agendamento.id_agendamento)
    return agendamento

def cancelar_agendamento(agendamento_id: int):
    """Cancela um agendamento (muda status para cancelado)."""
    update_status_agendamento(agendamento_id, "cancelado")
    logger.info("agendamento cancelado id=%s", agendamento_id)

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
