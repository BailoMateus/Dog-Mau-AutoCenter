import logging
from decimal import Decimal

from fastapi import APIRouter, File, Form, Request, UploadFile, status

from app.schemas.produto_schema import ProdutoCreate, ProdutoPublic, ProdutoUpdate
from app.services import produto_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])


def _to_public(produto):
    return ProdutoPublic(
        id_produto=produto.id_produto,
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        quantidade_estoque=produto.quantidade_estoque,
        imagem_produto=produto.imagem_produto,
        created_at=produto.created_at,
        updated_at=produto.updated_at,
    )


async def _parse_create_request(request: Request) -> tuple[ProdutoCreate, UploadFile | None]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        arquivo = form.get("imagem_produto")
        upload = arquivo if isinstance(arquivo, UploadFile) else None
        data = produto_service.parse_produto_form_fields(
            nome=form.get("nome"),
            descricao=form.get("descricao"),
            preco=form.get("preco"),
            quantidade_estoque=form.get("quantidade_estoque"),
            is_create=True,
        )
        return data, upload
    body = await request.json()
    return ProdutoCreate(**body), None


async def _parse_update_request(request: Request) -> tuple[ProdutoUpdate, UploadFile | None]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        arquivo = form.get("imagem_produto")
        upload = arquivo if isinstance(arquivo, UploadFile) else None
        data = produto_service.parse_produto_form_fields(
            nome=form.get("nome"),
            descricao=form.get("descricao"),
            preco=form.get("preco"),
            quantidade_estoque=form.get("quantidade_estoque"),
            is_create=False,
        )
        return data, upload
    body = await request.json()
    return ProdutoUpdate(**body), None


@router.post("", response_model=ProdutoPublic, status_code=status.HTTP_201_CREATED)
async def create_produto(request: Request):
    data, imagem_produto = await _parse_create_request(request)
    logger.info("POST /produtos nome=%s multipart=%s", data.nome, imagem_produto is not None)
    if imagem_produto:
        produto = produto_service.create_produto_with_image(data, imagem_produto)
    else:
        produto = produto_service.create_produto(data)
    return _to_public(produto)


@router.post("/form", response_model=ProdutoPublic, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_produto_form(
    nome: str = Form(...),
    preco: Decimal = Form(...),
    descricao: str | None = Form(None),
    quantidade_estoque: int = Form(0),
    imagem_produto: UploadFile | None = File(None),
):
    data = ProdutoCreate(
        nome=nome,
        descricao=descricao,
        preco=preco,
        quantidade_estoque=quantidade_estoque,
    )
    produto = produto_service.create_produto_with_image(data, imagem_produto)
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
async def update_produto(produto_id: int, request: Request):
    data, imagem_produto = await _parse_update_request(request)
    logger.info("PATCH /produtos/%s multipart=%s", produto_id, imagem_produto is not None)
    if imagem_produto:
        produto = produto_service.update_produto_with_image(produto_id, data, imagem_produto)
    else:
        produto = produto_service.update_produto(produto_id, data)
    return _to_public(produto)


@router.post("/{produto_id}/imagem-produto", response_model=ProdutoPublic)
def upload_produto_imagem_produto(
    produto_id: int,
    imagem_produto: UploadFile = File(...),
):
    logger.info("POST /produtos/%s/imagem-produto", produto_id)
    produto = produto_service.save_produto_imagem_produto(produto_id, imagem_produto)
    return _to_public(produto)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produto(produto_id: int):
    logger.info("DELETE /produtos/%s", produto_id)
    produto_service.delete_produto(produto_id)
