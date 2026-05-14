import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Peca, dict_to_peca, peca_to_dict

logger = logging.getLogger(__name__)

def get_peca_by_id(peca_id: int):
    """Busca peça por ID."""
    query = """
    SELECT id_peca, nome, preco_unitario, quantidade_estoque, created_at, updated_at, deleted_at
    FROM peca 
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (peca_id,), fetch="one")
    peca = dict_to_peca(result)
    logger.debug("get_peca_by_id id=%s found=%s", peca_id, peca is not None)
    return peca

def get_all_pecas():
    """Lista todas as peças."""
    query = """
    SELECT id_peca, nome, preco_unitario, quantidade_estoque, created_at, updated_at, deleted_at
    FROM peca 
    WHERE deleted_at IS NULL
    ORDER BY nome ASC
    """
    results = execute_query(query)
    pecas = [dict_to_peca(row) for row in results]
    logger.debug("get_all_pecas count=%s", len(pecas))
    return pecas

def create_peca(peca: Peca):
    """Cria uma nova peça."""
    query = """
    INSERT INTO peca (nome, preco_unitario, quantidade_estoque)
    VALUES (%s, %s, %s)
    RETURNING id_peca
    """
    params = (peca.nome, peca.preco_unitario, peca.quantidade_estoque)
    peca_id = execute_insert(query, params)
    peca.id_peca = peca_id
    logger.info("peça criada id=%s", peca.id_peca)
    return peca

def update_peca(peca: Peca):
    """Atualiza uma peça."""
    query = """
    UPDATE peca 
    SET nome = %s, preco_unitario = %s, quantidade_estoque = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    params = (peca.nome, peca.preco_unitario, peca.quantidade_estoque, peca.id_peca)
    execute_command(query, params)
    logger.info("peça atualizada id=%s", peca.id_peca)
    return peca

def soft_delete_peca(peca: Peca):
    """Soft delete de peça."""
    query = """
    UPDATE peca 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_peca = %s
    """
    params = (datetime.now(timezone.utc), peca.id_peca)
    execute_command(query, params)
    peca.deleted_at = datetime.now(timezone.utc)
    logger.info("peça soft-delete id=%s", peca.id_peca)
    return peca