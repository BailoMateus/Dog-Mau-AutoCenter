import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import PedidoProduto
from app.repositories import pedido_repository as pedido_repo
from app.repositories import produto_repository as produto_repo
from app.repositories import pedido_produto_repository as repo
from app.schemas.pedido_produto_schema import PedidoProdutoCreate, PedidoProdutoUpdate

logger = logging.getLogger(__name__)

def get_itens_pedido(pedido_id: int):
    """Lista todos os itens de um pedido."""
    # Verifica se pedido existe
    pedido = pedido_repo.get_pedido_by_id(pedido_id)
    if not pedido:
        logger.info("pedido não encontrado id=%s", pedido_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    
    return repo.get_itens_by_pedido(pedido_id)

def validate_pedido_produto_data(pedido_id: int, produto_id: int, quantidade: int):
    """Valida dados de item do pedido."""
    # Validação de pedido existente
    pedido = pedido_repo.get_pedido_by_id(pedido_id)
    if not pedido:
        logger.warning("pedido não encontrado pedido_id=%s", pedido_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado"
        )
    
    # Validação de produto existente
    produto = produto_repo.get_produto_by_id(produto_id)
    if not produto:
        logger.warning("produto não encontrado produto_id=%s", produto_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Validação de quantidade
    if quantidade <= 0:
        logger.warning("quantidade inválida quantidade=%s", quantidade)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero"
        )
    
    return pedido, produto

def add_produto_to_pedido(pedido_id: int, data: PedidoProdutoCreate):
    """Adiciona produto ao pedido com validações."""
    # Validações
    pedido, produto = validate_pedido_produto_data(pedido_id, data.id_produto, data.quantidade)
    
    # Verifica se produto já existe no pedido
    if repo.check_produto_exists_in_pedido(pedido_id, data.id_produto):
        logger.warning("produto já existe no pedido pedido=%s produto=%s", pedido_id, data.id_produto)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Produto já adicionado ao pedido"
        )
    
    # Verifica estoque disponível
    estoque_atual = repo.get_produto_stock(data.id_produto)
    if estoque_atual < data.quantidade:
        logger.warning("estoque insuficiente produto=%s estoque=%s solicitado=%s", 
                       data.id_produto, estoque_atual, data.quantidade)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {estoque_atual}, Solicitado: {data.quantidade}"
        )
    
    # Cria item do pedido
    item = PedidoProduto(
        id_pedido=pedido_id,
        id_produto=data.id_produto,
        quantidade=data.quantidade
    )
    
    try:
        # Adiciona item ao pedido
        repo.add_produto_to_pedido(item)
        
        # Atualiza estoque
        novo_estoque = estoque_atual - data.quantidade
        repo.update_produto_stock(data.id_produto, novo_estoque)
        
        # Recalcula valor total do pedido
        novo_valor_total = repo.calcular_valor_total_pedido(pedido_id)
        repo.update_valor_total_pedido(pedido_id, novo_valor_total)
        
        logger.info("produto adicionado ao pedido pedido=%s produto=%s quantidade=%s", 
                   pedido_id, data.id_produto, data.quantidade)
        
        # Retorna item com informações do produto
        item_com_info = repo.get_pedido_produto(pedido_id, data.id_produto)
        item_com_info.produto_nome = produto.nome
        item_com_info.produto_preco = produto.preco
        
        return item_com_info
        
    except psycopg2.IntegrityError:
        logger.error("add_produto_to_pedido erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar produto ao pedido"
        )

def update_quantidade_produto(pedido_id: int, produto_id: int, data: PedidoProdutoUpdate):
    """Atualiza quantidade de produto no pedido."""
    # Validações
    pedido, produto = validate_pedido_produto_data(pedido_id, produto_id, data.quantidade)
    
    # Verifica se produto existe no pedido
    item_existente = repo.get_pedido_produto(pedido_id, produto_id)
    if not item_existente:
        logger.warning("produto não encontrado no pedido pedido=%s produto=%s", pedido_id, produto_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado no pedido"
        )
    
    # Calcula diferença de quantidade
    diferenca = data.quantidade - item_existente.quantidade
    
    # Verifica estoque para aumento
    if diferenca > 0:
        estoque_atual = repo.get_produto_stock(produto_id)
        if estoque_atual < diferenca:
            logger.warning("estoque insuficiente para aumento produto=%s estoque=%s necessario=%s", 
                           produto_id, estoque_atual, diferenca)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {estoque_atual}, Necessário: {diferenca}"
            )
    
    try:
        # Atualiza quantidade
        item_atualizado = repo.update_quantidade_produto(pedido_id, produto_id, data.quantidade)
        
        # Atualiza estoque
        novo_estoque = repo.get_produto_stock(produto_id) - diferenca
        repo.update_produto_stock(produto_id, novo_estoque)
        
        # Recalcula valor total do pedido
        novo_valor_total = repo.calcular_valor_total_pedido(pedido_id)
        repo.update_valor_total_pedido(pedido_id, novo_valor_total)
        
        logger.info("quantidade atualizada pedido=%s produto=%s nova_quantidade=%s", 
                   pedido_id, produto_id, data.quantidade)
        
        # Retorna item com informações do produto
        item_atualizado.produto_nome = produto.nome
        item_atualizado.produto_preco = produto.preco
        
        return item_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("update_quantidade_produto erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar quantidade"
        )

def remove_produto_from_pedido(pedido_id: int, produto_id: int):
    """Remove produto do pedido e devolve ao estoque."""
    # Validações
    pedido, produto = validate_pedido_produto_data(pedido_id, produto_id, 1)
    
    # Verifica se produto existe no pedido
    item_existente = repo.get_pedido_produto(pedido_id, produto_id)
    if not item_existente:
        logger.warning("produto não encontrado no pedido pedido=%s produto=%s", pedido_id, produto_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado no pedido"
        )
    
    try:
        # Remove produto do pedido
        repo.remove_produto_from_pedido(pedido_id, produto_id)
        
        # Devolve ao estoque
        estoque_atual = repo.get_produto_stock(produto_id)
        novo_estoque = estoque_atual + item_existente.quantidade
        repo.update_produto_stock(produto_id, novo_estoque)
        
        # Recalcula valor total do pedido
        novo_valor_total = repo.calcular_valor_total_pedido(pedido_id)
        repo.update_valor_total_pedido(pedido_id, novo_valor_total)
        
        logger.info("produto removido do pedido pedido=%s produto=%s quantidade_devolvida=%s", 
                   pedido_id, produto_id, item_existente.quantidade)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("remove_produto_from_pedido erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover produto do pedido"
        )
