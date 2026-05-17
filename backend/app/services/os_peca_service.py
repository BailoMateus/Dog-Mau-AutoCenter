import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import OrdemServicoPeca
from app.repositories import os_peca_repository as os_peca_repo
from app.repositories import movimentacao_estoque_repository as movimentacao_repo
from app.schemas.os_peca_schema import (
    OsPecaCreate, OsPecaUpdate
)

logger = logging.getLogger(__name__)

def get_pecas_by_os(os_id: int):
    """Lista todas as peças de uma OS."""
    # Verifica se OS existe
    if not os_peca_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return os_peca_repo.get_pecas_by_os(os_id)

def validate_os_peca_data(os_id: int, peca_id: int, quantidade: int):
    """Valida dados de peça da OS."""
    # Validação de OS existente
    if not os_peca_repo.check_os_exists(os_id):
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
    
    # Validação de peça existente
    if not os_peca_repo.check_peca_exists(peca_id):
        logger.warning("peça não encontrada peca_id=%s", peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada"
        )

def validate_estoque_disponivel(peca_id: int, quantidade: int, quantidade_existente: int = 0):
    """Valida se há estoque disponível."""
    estoque_atual = os_peca_repo.get_peca_estoque(peca_id)
    quantidade_necessaria = quantidade - quantidade_existente
    
    if quantidade_necessaria > 0 and estoque_atual < quantidade_necessaria:
        logger.warning("estoque insuficiente peca=%s estoque=%s necessario=%s", 
                      peca_id, estoque_atual, quantidade_necessaria)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {estoque_atual}, Necessário: {quantidade_necessaria}"
        )
    
    return estoque_atual

def add_peca_to_os(os_id: int, data: OsPecaCreate):
    """Adiciona peça à OS com validação de estoque."""
    # Validações básicas
    validate_os_peca_data(os_id, data.id_peca, data.quantidade)
    
    # Verifica se peça já existe na OS
    item_existente = os_peca_repo.get_os_peca(os_id, data.id_peca)
    quantidade_existente = item_existente.quantidade if item_existente else 0
    
    # Valida estoque disponível
    estoque_atual = validate_estoque_disponivel(data.id_peca, data.quantidade, quantidade_existente)
    
    # Cria item da OS
    item = OrdemServicoPeca(
        id_os=os_id,
        id_peca=data.id_peca,
        quantidade=data.quantidade
    )
    
    try:
        # Adiciona peça à OS
        os_peca_repo.add_peca_to_os(item)
        
        # Calcula quantidade adicional para movimentação
        quantidade_adicional = data.quantidade - quantidade_existente
        
        # Registra movimentação de estoque se houver adição
        if quantidade_adicional > 0:
            movimentacao_repo.registrar_saida_estoque(
                peca_id=data.id_peca,
                quantidade=quantidade_adicional,
                id_os=os_id,
                motivo=f"Adição de peça na OS #{os_id}"
            )
        
        logger.info("peça adicionada à OS os=%s peca=%s quantidade=%s estoque_anterior=%s", 
                   os_id, data.id_peca, data.quantidade, estoque_atual)
        
        # Retorna item com informações da peça e subtotal
        item_com_info = os_peca_repo.get_os_peca(os_id, data.id_peca)
        peca_preco = os_peca_repo.get_peca_preco(data.id_peca)
        peca_estoque = os_peca_repo.get_peca_estoque(data.id_peca)
        item_com_info.peca_preco = peca_preco
        item_com_info.peca_estoque = peca_estoque
        item_com_info.subtotal = peca_preco * item_com_info.quantidade
        
        return item_com_info
        
    except psycopg2.IntegrityError:
        logger.error("add_peca_to_os erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar peça à OS"
        )
    except ValueError as e:
        logger.error("add_peca_to_os erro de estoque %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def update_quantidade_peca(os_id: int, peca_id: int, data: OsPecaUpdate):
    """Atualiza quantidade de peça na OS com validação de estoque."""
    # Validações básicas
    validate_os_peca_data(os_id, peca_id, data.quantidade)
    
    # Verifica se peça existe na OS
    item_existente = os_peca_repo.get_os_peca(os_id, peca_id)
    if not item_existente:
        logger.warning("peça não encontrada na OS os=%s peca=%s", os_id, peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada na ordem de serviço"
        )
    
    # Valida estoque disponível
    estoque_atual = validate_estoque_disponivel(peca_id, data.quantidade, item_existente.quantidade)
    
    try:
        # Calcula diferença para movimentação
        quantidade_diferenca = data.quantidade - item_existente.quantidade
        
        # Atualiza quantidade na OS
        item_atualizado = os_peca_repo.update_quantidade_peca(os_id, peca_id, data.quantidade)
        
        # Registra movimentação de estoque
        if quantidade_diferenca > 0:
            # Saída de estoque (adicionou mais peças)
            movimentacao_repo.registrar_saida_estoque(
                peca_id=peca_id,
                quantidade=quantidade_diferenca,
                id_os=os_id,
                motivo=f"Ajuste de quantidade na OS #{os_id} (+{quantidade_diferenca})"
            )
        elif quantidade_diferenca < 0:
            # Entrada de estoque (removeu peças)
            quantidade_devolver = abs(quantidade_diferenca)
            movimentacao_repo.registrar_entrada_estoque(
                peca_id=peca_id,
                quantidade=quantidade_devolver,
                motivo=f"Devolução de peça da OS #{os_id} (-{quantidade_devolver})"
            )
        
        logger.info("quantidade atualizada os=%s peca=%s antiga=%s nova=%s estoque_anterior=%s", 
                   os_id, peca_id, item_existente.quantidade, data.quantidade, estoque_atual)
        
        # Retorna item com informações da peça e subtotal
        peca_preco = os_peca_repo.get_peca_preco(peca_id)
        peca_estoque = os_peca_repo.get_peca_estoque(peca_id)
        item_atualizado.peca_preco = peca_preco
        item_atualizado.peca_estoque = peca_estoque
        item_atualizado.subtotal = peca_preco * item_atualizado.quantidade
        
        return item_atualizado
        
    except psycopg2.IntegrityError:
        logger.error("update_quantidade_peca erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar quantidade"
        )
    except ValueError as e:
        logger.error("update_quantidade_peca erro de estoque %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def remove_peca_from_os(os_id: int, peca_id: int):
    """Remove peça da OS e devolve ao estoque."""
    # Validações básicas
    validate_os_peca_data(os_id, peca_id, 1)
    
    # Verifica se peça existe na OS
    item_existente = os_peca_repo.get_os_peca(os_id, peca_id)
    if not item_existente:
        logger.warning("peça não encontrada na OS os=%s peca=%s", os_id, peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada na ordem de serviço"
        )
    
    try:
        quantidade_devolver = item_existente.quantidade
        
        # Remove peça da OS
        os_peca_repo.remove_peca_from_os(os_id, peca_id)
        
        # Devolve peças ao estoque
        movimentacao_repo.registrar_entrada_estoque(
            peca_id=peca_id,
            quantidade=quantidade_devolver,
            motivo=f"Remoção de peça da OS #{os_id} (devolução total)"
        )
        
        logger.info("peça removida da OS os=%s peca=%s quantidade_devolvida=%s", 
                   os_id, peca_id, quantidade_devolver)
        
        return None
        
    except psycopg2.IntegrityError:
        logger.error("remove_peca_from_os erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover peça da OS"
        )

def calcular_valor_total_pecas(os_id: int):
    """Calcula valor total das peças da OS."""
    # Verifica se OS existe
    if not os_peca_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return os_peca_repo.calcular_valor_total_pecas(os_id)

def get_peca_by_os(os_id: int, peca_id: int):
    """Busca peça específica de uma OS."""
    # Validações básicas
    validate_os_peca_data(os_id, peca_id, 1)
    
    item = os_peca_repo.get_os_peca(os_id, peca_id)
    if not item:
        logger.warning("peça não encontrada na OS os=%s peca=%s", os_id, peca_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Peça não encontrada na ordem de serviço"
        )
    
    # Adiciona informações da peça e subtotal
    peca_preco = os_peca_repo.get_peca_preco(peca_id)
    peca_estoque = os_peca_repo.get_peca_estoque(peca_id)
    item.peca_preco = peca_preco
    item.peca_estoque = peca_estoque
    item.subtotal = peca_preco * item.quantidade
    
    return item

def get_movimentacoes_by_os(os_id: int):
    """Lista movimentações de estoque de uma OS."""
    # Verifica se OS existe
    if not os_peca_repo.check_os_exists(os_id):
        logger.info("OS não encontrada os_id=%s", os_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordem de serviço não encontrada")
    
    return movimentacao_repo.get_movimentacoes_by_os(os_id)
