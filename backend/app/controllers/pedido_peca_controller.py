import logging

from fastapi import APIRouter, Depends, status

from app.services import pedido_peca_service
from app.schemas.pedido_peca_schema import PedidoPecaCreate, PedidoPecaPublic
from app.middlewares.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pedidos/{pedido_id}/pecas", tags=["Peças do Pedido"])


def _to_public(item) -> PedidoPecaPublic:
    return PedidoPecaPublic(
        id_pedido=item.id_pedido,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco,
        created_at=item.created_at.isoformat() if item.created_at else None,
        updated_at=item.updated_at.isoformat() if item.updated_at else None,
    )


@router.post("", response_model=PedidoPecaPublic, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=PedidoPecaPublic, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_peca_to_pedido(pedido_id: int, data: PedidoPecaCreate, user=Depends(get_current_user)):
    """Adiciona uma peça ao pedido. Requer autenticação."""
    logger.info("POST /pedidos/%s/pecas usuario=%s peca=%s quantidade=%s",
                pedido_id, user["user_id"], data.id_peca, data.quantidade)
    item = pedido_peca_service.add_peca_to_pedido(pedido_id, data)
    return _to_public(item)


@router.get("", response_model=list[PedidoPecaPublic])
@router.get("/", response_model=list[PedidoPecaPublic], include_in_schema=False)
def get_pecas_pedido(pedido_id: int):
    """Lista as peças de um pedido."""
    logger.info("GET /pedidos/%s/pecas", pedido_id)
    itens = pedido_peca_service.get_itens_pedido(pedido_id)
    return [_to_public(item) for item in itens]
