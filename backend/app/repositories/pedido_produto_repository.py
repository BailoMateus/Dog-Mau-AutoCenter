import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import PedidoProduto, dict_to_pedido_produto, pedido_produto_to_dict

logger = logging.getLogger(__name__)

def get_pedido_produto(pedido_id: int, produto_id: int):
    """Busca item do pedido por IDs."""
    query = """
    SELECT 
        pp.id_pedido,
        pp.id_produto,
        pp.quantidade,
        pp.created_at,
        pp.updated_at,
        pp.deleted_at,
        p.nome AS produto_nome,
        p.preco AS produto_preco
    FROM pedido_produto pp
    INNER JOIN produto p 
        ON pp.id_produto = p.id_produto
    WHERE pp.id_pedido = %s 
      AND pp.id_produto = %s 
      AND pp.deleted_at IS NULL
    """
    
    result = execute_query(query, (pedido_id, produto_id), fetch="one")

    if not result:
        return None

    item = PedidoProduto(
        id_pedido=result["id_pedido"],
        id_produto=result["id_produto"],
        quantidade=result["quantidade"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
        deleted_at=result["deleted_at"]
    )

    item.produto_nome = result["produto_nome"]
    item.produto_preco = result["produto_preco"]

    logger.debug(
        "get_pedido_produto pedido=%s produto=%s found=%s",
        pedido_id,
        produto_id,
        item is not None
    )

    return item

def get_itens_by_pedido(pedido_id: int):
    """Lista todos os itens de um pedido."""
    query = """
    SELECT pp.id_pedido, pp.id_produto, pp.quantidade, pp.created_at, pp.updated_at, pp.deleted_at,
           p.nome as produto_nome, p.preco as produto_preco
    FROM pedido_produto pp
    INNER JOIN produto p ON pp.id_produto = p.id_produto
    WHERE pp.id_pedido = %s AND pp.deleted_at IS NULL AND p.deleted_at IS NULL
    ORDER BY p.nome ASC
    """
    results = execute_query(query, (pedido_id,))
    itens = []
    for row in results:
        item = dict_to_pedido_produto(row)
        # Adiciona informações do produto
        item.produto_nome = row['produto_nome']
        item.produto_preco = row['produto_preco']
        itens.append(item)
    logger.debug("get_itens_by_pedido pedido_id=%s count=%s", pedido_id, len(itens))
    return itens

def add_produto_to_pedido(item: PedidoProduto):
    produto_existente = execute_query(
        """
        SELECT *
        FROM pedido_produto
        WHERE id_pedido = %s
          AND id_produto = %s
        """,
        (item.id_pedido, item.id_produto),
        fetch="one"
    )

    # Produto existia mas foi removido (soft delete)
    if produto_existente and produto_existente["deleted_at"] is not None:
        query = """
        UPDATE pedido_produto
        SET
            quantidade = %s,
            deleted_at = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id_pedido = %s
          AND id_produto = %s
        """

        execute_command(
            query,
            (
                item.quantidade,
                item.id_pedido,
                item.id_produto
            )
        )

        logger.info(
            "produto restaurado no pedido pedido=%s produto=%s",
            item.id_pedido,
            item.id_produto
        )

        return item

    # Produto já ativo no pedido
    if produto_existente and produto_existente["deleted_at"] is None:
        raise Exception("Produto já adicionado ao pedido")

    # INSERT normal
    query = """
    INSERT INTO pedido_produto (
        id_pedido,
        id_produto,
        quantidade
    )
    VALUES (%s, %s, %s)
    """

    execute_command(
        query,
        (
            item.id_pedido,
            item.id_produto,
            item.quantidade
        )
    )

    logger.info(
        "produto adicionado ao pedido pedido=%s produto=%s quantidade=%s",
        item.id_pedido,
        item.id_produto,
        item.quantidade
    )

    return item

def update_quantidade_produto(pedido_id: int, produto_id: int, nova_quantidade: int):
    """Atualiza quantidade de um produto no pedido."""
    query = """
    UPDATE pedido_produto 
    SET quantidade = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pedido = %s AND id_produto = %s AND deleted_at IS NULL
    """
    params = (nova_quantidade, pedido_id, produto_id)
    execute_command(query, params)
    logger.info("quantidade atualizada pedido=%s produto=%s nova_quantidade=%s", 
                pedido_id, produto_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_pedido_produto(pedido_id, produto_id)

def check_produto_exists_in_pedido(pedido_id: int, produto_id: int):
    """Verifica se produto existe no pedido."""
    query = """
    SELECT COUNT(*) as count
    FROM pedido_produto 
    WHERE id_pedido = %s AND id_produto = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id, produto_id), fetch="one")
    return result['count'] > 0 if result else False

def get_produto_stock(produto_id: int):
    """Busca quantidade em estoque de um produto."""
    query = """
    SELECT quantidade_estoque
    FROM produto 
    WHERE id_produto = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (produto_id,), fetch="one")
    return result['quantidade_estoque'] if result else 0

def update_produto_stock(produto_id: int, nova_quantidade: int):
    """Atualiza quantidade em estoque de um produto."""
    query = """
    UPDATE produto 
    SET quantidade_estoque = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_produto = %s AND deleted_at IS NULL
    """
    params = (nova_quantidade, produto_id)
    execute_command(query, params)
    logger.info("estoque atualizado produto=%s nova_quantidade=%s", produto_id, nova_quantidade)

def calcular_valor_total_pedido(pedido_id: int):
    """Calcula valor total do pedido baseado nos itens."""
    query = """
    SELECT SUM(p.preco * pp.quantidade) as valor_total
    FROM pedido_produto pp
    INNER JOIN produto p ON pp.id_produto = p.id_produto
    WHERE pp.id_pedido = %s AND pp.deleted_at IS NULL AND p.deleted_at IS NULL
    """
    result = execute_query(query, (pedido_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0

def update_valor_total_pedido(pedido_id: int, valor_total: float):
    """Atualiza valor total do pedido."""
    query = """
    UPDATE pedido 
    SET valor_total = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_pedido = %s AND deleted_at IS NULL
    """
    params = (valor_total, pedido_id)
    execute_command(query, params)
    logger.info("valor total atualizado pedido=%s valor=%s", pedido_id, valor_total)

def remove_produto_from_pedido(pedido_id: int, produto_id: int):
    """Remove produto do pedido (soft delete)."""

    query = """
    UPDATE pedido_produto
    SET
        deleted_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE id_pedido = %s
      AND id_produto = %s
      AND deleted_at IS NULL
    """

    execute_command(query, (pedido_id, produto_id))

    logger.info(
        "produto removido do pedido pedido=%s produto=%s",
        pedido_id,
        produto_id
    )