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

def list_pedidos_detalhados():
    """Lista todos os pedidos com detalhes de cliente e itens (produtos e peças)."""
    from app.repositories import pedido_peca_repository as pedido_peca_repo

    pedidos_raw = repo.get_all_pedidos_detalhado()

    # Agregar itens (produtos + peças) de cada pedido
    for p in pedidos_raw:
        p['itens'] = pedido_produto_repo.get_itens_by_pedido(p['id_pedido'])
        p['itens_peca'] = pedido_peca_repo.get_itens_by_pedido(p['id_pedido'])

    return pedidos_raw

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

def create_pedido_for_user(user_id: int, data: PedidoCreate):
    """Cria um novo pedido para um usuário autenticado.
    
    O user_id é extraído do token JWT autenticado.
    Isso impede que clientes criem pedidos em nome de outros usuários.
    """
    # Validações
    validate_pedido_data(
        usuario_id=user_id,
        valor_total=float(data.valor_total)
    )
    
    # Cria entidade Pedido com user_id do usuário autenticado
    pedido = Pedido(
        id_usuario=user_id,
        valor_total=float(data.valor_total),
        status=data.status or "processando"
    )
    
    try:
        return repo.create_pedido(pedido)
    except psycopg2.IntegrityError:
        logger.error("create_pedido_for_user erro de integridade user_id=%s", user_id)
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

        # --- Movimentação financeira automática na conclusão do pedido ---
        # Requisito 3: pedido concluído gera ENTRADA com a soma dos produtos e a
        # soma das peças vendidas. (O estoque já é baixado no momento em que cada
        # item é adicionado ao pedido — não há baixa duplicada aqui.)
        if status_anterior != "concluido" and pedido.status == "concluido":
            from app.repositories import pedido_produto_repository
            from app.repositories import pedido_peca_repository
            from app.repositories import movimentacao_financeira_repository

            total_produtos = float(pedido_produto_repository.calcular_valor_total_pedido(pedido_id) or 0)
            total_pecas = float(pedido_peca_repository.calcular_valor_total_pecas(pedido_id) or 0)

            if total_produtos > 0:
                movimentacao_financeira_repository.registrar_entrada_financeira(
                    valor=total_produtos,
                    descricao=f"Venda de produtos - Pedido #{pedido_id}"
                )
            if total_pecas > 0:
                movimentacao_financeira_repository.registrar_entrada_financeira(
                    valor=total_pecas,
                    descricao=f"Venda de peças - Pedido #{pedido_id}"
                )
            # Pedido manual (sem itens vinculados) mas com valor informado
            if total_produtos == 0 and total_pecas == 0:
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

def get_pedidos_detalhados_by_usuario(usuario_id: int):
    """Lista pedidos de um usuario específico com seus itens."""
    if not repo.check_usuario_exists(usuario_id):
        logger.warning("usuario não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )
    
    from app.models.entities import pedido_to_dict
    from app.repositories import pedido_peca_repository as pedido_peca_repo
    pedidos = repo.get_pedidos_by_usuario(usuario_id)
    pedidos_detalhados = []
    for p in pedidos:
        p_dict = pedido_to_dict(p)
        p_dict['itens'] = pedido_produto_repo.get_itens_by_pedido(p.id_pedido)
        p_dict['itens_peca'] = pedido_peca_repo.get_itens_by_pedido(p.id_pedido)
        pedidos_detalhados.append(p_dict)

    return pedidos_detalhados
