import logging

from app.database.db import execute_query, execute_command
from app.models.entities import OrdemServicoServico, dict_to_ordem_servico_servico, ordem_servico_servico_to_dict

logger = logging.getLogger(__name__)

def get_ordem_servico_servico(ordem_servico_id: int, servico_id: int):
    """Busca serviço da ordem de serviço por IDs."""
    query = """
    SELECT id_ordem_servico, id_servico, quantidade
    FROM ordem_servico_servico 
    WHERE id_ordem_servico = %s AND id_servico = %s
    """
    result = execute_query(query, (ordem_servico_id, servico_id), fetch="one")
    item = dict_to_ordem_servico_servico(result)
    logger.debug("get_ordem_servico_servico ordem=%s servico=%s found=%s", ordem_servico_id, servico_id, item is not None)
    return item

def get_servicos_by_ordem_servico(ordem_servico_id: int):
    """Lista todos os serviços de uma ordem de serviço."""
    query = """
    SELECT oss.id_ordem_servico, oss.id_servico, oss.quantidade,
           s.descricao as servico_descricao, s.preco as servico_preco
    FROM ordem_servico_servico oss
    INNER JOIN servico s ON oss.id_servico = s.id_servico
    WHERE oss.id_ordem_servico = %s
    ORDER BY s.descricao ASC
    """
    results = execute_query(query, (ordem_servico_id,))
    itens = []
    for row in results:
        item = dict_to_ordem_servico_servico(row)
        # Adiciona informações do serviço
        item.servico_descricao = row['servico_descricao']
        item.servico_preco = row['servico_preco']
        itens.append(item)
    logger.debug("get_servicos_by_ordem_servico ordem_servico_id=%s count=%s", ordem_servico_id, len(itens))
    return itens

def add_servico_to_ordem_servico(ordem_servico_servico: OrdemServicoServico):
    """Adiciona serviço à ordem de serviço."""
    query = """
    INSERT INTO ordem_servico_servico (id_ordem_servico, id_servico, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_ordem_servico, id_servico) 
    DO UPDATE SET quantidade = ordem_servico_servico.quantidade + EXCLUDED.quantidade
    """
    params = (
        ordem_servico_servico.id_ordem_servico, ordem_servico_servico.id_servico, 
        ordem_servico_servico.quantidade
    )
    execute_command(query, params)
    logger.info("serviço adicionado à ordem de serviço ordem=%s servico=%s quantidade=%s", 
                ordem_servico_servico.id_ordem_servico, ordem_servico_servico.id_servico, ordem_servico_servico.quantidade)
    return ordem_servico_servico

def update_quantidade_servico(ordem_servico_id: int, servico_id: int, nova_quantidade: int):
    """Atualiza quantidade de um serviço na ordem de serviço."""
    query = """
    UPDATE ordem_servico_servico 
    SET quantidade = %s
    WHERE id_ordem_servico = %s AND id_servico = %s
    """
    params = (nova_quantidade, ordem_servico_id, servico_id)
    execute_command(query, params)
    logger.info("quantidade atualizada ordem=%s servico=%s nova_quantidade=%s", 
                ordem_servico_id, servico_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_ordem_servico_servico(ordem_servico_id, servico_id)

def remove_servico_from_ordem_servico(ordem_servico_id: int, servico_id: int):
    """Remove serviço da ordem de serviço."""
    query = """
    DELETE FROM ordem_servico_servico 
    WHERE id_ordem_servico = %s AND id_servico = %s
    """
    params = (ordem_servico_id, servico_id)
    execute_command(query, params)
    logger.info("serviço removido da ordem de serviço ordem=%s servico=%s", ordem_servico_id, servico_id)

def check_servico_exists_in_ordem_servico(ordem_servico_id: int, servico_id: int):
    """Verifica se serviço existe na ordem de serviço."""
    query = """
    SELECT COUNT(*) as count
    FROM ordem_servico_servico 
    WHERE id_ordem_servico = %s AND id_servico = %s
    """
    result = execute_query(query, (ordem_servico_id, servico_id), fetch="one")
    return result['count'] > 0 if result else False

def calcular_valor_total_servicos(ordem_servico_id: int):
    """Calcula valor total dos serviços da ordem de serviço."""
    query = """
    SELECT SUM(s.preco * oss.quantidade) as valor_total
    FROM ordem_servico_servico oss
    INNER JOIN servico s ON oss.id_servico = s.id_servico
    WHERE oss.id_ordem_servico = %s AND s.deleted_at IS NULL
    """
    result = execute_query(query, (ordem_servico_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
