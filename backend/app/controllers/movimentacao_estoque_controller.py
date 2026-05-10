import logging

from fastapi import APIRouter, HTTPException, status, Query

from app.services import movimentacao_estoque_service
from app.schemas.movimentacao_estoque_schema import (
    MovimentacaoEstoqueCreate, MovimentacaoEstoquePublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movimentacoes-estoque", tags=["Movimentações de Estoque"])

@router.post("/entrada", response_model=MovimentacaoEstoquePublic, status_code=status.HTTP_201_CREATED)
def registrar_entrada_estoque(data: MovimentacaoEstoqueCreate):
    """Registra entrada de estoque."""
    logger.info("POST /movimentacoes-estoque/entrada peca=%s quantidade=%s", data.id_peca, data.quantidade)
    movimentacao = movimentacao_estoque_service.registrar_entrada_estoque(data)
    return MovimentacaoEstoquePublic(
        id_movimentacao=movimentacao.id_movimentacao,
        id_peca=movimentacao.id_peca,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        quantidade=movimentacao.quantidade,
        motivo=movimentacao.motivo,
        created_at=movimentacao.created_at
    )

@router.post("/saida", response_model=MovimentacaoEstoquePublic, status_code=status.HTTP_201_CREATED)
def registrar_saida_estoque(data: MovimentacaoEstoqueCreate):
    """Registra saída de estoque."""
    logger.info("POST /movimentacoes-estoque/saida peca=%s quantidade=%s", data.id_peca, data.quantidade)
    movimentacao = movimentacao_estoque_service.registrar_saida_estoque(data)
    return MovimentacaoEstoquePublic(
        id_movimentacao=movimentacao.id_movimentacao,
        id_peca=movimentacao.id_peca,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        quantidade=movimentacao.quantidade,
        motivo=movimentacao.motivo,
        created_at=movimentacao.created_at
    )

@router.get("/", response_model=list[MovimentacaoEstoquePublic])
def list_all_movimentacoes(limit: int = Query(default=100, le=500)):
    """Lista todas as movimentações de estoque."""
    logger.info("GET /movimentacoes-estoque limit=%s", limit)
    movimentacoes = movimentacao_estoque_service.list_all_movimentacoes(limit)
    return [
        MovimentacaoEstoquePublic(
            id_movimentacao=mov.id_movimentacao,
            id_peca=mov.id_peca,
            tipo_movimentacao=mov.tipo_movimentacao,
            quantidade=mov.quantidade,
            motivo=mov.motivo,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/tipo/{tipo}", response_model=list[MovimentacaoEstoquePublic])
def list_movimentacoes_by_tipo(tipo: str, limit: int = Query(default=50, le=200)):
    """Lista movimentações por tipo (entrada/saida)."""
    logger.info("GET /movimentacoes-estoque/tipo/%s limit=%s", tipo, limit)
    movimentacoes = movimentacao_estoque_service.list_movimentacoes_by_tipo(tipo, limit)
    return [
        MovimentacaoEstoquePublic(
            id_movimentacao=mov.id_movimentacao,
            id_peca=mov.id_peca,
            tipo_movimentacao=mov.tipo_movimentacao,
            quantidade=mov.quantidade,
            motivo=mov.motivo,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/peca/{peca_id}", response_model=list[MovimentacaoEstoquePublic])
def list_movimentacoes_by_peca(peca_id: int, limit: int = Query(default=50, le=200)):
    """Lista movimentações de uma peça específica."""
    logger.info("GET /movimentacoes-estoque/peca/%s limit=%s", peca_id, limit)
    movimentacoes = movimentacao_estoque_service.list_movimentacoes_by_peca(peca_id, limit)
    return [
        MovimentacaoEstoquePublic(
            id_movimentacao=mov.id_movimentacao,
            id_peca=mov.id_peca,
            tipo_movimentacao=mov.tipo_movimentacao,
            quantidade=mov.quantidade,
            motivo=mov.motivo,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/peca/{peca_id}/historico", response_model=list[MovimentacaoEstoquePublic])
def get_historico_peca(peca_id: int, dias: int = Query(default=30, ge=1, le=365)):
    """Busca histórico de movimentações de uma peça."""
    logger.info("GET /movimentacoes-estoque/peca/%s/historico dias=%s", peca_id, dias)
    movimentacoes = movimentacao_estoque_service.get_historico_peca(peca_id, dias)
    return [
        MovimentacaoEstoquePublic(
            id_movimentacao=mov.id_movimentacao,
            id_peca=mov.id_peca,
            tipo_movimentacao=mov.tipo_movimentacao,
            quantidade=mov.quantidade,
            motivo=mov.motivo,
            created_at=mov.created_at
        )
        for mov in movimentacoes
    ]

@router.get("/peca/{peca_id}/ultima", response_model=MovimentacaoEstoquePublic)
def get_ultima_movimentacao_peca(peca_id: int):
    """Busca última movimentação de uma peça."""
    logger.info("GET /movimentacoes-estoque/peca/%s/ultima", peca_id)
    movimentacao = movimentacao_estoque_service.get_ultima_movimentacao_peca(peca_id)
    if not movimentacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma movimentação encontrada para esta peça"
        )
    return MovimentacaoEstoquePublic(
        id_movimentacao=movimentacao.id_movimentacao,
        id_peca=mov.id_peca,
        tipo_movimentacao=mov.tipo_movimentacao,
        quantidade=mov.quantidade,
        motivo=mov.motivo,
        created_at=mov.created_at
    )
