import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Endereco, dict_to_endereco, endereco_to_dict

logger = logging.getLogger(__name__)

def get_endereco_by_id_for_user(user_id: int, endereco_id: int):
    """Busca endereço por ID para um cliente específico."""
    query = """
    SELECT id_endereco, id_cliente, logradouro, numero, cep, complemento, 
           bairro, cidade, estado, created_at, updated_at, deleted_at
    FROM endereco 
    WHERE id_endereco = %s AND id_cliente = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (endereco_id, user_id), fetch="one")
    endereco = dict_to_endereco(result)
    logger.debug(
        "get_endereco_by_id_for_user user=%s endereco=%s found=%s",
        user_id,
        endereco_id,
        endereco is not None,
    )
    return endereco

def create_endereco(endereco: Endereco):
    """Cria um novo endereço."""
    query = """
    INSERT INTO endereco (id_cliente, logradouro, numero, cep, complemento, bairro, cidade, estado)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id_endereco
    """
    params = (
        endereco.id_cliente, endereco.logradouro, endereco.numero, endereco.cep,
        endereco.complemento, endereco.bairro, endereco.cidade, endereco.estado
    )
    endereco_id = execute_insert(query, params)
    endereco.id_endereco = endereco_id
    logger.info("endereco criado id=%s cliente=%s", endereco.id_endereco, endereco.id_cliente)
    return endereco

def list_enderecos_by_user(user_id: int):
    """Lista todos os endereços de um cliente."""
    query = """
    SELECT id_endereco, id_cliente, logradouro, numero, cep, complemento, 
           bairro, cidade, estado, created_at, updated_at, deleted_at
    FROM endereco 
    WHERE id_cliente = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (user_id,))
    enderecos = [dict_to_endereco(row) for row in results]
    logger.debug("list_enderecos_by_user user=%s count=%s", user_id, len(enderecos))
    return enderecos

def update_endereco(endereco: Endereco):
    """Atualiza um endereço."""
    query = """
    UPDATE endereco 
    SET logradouro = %s, numero = %s, cep = %s, complemento = %s, 
        bairro = %s, cidade = %s, estado = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_endereco = %s AND deleted_at IS NULL
    """
    params = (
        endereco.logradouro, endereco.numero, endereco.cep, endereco.complemento,
        endereco.bairro, endereco.cidade, endereco.estado, endereco.id_endereco
    )
    execute_command(query, params)
    logger.info("endereco atualizado id=%s", endereco.id_endereco)
    return endereco

def soft_delete_endereco(endereco: Endereco):
    """Soft delete de endereço."""
    query = """
    UPDATE endereco 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_endereco = %s
    """
    params = (datetime.now(timezone.utc), endereco.id_endereco)
    execute_command(query, params)
    endereco.deleted_at = datetime.now(timezone.utc)
    logger.info("endereco soft-delete id=%s", endereco.id_endereco)
    return endereco
