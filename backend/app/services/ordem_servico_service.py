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
            orcamento_status = getattr(orc, "status", None) if not isinstance(orc, dict) else orc.get("status")
            
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
    if id_veiculo and not os_repo.check_veiculo_exists(id_veiculo):
        logger.warning("veículo não encontrado veiculo_id=%s", id_veiculo)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado"
        )
    
    if id_usuario and not os_repo.check_mecanico_atribuivel(id_usuario):
        logger.warning("mecânico não encontrado ou não atribuível mecanico_id=%s", id_usuario)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mecânico não encontrado ou não possui permissões necessárias"
        )
    
    if descricao_problema and len(descricao_problema.strip()) == 0:
        logger.warning("descrição do problema vazia")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição do problema é obrigatória"
        )


def create_ordem_servico(data: OrdemServicoCreate):
    """Cria uma nova ordem de serviço com validações."""
    validate_ordem_servico_data(
        id_veiculo=data.id_veiculo,
        id_usuario=data.id_usuario,
        descricao_problema=data.descricao_problema
    )
    
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
    get_ordem_servico_or_404(id_os)
    
    if not os_repo.check_usuario_exists(id_usuario):
        logger.warning("mecânico não encontrado mecanico_id=%s", id_usuario)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mecânico não encontrado"
        )
        
    if not os_repo.check_mecanico_atribuivel(id_usuario):
        logger.warning("usuário não possui perfil para assumir OS mecanico_id=%s", id_usuario)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário informado não pode ser atribuído como mecânico responsável"
        )
    
    updated = os_repo.atribuir_mecanico_os(id_os=id_os, id_usuario=id_usuario)
    
    if not updated:
        logger.error("erro ao atribuir mecânico os=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atribuir mecânico"
        )
    
    # CORREÇÃO: O repositório revisado já devolve um objeto OrdemServico, não um dict.
    return updated


def update_ordem_servico(id_os: int, data: OrdemServicoUpdate):
    """Atualiza uma ordem de serviço com validações."""
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    validate_ordem_servico_data(
        id_veiculo=data.id_veiculo,
        id_usuario=data.id_usuario,
        descricao_problema=data.descricao_problema
    )
    
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
    """Atualiza apenas o status da ordem de serviço guardando regras de negócio."""
    ordem_servico = get_ordem_servico_or_404(id_os)

    # Se a intenção for concluir, desvia o fluxo para a função correta que lida com faturamento
    if data.status == "concluida":
        return concluir_ordem_servico(id_os)

    if ordem_servico.id_orcamento:
        orc = orcamento_repo.get_orcamento_by_id(ordem_servico.id_orcamento)
        orc_status = orc.get("status") if isinstance(orc, dict) else getattr(orc, "status", None)
        if orc_status != "aprovado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A alteração de status só é permitida após aprovação do orçamento.",
            )
    
    status_validos = ["aberta", "em_andamento", "concluida", "cancelada"]
    if data.status not in status_validos:
        logger.warning("status inválido status=%s", data.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    if ordem_servico.status == "concluida":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída e não pode ser modificada"
        )
    
    if ordem_servico.status == "cancelada" and data.status != "aberta":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada só pode ser reaberta com status 'aberta'"
        )
    
    try:
        os_repo.update_status_ordem_servico(id_os, data.status)
        return get_ordem_servico_or_404(id_os)
    except psycopg2.IntegrityError:
        logger.error("update_status_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status da ordem de serviço"
        )


def concluir_ordem_servico(id_os: int):
    """Conclui uma ordem de serviço (preenche data_conclusao) e lança faturamento."""
    ordem_servico = get_ordem_servico_or_404(id_os)
    
    if ordem_servico.status == "concluida":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço já está concluída"
        )
    
    if ordem_servico.status == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ordem de serviço cancelada não pode ser concluída"
        )
    
    try:
        os_repo.concluir_ordem_servico(id_os)
        logger.info("ordem de serviço concluída id=%s", id_os)
        
        # --- Movimentação financeira na conclusão ---
        from app.repositories import movimentacao_financeira_repository
        
        ordem_servico_atualizada = get_ordem_servico_or_404(id_os)
        valor_total = float(ordem_servico_atualizada.valor_total) if ordem_servico_atualizada.valor_total else 0.0
        
        if valor_total > 0:
            movimentacao_financeira_repository.registrar_entrada_financeira(
                valor=valor_total,
                descricao=f"Faturamento da OS #{id_os}"
            )
        
        return ordem_servico_atualizada
    except psycopg2.IntegrityError:
        logger.error("concluir_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao concluir ordem de serviço"
        )


def get_ordens_by_status(status: str):
    """Lista ordens de serviço por status com validação de payload."""
    status_validos = ["aberta", "em_andamento", "concluida", "cancelada"]
    if status not in status_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    return os_repo.get_ordens_by_status(status)


def get_ordens_by_veiculo(veiculo_id: int):
    """Lista ordens de serviço de um veículo específico."""
    if not os_repo.check_veiculo_exists(veiculo_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return os_repo.get_ordens_by_veiculo(veiculo_id)


def iniciar_ordem_servico(id_os: int):
    """Inicia uma ordem de serviço aberta."""
    ordem_servico = get_ordem_servico_or_404(id_os)

    if ordem_servico.status != "aberta":
        logger.warning("ordem de serviço não pode ser iniciada status=%s id=%s", ordem_servico.status, id_os)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas ordens de serviço 'abertas' podem ser iniciadas"
        )

    try:
        os_repo.iniciar_ordem_servico(id_os)
        return get_ordem_servico_or_404(id_os)
    except psycopg2.IntegrityError:
        logger.error("iniciar_ordem_servico erro de integridade id=%s", id_os)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar ordem de serviço"
        )


def get_ordem_servico_servicos(id_os: int):
    """Busca serviços vinculados à ordem de serviço."""
    return os_repo.get_ordem_servico_servicos(id_os)


def get_ordem_servico_pecas(id_os: int):
    """Busca peças vinculadas à ordem de serviço."""
    return os_repo.get_ordem_servico_pecas(id_os)


def get_ordem_servico_movimentacoes(id_os: int):
    """Busca movimentações de estoque das peças da ordem de serviço."""
    return os_repo.get_ordem_servico_movimentacoes(id_os)