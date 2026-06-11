import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import PedidoPeca
from app.repositories import pedido_repository as pedido_repo
from app.repositories import peca_repository as peca_repo
from app.repositories import pedido_peca_repository as repo
from app.repositories import pedido_produto_repository as pedido_produto_repo
from app.repositories import os_peca_repository as peca_estoque_repo
from app.schemas.pedido_peca_schema import PedidoPecaCreate

logger = logging.getLogger(__name__)


def _recalcular_valor_total(pedido_id: int):
    """Atualiza o valor_total do pedido somando produtos + peças."""
    total_produtos = float(pedido_produto_repo.calcular_valor_total_pedido(pedido_id) or 0)
    total_pecas = repo.calcular_valor_total_pecas(pedido_id)
    pedido_produto_repo.update_valor_total_pedido(pedido_id, total_produtos + total_pecas)


def get_itens_pedido(pedido_id: int):
    """Lista as peças de um pedido."""
    pedido = pedido_repo.get_pedido_by_id(pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    return repo.get_itens_by_pedido(pedido_id)


def add_peca_to_pedido(pedido_id: int, data: PedidoPecaCreate):
    """Adiciona uma peça ao pedido com validação de existência e estoque."""
    pedido = pedido_repo.get_pedido_by_id(pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")

    peca = peca_repo.get_peca_by_id(data.id_peca)
    if not peca:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada")

    if data.quantidade <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantidade deve ser maior que zero")

    estoque = peca_estoque_repo.get_peca_estoque(data.id_peca)
    if estoque < data.quantidade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {estoque}, Solicitado: {data.quantidade}",
        )

    item = PedidoPeca(id_pedido=pedido_id, id_peca=data.id_peca, quantidade=data.quantidade)

    try:
        repo.add_peca_to_pedido(item)

        # Baixa de estoque no momento da inclusão (mesmo padrão de pedido_produto)
        peca_estoque_repo.update_peca_estoque(data.id_peca, estoque - data.quantidade)

        # Recalcula o valor total do pedido (produtos + peças)
        _recalcular_valor_total(pedido_id)

        logger.info("peça adicionada ao pedido pedido=%s peca=%s quantidade=%s",
                    pedido_id, data.id_peca, data.quantidade)

        item_com_info = repo.get_pedido_peca(pedido_id, data.id_peca)
        return item_com_info
    except psycopg2.IntegrityError:
        logger.error("add_peca_to_pedido erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar peça ao pedido",
        )
