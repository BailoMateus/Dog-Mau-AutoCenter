import logging

from fastapi import APIRouter, HTTPException, status

from app.services import produto_service
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate, ProdutoPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoPublic, status_code=status.HTTP_201_CREATED)
def create_produto(data: ProdutoCreate):
    """Cria um novo produto."""
    logger.info("POST /produtos nome=%s", data.nome)
    produto = produto_service.create_produto(data)
    return ProdutoPublic(
        id_produto=produto.id_produto,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        quantidade_estoque=produto.quantidade_estoque,
        created_at=produto.created_at,
        updated_at=produto.updated_at
    )

@router.get("/", response_model=list[ProdutoPublic])
def list_produtos():
    """Lista todos os produtos."""
    logger.info("GET /produtos")
    produtos = produto_service.list_produtos()
    return [
        ProdutoPublic(
            id_produto=p.id_produto,
            nome=p.nome,
            descricao=p.descricao,
            preco=p.preco,
            quantidade_estoque=p.quantidade_estoque,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in produtos
    ]

@router.get("/{produto_id}", response_model=ProdutoPublic)
def get_produto(produto_id: int):
    """Busca um produto por ID."""
    logger.info("GET /produtos/%s", produto_id)
    produto = produto_service.get_produto_or_404(produto_id)
    return ProdutoPublic(
        id_produto=produto.id_produto,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        quantidade_estoque=produto.quantidade_estoque,
        created_at=produto.created_at,
        updated_at=produto.updated_at
    )

@router.put("/{produto_id}", response_model=ProdutoPublic)
def update_produto(produto_id: int, data: ProdutoUpdate):
    """Atualiza um produto existente."""
    logger.info("PUT /produtos/%s", produto_id)
    produto = produto_service.update_produto(produto_id, data)
    return ProdutoPublic(
        id_produto=produto.id_produto,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        quantidade_estoque=produto.quantidade_estoque,
        created_at=produto.created_at,
        updated_at=produto.updated_at
    )

@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produto(produto_id: int):
    """Remove um produto (soft delete)."""
    logger.info("DELETE /produtos/%s", produto_id)
    produto_service.delete_produto(produto_id)
    return None
