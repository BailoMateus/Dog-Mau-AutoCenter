import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import MovimentacaoEstoque
from app.repositories import movimentacao_estoque_repository as movimentacao_repo
from app.repositories import peca_repository as peca_base_repo
from app.schemas.movimentacao_estoque_schema import (
    MovimentacaoEstoqueCreate
)

logger = logging.getLogger(__name__)

def list_all_movimentacoes(limit: int = 100):
    """Lista todas as movimentações de estoque."""
    return movimentacao_repo.get_all_movimentacoes(limit)

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

def list_movimentacoes_by_peca(peca_id: int, limit: int = 50):
    """Lista movimentações de uma peça específica."""
    # Verifica se peça existe
    if not peca_base_repo.check_peca_exists(peca_id):
        logger.warning("peça não encontrada peca_id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )
    
    return movimentacao_repo.get_movimentacoes_by_peca(peca_id, limit)

def validate_movimentacao_data(peca_id: int, quantidade: int, tipo_movimentacao: str):
    """Valida dados da movimentação."""
    # Validação de peça existente
    if not peca_base_repo.check_peca_exists(peca_id):
        logger.warning("peça não encontrada peca_id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )
    
    # Validação de quantidade
    if quantidade <= 0:
        logger.warning("quantidade inválida quantidade=%s", quantidade)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero"
        )
    
    # Validação de tipo
    tipos_validos = ["entrada", "saida"]
    if tipo_movimentacao not in tipos_validos:
        logger.warning("tipo inválido tipo=%s", tipo_movimentacao)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido. Valores permitidos: {', '.join(tipos_validos)}"
        )

def registrar_entrada_estoque(data: MovimentacaoEstoqueCreate):
    """Registra entrada de estoque com validações."""
    # Validações
    validate_movimentacao_data(data.id_peca, data.quantidade, "entrada")
    
    # Busca estoque atual para logging
    from app.repositories.os_peca_repository import get_peca_estoque
    estoque_anterior = get_peca_estoque(data.id_peca)
    
    try:
        # Registra entrada
        movimentacao = movimentacao_repo.registrar_entrada_estoque(
            peca_id=data.id_peca,
            quantidade=data.quantidade,
            motivo=data.motivo or "Entrada manual"
        )
        
        logger.info("entrada registrada peca=%s quantidade=%s estoque_anterior=%s motivo=%s", 
                   data.id_peca, data.quantidade, estoque_anterior, data.motivo)
        
        return movimentacao
        
    except psycopg2.IntegrityError:
        logger.error("registrar_entrada_estoque erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar entrada de estoque"
        )

def registrar_saida_estoque(data: MovimentacaoEstoqueCreate):
    """Registra saída de estoque com validações."""
    # Validações
    validate_movimentacao_data(data.id_peca, data.quantidade, "saida")
    
    # Busca estoque atual para validação
    from app.repositories.os_peca_repository import get_peca_estoque
    estoque_anterior = get_peca_estoque(data.id_peca)
    
    try:
        # Registra saída (validação de estoque suficiente acontece no repository)
        movimentacao = movimentacao_repo.registrar_saida_estoque(
            peca_id=data.id_peca,
            quantidade=data.quantidade,
            motivo=data.motivo or "Saída manual"
        )
        
        logger.info("saída registrada peca=%s quantidade=%s estoque_anterior=%s motivo=%s", 
                   data.id_peca, data.quantidade, estoque_anterior, data.motivo)
        
        return movimentacao
        
    except ValueError as e:
        logger.error("registrar_saida_estoque erro de estoque %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except psycopg2.IntegrityError:
        logger.error("registrar_saida_estoque erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar saída de estoque"
        )

def get_historico_peca(peca_id: int, dias: int = 30):
    """Busca histórico de movimentações de uma peça."""
    # Verifica se peça existe
    if not peca_base_repo.check_peca_exists(peca_id):
        logger.warning("peça não encontrada peca_id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )
    
    # Validação de dias
    if dias <= 0 or dias > 365:
        logger.warning("período inválido dias=%s", dias)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Período deve estar entre 1 e 365 dias"
        )
    
    return movimentacao_repo.get_historico_estoque(peca_id, dias)

def get_ultima_movimentacao_peca(peca_id: int):
    """Busca última movimentação de uma peça."""
    # Verifica se peça existe
    if not peca_base_repo.check_peca_exists(peca_id):
        logger.warning("peça não encontrada peca_id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )
    
    return movimentacao_repo.get_ultima_movimentacao_peca(peca_id)
