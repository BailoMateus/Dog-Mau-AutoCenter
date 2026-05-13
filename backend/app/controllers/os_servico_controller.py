import logging

from fastapi import APIRouter, HTTPException, status

from app.services import os_servico_service
from app.schemas.os_servico_schema import (
    OsServicoCreate, OsServicoUpdate, OsServicoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordens-servico/{os_id}/servicos", tags=["Serviços da OS"])

@router.post("/", response_model=OsServicoPublic, status_code=status.HTTP_201_CREATED)
def add_servico_to_os(os_id: int, data: OsServicoCreate):
    """Adiciona um serviço à ordem de serviço."""
    logger.info("POST /ordens-servico/%s/servicos servico=%s quantidade=%s", os_id, data.id_servico, data.quantidade)
    item = os_servico_service.add_servico_to_os(os_id, data)
    return OsServicoPublic(
        id_os=item.id_os,
        id_servico=item.id_servico,
        quantidade=item.quantidade,
        servico_descricao=item.servico_descricao,
        servico_preco=item.servico_preco,
        subtotal=item.subtotal
    )

@router.get("/", response_model=list[OsServicoPublic])
def get_servicos_by_os(os_id: int):
    """Lista todos os serviços de uma ordem de serviço."""
    logger.info("GET /ordens-servico/%s/servicos", os_id)
    itens = os_servico_service.get_servicos_by_os(os_id)
    return [
        OsServicoPublic(
            id_os=item.id_os,
            id_servico=item.id_servico,
            quantidade=item.quantidade,
            servico_descricao=item.servico_descricao,
            servico_preco=item.servico_preco,
            subtotal=item.subtotal
        )
        for item in itens
    ]

@router.get("/{servico_id}", response_model=OsServicoPublic)
def get_servico_by_os(os_id: int, servico_id: int):
    """Busca um serviço específico de uma ordem de serviço."""
    logger.info("GET /ordens-servico/%s/servicos/%s", os_id, servico_id)
    item = os_servico_service.get_servico_by_os(os_id, servico_id)
    return OsServicoPublic(
        id_os=item.id_os,
        id_servico=item.id_servico,
        quantidade=item.quantidade,
        servico_descricao=item.servico_descricao,
        servico_preco=item.servico_preco,
        subtotal=item.subtotal
    )

@router.put("/{servico_id}", response_model=OsServicoPublic)
def update_quantidade_servico(os_id: int, servico_id: int, data: OsServicoUpdate):
    """Atualiza quantidade de um serviço na ordem de serviço."""
    logger.info("PUT /ordens-servico/%s/servicos/%s nova_quantidade=%s", os_id, servico_id, data.quantidade)
    item = os_servico_service.update_quantidade_servico(os_id, servico_id, data)
    return OsServicoPublic(
        id_os=item.id_os,
        id_servico=item.id_servico,
        quantidade=item.quantidade,
        servico_descricao=item.servico_descricao,
        servico_preco=item.servico_preco,
        subtotal=item.subtotal
    )

@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_servico_from_os(os_id: int, servico_id: int):
    """Remove um serviço da ordem de serviço."""
    logger.info("DELETE /ordens-servico/%s/servicos/%s", os_id, servico_id)
    os_servico_service.remove_servico_from_os(os_id, servico_id)
    return None

@router.get("/valor-total", response_model=dict)
def get_valor_total_servicos(os_id: int):
    """Calcula valor total dos serviços da OS."""
    logger.info("GET /ordens-servico/%s/servicos/valor-total", os_id)
    valor_total = os_servico_service.calcular_valor_total_servicos(os_id)
    return {"valor_total_servicos": valor_total}
