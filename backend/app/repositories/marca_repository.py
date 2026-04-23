import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Marca, dict_to_marca, marca_to_dict

logger = logging.getLogger(__name__)

def get_marca_by_id(marca_id: int):
    """Busca marca por ID."""
    query = """
    SELECT id_marca, nome, pais_origem, site_oficial, created_at, updated_at, deleted_at
    FROM marca 
    WHERE id_marca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (marca_id,), fetch="one")
    marca = dict_to_marca(result)
    logger.debug("get_marca_by_id id=%s found=%s", marca_id, marca is not None)
    return marca

def get_all_marcas():
    """Lista todas as marcas."""
    query = """
    SELECT id_marca, nome, pais_origem, site_oficial, created_at, updated_at, deleted_at
    FROM marca 
    WHERE deleted_at IS NULL
    ORDER BY nome ASC
    """
    results = execute_query(query)
    marcas = [dict_to_marca(row) for row in results]
    logger.debug("get_all_marcas count=%s", len(marcas))
    return marcas

def create_marca(marca: Marca):
    """Cria uma nova marca."""
    query = """
    INSERT INTO marca (nome, pais_origem, site_oficial)
    VALUES (%s, %s, %s)
    RETURNING id_marca
    """
    params = (marca.nome, marca.pais_origem, marca.site_oficial)
    marca_id = execute_insert(query, params)
    marca.id_marca = marca_id
    logger.info("marca criada id=%s", marca.id_marca)
    return marca

def update_marca(marca: Marca):
    """Atualiza uma marca."""
    query = """
    UPDATE marca 
    SET nome = %s, pais_origem = %s, site_oficial = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_marca = %s AND deleted_at IS NULL
    """
    params = (marca.nome, marca.pais_origem, marca.site_oficial, marca.id_marca)
    execute_command(query, params)
    logger.info("marca atualizada id=%s", marca.id_marca)
    return marca

def soft_delete_marca(marca: Marca):
    """Soft delete de marca."""
    query = """
    UPDATE marca 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_marca = %s
    """
    params = (datetime.now(timezone.utc), marca.id_marca)
    execute_command(query, params)
    marca.deleted_at = datetime.now(timezone.utc)
    logger.info("marca soft-delete id=%s", marca.id_marca)
    return marca