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
    # Validação de usuario existente
    if usuario_id and not repo.check_usuario_exists(usuario_id):
        logger.warning("usuario não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario não encontrado"
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
    status_anterior = pedido.status
    if data.id_usuario is not None:
        pedido.id_usuario = data.id_usuario
    if data.valor_total is not None:
        pedido.valor_total = float(data.valor_total)
    if data.status is not None:
        pedido.status = data.status
    
    try:
        updated_pedido = repo.update_pedido(pedido)
        
        # --- Lógica de Automação de Estoque e Financeiro ---
        if status_anterior != "concluido" and pedido.status == "concluido":
            from app.repositories import pedido_produto_repository
            from app.repositories import movimentacao_estoque_repository
            from app.repositories import movimentacao_financeira_repository
            
            # 1. Baixar estoque dos produtos
            produtos_do_pedido = pedido_produto_repository.get_itens_by_pedido(pedido_id)
            for pp in produtos_do_pedido:
                try:
                    movimentacao_estoque_repository.registrar_saida_estoque_produto(
                        produto_id=pp.id_produto,
                        quantidade=pp.quantidade,
                        motivo=f"Venda no Pedido #{pedido_id}"
                    )
                except Exception as e:
                    logger.error("Erro ao dar baixa no estoque do produto=%s: %s", pp.id_produto, e)
            
            # 2. Registrar Entrada Financeira
            valor_total = float(pedido.valor_total) if pedido.valor_total else 0.0
            if valor_total > 0:
                movimentacao_financeira_repository.registrar_entrada_financeira(
                    valor=valor_total,
                    descricao=f"Faturamento do Pedido #{pedido_id}"
                )
        # ----------------------------------------------------
        
        return updated_pedido
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
    """Lista pedidos de um usuario específico."""
    if not repo.check_usuario_exists(usuario_id):
        logger.warning("usuario não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )
    
    return repo.get_pedidos_by_usuario(usuario_id)
