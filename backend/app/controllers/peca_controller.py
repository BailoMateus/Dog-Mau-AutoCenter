import logging

from fastapi import APIRouter, HTTPException, status

from app.services import peca_service
from app.schemas.peca_schema import PecaCreate, PecaUpdate, PecaPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pecas", tags=["Peças"])

@router.get("", response_model=list[PecaPublic])
def list_pecas():
    """Lista todas as peças."""
    logger.info("GET /pecas")
    pecas = peca_service.list_pecas()
    return [
        PecaPublic(
            id_peca=p.id_peca,
            nome=p.nome,
            preco_unitario=p.preco_unitario,
            quantidade_estoque=p.quantidade_estoque,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in pecas
    ]

@router.post("", response_model=PecaPublic, status_code=status.HTTP_201_CREATED)
def create_peca(data: PecaCreate):
    """Cria uma nova peça."""
    logger.info("POST /pecas nome=%s", data.nome)
    peca = peca_service.create_peca(data)
    return PecaPublic(
        id_peca=peca.id_peca,
        nome=peca.nome,
        preco_unitario=peca.preco_unitario,
        quantidade_estoque=peca.quantidade_estoque,
        created_at=peca.created_at,
        updated_at=peca.updated_at
    )

@router.get("/{peca_id}", response_model=PecaPublic)
def get_peca(peca_id: int):
    """Busca uma peça pelo ID."""
    logger.info("GET /pecas/%s", peca_id)
    peca = peca_service.get_peca_or_404(peca_id)
    return PecaPublic(
        id_peca=peca.id_peca,
        nome=peca.nome,
        preco_unitario=peca.preco_unitario,
        quantidade_estoque=peca.quantidade_estoque,
        created_at=peca.created_at,
        updated_at=peca.updated_at
    )

@router.patch("/{peca_id}", response_model=PecaPublic)
def update_peca(peca_id: int, data: PecaUpdate):
    """Atualiza os dados de uma peça."""
    logger.info("PATCH /pecas/%s", peca_id)
    peca = peca_service.update_peca(peca_id, data)
    return PecaPublic(
        id_peca=peca.id_peca,
        nome=peca.nome,
        preco_unitario=peca.preco_unitario,
        quantidade_estoque=peca.quantidade_estoque,
        created_at=peca.created_at,
        updated_at=peca.updated_at
    )

@router.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_peca(peca_id: int):
    """Remove uma peça (soft delete)."""
    logger.info("DELETE /pecas/%s", peca_id)
    peca_service.delete_peca(peca_id)
    return None