import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Agendamento
from app.repositories import agendamento_repository as repo
from app.schemas.agendamento_schema import AgendamentoCreate, AgendamentoUpdate, AgendamentoUpdateData

logger = logging.getLogger(__name__)

def list_agendamentos():
    """Lista todos os agendamentos."""
    return repo.get_all_agendamentos()

def get_agendamento_or_404(agendamento_id: int) -> Agendamento:
    """Busca agendamento por ID ou retorna 404."""
    agendamento = repo.get_agendamento_by_id(agendamento_id)
    if not agendamento:
        logger.info("agendamento não encontrado id=%s", agendamento_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")
    return agendamento

def validate_agendamento_data(usuario_id: int = None, veiculo_id: int = None, data_agendamento=None):
    """Valida dados do agendamento."""
    # Validação de usuario existente
    if usuario_id and not repo.check_usuario_exists(usuario_id):
        logger.warning("usuario não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario não encontrado"
        )
    
    # Validação de veículo existente
    if veiculo_id and not repo.check_veiculo_exists(veiculo_id):
        logger.warning("veículo não encontrado veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado"
        )
    
    # Validação de veículo pertencente ao usuario
    if usuario_id and veiculo_id and not repo.check_veiculo_pertence_usuario(veiculo_id, usuario_id):
        logger.warning("veículo não pertence ao usuario veiculo=%s usuario=%s", veiculo_id, usuario_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não pertence ao usuario informado"
        )
    
    # Validação de data no futuro
    if data_agendamento and data_agendamento <= datetime.now():
        logger.warning("data de agendamento no passado data=%s", data_agendamento)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data do agendamento deve ser no futuro"
        )

def create_agendamento(data: AgendamentoCreate):
    """Cria um novo agendamento com validações."""
    # Validações
    validate_agendamento_data(
        usuario_id=data.id_usuario,
        veiculo_id=data.id_veiculo,
        data_agendamento=data.data_agendamento
    )
    
    # Cria entidade Agendamento
    agendamento = Agendamento(
        id_usuario=data.id_usuario,
        id_veiculo=data.id_veiculo,
        data_agendamento=data.data_agendamento,
        descricao=data.descricao or "",
        status=data.status or "agendado"
    )
    
    try:
        return repo.create_agendamento(agendamento)
    except psycopg2.IntegrityError:
        logger.error("create_agendamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar agendamento"
        )

def update_agendamento(agendamento_id: int, data: AgendamentoUpdate):
    """Atualiza um agendamento com validações."""
    agendamento = get_agendamento_or_404(agendamento_id)
    
    # Validações
    validate_agendamento_data(
        usuario_id=data.id_usuario,
        veiculo_id=data.id_veiculo,
        data_agendamento=data.data_agendamento
    )
    
    # Atualiza campos
    if data.id_usuario is not None:
        agendamento.id_usuario = data.id_usuario
    if data.id_veiculo is not None:
        agendamento.id_veiculo = data.id_veiculo
    if data.data_agendamento is not None:
        agendamento.data_agendamento = data.data_agendamento
    if data.descricao is not None:
        agendamento.descricao = data.descricao
    if data.status is not None:
        agendamento.status = data.status
    
    try:
        return repo.update_agendamento(agendamento)
    except psycopg2.IntegrityError:
        logger.error("update_agendamento erro de integridade id=%s", agendamento_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar agendamento"
        )

def update_data_agendamento(agendamento_id: int, data: AgendamentoUpdateData):
    """Atualiza apenas a data do agendamento."""
    agendamento = get_agendamento_or_404(agendamento_id)
    
    # Validação de data
    validate_agendamento_data(data_agendamento=data.data_agendamento)
    
    try:
        repo.update_data_agendamento(agendamento_id, data.data_agendamento)
        # Retorna agendamento atualizado
        return get_agendamento_or_404(agendamento_id)
    except psycopg2.IntegrityError:
        logger.error("update_data_agendamento erro de integridade id=%s", agendamento_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar data do agendamento"
        )

def cancelar_agendamento(agendamento_id: int):
    """Cancela um agendamento."""
    agendamento = get_agendamento_or_404(agendamento_id)
    
    # Verifica se já está cancelado
    if agendamento.status == "cancelado":
        logger.warning("agendamento já está cancelado id=%s", agendamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento já está cancelado"
        )
    
    try:
        repo.cancelar_agendamento(agendamento_id)
        # Retorna agendamento atualizado
        return get_agendamento_or_404(agendamento_id)
    except psycopg2.IntegrityError:
        logger.error("cancelar_agendamento erro de integridade id=%s", agendamento_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cancelar agendamento"
        )

def delete_agendamento(agendamento_id: int):
    """Remove (soft delete) um agendamento."""
    agendamento = get_agendamento_or_404(agendamento_id)
    return repo.soft_delete_agendamento(agendamento)

def get_agendamentos_by_usuario(usuario_id: int):
    """Lista agendamentos de um usuario específico."""
    if not repo.check_usuario_exists(usuario_id):
        logger.warning("usuario não encontrado usuario_id=%s", usuario_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado"
        )
    
    return repo.get_agendamentos_by_usuario(usuario_id)

def get_agendamentos_by_veiculo(veiculo_id: int):
    """Lista agendamentos de um veículo específico."""
    if not repo.check_veiculo_exists(veiculo_id):
        logger.warning("veículo não encontrado veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    
    return repo.get_agendamentos_by_veiculo(veiculo_id)
