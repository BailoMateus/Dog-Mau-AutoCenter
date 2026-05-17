import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrdemServico
from app.repositories import ordem_servico_repository as os_repo
from app.repositories import mecanico_repository as mecanico_repo
from app.schemas.ordem_servico_schema import OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoStatusUpdate

logger = logging.getLogger(__name__)

def list_ordens_servico():
    """Lista todas as ordens de serviço."""
    return os_repo.get_all_ordens_servico()

def get_ordem_servico_or_404(ordem_servico_id: int) -> OrdemServico:
    """Busca ordem de serviço por ID ou retorna 404."""
    ordem_servico = os_repo.get_ordem_servico_by_id(ordem_servico_id)
    if not ordem_servico:
        logger.info("ordem de serviço não encontrada id=%s", ordem_servico_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    return ordem_servico

def validate_ordem_servico_data(id_veiculo: int = None, id_mecanico: int = None, descricao_problema: str = None):
    """Valida dados da ordem de serviço."""
    # Validação de veículo existente
    if id_veiculo and not os_repo.check_veiculo_exists(id_veiculo):
        logger.warning("veículo não encontrado veiculo_id=%s", id_veiculo)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado"
        )
    
    # Validação de mecânico existente
    if id_mecanico and not os_repo.check_mecanico_exists(id_mecanico):
        logger.warning("mecânico não encontrado mecanico_id=%s", id_mecanico)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mecânico não encontrado"
        )
    
    # Validação de descrição do problema
    if descricao_problema and len(descricao_problema.strip()) == 0:
        logger.warning("descrição do problema vazia")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição do problema é obrigatória"
        )

def create_ordem_servico(data: OrdemServicoCreate):
    """Cria uma nova ordem de serviço com validações."""
    # Validações
    validate_ordem_servico_data(
        id_veiculo=data.id_veiculo,
        id_mecanico=data.id_mecanico,
        descricao_problema=data.descricao_problema
    )
    
    # Cria entidade OrdemServico
    ordem_servico = OrdemServico(
        id_veiculo=data.id_veiculo,
        id_mecanico=data.id_mecanico,
        descricao_problema=data.descricao_problema,
        status="aberta",
        data_abertura=datetime.now(timezone.utc)
    )
    
    try:
        return os_repo.create_ordem_servico(ordem_servico)
    except psycopg2.IntegrityError:
        logger.error("create_ordem_servico erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar ordem de serviço"
        )

def update_ordem_servico(ordem_servico_id: int, data: OrdemServicoUpdate):
    """Atualiza uma ordem de serviço com validações."""
    ordem_servico = get_ordem_servico_or_404(ordem_servico_id)
    
    # Validações
    validate_ordem_servico_data(
        id_veiculo=data.id_veiculo,
        id_mecanico=data.id_mecanico,
        descricao_problema=data.descricao_problema
    )
    
    # Atualiza campos
    if data.id_veiculo is not None:
        ordem_servico.id_veiculo = data.id_veiculo
    if data.id_mecanico is not None:
        ordem_servico.id_mecanico = data.id_mecanico
    if data.descricao_problema is not None:
        ordem_servico.descricao_problema = data.descricao_problema
    
    try:
        return os_repo.update_ordem_servico(ordem_servico)
    except psycopg2.IntegrityError:
        logger.error("update_ordem_servico erro de integridade id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar ordem de serviço"
        )

def update_status_ordem_servico(ordem_servico_id: int, data: OrdemServicoStatusUpdate):
    """Atualiza apenas o status da ordem de serviço."""
    ordem_servico = get_ordem_servico_or_404(ordem_servico_id)
    
    # Validação de status
    status_validos = ["aberta", "em_andamento", "concluida", "cancelada"]
    if data.status not in status_validos:
        logger.warning("status inválido status=%s", data.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    # Validação de fluxo de status
    if ordem_servico.status == "concluida":
        logger.warning("tentativa de alterar status de OS concluída id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída"
        )
    
    if ordem_servico.status == "cancelada" and data.status not in ["aberta"]:
        logger.warning("tentativa de alterar status de OS cancelada id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada só pode ser reaberta"
        )
    
    try:
        os_repo.update_status_ordem_servico(ordem_servico_id, data.status)
        # Retorna ordem de serviço atualizada
        return get_ordem_servico_or_404(ordem_servico_id)
    except psycopg2.IntegrityError:
        logger.error("update_status_ordem_servico erro de integridade id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status da ordem de serviço"
        )

def concluir_ordem_servico(ordem_servico_id: int):
    """Conclui uma ordem de serviço (preenche data_conclusao)."""
    ordem_servico = get_ordem_servico_or_404(ordem_servico_id)
    
    # Validação de status
    if ordem_servico.status == "concluida":
        logger.warning("ordem de serviço já está concluída id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída"
        )
    
    if ordem_servico.status == "cancelada":
        logger.warning("tentativa de concluir OS cancelada id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada não pode ser concluída"
        )
    
    try:
        os_repo.concluir_ordem_servico(ordem_servico_id)
        logger.info("ordem de serviço concluída id=%s", ordem_servico_id)
        # Retorna ordem de serviço atualizada
        return get_ordem_servico_or_404(ordem_servico_id)
    except psycopg2.IntegrityError:
        logger.error("concluir_ordem_servico erro de integridade id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao concluir ordem de serviço"
        )

def get_ordens_by_status(status: str):
    """Lista ordens de serviço por status."""
    # Validação de status
    status_validos = ["aberta", "em_andamento", "concluida", "cancelada"]
    if status not in status_validos:
        logger.warning("status inválido status=%s", status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    return os_repo.get_ordens_by_status(status)

def get_ordens_by_veiculo(veiculo_id: int):
    """Lista ordens de serviço de um veículo específico."""
    if not os_repo.check_veiculo_exists(veiculo_id):
        logger.warning("veículo não encontrado veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    
    return os_repo.get_ordens_by_veiculo(veiculo_id)

def iniciar_ordem_servico(ordem_servico_id: int):
    """Inicia uma ordem de serviço."""
    ordem_servico = get_ordem_servico_or_404(ordem_servico_id)
    
    # Validação de status
    if ordem_servico.status != "aberta":
        logger.warning("ordem de serviço não pode ser iniciada status=%s id=%s", 
                     ordem_servico.status, ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas ordens de serviço 'abertas' podem ser iniciadas"
        )
    
    try:
        os_repo.iniciar_ordem_servico(ordem_servico_id)
        logger.info("ordem de serviço iniciada id=%s", ordem_servico_id)
        # Retorna ordem de serviço atualizada
        return get_ordem_servico_or_404(ordem_servico_id)
    except psycopg2.IntegrityError:
        logger.error("iniciar_ordem_servico erro de integridade id=%s", ordem_servico_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar ordem de serviço"
        )
