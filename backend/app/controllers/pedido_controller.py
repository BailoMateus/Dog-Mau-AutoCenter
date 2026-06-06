import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.services import pedido_service
from app.schemas.pedido_schema import PedidoCreate, PedidoUpdate, PedidoPublic
from app.middlewares.auth_middleware import get_current_user
from app.core.security import require_role
from app.core.roles import ADMIN, MECANICO

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])

@router.get("", response_model=list[PedidoPublic])
def list_pedidos(_=Depends(require_role([ADMIN, MECANICO]))):
    """Lista todos os pedidos."""
    logger.info("GET /pedidos")
    pedidos = pedido_service.list_pedidos()
    return [
        PedidoPublic(
            id_pedido=p.id_pedido,
            id_usuario=p.id_usuario,
            valor_total=p.valor_total,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pedidos
    ]

# AJUSTE DE CONCORRÊNCIA: Mudado para async def para lidar de forma nativa com as travas de banco e filas
@router.post("", response_model=PedidoPublic, status_code=status.HTTP_201_CREATED)
async def create_pedido(data: PedidoCreate, user=Depends(get_current_user)):
    """Cria um novo pedido. Requer autenticação de qualquer nível."""
    logger.info("POST /pedidos usuario=%s valor=%s", user["user_id"], data.valor_total)
    
    # Se o ator não for admin/mecanico, ele jamais pode injetar um id_usuario de terceiros no payload
    if user["role"] not in [ADMIN, MECANICO]:
        data.id_usuario = int(user["user_id"])
    elif data.id_usuario is None:
        data.id_usuario = int(user["user_id"])
        
    pedido = pedido_service.create_pedido(data)
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.get("/{pedido_id}", response_model=PedidoPublic)
def get_pedido(pedido_id: int, user=Depends(get_current_user)):
    """Busca um pedido por ID com isolamento estrito de visibilidade."""
    logger.info("GET /pedidos/%s", pedido_id)
    pedido = pedido_service.get_pedido_or_404(pedido_id)
    
    # Se o pedido não pertence ao cliente logado e o ator não é corporativo, barra o acesso imediatamente
    if user["role"] not in [ADMIN, MECANICO] and int(user["user_id"]) != pedido.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado a este registro de compra")
        
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.patch("/{pedido_id}", response_model=PedidoPublic)
def update_pedido(pedido_id: int, data: PedidoUpdate, _=Depends(require_role([ADMIN, MECANICO]))):
    """Atualiza um pedido existente (Ex: Alterar status para faturado ou entregue)."""
    logger.info("PATCH /pedidos/%s", pedido_id)
    pedido = pedido_service.update_pedido(pedido_id, data)
    return PedidoPublic(
        id_pedido=pedido.id_pedido,
        id_usuario=pedido.id_usuario,
        valor_total=pedido.valor_total,
        status=pedido.status,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at
    )

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedido(pedido_id: int, _=Depends(require_role([ADMIN, MECANICO]))):
    """Remove um pedido (soft delete)."""
    logger.info("DELETE /pedidos/%s", pedido_id)
    pedido_service.delete_pedido(pedido_id)
    return None

@router.get("/usuario/{usuario_id}", response_model=list[PedidoPublic])
def get_pedidos_by_usuario(usuario_id: int, user=Depends(get_current_user)):
    """Lista pedidos de um usuario específico."""
    logger.info("GET /pedidos/usuario/%s", usuario_id)
    if user["role"] not in [ADMIN, MECANICO] and int(user["user_id"]) != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")
    pedidos = pedido_service.get_pedidos_by_usuario(usuario_id)
    return [
        PedidoPublic(
            id_pedido=p.id_pedido,
            id_usuario=p.id_usuario,
            valor_total=p.valor_total,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pedidos
    ]