import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import OrdemServico, dict_to_ordem_servico, ordem_servico_to_dict

logger = logging.getLogger(__name__)

def get_ordem_servico_by_id(ordem_servico_id: int):
    """Busca ordem de serviço por ID."""
    query = """
    SELECT id_os, id_veiculo, id_mecanico, descricao_problema, status, data_abertura,
           data_conclusao, created_at, updated_at, deleted_at
    FROM ordem_servico 
    WHERE id_os = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (ordem_servico_id,), fetch="one")
    ordem = dict_to_ordem_servico(result)
    logger.debug("get_ordem_servico_by_id id=%s found=%s", ordem_servico_id, ordem is not None)
    return ordem

def get_all_ordens_servico():
    """Lista todas as ordens de serviço."""
    query = """
    SELECT id_os, id_veiculo, id_mecanico, descricao_problema, status, data_abertura,
           data_conclusao, created_at, updated_at, deleted_at
    FROM ordem_servico 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query)
    ordens = [dict_to_ordem_servico(row) for row in results]
    logger.debug("get_all_ordens_servico count=%s", len(ordens))
    return ordens

def get_ordens_by_status(status: str):
    """Lista ordens de serviço por status."""
    query = """
    SELECT id_os, id_veiculo, id_mecanico, descricao_problema, status, data_abertura,
           data_conclusao, created_at, updated_at, deleted_at
    FROM ordem_servico 
    WHERE status = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (status,))
    ordens = [dict_to_ordem_servico(row) for row in results]
    logger.debug("get_ordens_by_status status=%s count=%s", status, len(ordens))
    return ordens

def get_ordens_by_veiculo(veiculo_id: int):
    """Lista ordens de serviço de um veículo."""
    query = """
    SELECT id_os, id_veiculo, id_mecanico, descricao_problema, status, data_abertura,
           data_conclusao, created_at, updated_at, deleted_at
    FROM ordem_servico 
    WHERE id_veiculo = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (veiculo_id,))
    ordens = [dict_to_ordem_servico(row) for row in results]
    logger.debug("get_ordens_by_veiculo veiculo_id=%s count=%s", veiculo_id, len(ordens))
    return ordens

def create_ordem_servico(ordem_servico: OrdemServico):
    """Cria uma nova ordem de serviço."""
    query = """
    INSERT INTO ordem_servico (id_veiculo, id_mecanico, descricao_problema, status, data_abertura)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_os
    """
    params = (
        ordem_servico.id_veiculo, ordem_servico.id_mecanico,
        ordem_servico.descricao_problema, ordem_servico.status, ordem_servico.data_abertura
    )
    ordem_servico_id = execute_insert(query, params)
    ordem_servico.id_os = ordem_servico_id
    logger.info("ordem de serviço criada id=%s veiculo=%s mecanico=%s", 
                ordem_servico.id_os, ordem_servico.id_veiculo, ordem_servico.id_mecanico)
    return ordem_servico

def update_ordem_servico(ordem_servico: OrdemServico):
    """Atualiza uma ordem de serviço."""
    query = """
    UPDATE ordem_servico 
    SET id_veiculo = %s, id_mecanico = %s, descricao_problema = %s, status = %s, 
        data_conclusao = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_os = %s AND deleted_at IS NULL
    """
    params = (
        ordem_servico.id_veiculo, ordem_servico.id_mecanico, ordem_servico.descricao_problema,
        ordem_servico.status, ordem_servico.data_conclusao, ordem_servico.id_os
    )
    execute_command(query, params)
    logger.info("ordem de serviço atualizada id=%s", ordem_servico.id_os)
    return ordem_servico

def update_status_ordem_servico(ordem_servico_id: int, novo_status: str):
    """Atualiza apenas o status da ordem de serviço."""
    query = """
    UPDATE ordem_servico 
    SET status = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_os = %s AND deleted_at IS NULL
    """
    params = (novo_status, ordem_servico_id)
    execute_command(query, params)
    logger.info("status da ordem de serviço atualizado id=%s novo_status=%s", ordem_servico_id, novo_status)

def iniciar_ordem_servico(ordem_servico_id: int):
    """Inicia uma ordem de serviço."""
    query = """
    UPDATE ordem_servico 
    SET status = 'em_andamento', updated_at = CURRENT_TIMESTAMP
    WHERE id_os = %s AND deleted_at IS NULL
    """
    execute_command(query, (ordem_servico_id,))
    logger.info("ordem de serviço iniciada id=%s", ordem_servico_id)

def concluir_ordem_servico(ordem_servico_id: int):
    """Conclui uma ordem de serviço."""
    query = """
    UPDATE ordem_servico 
    SET status = 'concluida', data_conclusao = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
    WHERE id_os = %s AND deleted_at IS NULL
    """
    execute_command(query, (ordem_servico_id,))
    logger.info("ordem de serviço concluída id=%s", ordem_servico_id)

def soft_delete_ordem_servico(ordem_servico: OrdemServico):
    """Soft delete de ordem de serviço."""
    query = """
    UPDATE ordem_servico 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_os = %s
    """
    params = (datetime.now(timezone.utc), ordem_servico.id_os)
    execute_command(query, params)
    ordem_servico.deleted_at = datetime.now(timezone.utc)
    logger.info("ordem de serviço soft-delete id=%s", ordem_servico.id_os)
    return ordem_servico

def check_veiculo_exists(veiculo_id: int):
    """Verifica se veículo existe."""
    query = """
    SELECT COUNT(*) as count
    FROM veiculo 
    WHERE id_veiculo = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (veiculo_id,), fetch="one")
    return result['count'] > 0 if result else False

def check_mecanico_exists(mecanico_id: int):
    """Verifica se mecânico existe."""
    query = """
    SELECT COUNT(*) as count
    FROM mecanico 
    WHERE id_mecanico = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (mecanico_id,), fetch="one")
    return result['count'] > 0 if result else False
