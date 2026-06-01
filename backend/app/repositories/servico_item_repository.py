import logging

from app.database.db import execute_query

logger = logging.getLogger(__name__)


def get_pecas_by_servico(servico_id: int):
    """Lista peças vinculadas a um serviço."""
    query = """
    SELECT sp.id_servico, sp.id_peca, sp.quantidade
    FROM servico_peca sp
    WHERE sp.id_servico = %s
    """
    try:
        return execute_query(query, (servico_id,))
    except Exception as exc:
        logger.debug("servico_peca indisponível servico=%s: %s", servico_id, exc)
        return []


def get_produtos_by_servico(servico_id: int):
    """Lista produtos vinculados a um serviço."""
    query = """
    SELECT sp.id_servico, sp.id_produto, sp.quantidade
    FROM servico_produto sp
    WHERE sp.id_servico = %s
    """
    try:
        return execute_query(query, (servico_id,))
    except Exception as exc:
        logger.debug("servico_produto indisponível servico=%s: %s", servico_id, exc)
        return []
