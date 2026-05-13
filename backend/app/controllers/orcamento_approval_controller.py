import logging

from fastapi import APIRouter, HTTPException, status

from app.services import orcamento_approval_service
from app.schemas.orcamento_approval_schema import OrdemServicoPublic

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orcamentos/{orcamento_id}/aprovacao", tags=["Aprovação de Orçamentos"])

@router.post("/aprovar", response_model=OrdemServicoPublic, status_code=status.HTTP_201_CREATED)
def aprovar_orcamento(orcamento_id: int):
    """Aprova orçamento e gera OS automaticamente."""
    logger.info("POST /orcamentos/%s/aprovacao/aprovar", orcamento_id)
    ordem_servico = orcamento_approval_service.aprovar_orcamento(orcamento_id)
    return OrdemServicoPublic(
        id_ordem_servico=ordem_servico.id_ordem_servico,
        id_orcamento=ordem_servico.id_orcamento,
        id_veiculo=ordem_servico.id_veiculo,
        status=ordem_servico.status,
        valor_total=ordem_servico.valor_total,
        data_inicio=ordem_servico.data_inicio,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.post("/rejeitar", status_code=status.HTTP_204_NO_CONTENT)
def rejeitar_orcamento(orcamento_id: int):
    """Rejeita orçamento."""
    logger.info("POST /orcamentos/%s/aprovacao/rejeitar", orcamento_id)
    orcamento_approval_service.rejeitar_orcamento(orcamento_id)
    return None

@router.get("/ordens", response_model=list[OrdemServicoPublic])
def get_ordens_by_orcamento(orcamento_id: int):
    """Lista ordens de serviço de um orçamento."""
    logger.info("GET /orcamentos/%s/aprovacao/ordens", orcamento_id)
    ordens = orcamento_approval_service.get_ordens_by_orcamento(orcamento_id)
    return [
        OrdemServicoPublic(
            id_ordem_servico=os.id_ordem_servico,
            id_orcamento=os.id_orcamento,
            id_veiculo=os.id_veiculo,
            status=os.status,
            valor_total=os.valor_total,
            data_inicio=os.data_inicio,
            data_conclusao=os.data_conclusao,
            created_at=os.created_at,
            updated_at=os.updated_at
        )
        for os in ordens
    ]
