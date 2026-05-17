import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Produto, dict_to_produto, produto_to_dict

logger = logging.getLogger(__name__)

def get_produto_by_id(produto_id: int):
    """Busca produto por ID."""
    query = """
    SELECT id_produto, nome, descricao, preco, quantidade_estoque, created_at, updated_at, deleted_at
    FROM produto 
    WHERE id_produto = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (produto_id,), fetch="one")
    produto = dict_to_produto(result)
    logger.debug("get_produto_by_id id=%s found=%s", produto_id, produto is not None)
    return produto

def get_all_produtos():
    """Lista todos os produtos."""
    query = """
    SELECT id_produto, nome, descricao, preco, quantidade_estoque, created_at, updated_at, deleted_at
    FROM produto 
    WHERE deleted_at IS NULL
    ORDER BY nome ASC
    """
    results = execute_query(query)
    produtos = [dict_to_produto(row) for row in results]
    logger.debug("get_all_produtos count=%s", len(produtos))
    return produtos

def create_produto(produto: Produto):
    """Cria um novo produto."""
    query = """
    INSERT INTO produto (nome, descricao, preco, quantidade_estoque)
    VALUES (%s, %s, %s, %s)
    RETURNING id_produto
    """
    params = (produto.nome, produto.descricao, produto.preco, produto.quantidade_estoque)
    produto_id = execute_insert(query, params)
    produto.id_produto = produto_id
    logger.info("produto criado id=%s", produto.id_produto)
    return produto

def update_produto(produto: Produto):
    """Atualiza um produto."""
    query = """
    UPDATE produto 
    SET nome = %s, descricao = %s, preco = %s, quantidade_estoque = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_produto = %s AND deleted_at IS NULL
    """
    params = (produto.nome, produto.descricao, produto.preco, produto.quantidade_estoque, produto.id_produto)
    execute_command(query, params)
    logger.info("produto atualizado id=%s", produto.id_produto)
    return produto

def soft_delete_produto(produto: Produto):
    """Soft delete de produto."""
    query = """
    UPDATE produto 
    SET deleted_at = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_produto = %s
    """
    params = (datetime.now(timezone.utc), produto.id_produto)
    execute_command(query, params)
    produto.deleted_at = datetime.now(timezone.utc)
    logger.info("produto soft-delete id=%s", produto.id_produto)
    return produto

def check_produto_exists_by_nome(nome: str, exclude_id: int = None):
    """Verifica se já existe produto com mesmo nome."""
    query = """
    SELECT COUNT(*) as count
    FROM produto 
    WHERE nome = %s AND deleted_at IS NULL
    """
    params = (nome,)
    
    if exclude_id:
        query += " AND id_produto != %s"
        params = (nome, exclude_id)
    
    result = execute_query(query, params, fetch="one")
    return result['count'] > 0 if result else False