import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrdemServico, dict_to_ordem_servico
from app.repositories import ordem_servico_repository as os_repo
from app.repositories import mecanico_repository as mecanico_repo
from app.repositories import orcamento_repository as orcamento_repo
from app.schemas.ordem_servico_schema import (
    OrdemServicoCreate,
    OrdemServicoPublic,
    OrdemServicoUpdate,
    OrdemServicoStatusUpdate,
)

logger = logging.getLogger(__name__)

def build_ordem_servico_public(ordem_servico: OrdemServico) -> OrdemServicoPublic:
    orcamento_status = None
    if ordem_servico.id_orcamento:
        orc = orcamento_repo.get_orcamento_by_id(ordem_servico.id_orcamento)
        if orc:
            orcamento_status = getattr(orc, "status", None)
    return OrdemServicoPublic(
        id_os=ordem_servico.id_os,
        id_orcamento=ordem_servico.id_orcamento,
        id_veiculo=ordem_servico.id_veiculo,
        id_usuario=ordem_servico.id_usuario,
        descricao_problema=ordem_servico.descricao_problema,
        status=ordem_servico.status,
        valor_total=getattr(ordem_servico, "valor_total", None),
        orcamento_status=orcamento_status,
        data_abertura=ordem_servico.data_abertura,
        data_conclusao=ordem_servico.data_conclusao,
        created_at=ordem_servico.created_at,
        updated_at=ordem_servico.updated_at,
    )


def build_ordem_servico_public_from_row(row: dict) -> OrdemServicoPublic:
    os = dict_to_ordem_servico(row)
    pub = build_ordem_servico_public(os)
    return pub.model_copy(update={
        "valor_total": float(row.get("valor_total") or 0),
        "orcamento_status": row.get("orcamento_status"),
        "placa": row.get("placa"),
        "cor": row.get("cor"),
        "ano_fabricacao": row.get("ano_fabricacao"),
        "nome_modelo": row.get("nome_modelo"),
        "proprietario_nome": row.get("proprietario_nome"),
        "mecanico_nome": row.get("mecanico_nome"),
    })


def get_ordem_servico_detalhada_or_404(id_os: int) -> OrdemServicoPublic:
    row = os_repo.get_ordem_servico_detalhada(id_os)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    return build_ordem_servico_public_from_row(row)


def list_ordens_servico():
    """Lista todas as ordens de serviço."""
    return os_repo.get_all_ordens_servico()

def get_ordem_servico_or_404(id_os: int) -> OrdemServico:
    """Busca ordem de serviço por ID ou retorna 404."""
    ordem_servico = os_repo.get_ordem_servico_by_id(id_os)
    if not ordem_servico:
        logger.info("ordem de serviço não encontrada id=%s", id_os)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    return ordem_servico

def validate_ordem_servico_data(id_veiculo: int = None, id_usuario: int = None, descricao_problema: str = None):
    """Valida dados da ordem de serviço."""
    # Validação de veículo existente
    if id_veiculo and not os_repo.check_veiculo_exists(id_veiculo):
        logger.warning("veículo não encontrado veiculo_id=%s", id_veiculo)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado"
        )
    
    # Validação de mecânico existente (usuário com perfil mecânico/admin)
    if id_usuario and not os_repo.check_mecanico_atribuivel(id_usuario):
        logger.warning("mecânico não encontrado mecanico_id=%s", id_usuario)
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
        id_usuario=data.id_usuario,
        descricao_problema=data.descricao_problema
    )
    
    # Cria entidade OrdemServico
    ordem_servico = OrdemServico(
        id_veiculo=data.id_veiculo,
        id_usuario=data.id_usuario,
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

def atribuir_mecanico(id_os: int, id_usuario: int):
    """Atribui mecânico à ordem de serviço."""
    
    # Verifica se OS existe
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    # Verifica se usuário mecânico existe
    if not os_repo.check_usuario_exists(id_usuario):
        logger.warning(
            "mecânico não encontrado mecanico_id=%s",
            id_usuario
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mecânico não encontrado"
        )
    
    # Atribui mecânico
    updated = os_repo.atribuir_mecanico_os(
        id_os=id_os,
        id_usuario=id_usuario
    )
    
    if not updated:
        logger.error(
            "erro ao atribuir mecânico os=%s",
            id_os
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atribuir mecânico"
        )
    
    return OrdemServico(**updated)

def update_ordem_servico(id_os: int, data: OrdemServicoUpdate):
    """Atualiza uma ordem de serviço com validações."""
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    # Validações
    validate_ordem_servico_data(
        id_veiculo=data.id_veiculo,
        id_usuario=data.id_usuario,
        descricao_problema=data.descricao_problema
    )
    
    # Atualiza campos
    if data.id_veiculo is not None:
        ordem_servico.id_veiculo = data.id_veiculo
    if data.id_usuario is not None:
        ordem_servico.id_usuario = data.id_usuario
    if data.descricao_problema is not None:
        ordem_servico.descricao_problema = data.descricao_problema
    
    try:
        return os_repo.update_ordem_servico(ordem_servico)
    except psycopg2.IntegrityError:
        logger.error("update_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar ordem de serviço"
        )

def update_status_ordem_servico(id_os: int, data: OrdemServicoStatusUpdate):
    """Atualiza apenas o status da ordem de serviço."""
    ordem_servico = get_ordem_servico_or_404(id_os)

    if ordem_servico.id_orcamento:
        orc = orcamento_repo.get_orcamento_by_id(ordem_servico.id_orcamento)
        orc_status = getattr(orc, "status", None) if orc else None
        if isinstance(orc, dict):
            orc_status = orc.get("status")
        if orc_status != "aprovado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A alteração de status só é permitida após aprovação do orçamento.",
            )
    
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
        logger.warning("tentativa de alterar status de OS concluída id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída"
        )
    
    if ordem_servico.status == "cancelada" and data.status not in ["aberta"]:
        logger.warning("tentativa de alterar status de OS cancelada id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada só pode ser reaberta"
        )
    
    try:
        os_repo.update_status_ordem_servico(id_os, data.status)
        # Retorna ordem de serviço atualizada
        return get_ordem_servico_or_404(id_os)
    except psycopg2.IntegrityError:
        logger.error("update_status_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status da ordem de serviço"
        )

def concluir_ordem_servico(id_os: int):
    """Conclui uma ordem de serviço (preenche data_conclusao)."""
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    # Validação de status
    if ordem_servico.status == "concluida":
        logger.warning("ordem de serviço já está concluída id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída"
        )
    
    if ordem_servico.status == "cancelada":
        logger.warning("tentativa de concluir OS cancelada id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada não pode ser concluída"
        )
    
    try:
        os_repo.concluir_ordem_servico(id_os)
        logger.info("ordem de serviço concluída id=%s", id_os)
        
        # --- Movimentação financeira na conclusão (estoque já baixado na reserva/consumo) ---
        from app.repositories import movimentacao_financeira_repository
        
        ordem_servico_atualizada = get_ordem_servico_or_404(id_os)
        valor_total = float(ordem_servico_atualizada.valor_total) if ordem_servico_atualizada.valor_total else 0.0
        
        if valor_total > 0:
            movimentacao_financeira_repository.registrar_entrada_financeira(
                valor=valor_total,
                descricao=f"Faturamento da OS #{id_os}"
            )
        # ----------------------------------------------------
        
        # Retorna ordem de serviço atualizada
        return ordem_servico_atualizada
    except psycopg2.IntegrityError:
        logger.error("concluir_ordem_servico erro de integridade id=%s", id_os)
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

def iniciar_ordem_servico(id_os: int):
    """Inicia uma ordem de serviço."""
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    # Validação de status
    if ordem_servico.status != "aberta":
        logger.warning("ordem de serviço não pode ser iniciada status=%s id=%s", 
                     ordem_servico.status, id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas ordens de serviço 'abertas' podem ser iniciadas"
        )
    
    try:
        os_repo.iniciar_ordem_servico(id_os)
        logger.info("ordem de serviço iniciada id=%s", id_os)
        # Retorna ordem de serviço atualizada
        return get_ordem_servico_or_404(id_os)
    except psycopg2.IntegrityError:
        logger.error("iniciar_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar ordem de serviço"
        )
