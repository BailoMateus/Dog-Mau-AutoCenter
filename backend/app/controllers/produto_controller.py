import logging
from fastapi import APIRouter, status

from app.services import produto_service
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate, ProdutoPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _to_public(produto):
    return ProdutoPublic(
        id_produto=produto.id_produto,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        quantidade_estoque=produto.quantidade_estoque,
        created_at=produto.created_at,
        updated_at=produto.updated_at
    )


@router.post("", response_model=ProdutoPublic, status_code=status.HTTP_201_CREATED)
def create_produto(data: ProdutoCreate):
    logger.info("POST /produtos nome=%s", data.nome)
    produto = produto_service.create_produto(data)
    return _to_public(produto)


@router.get("", response_model=list[ProdutoPublic])
def list_produtos():
    logger.info("GET /produtos")
    produtos = produto_service.list_produtos()
    return [_to_public(p) for p in produtos]


@router.get("/{produto_id}", response_model=ProdutoPublic)
def get_produto(produto_id: int):
    logger.info("GET /produtos/%s", produto_id)
    produto = produto_service.get_produto_or_404(produto_id)
    return _to_public(produto)


@router.patch("/{produto_id}", response_model=ProdutoPublic)
def update_produto(produto_id: int, data: ProdutoUpdate):
    logger.info("PATCH /produtos/%s", produto_id)
    produto = produto_service.update_produto(produto_id, data)
    return _to_public(produto)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produto(produto_id: int):
    logger.info("DELETE /produtos/%s", produto_id)
    produto_service.delete_produto(produto_id)