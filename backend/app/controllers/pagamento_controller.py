import logging

from fastapi import APIRouter, HTTPException, status, Query

from app.services import pagamento_service
from app.schemas.pagamento_schema import (
    PagamentoCreate, PagamentoUpdate, PagamentoStatusUpdate, PagamentoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/", response_model=PagamentoPublic, status_code=status.HTTP_201_CREATED)
def registrar_pagamento(data: PagamentoCreate):
    """Registra um novo pagamento."""
    logger.info("POST /pagamentos os=%s valor=%s forma=%s", data.id_os, data.valor, data.forma_pagamento)
    pagamento = pagamento_service.registrar_pagamento(data)
    return PagamentoPublic(
        id_pagamento=pagamento.id_pagamento,
        id_os=pagamento.id_os,
        valor=pagamento.valor,
        forma_pagamento=pagamento.forma_pagamento,
        status=pagamento.status,
        data_pagamento=pagamento.data_pagamento,
        created_at=pagamento.created_at,
        updated_at=pagamento.updated_at
    )

@router.get("/", response_model=list[PagamentoPublic])
def list_all_pagamentos(limit: int = Query(default=100, le=500)):
    """Lista todos os pagamentos."""
    logger.info("GET /pagamentos limit=%s", limit)
    pagamentos = pagamento_service.list_all_pagamentos(limit)
    return [
        PagamentoPublic(
            id_pagamento=pag.id_pagamento,
            id_os=pag.id_os,
            valor=pag.valor,
            forma_pagamento=pag.forma_pagamento,
            status=pag.status,
            data_pagamento=pag.data_pagamento,
            created_at=pag.created_at,
            updated_at=pag.updated_at
        )
        for pag in pagamentos
    ]

@router.get("/os/{os_id}", response_model=list[PagamentoPublic])
def list_pagamentos_by_os(os_id: int):
    """Lista pagamentos de uma OS específica."""
    logger.info("GET /pagamentos/os/%s", os_id)
    pagamentos = pagamento_service.list_pagamentos_by_os(os_id)
    return [
        PagamentoPublic(
            id_pagamento=pag.id_pagamento,
            id_os=pag.id_os,
            valor=pag.valor,
            forma_pagamento=pag.forma_pagamento,
            status=pag.status,
            data_pagamento=pag.data_pagamento,
            created_at=pag.created_at,
            updated_at=pag.updated_at
        )
        for pag in pagamentos
    ]

@router.get("/status/{status}", response_model=list[PagamentoPublic])
def list_pagamentos_by_status(status: str, limit: int = Query(default=50, le=200)):
    """Lista pagamentos por status."""
    logger.info("GET /pagamentos/status/%s limit=%s", status, limit)
    pagamentos = pagamento_service.list_pagamentos_by_status(status, limit)
    return [
        PagamentoPublic(
            id_pagamento=pag.id_pagamento,
            id_os=pag.id_os,
            valor=pag.valor,
            forma_pagamento=pag.forma_pagamento,
            status=pag.status,
            data_pagamento=pag.data_pagamento,
            created_at=pag.created_at,
            updated_at=pag.updated_at
        )
        for pag in pagamentos
    ]

@router.get("/{pagamento_id}", response_model=PagamentoPublic)
def get_pagamento_by_id(pagamento_id: int):
    """Busca pagamento por ID."""
    logger.info("GET /pagamentos/%s", pagamento_id)
    pagamento = pagamento_service.get_pagamento_by_id(pagamento_id)
    return PagamentoPublic(
        id_pagamento=pagamento.id_pagamento,
        id_os=pagamento.id_os,
        valor=pagamento.valor,
        forma_pagamento=pagamento.forma_pagamento,
        status=pagamento.status,
        data_pagamento=pagamento.data_pagamento,
        created_at=pagamento.created_at,
        updated_at=pagamento.updated_at
    )

@router.put("/{pagamento_id}", response_model=PagamentoPublic)
def atualizar_pagamento(pagamento_id: int, data: PagamentoUpdate):
    """Atualiza dados completos de um pagamento."""
    logger.info("PUT /pagamentos/%s valor=%s status=%s", pagamento_id, data.valor, data.status)
    pagamento = pagamento_service.atualizar_pagamento(pagamento_id, data)
    return PagamentoPublic(
        id_pagamento=pagamento.id_pagamento,
        id_os=pagamento.id_os,
        valor=pagamento.valor,
        forma_pagamento=pagamento.forma_pagamento,
        status=pagamento.status,
        data_pagamento=pagamento.data_pagamento,
        created_at=pagamento.created_at,
        updated_at=pagamento.updated_at
    )

@router.patch("/{pagamento_id}/status", response_model=PagamentoPublic)
def atualizar_status_pagamento(pagamento_id: int, data: PagamentoStatusUpdate):
    """Atualiza apenas o status de um pagamento."""
    logger.info("PATCH /pagamentos/%s/status status=%s", pagamento_id, data.status)
    pagamento = pagamento_service.atualizar_status_pagamento(pagamento_id, data)
    return PagamentoPublic(
        id_pagamento=pagamento.id_pagamento,
        id_os=pagamento.id_os,
        valor=pagamento.valor,
        forma_pagamento=pagamento.forma_pagamento,
        status=pagamento.status,
        data_pagamento=pagamento.data_pagamento,
        created_at=pagamento.created_at,
        updated_at=pagamento.updated_at
    )

@router.delete("/{pagamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pagamento(pagamento_id: int):
    """Remove um pagamento (soft delete)."""
    logger.info("DELETE /pagamentos/%s", pagamento_id)
    pagamento_service.soft_delete_pagamento(pagamento_id)
    return None

@router.get("/os/{os_id}/total", response_model=dict)
def calcular_total_pagamentos_os(os_id: int):
    """Calcula valor total dos pagamentos confirmados de uma OS."""
    logger.info("GET /pagamentos/os/%s/total", os_id)
    valor_total = pagamento_service.calcular_total_pagamentos_os(os_id)
    return {"valor_total_pagamentos": valor_total}
