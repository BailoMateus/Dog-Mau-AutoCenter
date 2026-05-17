import logging

from fastapi import APIRouter, HTTPException, status

from app.services import os_peca_service
from app.schemas.os_peca_schema import (
    OsPecaCreate, OsPecaUpdate, OsPecaPublic, MovimentacaoEstoquePublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordens-servico/{os_id}/pecas", tags=["Peças da OS"])

@router.post("/", response_model=OsPecaPublic, status_code=status.HTTP_201_CREATED)
def add_peca_to_os(os_id: int, data: OsPecaCreate):
    """Adiciona uma peça à ordem de serviço."""
    logger.info("POST /ordens-servico/%s/pecas peca=%s quantidade=%s", os_id, data.id_peca, data.quantidade)
    item = os_peca_service.add_peca_to_os(os_id, data)
    return OsPecaPublic(
        id_os=item.id_os,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco,
        peca_estoque=item.peca_estoque,
        subtotal=item.subtotal
    )

@router.get("/", response_model=list[OsPecaPublic])
def get_pecas_by_os(os_id: int):
    """Lista todas as peças de uma ordem de serviço."""
    logger.info("GET /ordens-servico/%s/pecas", os_id)
    itens = os_peca_service.get_pecas_by_os(os_id)
    return [
        OsPecaPublic(
            id_os=item.id_os,
            id_peca=item.id_peca,
            quantidade=item.quantidade,
            peca_nome=item.peca_nome,
            peca_preco=item.peca_preco,
            peca_estoque=item.peca_estoque,
            subtotal=item.subtotal
        )
        for item in itens
    ]

@router.get("/{peca_id}", response_model=OsPecaPublic)
def get_peca_by_os(os_id: int, peca_id: int):
    """Busca uma peça específica de uma ordem de serviço."""
    logger.info("GET /ordens-servico/%s/pecas/%s", os_id, peca_id)
    item = os_peca_service.get_peca_by_os(os_id, peca_id)
    return OsPecaPublic(
        id_os=item.id_os,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco,
        peca_estoque=item.peca_estoque,
        subtotal=item.subtotal
    )

@router.put("/{peca_id}", response_model=OsPecaPublic)
def update_quantidade_peca(os_id: int, peca_id: int, data: OsPecaUpdate):
    """Atualiza quantidade de uma peça na ordem de serviço."""
    logger.info("PUT /ordens-servico/%s/pecas/%s nova_quantidade=%s", os_id, peca_id, data.quantidade)
    item = os_peca_service.update_quantidade_peca(os_id, peca_id, data)
    return OsPecaPublic(
        id_os=item.id_os,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco,
        peca_estoque=item.peca_estoque,
        subtotal=item.subtotal
    )

@router.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_peca_from_os(os_id: int, peca_id: int):
    """Remove uma peça da ordem de serviço."""
    logger.info("DELETE /ordens-servico/%s/pecas/%s", os_id, peca_id)
    os_peca_service.remove_peca_from_os(os_id, peca_id)
    return None

@router.get("/valor-total", response_model=dict)
def get_valor_total_pecas(os_id: int):
    """Calcula valor total das peças da OS."""
    logger.info("GET /ordens-servico/%s/pecas/valor-total", os_id)
    valor_total = os_peca_service.calcular_valor_total_pecas(os_id)
    return {"valor_total_pecas": valor_total}

@router.get("/movimentacoes", response_model=list[MovimentacaoEstoquePublic])
def get_movimentacoes_by_os(os_id: int):
    """Lista movimentações de estoque da OS."""
    logger.info("GET /ordens-servico/%s/pecas/movimentacoes", os_id)
    movimentacoes = os_peca_service.get_movimentacoes_by_os(os_id)
    return [
        MovimentacaoEstoquePublic(
            id_movimentacao=mov.id_movimentacao,
            id_peca=mov.id_peca,
            id_os=mov.id_os,
            id_pedido=mov.id_pedido,
            tipo_movimentacao=mov.tipo_movimentacao,
            quantidade=mov.quantidade,
            estoque_anterior=mov.estoque_anterior,
            estoque_posterior=mov.estoque_posterior,
            motivo=mov.motivo,
            created_at=mov.created_at.isoformat() if mov.created_at else ""
        )
        for mov in movimentacoes
    ]
