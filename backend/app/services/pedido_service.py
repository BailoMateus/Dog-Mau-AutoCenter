import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Pedido
from app.repositories import pedido_repository as repo
from app.repositories import pedido_produto_repository as pedido_produto_repo
from app.schemas.pedido_schema import PedidoCreate, PedidoUpdate

logger = logging.getLogger(__name__)

def list_pedidos():
    """Lista todos os pedidos."""
    return repo.get_all_pedidos()

def get_pedido_or_404(pedido_id: int) -> Pedido:
    """Busca pedido por ID ou retorna 404."""
    pedido = repo.get_pedido_by_id(pedido_id)
    if not pedido:
        logger.info("pedido não encontrado id=%s", pedido_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    return pedido

def validate_pedido_data(usuario_id: int = None, valor_total: float = None):
    """Valida dados do pedido."""
    # Validação de usuário existente
    if usuario_id and not repo.check_usuario_exists(usuario_id):
        logger.warning("usuário não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não encontrado"
        )
    
    # Validação de valor total
    if valor_total is not None and valor_total < 0:
        logger.warning("valor total inválido valor_total=%s", valor_total)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor total deve ser maior ou igual a zero"
        )

def create_pedido(data: PedidoCreate):
    """Cria um novo pedido com validações."""
    # Validações
    validate_pedido_data(
        usuario_id=data.id_usuario,
        valor_total=float(data.valor_total)
    )
    
    # Cria entidade Pedido com valor_total inicial (será recalculado quando itens forem adicionados)
    pedido = Pedido(
        id_usuario=data.id_usuario,
        valor_total=float(data.valor_total),
        status=data.status or "processando"
    )
    
    try:
        return repo.create_pedido(pedido)
    except psycopg2.IntegrityError:
        logger.error("create_pedido erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar pedido"
        )

def update_pedido(pedido_id: int, data: PedidoUpdate):
    """Atualiza um pedido com validações."""
    pedido = get_pedido_or_404(pedido_id)
    
    # Validações
    validate_pedido_data(
        usuario_id=data.id_usuario,
        valor_total=float(data.valor_total) if data.valor_total is not None else None
    )
    
    # Atualiza campos
    if data.id_usuario is not None:
        pedido.id_usuario = data.id_usuario
    if data.valor_total is not None:
        pedido.valor_total = float(data.valor_total)
    if data.status is not None:
        pedido.status = data.status
    
    try:
        return repo.update_pedido(pedido)
    except psycopg2.IntegrityError:
        logger.error("update_pedido erro de integridade id=%s", pedido_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar pedido"
        )

def delete_pedido(pedido_id: int):
    """Remove (soft delete) um pedido."""
    pedido = get_pedido_or_404(pedido_id)
    return repo.soft_delete_pedido(pedido)

def get_pedidos_by_usuario(usuario_id: int):
    """Lista pedidos de um usuário específico."""
    if not repo.check_usuario_exists(usuario_id):
        logger.warning("usuário não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return repo.get_pedidos_by_usuario(usuario_id)
