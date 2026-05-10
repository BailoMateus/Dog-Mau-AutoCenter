import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Produto
from app.repositories import produto_repository as repo
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate

logger = logging.getLogger(__name__)

def list_produtos():
    """Lista todos os produtos."""
    return repo.get_all_produtos()

def get_produto_or_404(produto_id: int) -> Produto:
    """Busca produto por ID ou retorna 404."""
    produto = repo.get_produto_by_id(produto_id)
    if not produto:
        logger.info("produto não encontrado id=%s", produto_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto

def validate_produto_data(nome: str = None, preco: float = None, quantidade_estoque: int = None, exclude_id: int = None):
    """Valida dados do produto."""
    # Validação de nome duplicado
    if nome:
        if repo.check_produto_exists_by_nome(nome, exclude_id):
            logger.warning("nome de produto duplicado nome=%s", nome)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Nome de produto já cadastrado"
            )
    
    # Validação de preço
    if preco is not None and preco < 0:
        logger.warning("preço inválido preco=%s", preco)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preço deve ser maior ou igual a zero"
        )
    
    # Validação de quantidade em estoque
    if quantidade_estoque is not None and quantidade_estoque < 0:
        logger.warning("quantidade em estoque inválida quantidade=%s", quantidade_estoque)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade em estoque deve ser maior ou igual a zero"
        )

def create_produto(data: ProdutoCreate):
    """Cria um novo produto com validações."""
    # Validações
    validate_produto_data(
        nome=data.nome,
        preco=float(data.preco),
        quantidade_estoque=data.quantidade_estoque if hasattr(data, 'quantidade_estoque') and data.quantidade_estoque is not None else 0
    )
    
    # Cria entidade Produto
    produto = Produto(
        nome=data.nome,
        descricao=data.descricao or "",
        preco=float(data.preco),
        quantidade_estoque=data.quantidade_estoque if hasattr(data, 'quantidade_estoque') and data.quantidade_estoque is not None else 0
    )
    
    try:
        return repo.create_produto(produto)
    except psycopg2.IntegrityError:
        logger.error("create_produto erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar produto"
        )

def update_produto(produto_id: int, data: ProdutoUpdate):
    """Atualiza um produto com validações."""
    produto = get_produto_or_404(produto_id)
    
    # Validações (exclui o ID atual da verificação de duplicidade)
    validate_produto_data(
        nome=data.nome,
        preco=float(data.preco) if data.preco is not None else None,
        quantidade_estoque=data.quantidade_estoque if data.quantidade_estoque is not None else None,
        exclude_id=produto_id
    )
    
    # Atualiza campos
    if data.nome is not None:
        produto.nome = data.nome
    if data.descricao is not None:
        produto.descricao = data.descricao
    if data.preco is not None:
        produto.preco = float(data.preco)
    if data.quantidade_estoque is not None:
        produto.quantidade_estoque = data.quantidade_estoque
    
    try:
        return repo.update_produto(produto)
    except psycopg2.IntegrityError:
        logger.error("update_produto erro de integridade id=%s", produto_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar produto"
        )

def delete_produto(produto_id: int):
    """Remove (soft delete) um produto."""
    produto = get_produto_or_404(produto_id)
    return repo.soft_delete_produto(produto)