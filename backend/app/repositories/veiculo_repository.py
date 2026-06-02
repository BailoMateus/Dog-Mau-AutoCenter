import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Veiculo, dict_to_veiculo, veiculo_to_dict

logger = logging.getLogger(__name__)

def get_all_veiculos():
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_usuario, id_modelo,
           created_at, updated_at, deleted_at
    FROM veiculo
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query)
    return [dict_to_veiculo(row) for row in results]

def get_veiculo_by_id(veiculo_id: int):
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_usuario, id_modelo,
           created_at, updated_at, deleted_at
    FROM veiculo
    WHERE id_veiculo = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (veiculo_id,), fetch="one")

    if not result:
        return None

    return dict_to_veiculo(result)


def get_veiculo_by_placa_for_user(placa: str, user_id: int):
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_usuario, id_modelo,
           created_at, updated_at, deleted_at
    FROM veiculo
    WHERE UPPER(REPLACE(placa, '-', '')) = UPPER(REPLACE(%s, '-', ''))
      AND id_usuario = %s AND deleted_at IS NULL
    LIMIT 1
    """
    result = execute_query(query, (placa, user_id), fetch="one")
    if not result:
        return None
    return dict_to_veiculo(result)


def list_veiculos_by_user(user_id: int):
    query = """
    SELECT id_veiculo, placa, ano_fabricacao, cor, id_usuario, id_modelo,
           created_at, updated_at, deleted_at
    FROM veiculo
    WHERE id_usuario = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (user_id,))
    return [dict_to_veiculo(row) for row in results]

def create_veiculo(veiculo: Veiculo):
    query = """
    INSERT INTO veiculo (placa, ano_fabricacao, cor, id_usuario, id_modelo)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_veiculo
    """

    params = (
        veiculo.placa,
        veiculo.ano_fabricacao,
        veiculo.cor,
        veiculo.id_usuario,
        veiculo.id_modelo,
    )

    veiculo_id = execute_insert(query, params)
    veiculo.id_veiculo = veiculo_id

    return veiculo

def update_veiculo(veiculo: Veiculo):
    query = """
    UPDATE veiculo
    SET placa = %s,
        ano_fabricacao = %s,
        cor = %s,
        id_modelo = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id_veiculo = %s AND deleted_at IS NULL
    """

    params = (
        veiculo.placa,
        veiculo.ano_fabricacao,
        veiculo.cor,
        veiculo.id_modelo,
        veiculo.id_veiculo,
    )

    execute_command(query, params)
    return veiculo

def soft_delete_veiculo(veiculo: Veiculo):
    query = """
    UPDATE veiculo
    SET deleted_at = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id_veiculo = %s
    """

    params = (datetime.now(timezone.utc), veiculo.id_veiculo)

    execute_command(query, params)
    veiculo.deleted_at = datetime.now(timezone.utc)

    return veiculo