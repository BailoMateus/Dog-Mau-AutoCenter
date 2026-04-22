import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Servico, dict_to_servico, servico_to_dict

logger = logging.getLogger(__name__)

def get_servico_by_id(servico_id: int):
    """Busca serviço por ID."""
    query = """
    SELECT id_servico, descricao, preco, created_at, updated_at, deleted_at
    FROM servico 
    WHERE id_servico = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (servico_id,), fetch="one")
    servico = dict_to_servico(result)
    logger.debug("get_servico_by_id id=%s found=%s", servico_id, servico is not None)
    return servico

def get_all_servicos():
    """Lista todos os serviços."""
    query = """
    SELECT id_servico, descricao, preco, created_at, updated_at, deleted_at
    FROM servico 
    WHERE deleted_at IS NULL
    ORDER BY descricao ASC
    """
    results = execute_query(query)
    servicos = [dict_to_servico(row) for row in results]
    logger.debug("get_all_servicos count=%s", len(servicos))
    return servicos

def create_servico(servico: Servico):
    """Cria um novo serviço."""
    query = """
    INSERT INTO servico (descricao, preco)
    VALUES (%s, %s)
    RETURNING id_servico
    """
    params = (servico.descricao, servico.preco)
    servico_id = execute_insert(query, params)
    servico.id_servico = servico_id
    logger.info("servico criado id=%s", servico.id_servico)
    return servico

def update_servico(servico: Servico):
    """Atualiza um serviço."""
    query = """
    UPDATE servico 
    SET descricao = %s, preco = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_servico = %s AND deleted_at IS NULL
    """
    params = (servico.descricao, servico.preco, servico.id_servico)
    execute_command(query, params)
    logger.info("servico atualizado id=%s", servico.id_servico)
    return servico

def soft_delete_servico(servico: Servico):
    """Soft delete de serviço."""
    query = """
    UPDATE servico 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_servico = %s
    """
    params = (datetime.now(timezone.utc), servico.id_servico)
    execute_command(query, params)
    servico.deleted_at = datetime.now(timezone.utc)
    logger.info("servico soft-delete id=%s", servico.id_servico)
    return servico