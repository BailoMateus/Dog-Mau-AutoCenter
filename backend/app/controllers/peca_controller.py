import logging

from fastapi import APIRouter, File, Form, Request, UploadFile, status

from app.schemas.peca_schema import PecaCreate, PecaPublic, PecaUpdate
from app.services import peca_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pecas", tags=["Peças"])


def _to_public(peca) -> PecaPublic:
    return PecaPublic(
        id_peca=peca.id_peca,
        nome=peca.nome,
        preco_unitario=peca.preco_unitario,
        quantidade_estoque=peca.quantidade_estoque,
        imagem_peca=peca.imagem_peca,
        created_at=peca.created_at,
        updated_at=peca.updated_at,
    )


async def _parse_create_request(request: Request) -> tuple[PecaCreate, UploadFile | None]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        arquivo = form.get("imagem_peca")
        upload = arquivo if isinstance(arquivo, UploadFile) else None
        data = peca_service.parse_peca_form_fields(
            nome=form.get("nome"),
            preco_unitario=form.get("preco_unitario"),
            quantidade_estoque=form.get("quantidade_estoque"),
            is_create=True,
        )
        return data, upload
    body = await request.json()
    return PecaCreate(**body), None


async def _parse_update_request(request: Request) -> tuple[PecaUpdate, UploadFile | None]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        arquivo = form.get("imagem_peca")
        upload = arquivo if isinstance(arquivo, UploadFile) else None
        data = peca_service.parse_peca_form_fields(
            nome=form.get("nome"),
            preco_unitario=form.get("preco_unitario"),
            quantidade_estoque=form.get("quantidade_estoque"),
            is_create=False,
        )
        return data, upload
    body = await request.json()
    return PecaUpdate(**body), None


@router.get("", response_model=list[PecaPublic])
def list_pecas():
    logger.info("GET /pecas")
    pecas = peca_service.list_pecas()
    return [_to_public(p) for p in pecas]


@router.post("", response_model=PecaPublic, status_code=status.HTTP_201_CREATED)
async def create_peca(request: Request):
    data, imagem_peca = await _parse_create_request(request)
    logger.info("POST /pecas nome=%s multipart=%s", data.nome, imagem_peca is not None)
    if imagem_peca:
        peca = peca_service.create_peca_with_image(data, imagem_peca)
    else:
        peca = peca_service.create_peca(data)
    return _to_public(peca)


@router.get("/{peca_id}", response_model=PecaPublic)
def get_peca(peca_id: int):
    logger.info("GET /pecas/%s", peca_id)
    peca = peca_service.get_peca_or_404(peca_id)
    return _to_public(peca)


@router.patch("/{peca_id}", response_model=PecaPublic)
async def update_peca(peca_id: int, request: Request):
    data, imagem_peca = await _parse_update_request(request)
    logger.info("PATCH /pecas/%s multipart=%s", peca_id, imagem_peca is not None)
    if imagem_peca:
        peca = peca_service.update_peca_with_image(peca_id, data, imagem_peca)
    else:
        peca = peca_service.update_peca(peca_id, data)
    return _to_public(peca)


@router.post("/{peca_id}/imagem-peca", response_model=PecaPublic)
def upload_peca_imagem_peca(
    peca_id: int,
    imagem_peca: UploadFile = File(...),
):
    logger.info("POST /pecas/%s/imagem-peca", peca_id)
    peca = peca_service.save_peca_imagem_peca(peca_id, imagem_peca)
    return _to_public(peca)


@router.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_peca(peca_id: int):
    logger.info("DELETE /pecas/%s", peca_id)
    peca_service.delete_peca(peca_id)
