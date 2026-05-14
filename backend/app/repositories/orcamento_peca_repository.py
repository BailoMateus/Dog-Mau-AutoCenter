import logging

from app.database.db import execute_query, execute_command
from app.models.entities import OrcamentoPeca, dict_to_orcamento_peca, orcamento_peca_to_dict

logger = logging.getLogger(__name__)

def get_orcamento_peca(orcamento_id: int, peca_id: int):
    """Busca peça do orçamento por IDs."""
    query = """
    SELECT id_orcamento, id_peca, quantidade
    FROM orcamento_peca 
    WHERE id_orcamento = %s AND id_peca = %s
    """
    result = execute_query(query, (orcamento_id, peca_id), fetch="one")
    item = dict_to_orcamento_peca(result)
    logger.debug("get_orcamento_peca orcamento=%s peca=%s found=%s", orcamento_id, peca_id, item is not None)
    return item

def get_pecas_by_orcamento(orcamento_id: int):
    """Lista todas as peças de um orçamento."""
    query = """
    SELECT op.id_orcamento, op.id_peca, op.quantidade,
           p.nome as peca_nome, p.preco_unitario as peca_preco
    FROM orcamento_peca op
    INNER JOIN peca p ON op.id_peca = p.id_peca
    WHERE op.id_orcamento = %s
    ORDER BY p.nome ASC
    """
    results = execute_query(query, (orcamento_id,))
    itens = []
    for row in results:
        item = dict_to_orcamento_peca(row)
        # Adiciona informações da peça
        item.peca_nome = row['peca_nome']
        item.peca_preco = row['peca_preco']
        itens.append(item)
    logger.debug("get_pecas_by_orcamento orcamento_id=%s count=%s", orcamento_id, len(itens))
    return itens

def add_peca_to_orcamento(orcamento_peca: OrcamentoPeca):
    """Adiciona peça ao orçamento."""
    query = """
    INSERT INTO orcamento_peca (id_orcamento, id_peca, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_orcamento, id_peca) 
    DO UPDATE SET quantidade = orcamento_peca.quantidade + EXCLUDED.quantidade
    """
    params = (
        orcamento_peca.id_orcamento, orcamento_peca.id_peca, orcamento_peca.quantidade
    )
    execute_command(query, params)
    logger.info("peça adicionada ao orçamento orcamento=%s peca=%s quantidade=%s", 
                orcamento_peca.id_orcamento, orcamento_peca.id_peca, orcamento_peca.quantidade)
    return orcamento_peca

def update_quantidade_peca(orcamento_id: int, peca_id: int, nova_quantidade: int):
    """Atualiza quantidade de uma peça no orçamento."""
    query = """
    UPDATE orcamento_peca 
    SET quantidade = %s
    WHERE id_orcamento = %s AND id_peca = %s
    """
    params = (nova_quantidade, orcamento_id, peca_id)
    execute_command(query, params)
    logger.info("quantidade atualizada orcamento=%s peca=%s nova_quantidade=%s", 
                orcamento_id, peca_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_orcamento_peca(orcamento_id, peca_id)

def remove_peca_from_orcamento(orcamento_id: int, peca_id: int):
    """Remove peça do orçamento."""
    query = """
    DELETE FROM orcamento_peca 
    WHERE id_orcamento = %s AND id_peca = %s
    """
    params = (orcamento_id, peca_id)
    execute_command(query, params)
    logger.info("peça removida do orçamento orcamento=%s peca=%s", orcamento_id, peca_id)

def check_peca_exists_in_orcamento(orcamento_id: int, peca_id: int):
    """Verifica se peça existe no orçamento."""
    query = """
    SELECT COUNT(*) as count
    FROM orcamento_peca 
    WHERE id_orcamento = %s AND id_peca = %s
    """
    result = execute_query(query, (orcamento_id, peca_id), fetch="one")
    return result['count'] > 0 if result else False

def get_peca_preco(peca_id: int):
    """Busca preço unitário de uma peça."""
    query = """
    SELECT preco_unitario
    FROM peca 
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (peca_id,), fetch="one")
    return result['preco_unitario'] if result else 0.0

def calcular_valor_total_pecas(orcamento_id: int):
    """Calcula valor total das peças do orçamento."""
    query = """
    SELECT SUM(p.preco_unitario * op.quantidade) as valor_total
    FROM orcamento_peca op
    INNER JOIN peca p ON op.id_peca = p.id_peca
    WHERE op.id_orcamento = %s AND p.deleted_at IS NULL
    """
    result = execute_query(query, (orcamento_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
