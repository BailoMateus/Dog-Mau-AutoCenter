import logging

from fastapi import APIRouter, HTTPException, status

from app.services import agendamento_service
from app.schemas.agendamento_schema import (
    AgendamentoCreate, AgendamentoUpdate, AgendamentoUpdateData, AgendamentoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])

@router.post("/", response_model=AgendamentoPublic, status_code=status.HTTP_201_CREATED)
def create_agendamento(data: AgendamentoCreate):
    """Cria um novo agendamento."""
    logger.info("POST /agendamentos usuario=%s veiculo=%s data=%s", 
                data.id_usuario, data.id_veiculo, data.data_agendamento)
    agendamento = agendamento_service.create_agendamento(data)
    return AgendamentoPublic(
        id_agendamento=agendamento.id_agendamento,
        id_usuario=agendamento.id_usuario,
        id_veiculo=agendamento.id_veiculo,
        data_agendamento=agendamento.data_agendamento,
        descricao=agendamento.descricao,
        status=agendamento.status,
        created_at=agendamento.created_at,
        updated_at=agendamento.updated_at
    )

@router.get("/", response_model=list[AgendamentoPublic])
def list_agendamentos():
    """Lista todos os agendamentos."""
    logger.info("GET /agendamentos")
    agendamentos = agendamento_service.list_agendamentos()
    return [
        AgendamentoPublic(
            id_agendamento=a.id_agendamento,
            id_usuario=a.id_usuario,
            id_veiculo=a.id_veiculo,
            data_agendamento=a.data_agendamento,
            descricao=a.descricao,
            status=a.status,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in agendamentos
    ]

@router.get("/{agendamento_id}", response_model=AgendamentoPublic)
def get_agendamento(agendamento_id: int):
    """Busca um agendamento por ID."""
    logger.info("GET /agendamentos/%s", agendamento_id)
    agendamento = agendamento_service.get_agendamento_or_404(agendamento_id)
    return AgendamentoPublic(
        id_agendamento=agendamento.id_agendamento,
        id_usuario=agendamento.id_usuario,
        id_veiculo=agendamento.id_veiculo,
        data_agendamento=agendamento.data_agendamento,
        descricao=agendamento.descricao,
        status=agendamento.status,
        created_at=agendamento.created_at,
        updated_at=agendamento.updated_at
    )

@router.put("/{agendamento_id}", response_model=AgendamentoPublic)
def update_agendamento(agendamento_id: int, data: AgendamentoUpdate):
    """Atualiza um agendamento existente."""
    logger.info("PUT /agendamentos/%s", agendamento_id)
    agendamento = agendamento_service.update_agendamento(agendamento_id, data)
    return AgendamentoPublic(
        id_agendamento=agendamento.id_agendamento,
        id_usuario=agendamento.id_usuario,
        id_veiculo=agendamento.id_veiculo,
        data_agendamento=agendamento.data_agendamento,
        descricao=agendamento.descricao,
        status=agendamento.status,
        created_at=agendamento.created_at,
        updated_at=agendamento.updated_at
    )

@router.patch("/{agendamento_id}/data", response_model=AgendamentoPublic)
def update_data_agendamento(agendamento_id: int, data: AgendamentoUpdateData):
    """Atualiza apenas a data do agendamento."""
    logger.info("PATCH /agendamentos/%s/data nova_data=%s", agendamento_id, data.data_agendamento)
    agendamento = agendamento_service.update_data_agendamento(agendamento_id, data)
    return AgendamentoPublic(
        id_agendamento=agendamento.id_agendamento,
        id_usuario=agendamento.id_usuario,
        id_veiculo=agendamento.id_veiculo,
        data_agendamento=agendamento.data_agendamento,
        descricao=agendamento.descricao,
        status=agendamento.status,
        created_at=agendamento.created_at,
        updated_at=agendamento.updated_at
    )

@router.patch("/{agendamento_id}/cancelar", response_model=AgendamentoPublic)
def cancelar_agendamento(agendamento_id: int):
    """Cancela um agendamento."""
    logger.info("PATCH /agendamentos/%s/cancelar", agendamento_id)
    agendamento = agendamento_service.cancelar_agendamento(agendamento_id)
    return AgendamentoPublic(
        id_agendamento=agendamento.id_agendamento,
        id_usuario=agendamento.id_usuario,
        id_veiculo=agendamento.id_veiculo,
        data_agendamento=agendamento.data_agendamento,
        descricao=agendamento.descricao,
        status=agendamento.status,
        created_at=agendamento.created_at,
        updated_at=agendamento.updated_at
    )

@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agendamento(agendamento_id: int):
    """Remove um agendamento (soft delete)."""
    logger.info("DELETE /agendamentos/%s", agendamento_id)
    agendamento_service.delete_agendamento(agendamento_id)
    return None

@router.get("/cliente/{cliente_id}", response_model=list[AgendamentoPublic])
def get_agendamentos_by_cliente(cliente_id: int):
    """Lista agendamentos de um cliente específico."""
    logger.info("GET /agendamentos/cliente/%s", cliente_id)
    agendamentos = agendamento_service.get_agendamentos_by_cliente(cliente_id)
    return [
        AgendamentoPublic(
            id_agendamento=a.id_agendamento,
            id_cliente=a.id_cliente,
            id_veiculo=a.id_veiculo,
            data_agendamento=a.data_agendamento,
            descricao=a.descricao,
            status=a.status,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in agendamentos
    ]

@router.get("/veiculo/{veiculo_id}", response_model=list[AgendamentoPublic])
def get_agendamentos_by_veiculo(veiculo_id: int):
    """Lista agendamentos de um veículo específico."""
    logger.info("GET /agendamentos/veiculo/%s", veiculo_id)
    agendamentos = agendamento_service.get_agendamentos_by_veiculo(veiculo_id)
    return [
        AgendamentoPublic(
            id_agendamento=a.id_agendamento,
            id_cliente=a.id_cliente,
            id_veiculo=a.id_veiculo,
            data_agendamento=a.data_agendamento,
            descricao=a.descricao,
            status=a.status,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in agendamentos
    ]
