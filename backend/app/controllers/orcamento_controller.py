import logging

from fastapi import APIRouter, HTTPException, status

from app.services import orcamento_service
from app.schemas.orcamento_schema import (
    OrcamentoCreate, OrcamentoUpdate, OrcamentoUpdateStatus, OrcamentoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])

@router.post("/", response_model=OrcamentoPublic, status_code=status.HTTP_201_CREATED)
def create_orcamento(data: OrcamentoCreate):
    """Cria um novo orçamento."""
    logger.info("POST /orcamentos usuario=%s veiculo=%s valor=%s", 
                data.id_usuario, data.id_veiculo, data.valor_total)
    orcamento = orcamento_service.create_orcamento(data)
    return OrcamentoPublic(
        id_orcamento=orcamento.id_orcamento,
        id_usuario=orcamento.id_usuario,
        id_veiculo=orcamento.id_veiculo,
        status=orcamento.status,
        valor_total=orcamento.valor_total,
        created_at=orcamento.created_at,
        updated_at=orcamento.updated_at
    )

@router.get("/", response_model=list[OrcamentoPublic])
def list_orcamentos():
    """Lista todos os orçamentos."""
    logger.info("GET /orcamentos")
    orcamentos = orcamento_service.list_orcamentos()
    return [
        OrcamentoPublic(
            id_orcamento=o.id_orcamento,
            id_usuario=o.id_usuario,
            id_veiculo=o.id_veiculo,
            status=o.status,
            valor_total=o.valor_total,
            created_at=o.created_at,
            updated_at=o.updated_at
        )
        for o in orcamentos
    ]

@router.get("/{orcamento_id}", response_model=OrcamentoPublic)
def get_orcamento(orcamento_id: int):
    """Busca um orçamento por ID."""
    logger.info("GET /orcamentos/%s", orcamento_id)
    orcamento = orcamento_service.get_orcamento_or_404(orcamento_id)
    return OrcamentoPublic(
        id_orcamento=orcamento.id_orcamento,
        id_usuario=orcamento.id_usuario,
        id_veiculo=orcamento.id_veiculo,
        status=orcamento.status,
        valor_total=orcamento.valor_total,
        created_at=orcamento.created_at,
        updated_at=orcamento.updated_at
    )

@router.put("/{orcamento_id}", response_model=OrcamentoPublic)
def update_orcamento(orcamento_id: int, data: OrcamentoUpdate):
    """Atualiza um orçamento existente."""
    logger.info("PUT /orcamentos/%s", orcamento_id)
    orcamento = orcamento_service.update_orcamento(orcamento_id, data)
    return OrcamentoPublic(
        id_orcamento=orcamento.id_orcamento,
        id_usuario=orcamento.id_usuario,
        id_veiculo=orcamento.id_veiculo,
        status=orcamento.status,
        valor_total=orcamento.valor_total,
        created_at=orcamento.created_at,
        updated_at=orcamento.updated_at
    )

@router.patch("/{orcamento_id}/status", response_model=OrcamentoPublic)
def update_status_orcamento(orcamento_id: int, data: OrcamentoUpdateStatus):
    """Atualiza apenas o status do orçamento."""
    logger.info("PATCH /orcamentos/%s/status novo_status=%s", orcamento_id, data.status)
    orcamento = orcamento_service.update_status_orcamento(orcamento_id, data)
    return OrcamentoPublic(
        id_orcamento=orcamento.id_orcamento,
        id_usuario=orcamento.id_usuario,
        id_veiculo=orcamento.id_veiculo,
        status=orcamento.status,
        valor_total=orcamento.valor_total,
        created_at=orcamento.created_at,
        updated_at=orcamento.updated_at
    )

@router.delete("/{orcamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_orcamento(orcamento_id: int):
    """Remove um orçamento (soft delete)."""
    logger.info("DELETE /orcamentos/%s", orcamento_id)
    orcamento_service.delete_orcamento(orcamento_id)
    return None

@router.get("/usuario/{usuario_id}", response_model=list[OrcamentoPublic])
def get_orcamentos_by_usuario(usuario_id: int):
    """Lista orçamentos de um usuario específico."""
    logger.info("GET /orcamentos/usuario/%s", usuario_id)
    orcamentos = orcamento_service.get_orcamentos_by_usuario(usuario_id)
    return [
        OrcamentoPublic(
            id_orcamento=o.id_orcamento,
            id_usuario=o.id_usuario,
            id_veiculo=o.id_veiculo,
            status=o.status,
            valor_total=o.valor_total,
            created_at=o.created_at,
            updated_at=o.updated_at
        )
        for o in orcamentos
    ]

@router.get("/veiculo/{veiculo_id}", response_model=list[OrcamentoPublic])
def get_orcamentos_by_veiculo(veiculo_id: int):
    """Lista orçamentos de um veículo específico."""
    logger.info("GET /orcamentos/veiculo/%s", veiculo_id)
    orcamentos = orcamento_service.get_orcamentos_by_veiculo(veiculo_id)
    return [
        OrcamentoPublic(
            id_orcamento=o.id_orcamento,
            id_usuario=o.id_usuario,
            id_veiculo=o.id_veiculo,
            status=o.status,
            valor_total=o.valor_total,
            created_at=o.created_at,
            updated_at=o.updated_at
        )
        for o in orcamentos
    ]
