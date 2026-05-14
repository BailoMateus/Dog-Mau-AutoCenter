import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrcamentoPeca, OrcamentoServico
from app.repositories import orcamento_repository as orcamento_repo
from app.repositories import orcamento_peca_repository as peca_repo
from app.repositories import orcamento_servico_repository as servico_repo
from app.repositories import peca_repository as peca_base_repo
from app.repositories import servico_repository as servico_base_repo
from app.schemas.orcamento_item_schema import (
    OrcamentoPecaCreate, OrcamentoPecaUpdate, OrcamentoServicoCreate, OrcamentoServicoUpdate
)

logger = logging.getLogger(__name__)

def get_itens_orcamento(orcamento_id: int, tipo_item: str):
    """Lista todos os itens de um orçamento por tipo."""
    # Verifica se orçamento existe
    orcamento = orcamento_repo.get_orcamento_by_id(orcamento_id)
    if not orcamento:
        logger.info("orçamento não encontrado id=%s", orcamento_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    
    if tipo_item == "peca":
        return peca_repo.get_pecas_by_orcamento(orcamento_id)
    elif tipo_item == "servico":
        return servico_repo.get_servicos_by_orcamento(orcamento_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de item inválido")

def validate_orcamento_item_data(orcamento_id: int, item_id: int, quantidade: int, tipo_item: str):
    """Valida dados de item do orçamento."""
    # Validação de orçamento existente
    orcamento = orcamento_repo.get_orcamento_by_id(orcamento_id)
    if not orcamento:
        logger.warning("orçamento não encontrado orcamento_id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Validação de quantidade
    if quantidade <= 0:
        logger.warning("quantidade inválida quantidade=%s", quantidade)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero"
        )
    
    # Validação de item existente
    if tipo_item == "peca":
        item = peca_base_repo.get_peca_by_id(item_id)
        if not item:
            logger.warning("peça não encontrada peca_id=%s", item_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peça não encontrada"
            )
    elif tipo_item == "servico":
        item = servico_base_repo.get_servico_by_id(item_id)
        if not item:
            logger.warning("serviço não encontrado servico_id=%s", item_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Serviço não encontrado"
            )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de item inválido")
    
    return orcamento, item

def recalcular_valor_total_orcamento(orcamento_id: int):
    """Recalcula e atualiza o valor total do orçamento."""
    valor_pecas = peca_repo.calcular_valor_total_pecas(orcamento_id)
    valor_servicos = servico_repo.calcular_valor_total_servicos(orcamento_id)
    novo_valor_total = valor_pecas + valor_servicos
    
    orcamento_repo.update_valor_total_orcamento(orcamento_id, novo_valor_total)
    logger.info("valor total recalculado orcamento=%s novo_valor=%s", orcamento_id, novo_valor_total)
    
    return novo_valor_total

def add_peca_to_orcamento(orcamento_id: int, data: OrcamentoPecaCreate):
    """Adiciona peça ao orçamento com validações."""
    # Validações
    orcamento, peca = validate_orcamento_item_data(orcamento_id, data.id_peca, data.quantidade, "peca")
    
    # Cria item do orçamento
    item = OrcamentoPeca(
        id_orcamento=orcamento_id,
        id_peca=data.id_peca,
        quantidade=data.quantidade
    )
    
    try:
        # Adiciona peça ao orçamento
        peca_repo.add_peca_to_orcamento(item)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("peça adicionada ao orçamento orcamento=%s peca=%s quantidade=%s", 
                   orcamento_id, data.id_peca, data.quantidade)
        
        # Retorna item com informações da peça
        item_com_info = peca_repo.get_orcamento_peca(orcamento_id, data.id_peca)
        item_com_info.peca_nome = peca.nome
        item_com_info.peca_preco = peca.preco_unitario
        
        return item_com_info
        
    except psycopg2.IntegrityError:
        logger.error("add_peca_to_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar peça ao orçamento"
        )

def add_servico_to_orcamento(orcamento_id: int, data: OrcamentoServicoCreate):
    """Adiciona serviço ao orçamento com validações."""
    # Validações
    orcamento, servico = validate_orcamento_item_data(orcamento_id, data.id_servico, data.quantidade, "servico")
    
    # Cria item do orçamento
    item = OrcamentoServico(
        id_orcamento=orcamento_id,
        id_servico=data.id_servico,
        quantidade=data.quantidade
    )
    
    try:
        # Adiciona serviço ao orçamento
        servico_repo.add_servico_to_orcamento(item)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("serviço adicionado ao orçamento orcamento=%s servico=%s quantidade=%s", 
                   orcamento_id, data.id_servico, data.quantidade)
        
        # Retorna item com informações do serviço
        item_com_info = servico_repo.get_orcamento_servico(orcamento_id, data.id_servico)
        item_com_info.servico_descricao = servico.descricao
        item_com_info.servico_preco = servico.preco
        
        return item_com_info
        
    except psycopg2.IntegrityError:
        logger.error("add_servico_to_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar serviço ao orçamento"
        )

def update_quantidade_peca(orcamento_id: int, peca_id: int, data: OrcamentoPecaUpdate):
    """Atualiza quantidade de peça no orçamento."""
    # Validações
    orcamento, peca = validate_orcamento_item_data(orcamento_id, peca_id, data.quantidade, "peca")
    
    # Verifica se peça existe no orçamento
    item_existente = peca_repo.get_orcamento_peca(orcamento_id, peca_id)
    if not item_existente:
        logger.warning("peça não encontrada no orçamento orcamento=%s peca=%s", orcamento_id, peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada no orçamento"
        )
    
    try:
        # Atualiza quantidade
        item_atualizado = peca_repo.update_quantidade_peca(orcamento_id, peca_id, data.quantidade)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("quantidade atualizada orcamento=%s peca=%s nova_quantidade=%s", 
                   orcamento_id, peca_id, data.quantidade)
        
        # Retorna item com informações da peça
        item_atualizado.peca_nome = peca.nome
        item_atualizado.peca_preco = peca.preco_unitario
        
        return item_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("update_quantidade_peca erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar quantidade"
        )

def update_quantidade_servico(orcamento_id: int, servico_id: int, data: OrcamentoServicoUpdate):
    """Atualiza quantidade de serviço no orçamento."""
    # Validações
    orcamento, servico = validate_orcamento_item_data(orcamento_id, servico_id, data.quantidade, "servico")
    
    # Verifica se serviço existe no orçamento
    item_existente = servico_repo.get_orcamento_servico(orcamento_id, servico_id)
    if not item_existente:
        logger.warning("serviço não encontrado no orçamento orcamento=%s servico=%s", orcamento_id, servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado no orçamento"
        )
    
    try:
        # Atualiza quantidade
        item_atualizado = servico_repo.update_quantidade_servico(orcamento_id, servico_id, data.quantidade)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("quantidade atualizada orcamento=%s servico=%s nova_quantidade=%s", 
                   orcamento_id, servico_id, data.quantidade)
        
        # Retorna item com informações do serviço
        item_atualizado.servico_descricao = servico.descricao
        item_atualizado.servico_preco = servico.preco
        
        return item_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("update_quantidade_servico erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar quantidade"
        )

def remove_peca_from_orcamento(orcamento_id: int, peca_id: int):
    """Remove peça do orçamento."""
    # Validações
    orcamento, peca = validate_orcamento_item_data(orcamento_id, peca_id, 1, "peca")
    
    # Verifica se peça existe no orçamento
    item_existente = peca_repo.get_orcamento_peca(orcamento_id, peca_id)
    if not item_existente:
        logger.warning("peça não encontrada no orçamento orcamento=%s peca=%s", orcamento_id, peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada no orçamento"
        )
    
    try:
        # Remove peça do orçamento
        peca_repo.remove_peca_from_orcamento(orcamento_id, peca_id)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("peça removida do orçamento orcamento=%s peca=%s", orcamento_id, peca_id)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("remove_peca_from_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover peça do orçamento"
        )

def remove_servico_from_orcamento(orcamento_id: int, servico_id: int):
    """Remove serviço do orçamento."""
    # Validações
    orcamento, servico = validate_orcamento_item_data(orcamento_id, servico_id, 1, "servico")
    
    # Verifica se serviço existe no orçamento
    item_existente = servico_repo.get_orcamento_servico(orcamento_id, servico_id)
    if not item_existente:
        logger.warning("serviço não encontrado no orçamento orcamento=%s servico=%s", orcamento_id, servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado no orçamento"
        )
    
    try:
        # Remove serviço do orçamento
        servico_repo.remove_servico_from_orcamento(orcamento_id, servico_id)
        
        # Recalcula valor total do orçamento
        recalcular_valor_total_orcamento(orcamento_id)
        
        logger.info("serviço removido do orçamento orcamento=%s servico=%s", orcamento_id, servico_id)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("remove_servico_from_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover serviço do orçamento"
        )
