import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Modelo, dict_to_modelo, modelo_to_dict

logger = logging.getLogger(__name__)

def get_modelo_by_id(modelo_id: int):
    """Busca modelo por ID."""
    query = """
    SELECT id_modelo, id_marca, nome_modelo, ano_lancamento, tipo_combustivel, 
           categoria, num_portas, created_at, updated_at, deleted_at
    FROM modelo 
    WHERE id_modelo = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (modelo_id,), fetch="one")
    modelo = dict_to_modelo(result)
    logger.debug("get_modelo_by_id id=%s found=%s", modelo_id, modelo is not None)
    return modelo

def get_modelos_by_marca(marca_id: int):
    """Lista modelos por marca."""
    query = """
    SELECT id_modelo, id_marca, nome_modelo, ano_lancamento, tipo_combustivel, 
           categoria, num_portas, created_at, updated_at, deleted_at
    FROM modelo 
    WHERE id_marca = %s AND deleted_at IS NULL
    ORDER BY nome_modelo ASC
    """
    results = execute_query(query, (marca_id,))
    modelos = [dict_to_modelo(row) for row in results]
    logger.debug("get_modelos_by_marca marca_id=%s count=%s", marca_id, len(modelos))
    return modelos

def get_all_modelos():
    """Lista todos os modelos."""
    query = """
    SELECT id_modelo, id_marca, nome_modelo, ano_lancamento, tipo_combustivel, 
           categoria, num_portas, created_at, updated_at, deleted_at
    FROM modelo 
    WHERE deleted_at IS NULL
    ORDER BY nome_modelo ASC
    """
    results = execute_query(query)
    modelos = [dict_to_modelo(row) for row in results]
    logger.debug("get_all_modelos count=%s", len(modelos))
    return modelos

def create_modelo(modelo: Modelo):
    """Cria um novo modelo."""
    query = """
    INSERT INTO modelo (id_marca, nome_modelo, ano_lancamento, tipo_combustivel, categoria, num_portas)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id_modelo
    """
    params = (
        modelo.id_marca, modelo.nome_modelo, modelo.ano_lancamento, 
        modelo.tipo_combustivel, modelo.categoria, modelo.num_portas
    )
    modelo_id = execute_insert(query, params)
    modelo.id_modelo = modelo_id
    logger.info("modelo criado id=%s", modelo.id_modelo)
    return modelo

def update_modelo(modelo: Modelo):
    """Atualiza um modelo."""
    query = """
    UPDATE modelo 
    SET id_marca = %s, nome_modelo = %s, ano_lancamento = %s, tipo_combustivel = %s, 
        categoria = %s, num_portas = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_modelo = %s AND deleted_at IS NULL
    """
    params = (
        modelo.id_marca, modelo.nome_modelo, modelo.ano_lancamento, 
        modelo.tipo_combustivel, modelo.categoria, modelo.num_portas, modelo.id_modelo
    )
    execute_command(query, params)
    logger.info("modelo atualizado id=%s", modelo.id_modelo)
    return modelo

def soft_delete_modelo(modelo: Modelo):
    """Soft delete de modelo."""
    query = """
    UPDATE modelo 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_modelo = %s
    """
    params = (datetime.now(timezone.utc), modelo.id_modelo)
    execute_command(query, params)
    modelo.deleted_at = datetime.now(timezone.utc)
    logger.info("modelo soft-delete id=%s", modelo.id_modelo)
    return modelo