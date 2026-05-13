import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Orcamento
from app.repositories import orcamento_repository as repo
from app.repositories import orcamento_peca_repository as peca_repo
from app.repositories import orcamento_servico_repository as servico_repo
from app.schemas.orcamento_schema import OrcamentoCreate, OrcamentoUpdate, OrcamentoUpdateStatus

logger = logging.getLogger(__name__)

def list_orcamentos():
    """Lista todos os orçamentos."""
    return repo.get_all_orcamentos()

def get_orcamento_or_404(orcamento_id: int) -> Orcamento:
    """Busca orçamento por ID ou retorna 404."""
    orcamento = repo.get_orcamento_by_id(orcamento_id)
    if not orcamento:
        logger.info("orçamento não encontrado id=%s", orcamento_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    return orcamento

def validate_orcamento_data(cliente_id: int = None, veiculo_id: int = None, valor_total: float = None):
    """Valida dados do orçamento."""
    # Validação de cliente existente
    if cliente_id and not repo.check_cliente_exists(cliente_id):
        logger.warning("cliente não encontrado cliente_id=%s", cliente_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente não encontrado"
        )
    
    # Validação de veículo existente
    if veiculo_id and not repo.check_veiculo_exists(veiculo_id):
        logger.warning("veículo não encontrado veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não encontrado"
        )
    
    # Validação de veículo pertencente ao cliente
    if cliente_id and veiculo_id and not repo.check_veiculo_pertence_cliente(veiculo_id, cliente_id):
        logger.warning("veículo não pertence ao cliente veiculo=%s cliente=%s", veiculo_id, cliente_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não pertence ao cliente informado"
        )
    
    # Validação de valor total
    if valor_total is not None and valor_total < 0:
        logger.warning("valor total inválido valor_total=%s", valor_total)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor total deve ser maior ou igual a zero"
        )

def create_orcamento(data: OrcamentoCreate):
    """Cria um novo orçamento com validações."""
    # Validações
    validate_orcamento_data(
        cliente_id=data.id_cliente,
        veiculo_id=data.id_veiculo,
        valor_total=float(data.valor_total)
    )
    
    # Cria entidade Orcamento
    orcamento = Orcamento(
        id_cliente=data.id_cliente,
        id_veiculo=data.id_veiculo,
        status=data.status or "pendente",
        valor_total=float(data.valor_total)
    )
    
    try:
        return repo.create_orcamento(orcamento)
    except psycopg2.IntegrityError:
        logger.error("create_orcamento erro de integridade")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar orçamento"
        )

def update_orcamento(orcamento_id: int, data: OrcamentoUpdate):
    """Atualiza um orçamento com validações."""
    orcamento = get_orcamento_or_404(orcamento_id)
    
    # Validações
    validate_orcamento_data(
        cliente_id=data.id_cliente,
        veiculo_id=data.id_veiculo,
        valor_total=float(data.valor_total) if data.valor_total is not None else None
    )
    
    # Atualiza campos
    if data.id_cliente is not None:
        orcamento.id_cliente = data.id_cliente
    if data.id_veiculo is not None:
        orcamento.id_veiculo = data.id_veiculo
    if data.status is not None:
        orcamento.status = data.status
    if data.valor_total is not None:
        orcamento.valor_total = float(data.valor_total)
    
    try:
        return repo.update_orcamento(orcamento)
    except psycopg2.IntegrityError:
        logger.error("update_orcamento erro de integridade id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar orçamento"
        )

def update_status_orcamento(orcamento_id: int, data: OrcamentoUpdateStatus):
    """Atualiza apenas o status do orçamento."""
    orcamento = get_orcamento_or_404(orcamento_id)
    
    # Validação de status
    status_validos = ["pendente", "aprovado", "rejeitado", "concluido"]
    if data.status not in status_validos:
        logger.warning("status inválido status=%s", data.status)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        )
    
    try:
        repo.update_status_orcamento(orcamento_id, data.status)
        # Retorna orçamento atualizado
        return get_orcamento_or_404(orcamento_id)
    except psycopg2.IntegrityError:
        logger.error("update_status_orcamento erro de integridade id=%s", orcamento_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status do orçamento"
        )

def delete_orcamento(orcamento_id: int):
    """Remove (soft delete) um orçamento."""
    orcamento = get_orcamento_or_404(orcamento_id)
    return repo.soft_delete_orcamento(orcamento)

def get_orcamentos_by_cliente(cliente_id: int):
    """Lista orçamentos de um cliente específico."""
    if not repo.check_cliente_exists(cliente_id):
        logger.warning("cliente não encontrado cliente_id=%s", cliente_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return repo.get_orcamentos_by_cliente(cliente_id)

def get_orcamentos_by_veiculo(veiculo_id: int):
    """Lista orçamentos de um veículo específico."""
    if not repo.check_veiculo_exists(veiculo_id):
        logger.warning("veículo não encontrado veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    
    return repo.get_orcamentos_by_veiculo(veiculo_id)

def calcular_valor_total_orcamento(orcamento_id: int):
    """Calcula valor total do orçamento baseado em seus itens (serviços/peças)."""
    valor_pecas = peca_repo.calcular_valor_total_pecas(orcamento_id)
    valor_servicos = servico_repo.calcular_valor_total_servicos(orcamento_id)
    valor_total = valor_pecas + valor_servicos
    logger.info("valor total calculado orcamento=%s valor=%s (pecas=%s, servicos=%s)", 
                orcamento_id, valor_total, valor_pecas, valor_servicos)
    return valor_total

def recalcular_valor_total_orcamento(orcamento_id: int):
    """Recalcula e atualiza o valor total do orçamento."""
    novo_valor_total = calcular_valor_total_orcamento(orcamento_id)
    repo.update_valor_total_orcamento(orcamento_id, novo_valor_total)
    logger.info("valor total recalculado e atualizado orcamento=%s novo_valor=%s", 
                orcamento_id, novo_valor_total)
    
    # Retorna orçamento atualizado
    return get_orcamento_or_404(orcamento_id)
