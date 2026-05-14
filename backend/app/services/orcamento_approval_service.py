import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrdemServico, OrdemServicoPeca, OrdemServicoServico
from app.repositories import orcamento_repository as orcamento_repo
from app.repositories import ordem_servico_repository as os_repo
from app.repositories import ordem_servico_peca_repository as os_peca_repo
from app.repositories import ordem_servico_servico_repository as os_servico_repo
from app.repositories import orcamento_peca_repository as orc_peca_repo
from app.repositories import orcamento_servico_repository as orc_servico_repo

logger = logging.getLogger(__name__)

def aprovar_orcamento(orcamento_id: int):
    """Aprova orçamento e gera OS automaticamente."""
    # Validação do orçamento
    orcamento = orcamento_repo.get_orcamento_by_id(orcamento_id)
    if not orcamento:
        logger.warning("orçamento não encontrado id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Verifica se orçamento já foi aprovado/rejeitado
    if orcamento.status not in ["pendente"]:
        logger.warning("orçamento não pode ser aprovado status=%s", orcamento.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Orçamento não pode ser aprovado no status atual"
        )
    
    try:
        # Atualiza status do orçamento
        orcamento_repo.update_status_orcamento(orcamento_id, "aprovado")
        
        # Cria ordem de serviço
        ordem_servico = OrdemServico(
            id_orcamento=orcamento_id,
            id_veiculo=orcamento.id_veiculo,
            status="aberta",
            valor_total=orcamento.valor_total,
            data_inicio=datetime.now(timezone.utc)
        )
        ordem_servico = os_repo.create_ordem_servico(ordem_servico)
        
        # Copia itens do orçamento para a OS
        _copiar_itens_orcamento_para_os(orcamento_id, ordem_servico.id_ordem_servico)
        
        logger.info("orçamento aprovado e OS gerada orcamento=%s os=%s", 
                   orcamento_id, ordem_servico.id_ordem_servico)
        
        return ordem_servico
        
    except psycopg2.IntegrityError:
        logger.error("aprovar_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao aprovar orçamento"
        )

def rejeitar_orcamento(orcamento_id: int):
    """Rejeita orçamento."""
    # Validação do orçamento
    orcamento = orcamento_repo.get_orcamento_by_id(orcamento_id)
    if not orcamento:
        logger.warning("orçamento não encontrado id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Verifica se orçamento já foi aprovado/rejeitado
    if orcamento.status not in ["pendente"]:
        logger.warning("orçamento não pode ser rejeitado status=%s", orcamento.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Orçamento não pode ser rejeitado no status atual"
        )
    
    try:
        # Apenas atualiza status do orçamento
        orcamento_repo.update_status_orcamento(orcamento_id, "rejeitado")
        
        logger.info("orçamento rejeitado orcamento=%s", orcamento_id)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("rejeitar_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao rejeitar orçamento"
        )

def _copiar_itens_orcamento_para_os(orcamento_id: int, ordem_servico_id: int):
    """Função interna para copiar itens do orçamento para a OS."""
    # Copia peças
    pecas_orcamento = orc_peca_repo.get_pecas_by_orcamento(orcamento_id)
    for peca_orc in pecas_orcamento:
        os_peca = OrdemServicoPeca(
            id_ordem_servico=ordem_servico_id,
            id_peca=peca_orc.id_peca,
            quantidade=peca_orc.quantidade
        )
        os_peca_repo.add_peca_to_ordem_servico(os_peca)
    
    # Copia serviços
    servicos_orcamento = orc_servico_repo.get_servicos_by_orcamento(orcamento_id)
    for servico_orc in servicos_orcamento:
        os_servico = OrdemServicoServico(
            id_ordem_servico=ordem_servico_id,
            id_servico=servico_orc.id_servico,
            quantidade=servico_orc.quantidade
        )
        os_servico_repo.add_servico_to_ordem_servico(os_servico)
    
    logger.info("itens copiados para OS orcamento=%s os=%s pecas=%s servicos=%s", 
                orcamento_id, ordem_servico_id, len(pecas_orcamento), len(servicos_orcamento))

def get_ordens_by_orcamento(orcamento_id: int):
    """Lista ordens de serviço de um orçamento."""
    if not orcamento_repo.check_orcamento_exists(orcamento_id):
        logger.warning("orçamento não encontrado id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    return os_repo.get_ordens_by_orcamento(orcamento_id)
