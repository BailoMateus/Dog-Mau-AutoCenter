import logging

from app.database.db import execute_query, execute_command
from app.models.entities import PedidoPeca, dict_to_pedido_peca

logger = logging.getLogger(__name__)


def get_pedido_peca(pedido_id: int, peca_id: int):
    """Busca item (peça) do pedido por IDs, com dados enriquecidos."""
    query = """
    SELECT pp.id_pedido, pp.id_peca, pp.quantidade, pp.created_at, pp.updated_at, pp.deleted_at,
           p.nome AS peca_nome, p.preco_unitario AS peca_preco
    FROM pedido_peca pp
    INNER JOIN peca p ON pp.id_peca = p.id_peca
    WHERE pp.id_pedido = %s AND pp.id_peca = %s AND pp.deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id, peca_id), fetch="one")
    if not result:
        return None
    item = dict_to_pedido_peca(result)
    item.peca_nome = result["peca_nome"]
    item.peca_preco = result["peca_preco"]
    return item


def get_itens_by_pedido(pedido_id: int):
    """Lista todas as peças de um pedido com dados enriquecidos."""
    query = """
    SELECT pp.id_pedido, pp.id_peca, pp.quantidade, pp.created_at, pp.updated_at, pp.deleted_at,
           p.nome AS peca_nome, p.preco_unitario AS peca_preco
    FROM pedido_peca pp
    INNER JOIN peca p ON pp.id_peca = p.id_peca
    WHERE pp.id_pedido = %s AND pp.deleted_at IS NULL AND p.deleted_at IS NULL
    ORDER BY p.nome ASC
    """
    results = execute_query(query, (pedido_id,))
    itens = []
    for row in results:
        item = dict_to_pedido_peca(row)
        item.peca_nome = row["peca_nome"]
        item.peca_preco = row["peca_preco"]
        itens.append(item)
    logger.debug("get_itens_by_pedido(peca) pedido_id=%s count=%s", pedido_id, len(itens))
    return itens


def add_peca_to_pedido(item: PedidoPeca):
    """Adiciona peça ao pedido (ou restaura/soma caso já exista)."""
    existente = execute_query(
        "SELECT quantidade, deleted_at FROM pedido_peca WHERE id_pedido = %s AND id_peca = %s",
        (item.id_pedido, item.id_peca),
        fetch="one",
    )

    if existente and existente["deleted_at"] is None:
        # Já ativo: soma a quantidade
        execute_command(
            """
            UPDATE pedido_peca
            SET quantidade = quantidade + %s, updated_at = CURRENT_TIMESTAMP
            WHERE id_pedido = %s AND id_peca = %s
            """,
            (item.quantidade, item.id_pedido, item.id_peca),
        )
        logger.info("peça somada ao pedido pedido=%s peca=%s", item.id_pedido, item.id_peca)
        return item

    if existente and existente["deleted_at"] is not None:
        # Restaura item removido
        execute_command(
            """
            UPDATE pedido_peca
            SET quantidade = %s, deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id_pedido = %s AND id_peca = %s
            """,
            (item.quantidade, item.id_pedido, item.id_peca),
        )
        logger.info("peça restaurada no pedido pedido=%s peca=%s", item.id_pedido, item.id_peca)
        return item

    execute_command(
        "INSERT INTO pedido_peca (id_pedido, id_peca, quantidade) VALUES (%s, %s, %s)",
        (item.id_pedido, item.id_peca, item.quantidade),
    )
    logger.info("peça adicionada ao pedido pedido=%s peca=%s quantidade=%s",
                item.id_pedido, item.id_peca, item.quantidade)
    return item


def check_peca_exists_in_pedido(pedido_id: int, peca_id: int):
    """Verifica se a peça já está ativa no pedido."""
    query = """
    SELECT COUNT(*) as count
    FROM pedido_peca
    WHERE id_pedido = %s AND id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id, peca_id), fetch="one")
    return result["count"] > 0 if result else False


def calcular_valor_total_pecas(pedido_id: int):
    """Soma o valor das peças de um pedido (preço unitário × quantidade)."""
    query = """
    SELECT COALESCE(SUM(p.preco_unitario * pp.quantidade), 0) as valor_total
    FROM pedido_peca pp
    INNER JOIN peca p ON pp.id_peca = p.id_peca
    WHERE pp.id_pedido = %s AND pp.deleted_at IS NULL AND p.deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id,), fetch="one")
    return float(result["valor_total"]) if result and result["valor_total"] else 0.0


def remove_peca_from_pedido(pedido_id: int, peca_id: int):
    """Remove (soft delete) peça do pedido."""
    execute_command(
        """
        UPDATE pedido_peca
        SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id_pedido = %s AND id_peca = %s AND deleted_at IS NULL
        """,
        (pedido_id, peca_id),
    )
    logger.info("peça removida do pedido pedido=%s peca=%s", pedido_id, peca_id)
