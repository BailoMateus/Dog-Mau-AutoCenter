import logging

from fastapi import APIRouter, HTTPException, status

from app.services import pedido_produto_service
from app.schemas.pedido_produto_schema import PedidoProdutoCreate, PedidoProdutoUpdate, PedidoProdutoPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedidos/{pedido_id}/itens", tags=["Itens do Pedido"])

@router.post("/", response_model=PedidoProdutoPublic, status_code=status.HTTP_201_CREATED)
def add_produto_to_pedido(pedido_id: int, data: PedidoProdutoCreate):
    """Adiciona um produto ao pedido."""
    logger.info("POST /pedidos/%s/itens produto=%s quantidade=%s", pedido_id, data.id_produto, data.quantidade)
    item = pedido_produto_service.add_produto_to_pedido(pedido_id, data)
    return PedidoProdutoPublic(
        id_pedido=item.id_pedido,
        id_produto=item.id_produto,
        quantidade=item.quantidade,
        produto_nome=item.produto_nome,
        produto_preco=item.produto_preco,
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None
    )

@router.get("/", response_model=list[PedidoProdutoPublic])
def get_itens_pedido(pedido_id: int):
    """Lista todos os itens de um pedido."""
    logger.info("GET /pedidos/%s/itens", pedido_id)
    itens = pedido_produto_service.get_itens_pedido(pedido_id)
    return [
        PedidoProdutoPublic(
            id_pedido=item.id_pedido,
            id_produto=item.id_produto,
            quantidade=item.quantidade,
            produto_nome=item.produto_nome,
            produto_preco=item.produto_preco,
            created_at=item.created_at.isoformat() if item.created_at else None,
            updated_at=item.updated_at.isoformat() if item.updated_at else None
        )
        for item in itens
    ]

@router.put("/{produto_id}", response_model=PedidoProdutoPublic)
def update_quantidade_produto(pedido_id: int, produto_id: int, data: PedidoProdutoUpdate):
    """Atualiza quantidade de um produto no pedido."""
    logger.info("PUT /pedidos/%s/itens/%s quantidade=%s", pedido_id, produto_id, data.quantidade)
    item = pedido_produto_service.update_quantidade_produto(pedido_id, produto_id, data)
    return PedidoProdutoPublic(
        id_pedido=item.id_pedido,
        id_produto=item.id_produto,
        quantidade=item.quantidade,
        produto_nome=item.produto_nome,
        produto_preco=item.produto_preco,
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None
    )

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_produto_from_pedido(pedido_id: int, produto_id: int):
    """Remove um produto do pedido e devolve ao estoque."""
    logger.info("DELETE /pedidos/%s/itens/%s", pedido_id, produto_id)
    pedido_produto_service.remove_produto_from_pedido(pedido_id, produto_id)
    return None
