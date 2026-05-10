import logging

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import OrdemServicoPeca, dict_to_ordem_servico_peca, ordem_servico_peca_to_dict

logger = logging.getLogger(__name__)

def get_os_peca(os_id: int, peca_id: int):
    """Busca peça da OS por IDs."""
    query = """
    SELECT id_os, id_peca, quantidade
    FROM os_peca 
    WHERE id_os = %s AND id_peca = %s
    """
    result = execute_query(query, (os_id, peca_id), fetch="one")
    item = dict_to_ordem_servico_peca(result)
    logger.debug("get_os_peca os=%s peca=%s found=%s", os_id, peca_id, item is not None)
    return item

def get_pecas_by_os(os_id: int):
    """Lista todas as peças de uma OS."""
    query = """
    SELECT op.id_os, op.id_peca, op.quantidade,
           p.nome as peca_nome, p.preco_unitario as peca_preco, p.estoque_atual as peca_estoque
    FROM os_peca op
    INNER JOIN peca p ON op.id_peca = p.id_peca
    WHERE op.id_os = %s
    ORDER BY p.nome ASC
    """
    results = execute_query(query, (os_id,))
    itens = []
    for row in results:
        item = dict_to_ordem_servico_peca(row)
        # Adiciona informações da peça
        item.peca_nome = row['peca_nome']
        item.peca_preco = row['peca_preco']
        item.peca_estoque = row['peca_estoque']
        # Calcula subtotal
        item.subtotal = item.peca_preco * item.quantidade
        itens.append(item)
    logger.debug("get_pecas_by_os os_id=%s count=%s", os_id, len(itens))
    return itens

def add_peca_to_os(os_peca: OrdemServicoPeca):
    """Adiciona peça à OS."""
    query = """
    INSERT INTO os_peca (id_os, id_peca, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_os, id_peca) 
    DO UPDATE SET quantidade = os_peca.quantidade + EXCLUDED.quantidade
    """
    params = (
        os_peca.id_os, os_peca.id_peca, os_peca.quantidade
    )
    execute_command(query, params)
    logger.info("peça adicionada à OS os=%s peca=%s quantidade=%s", 
                os_peca.id_os, os_peca.id_peca, os_peca.quantidade)
    return os_peca

def update_quantidade_peca(os_id: int, peca_id: int, nova_quantidade: int):
    """Atualiza quantidade de uma peça na OS."""
    query = """
    UPDATE os_peca 
    SET quantidade = %s
    WHERE id_os = %s AND id_peca = %s
    """
    params = (nova_quantidade, os_id, peca_id)
    execute_command(query, params)
    logger.info("quantidade atualizada os=%s peca=%s nova_quantidade=%s", 
                os_id, peca_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_os_peca(os_id, peca_id)

def remove_peca_from_os(os_id: int, peca_id: int):
    """Remove peça da OS."""
    query = """
    DELETE FROM os_peca 
    WHERE id_os = %s AND id_peca = %s
    """
    params = (os_id, peca_id)
    execute_command(query, params)
    logger.info("peça removida da OS os=%s peca=%s", os_id, peca_id)

def check_peca_exists_in_os(os_id: int, peca_id: int):
    """Verifica se peça existe na OS."""
    query = """
    SELECT COUNT(*) as count
    FROM os_peca 
    WHERE id_os = %s AND id_peca = %s
    """
    result = execute_query(query, (os_id, peca_id), fetch="one")
    return result['count'] > 0 if result else False

def check_peca_exists(peca_id: int):
    """Verifica se peça existe."""
    query = """
    SELECT COUNT(*) as count
    FROM peca 
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (peca_id,), fetch="one")
    return result['count'] > 0 if result else False

def check_os_exists(os_id: int):
    """Verifica se OS existe."""
    query = """
    SELECT COUNT(*) as count
    FROM ordem_servico 
    WHERE id_os = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (os_id,), fetch="one")
    return result['count'] > 0 if result else False

def get_peca_preco(peca_id: int):
    """Busca preço de uma peça."""
    query = """
    SELECT preco_unitario
    FROM peca 
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (peca_id,), fetch="one")
    return result['preco_unitario'] if result else 0.0

def get_peca_estoque(peca_id: int):
    """Busca estoque atual de uma peça."""
    query = """
    SELECT estoque_atual
    FROM peca 
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (peca_id,), fetch="one")
    return result['estoque_atual'] if result else 0

def update_peca_estoque(peca_id: int, nova_quantidade: int):
    """Atualiza estoque de uma peça."""
    query = """
    UPDATE peca 
    SET estoque_atual = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_peca = %s AND deleted_at IS NULL
    """
    params = (nova_quantidade, peca_id)
    execute_command(query, params)
    logger.info("estoque atualizado peca=%s nova_quantidade=%s", peca_id, nova_quantidade)

def calcular_valor_total_pecas(os_id: int):
    """Calcula valor total das peças da OS."""
    query = """
    SELECT SUM(p.preco_unitario * op.quantidade) as valor_total
    FROM os_peca op
    INNER JOIN peca p ON op.id_peca = p.id_peca
    WHERE op.id_os = %s AND p.deleted_at IS NULL
    """
    result = execute_query(query, (os_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
