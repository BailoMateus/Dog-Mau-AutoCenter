import logging

from fastapi import APIRouter, HTTPException, status

from app.services import ordem_servico_service
from app.schemas.ordem_servico_schema import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoStatusUpdate, OrdemServicoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])

@router.post("/", response_model=OrdemServicoPublic, status_code=status.HTTP_201_CREATED)
def create_ordem_servico(data: OrdemServicoCreate):
    """Cria uma nova ordem de serviço."""
    logger.info("POST /ordens-servico veiculo=%s mecanico=%s", data.id_veiculo, data.id_mecanico)
    ordem_servico = ordem_servico_service.create_ordem_servico(data)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.get("/", response_model=list[OrdemServicoPublic])
def list_ordens_servico():
    """Lista todas as ordens de serviço."""
    logger.info("GET /ordens-servico")
    ordens = ordem_servico_service.list_ordens_servico()
    return [
        OrdemServicoPublic(
            id_os=os.id_os,
            id_veiculo=os.id_veiculo,
            id_mecanico=os.id_mecanico,
            descricao_problema=os.descricao_problema,
            status=os.status,
            data_abertura=os.data_abertura,
            data_conclusao=os.data_conclusao,
            created_at=os.created_at,
            updated_at=os.updated_at
        )
        for os in ordens
    ]

@router.get("/{ordem_servico_id}", response_model=OrdemServicoPublic)
def get_ordem_servico(ordem_servico_id: int):
    """Busca uma ordem de serviço por ID."""
    logger.info("GET /ordens-servico/%s", ordem_servico_id)
    ordem_servico = ordem_servico_service.get_ordem_servico_or_404(ordem_servico_id)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.put("/{ordem_servico_id}", response_model=OrdemServicoPublic)
def update_ordem_servico(ordem_servico_id: int, data: OrdemServicoUpdate):
    """Atualiza uma ordem de serviço existente."""
    logger.info("PUT /ordens-servico/%s", ordem_servico_id)
    ordem_servico = ordem_servico_service.update_ordem_servico(ordem_servico_id, data)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.patch("/{ordem_servico_id}/status", response_model=OrdemServicoPublic)
def update_status_ordem_servico(ordem_servico_id: int, data: OrdemServicoStatusUpdate):
    """Atualiza apenas o status da ordem de serviço."""
    logger.info("PATCH /ordens-servico/%s/status novo_status=%s", ordem_servico_id, data.status)
    ordem_servico = ordem_servico_service.update_status_ordem_servico(ordem_servico_id, data)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.post("/{ordem_servico_id}/concluir", response_model=OrdemServicoPublic)
def concluir_ordem_servico(ordem_servico_id: int):
    """Conclui uma ordem de serviço (preenche data_conclusao)."""
    logger.info("POST /ordens-servico/%s/concluir", ordem_servico_id)
    ordem_servico = ordem_servico_service.concluir_ordem_servico(ordem_servico_id)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.post("/{ordem_servico_id}/iniciar", response_model=OrdemServicoPublic)
def iniciar_ordem_servico(ordem_servico_id: int):
    """Inicia uma ordem de serviço."""
    logger.info("POST /ordens-servico/%s/iniciar", ordem_servico_id)
    ordem_servico = ordem_servico_service.iniciar_ordem_servico(ordem_servico_id)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_veiculo=ordem_servico.id_veiculo,
        id_mecanico=ordem_servico.id_mecanico,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at
    )

@router.get("/status/{status}", response_model=list[OrdemServicoPublic])
def get_ordens_by_status(status: str):
    """Lista ordens de serviço por status."""
    logger.info("GET /ordens-servico/status/%s", status)
    ordens = ordem_servico_service.get_ordens_by_status(status)
    return [
        OrdemServicoPublic(
            id_os=os.id_os,
            id_veiculo=os.id_veiculo,
            id_mecanico=os.id_mecanico,
            descricao_problema=os.descricao_problema,
            status=os.status,
            data_abertura=os.data_abertura,
            data_conclusao=os.data_conclusao,
            created_at=os.created_at,
            updated_at=os.updated_at
        )
        for os in ordens
    ]

@router.get("/veiculo/{veiculo_id}", response_model=list[OrdemServicoPublic])
def get_ordens_by_veiculo(veiculo_id: int):
    """Lista ordens de serviço de um veículo específico."""
    logger.info("GET /ordens-servico/veiculo/%s", veiculo_id)
    ordens = ordem_servico_service.get_ordens_by_veiculo(veiculo_id)
    return [
        OrdemServicoPublic(
            id_os=os.id_os,
            id_veiculo=os.id_veiculo,
            id_mecanico=os.id_mecanico,
            descricao_problema=os.descricao_problema,
            status=os.status,
            data_abertura=os.data_abertura,
            data_conclusao=os.data_conclusao,
            created_at=os.created_at,
            updated_at=os.updated_at
        )
        for os in ordens
    ]
