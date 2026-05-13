import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Peca
from app.repositories import peca_repository as repo
from app.schemas.peca_schema import PecaCreate, PecaUpdate

logger = logging.getLogger(__name__)

def list_pecas():
    """Lista todas as peças disponíveis."""
    pecas = repo.get_all_pecas()
    logger.debug("list_pecas count=%s", len(pecas))
    return pecas

def get_peca_or_404(peca_id: int) -> Peca:
    """Busca uma peça pelo ID ou retorna 404."""
    peca = repo.get_peca_by_id(peca_id)
    if not peca:
        logger.info("peça não encontrada id=%s", peca_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peça não encontrada")
    return peca

def validate_peca_data(preco_unitario: float = None, quantidade_estoque: int = None):
    """Valida dados da peça."""
    if preco_unitario is not None and preco_unitario < 0:
        logger.warning("preço unitário inválido preco=%s", preco_unitario)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preço unitário não pode ser negativo"
        )
    
    if quantidade_estoque is not None and quantidade_estoque < 0:
        logger.warning("quantidade em estoque inválida quantidade=%s", quantidade_estoque)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade em estoque não pode ser negativa"
        )

def create_peca(data: PecaCreate):
    """Cria uma nova peça."""
    # Validações
    validate_peca_data(data.valor_unitario, data.quantidade_estoque)
    
    # Cria entidade Peca
    peca = Peca(
        nome=data.nome,
        valor_unitario=data.valor_unitario,
        quantidade_estoque=data.quantidade_estoque
    )
    
    try:
        return repo.create_peca(peca)
    except psycopg2.IntegrityError:
        logger.error("create_peca erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar peça"
        )

def update_peca(peca_id: int, data: PecaUpdate):
    """Atualiza os dados de uma peça existente."""
    peca = get_peca_or_404(peca_id)
    
    # Validações
    validate_peca_data(data.valor_unitario, data.quantidade_estoque)
    
    # Atualiza campos
    if data.nome is not None:
        peca.nome = data.nome
    if data.valor_unitario is not None:
        peca.valor_unitario = data.valor_unitario
    if data.quantidade_estoque is not None:
        peca.quantidade_estoque = data.quantidade_estoque
    
    try:
        return repo.update_peca(peca)
    except psycopg2.IntegrityError:
        logger.error("update_peca erro de integridade id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar peça"
        )

def delete_peca(peca_id: int):
    """Remove uma peça (soft delete)."""
    peca = get_peca_or_404(peca_id)
    return repo.soft_delete_peca(peca)