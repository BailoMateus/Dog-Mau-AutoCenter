import logging
from app.models.entities import Peca
from app.repositories.peca_repository import (
    get_peca_by_id,
    get_all_pecas,
    create_peca,
    update_peca,
    soft_delete_peca,
)

logger = logging.getLogger(__name__)

def listar_pecas():
    """Lista todas as peças disponíveis."""
    pecas = get_all_pecas()
    logger.debug("listar_pecas count=%s", len(pecas))
    return pecas

def buscar_peca_por_id(peca_id: int):
    """Busca uma peça pelo ID."""
    peca = get_peca_by_id(peca_id)
    if not peca:
        logger.warning("buscar_peca_por_id id=%s not found", peca_id)
        raise ValueError("Peça não encontrada.")
    return peca

def criar_peca(nome: str, preco_unitario: float, quantidade_estoque: int = 0):
    """Cria uma nova peça."""
    if preco_unitario < 0:
        raise ValueError("O preço unitário não pode ser negativo.")
    if quantidade_estoque < 0:
        raise ValueError("A quantidade em estoque não pode ser negativa.")

    nova_peca = Peca(nome=nome, preco_unitario=preco_unitario, quantidade_estoque=quantidade_estoque)
    peca = create_peca(nova_peca)
    logger.info("criar_peca id=%s nome=%s", peca.id_peca, peca.nome)
    return peca

def atualizar_peca(peca_id: int, nome: str, preco_unitario: float, quantidade_estoque: int):
    """Atualiza os dados de uma peça existente."""
    peca = buscar_peca_por_id(peca_id)

    if preco_unitario < 0:
        raise ValueError("O preço unitário não pode ser negativo.")
    if quantidade_estoque < 0:
        raise ValueError("A quantidade em estoque não pode ser negativa.")

    peca.nome = nome
    peca.preco_unitario = preco_unitario
    peca.quantidade_estoque = quantidade_estoque
    peca = update_peca(peca)
    logger.info("atualizar_peca id=%s", peca.id_peca)
    return peca

def remover_peca(peca_id: int):
    """Remove uma peça (soft delete)."""
    peca = buscar_peca_por_id(peca_id)
    peca = soft_delete_peca(peca)
    logger.info("remover_peca id=%s", peca.id_peca)
    return peca