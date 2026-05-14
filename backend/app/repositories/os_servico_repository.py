import logging

from app.database.db import execute_query, execute_command
from app.models.entities import OrdemServicoServico, dict_to_ordem_servico_servico, ordem_servico_servico_to_dict

logger = logging.getLogger(__name__)

def get_os_servico(os_id: int, servico_id: int):
    """Busca serviço da OS por IDs."""
    query = """
    SELECT id_os, id_servico, quantidade
    FROM os_servico 
    WHERE id_os = %s AND id_servico = %s
    """
    result = execute_query(query, (os_id, servico_id), fetch="one")
    item = dict_to_ordem_servico_servico(result)
    logger.debug("get_os_servico os=%s servico=%s found=%s", os_id, servico_id, item is not None)
    return item

def get_servicos_by_os(os_id: int):
    """Lista todos os serviços de uma OS."""
    query = """
    SELECT oss.id_os, oss.id_servico, oss.quantidade,
           s.descricao as servico_descricao, s.preco as servico_preco
    FROM os_servico oss
    INNER JOIN servico s ON oss.id_servico = s.id_servico
    WHERE oss.id_os = %s
    ORDER BY s.descricao ASC
    """
    results = execute_query(query, (os_id,))
    itens = []
    for row in results:
        item = dict_to_ordem_servico_servico(row)
        # Adiciona informações do serviço
        item.servico_descricao = row['servico_descricao']
        item.servico_preco = row['servico_preco']
        # Calcula subtotal
        item.subtotal = item.servico_preco * item.quantidade
        itens.append(item)
    logger.debug("get_servicos_by_os os_id=%s count=%s", os_id, len(itens))
    return itens

def add_servico_to_os(os_servico: OrdemServicoServico):
    """Adiciona serviço à OS."""
    query = """
    INSERT INTO os_servico (id_os, id_servico, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_os, id_servico) 
    DO UPDATE SET quantidade = os_servico.quantidade + EXCLUDED.quantidade
    """
    params = (
        os_servico.id_os, os_servico.id_servico, os_servico.quantidade
    )
    execute_command(query, params)
    logger.info("serviço adicionado à OS os=%s servico=%s quantidade=%s", 
                os_servico.id_os, os_servico.id_servico, os_servico.quantidade)
    return os_servico

def update_quantidade_servico(os_id: int, servico_id: int, nova_quantidade: int):
    """Atualiza quantidade de um serviço na OS."""
    query = """
    UPDATE os_servico 
    SET quantidade = %s
    WHERE id_os = %s AND id_servico = %s
    """
    params = (nova_quantidade, os_id, servico_id)
    execute_command(query, params)
    logger.info("quantidade atualizada os=%s servico=%s nova_quantidade=%s", 
                os_id, servico_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_os_servico(os_id, servico_id)

def remove_servico_from_os(os_id: int, servico_id: int):
    """Remove serviço da OS."""
    query = """
    DELETE FROM os_servico 
    WHERE id_os = %s AND id_servico = %s
    """
    params = (os_id, servico_id)
    execute_command(query, params)
    logger.info("serviço removido da OS os=%s servico=%s", os_id, servico_id)

def check_servico_exists_in_os(os_id: int, servico_id: int):
    """Verifica se serviço existe na OS."""
    query = """
    SELECT COUNT(*) as count
    FROM os_servico 
    WHERE id_os = %s AND id_servico = %s
    """
    result = execute_query(query, (os_id, servico_id), fetch="one")
    return result['count'] > 0 if result else False

def check_servico_exists(servico_id: int):
    """Verifica se serviço existe."""
    query = """
    SELECT COUNT(*) as count
    FROM servico 
    WHERE id_servico = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (servico_id,), fetch="one")
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

def get_servico_preco(servico_id: int):
    """Busca preço de um serviço."""
    query = """
    SELECT preco
    FROM servico 
    WHERE id_servico = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (servico_id,), fetch="one")
    return result['preco'] if result else 0.0

def calcular_valor_total_servicos(os_id: int):
    """Calcula valor total dos serviços da OS."""
    query = """
    SELECT SUM(s.preco * oss.quantidade) as valor_total
    FROM os_servico oss
    INNER JOIN servico s ON oss.id_servico = s.id_servico
    WHERE oss.id_os = %s AND s.deleted_at IS NULL
    """
    result = execute_query(query, (os_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
