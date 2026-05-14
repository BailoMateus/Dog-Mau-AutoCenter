import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrdemServicoServico
from app.repositories import os_servico_repository as os_servico_repo
from app.repositories import servico_repository as servico_base_repo
from app.schemas.os_servico_schema import (
    OsServicoCreate, OsServicoUpdate
)

logger = logging.getLogger(__name__)

def get_servicos_by_os(os_id: int):
    """Lista todos os serviços de uma OS."""
    # Verifica se OS existe
    if not os_servico_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return os_servico_repo.get_servicos_by_os(os_id)

def validate_os_servico_data(os_id: int, servico_id: int, quantidade: int):
    """Valida dados de serviço da OS."""
    # Validação de OS existente
    if not os_servico_repo.check_os_exists(os_id):
        logger.warning("OS não encontrada os_id=%s", os_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )
    
    # Validação de quantidade
    if quantidade <= 0:
        logger.warning("quantidade inválida quantidade=%s", quantidade)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero"
        )
    
    # Validação de serviço existente
    if not os_servico_repo.check_servico_exists(servico_id):
        logger.warning("serviço não encontrado servico_id=%s", servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

def add_servico_to_os(os_id: int, data: OsServicoCreate):
    """Adiciona serviço à OS com validações."""
    # Validações
    validate_os_servico_data(os_id, data.id_servico, data.quantidade)
    
    # Cria item da OS
    item = OrdemServicoServico(
        id_os=os_id,
        id_servico=data.id_servico,
        quantidade=data.quantidade
    )
    
    try:
        # Adiciona serviço à OS
        os_servico_repo.add_servico_to_os(item)
        
        logger.info("serviço adicionado à OS os=%s servico=%s quantidade=%s", 
                   os_id, data.id_servico, data.quantidade)
        
        # Retorna item com informações do serviço e subtotal
        item_com_info = os_servico_repo.get_os_servico(os_id, data.id_servico)
        servico_preco = os_servico_repo.get_servico_preco(data.id_servico)
        item_com_info.servico_preco = servico_preco
        item_com_info.subtotal = servico_preco * item_com_info.quantidade
        
        return item_com_info
        
    except psycopg2.IntegrityError:
        logger.error("add_servico_to_os erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar serviço à OS"
        )

def update_quantidade_servico(os_id: int, servico_id: int, data: OsServicoUpdate):
    """Atualiza quantidade de serviço na OS."""
    # Validações
    validate_os_servico_data(os_id, servico_id, data.quantidade)
    
    # Verifica se serviço existe na OS
    item_existente = os_servico_repo.get_os_servico(os_id, servico_id)
    if not item_existente:
        logger.warning("serviço não encontrado na OS os=%s servico=%s", os_id, servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado na ordem de serviço"
        )
    
    try:
        # Atualiza quantidade
        item_atualizado = os_servico_repo.update_quantidade_servico(os_id, servico_id, data.quantidade)
        
        logger.info("quantidade atualizada os=%s servico=%s nova_quantidade=%s", 
                   os_id, servico_id, data.quantidade)
        
        # Retorna item com informações do serviço e subtotal
        servico_preco = os_servico_repo.get_servico_preco(servico_id)
        item_atualizado.servico_preco = servico_preco
        item_atualizado.subtotal = servico_preco * item_atualizado.quantidade
        
        return item_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("update_quantidade_servico erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar quantidade"
        )

def remove_servico_from_os(os_id: int, servico_id: int):
    """Remove serviço da OS."""
    # Validações (quantidade=1 só para verificação de existência)
    validate_os_servico_data(os_id, servico_id, 1)
    
    # Verifica se serviço existe na OS
    item_existente = os_servico_repo.get_os_servico(os_id, servico_id)
    if not item_existente:
        logger.warning("serviço não encontrado na OS os=%s servico=%s", os_id, servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado na ordem de serviço"
        )
    
    try:
        # Remove serviço da OS
        os_servico_repo.remove_servico_from_os(os_id, servico_id)
        
        logger.info("serviço removido da OS os=%s servico=%s", os_id, servico_id)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("remove_servico_from_os erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover serviço da OS"
        )

def calcular_valor_total_servicos(os_id: int):
    """Calcula valor total dos serviços da OS."""
    # Verifica se OS existe
    if not os_servico_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return os_servico_repo.calcular_valor_total_servicos(os_id)

def get_servico_by_os(os_id: int, servico_id: int):
    """Busca serviço específico de uma OS."""
    # Validações (quantidade=1 só para verificação de existência)
    validate_os_servico_data(os_id, servico_id, 1)
    
    item = os_servico_repo.get_os_servico(os_id, servico_id)
    if not item:
        logger.warning("serviço não encontrado na OS os=%s servico=%s", os_id, servico_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado na ordem de serviço"
        )
    
    # Adiciona informações do serviço e subtotal
    servico_preco = os_servico_repo.get_servico_preco(servico_id)
    item.servico_preco = servico_preco
    item.subtotal = servico_preco * item.quantidade
    
    return item
