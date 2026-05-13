import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Pagamento
from app.repositories import pagamento_repository as pagamento_repo
from app.schemas.pagamento_schema import (
    PagamentoCreate, PagamentoUpdate, PagamentoStatusUpdate
)

logger = logging.getLogger(__name__)

def list_all_pagamentos(limit: int = 100):
    """Lista todos os pagamentos."""
    return pagamento_repo.get_all_pagamentos(limit)

def list_pagamentos_by_os(os_id: int):
    """Lista pagamentos de uma OS específica."""
    # Verifica se OS existe
    if not pagamento_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return pagamento_repo.get_pagamentos_by_os(os_id)

def list_pagamentos_by_status(status: str, limit: int = 50):
    """Lista pagamentos por status."""
    # Validação de status
    status_validos = ["pendente", "confirmado", "cancelado"]
    if status not in status_validos:
        logger.warning("status inválido status=%s", status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    return pagamento_repo.get_pagamentos_by_status(status, limit)

def get_pagamento_by_id(pagamento_id: int):
    """Busca pagamento por ID."""
    pagamento = pagamento_repo.get_pagamento_by_id(pagamento_id)
    if not pagamento:
        logger.warning("pagamento não encontrado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado"
        )
    return pagamento

def validate_pagamento_data(os_id: int, valor: float, forma_pagamento: str):
    """Valida dados do pagamento."""
    # Validação de OS existente
    if not pagamento_repo.check_os_exists(os_id):
        logger.warning("OS não encontrada os_id=%s", os_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordem de serviço não encontrada"
        )
    
    # Validação de valor
    if valor <= 0:
        logger.warning("valor inválido valor=%s", valor)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor deve ser maior que zero"
        )
    
    # Validação de forma de pagamento
    if not forma_pagamento or len(forma_pagamento.strip()) == 0:
        logger.warning("forma de pagamento vazia")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forma de pagamento é obrigatória"
        )

def registrar_pagamento(data: PagamentoCreate):
    """Registra um novo pagamento."""
    # Validações
    validate_pagamento_data(data.id_os, data.valor, data.forma_pagamento)
    
    # Cria pagamento
    pagamento = Pagamento(
        id_os=data.id_os,
        valor=data.valor,
        forma_pagamento=data.forma_pagamento,
        status="pendente"
    )
    
    try:
        # Salva pagamento
        pagamento = pagamento_repo.create_pagamento(pagamento)
        
        logger.info("pagamento registrado id=%s os=%s valor=%s forma=%s", 
                   pagamento.id_pagamento, pagamento.id_os, pagamento.valor, pagamento.forma_pagamento)
        
        return pagamento
        
    except psycopg2.IntegrityError:
        logger.error("registrar_pagamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar pagamento"
        )

def atualizar_status_pagamento(pagamento_id: int, data: PagamentoStatusUpdate):
    """Atualiza status de um pagamento."""
    # Verifica se pagamento existe
    pagamento_existente = get_pagamento_by_id(pagamento_id)
    
    # Validação de status
    status_validos = ["pendente", "confirmado", "cancelado"]
    if data.status not in status_validos:
        logger.warning("status inválido status=%s", data.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    # Validação de fluxo de status
    if pagamento_existente.status == "confirmado" and data.status != "cancelado":
        logger.warning("tentativa de alterar pagamento confirmado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento confirmado só pode ser cancelado"
        )
    
    if pagamento_existente.status == "cancelado":
        logger.warning("tentativa de alterar pagamento cancelado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento cancelado não pode ser alterado"
        )
    
    try:
        # Atualiza status
        pagamento_atualizado = pagamento_repo.update_status_pagamento(pagamento_id, data.status)
        
        logger.info("status pagamento atualizado id=%s antigo=%s novo=%s", 
                   pagamento_id, pagamento_existente.status, data.status)
        
        return pagamento_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("atualizar_status_pagamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status do pagamento"
        )

def atualizar_pagamento(pagamento_id: int, data: PagamentoUpdate):
    """Atualiza dados completos de um pagamento."""
    # Verifica se pagamento existe
    pagamento_existente = get_pagamento_by_id(pagamento_id)
    
    # Validações
    validate_pagamento_data(pagamento_existente.id_os, data.valor, data.forma_pagamento)
    
    # Validação de status
    status_validos = ["pendente", "confirmado", "cancelado"]
    if data.status not in status_validos:
        logger.warning("status inválido status=%s", data.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    # Validação de fluxo de status
    if pagamento_existente.status == "confirmado" and data.status != "cancelado":
        logger.warning("tentativa de alterar pagamento confirmado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento confirmado só pode ser cancelado"
        )
    
    if pagamento_existente.status == "cancelado":
        logger.warning("tentativa de alterar pagamento cancelado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento cancelado não pode ser alterado"
        )
    
    # Atualiza pagamento
    pagamento_atualizado = Pagamento(
        id_pagamento=pagamento_id,
        id_os=pagamento_existente.id_os,
        valor=data.valor,
        forma_pagamento=data.forma_pagamento,
        status=data.status,
        data_pagamento=pagamento_existente.data_pagamento
    )
    
    try:
        pagamento_atualizado = pagamento_repo.update_pagamento(pagamento_atualizado)
        
        logger.info("pagamento atualizado id=%s valor=%s status=%s", 
                   pagamento_id, data.valor, data.status)
        
        return pagamento_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("atualizar_pagamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar pagamento"
        )

def calcular_total_pagamentos_os(os_id: int):
    """Calcula valor total dos pagamentos confirmados de uma OS."""
    # Verifica se OS existe
    if not pagamento_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return pagamento_repo.calcular_total_pagamentos_os(os_id)

def soft_delete_pagamento(pagamento_id: int):
    """Remove um pagamento (soft delete)."""
    # Verifica se pagamento existe
    pagamento_existente = get_pagamento_by_id(pagamento_id)
    
    # Validação: não pode remover pagamento confirmado
    if pagamento_existente.status == "confirmado":
        logger.warning("tentativa de remover pagamento confirmado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagamento confirmado não pode ser removido"
        )
    
    try:
        pagamento_repo.soft_delete_pagamento(pagamento_id)
        logger.info("pagamento removido id=%s", pagamento_id)
        
    except psycopg2.IntegrityError:
        logger.error("soft_delete_pagamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover pagamento"
        )
