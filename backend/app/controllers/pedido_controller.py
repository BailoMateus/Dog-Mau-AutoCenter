import logging

from fastapi import APIRouter, HTTPException, status

from app.services import pedido_service
from app.schemas.pedido_schema import PedidoCreate, PedidoUpdate, PedidoPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("/", response_model=PedidoPublic, status_code=status.HTTP_201_CREATED)
def create_pedido(data: PedidoCreate):
    """Cria um novo pedido."""
    logger.info("POST /pedidos cliente=%s valor=%s", data.id_cliente, data.valor_total)
    pedido = pedido_service.create_pedido(data)
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_cliente=pedido.id_cliente,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.get("/", response_model=list[PedidoPublic])
def list_pedidos():
    """Lista todos os pedidos."""
    logger.info("GET /pedidos")
    pedidos = pedido_service.list_pedidos()
    return [
        PedidoPublic(
            id_pedido=p.id_pedido,
            id_cliente=p.id_cliente,
            valor_total=p.valor_total,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pedidos
    ]

@router.get("/{pedido_id}", response_model=PedidoPublic)
def get_pedido(pedido_id: int):
    """Busca um pedido por ID."""
    logger.info("GET /pedidos/%s", pedido_id)
    pedido = pedido_service.get_pedido_or_404(pedido_id)
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_cliente=pedido.id_cliente,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.put("/{pedido_id}", response_model=PedidoPublic)
def update_pedido(pedido_id: int, data: PedidoUpdate):
    """Atualiza um pedido existente."""
    logger.info("PUT /pedidos/%s", pedido_id)
    pedido = pedido_service.update_pedido(pedido_id, data)
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_cliente=pedido.id_cliente,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedido(pedido_id: int):
    """Remove um pedido (soft delete)."""
    logger.info("DELETE /pedidos/%s", pedido_id)
    pedido_service.delete_pedido(pedido_id)
    return None

@router.get("/cliente/{cliente_id}", response_model=list[PedidoPublic])
def get_pedidos_by_cliente(cliente_id: int):
    """Lista pedidos de um cliente específico."""
    logger.info("GET /pedidos/cliente/%s", cliente_id)
    pedidos = pedido_service.get_pedidos_by_cliente(cliente_id)
    return [
        PedidoPublic(
            id_pedido=p.id_pedido,
            id_cliente=p.id_cliente,
            valor_total=p.valor_total,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pedidos
    ]
