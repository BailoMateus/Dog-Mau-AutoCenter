import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Veiculo, dict_to_veiculo, veiculo_to_dict

logger = logging.getLogger(__name__)

def get_veiculo_by_id_for_user(user_id: int, veiculo_id: int):
    """Busca veículo por ID para um cliente específico."""
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_cliente, id_modelo, 
           created_at, updated_at, deleted_at
    FROM veiculo 
    WHERE id_veiculo = %s AND id_cliente = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (veiculo_id, user_id), fetch="one")
    veiculo = dict_to_veiculo(result)
    logger.debug(
        "get_veiculo_by_id_for_user user=%s veiculo=%s found=%s",
        user_id,
        veiculo_id,
        veiculo is not None,
    )
    return veiculo

def create_veiculo(veiculo: Veiculo):
    """Cria um novo veículo."""
    query = """
    INSERT INTO veiculo (placa, ano_fabricacao, cor, id_cliente, id_modelo)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_veiculo
    """
    params = (veiculo.placa, veiculo.ano_fabricacao, veiculo.cor, veiculo.id_cliente, veiculo.id_modelo)
    veiculo_id = execute_insert(query, params)
    veiculo.id_veiculo = veiculo_id
    logger.info("veiculo criado id=%s cliente=%s", veiculo.id_veiculo, veiculo.id_cliente)
    return veiculo

def list_veiculos_by_user(user_id: int):
    """Lista todos os veículos de um cliente."""
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_cliente, id_modelo, 
           created_at, updated_at, deleted_at
    FROM veiculo 
    WHERE id_cliente = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (user_id,))
    veiculos = [dict_to_veiculo(row) for row in results]
    logger.debug("list_veiculos_by_user user=%s count=%s", user_id, len(veiculos))
    return veiculos

def update_veiculo(veiculo: Veiculo):
    """Atualiza um veículo."""
    query = """
    UPDATE veiculo 
    SET placa = %s, ano_fabricacao = %s, cor = %s, id_modelo = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_veiculo = %s AND deleted_at IS NULL
    """
    params = (veiculo.placa, veiculo.ano_fabricacao, veiculo.cor, veiculo.id_modelo, veiculo.id_veiculo)
    execute_command(query, params)
    logger.info("veiculo atualizado id=%s", veiculo.id_veiculo)
    return veiculo

def soft_delete_veiculo(veiculo: Veiculo):
    """Soft delete de veículo."""
    query = """
    UPDATE veiculo 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_veiculo = %s
    """
    params = (datetime.now(timezone.utc), veiculo.id_veiculo)
    execute_command(query, params)
    veiculo.deleted_at = datetime.now(timezone.utc)
    logger.info("veiculo soft-delete id=%s", veiculo.id_veiculo)
    return veiculo
