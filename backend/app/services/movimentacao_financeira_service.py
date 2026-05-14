import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import MovimentacaoFinanceira
from app.repositories import movimentacao_financeira_repository as movimentacao_repo
from app.schemas.movimentacao_financeira_schema import (
    MovimentacaoFinanceiraCreate, MovimentacaoFinanceiraPeriodo
)

logger = logging.getLogger(__name__)

def list_all_movimentacoes_financeiras(limit: int = 100):
    """Lista todas as movimentações financeiras."""
    return movimentacao_repo.get_all_movimentacoes_financeiras(limit)

def list_movimentacoes_by_tipo(tipo: str, limit: int = 50):
    """Lista movimentações por tipo (entrada/saida)."""
    # Validação de tipo
    tipos_validos = ["entrada", "saida"]
    if tipo not in tipos_validos:
        logger.warning("tipo inválido tipo=%s", tipo)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Valores permitidos: {', '.join(tipos_validos)}"
        )
    
    return movimentacao_repo.get_movimentacoes_by_tipo(tipo, limit)

def list_movimentacoes_by_periodo(data: MovimentacaoFinanceiraPeriodo):
    """Lista movimentações por período."""
    # Validação de datas
    if data.data_inicio >= data.data_fim:
        logger.warning("período inválido inicio=%s fim=%s", data.data_inicio, data.data_fim)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de início deve ser anterior à data de fim"
        )
    
    # Validação de período máximo (1 ano)
    diferenca = data.data_fim - data.data_inicio
    if diferenca.days > 365:
        logger.warning("período muito longo dias=%s", diferenca.days)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Período não pode ser superior a 365 dias"
        )
    
    return movimentacao_repo.get_movimentacoes_by_periodo(
        data.data_inicio, data.data_fim, data.limit
    )

def get_movimentacao_financeira_by_id(movimentacao_id: int):
    """Busca movimentação financeira por ID."""
    movimentacao = movimentacao_repo.get_movimentacao_financeira_by_id(movimentacao_id)
    if not movimentacao:
        logger.warning("movimentação não encontrada id=%s", movimentacao_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimentação financeira não encontrada"
        )
    return movimentacao

def validate_movimentacao_data(valor: float, descricao: str, tipo_movimentacao: str):
    """Valida dados da movimentação financeira."""
    # Validação de valor
    if valor <= 0:
        logger.warning("valor inválido valor=%s", valor)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor deve ser maior que zero"
        )
    
    # Validação de descrição
    if not descricao or len(descricao.strip()) == 0:
        logger.warning("descrição vazia")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição é obrigatória"
        )
    
    if len(descricao) > 255:
        logger.warning("descrição muito longa tamanho=%s", len(descricao))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Descrição deve ter no máximo 255 caracteres"
        )
    
    # Validação de tipo
    tipos_validos = ["entrada", "saida"]
    if tipo_movimentacao not in tipos_validos:
        logger.warning("tipo inválido tipo=%s", tipo_movimentacao)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Valores permitidos: {', '.join(tipos_validos)}"
        )

def registrar_entrada_financeira(data: MovimentacaoFinanceiraCreate):
    """Registra entrada financeira com validações."""
    # Validações
    validate_movimentacao_data(data.valor, data.descricao, "entrada")
    
    try:
        # Registra entrada
        movimentacao = movimentacao_repo.registrar_entrada_financeira(
            valor=data.valor,
            descricao=data.descricao,
            pagamento_id=data.id_pagamento
        )
        
        logger.info("entrada financeira registrada valor=%s descricao=%s pagamento_id=%s", 
                   data.valor, data.descricao, data.id_pagamento)
        
        return movimentacao
        
    except ValueError as e:
        logger.error("registrar_entrada_financeira erro %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except psycopg2.IntegrityError:
        logger.error("registrar_entrada_financeira erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar entrada financeira"
        )

def registrar_saida_financeira(data: MovimentacaoFinanceiraCreate):
    """Registra saída financeira com validações."""
    # Validações
    validate_movimentacao_data(data.valor, data.descricao, "saida")
    
    try:
        # Registra saída
        movimentacao = movimentacao_repo.registrar_saida_financeira(
            valor=data.valor,
            descricao=data.descricao,
            pagamento_id=data.id_pagamento
        )
        
        logger.info("saída financeira registrada valor=%s descricao=%s pagamento_id=%s", 
                   data.valor, data.descricao, data.id_pagamento)
        
        return movimentacao
        
    except ValueError as e:
        logger.error("registrar_saida_financeira erro %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except psycopg2.IntegrityError:
        logger.error("registrar_saida_financeira erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar saída financeira"
        )

def calcular_saldo_periodo(data: MovimentacaoFinanceiraPeriodo):
    """Calcula saldo de entradas e saídas em um período."""
    # Validação de datas
    if data.data_inicio >= data.data_fim:
        logger.warning("período inválido inicio=%s fim=%s", data.data_inicio, data.data_fim)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data de início deve ser anterior à data de fim"
        )
    
    # Validação de período máximo (1 ano)
    diferenca = data.data_fim - data.data_inicio
    if diferenca.days > 365:
        logger.warning("período muito longo dias=%s", diferenca.days)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Período não pode ser superior a 365 dias"
        )
    
    return movimentacao_repo.calcular_saldo_periodo(data.data_inicio, data.data_fim)

def get_resumo_financeiro(data_inicio: datetime = None, data_fim: datetime = None):
    """Gera resumo financeiro geral ou por período."""
    # Se não fornecido, usa mês atual
    if not data_inicio:
        agora = datetime.now(timezone.utc)
        data_inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not data_fim:
        data_fim = datetime.now(timezone.utc)
    
    # Validação de período máximo (1 ano)
    if data_inicio and data_fim:
        diferenca = data_fim - data_inicio
        if diferenca.days > 365:
            logger.warning("período muito longo dias=%s", diferenca.days)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Período não pode ser superior a 365 dias"
            )
    
    return movimentacao_repo.get_resumo_financeiro(data_inicio, data_fim)

def get_movimentacoes_by_pagamento(pagamento_id: int):
    """Lista movimentações de um pagamento."""
    # Validação de pagamento
    if not movimentacao_repo.check_pagamento_exists(pagamento_id):
        logger.warning("pagamento não encontrado pagamento_id=%s", pagamento_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado"
        )
    
    return movimentacao_repo.get_movimentacoes_by_pagamento(pagamento_id)
