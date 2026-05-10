import logging

from app.database.db import execute_query, execute_command
from app.models.entities import OrcamentoServico, dict_to_orcamento_servico, orcamento_servico_to_dict

logger = logging.getLogger(__name__)

def get_orcamento_servico(orcamento_id: int, servico_id: int):
    """Busca serviço do orçamento por IDs."""
    query = """
    SELECT id_orcamento, id_servico, quantidade
    FROM orcamento_servico 
    WHERE id_orcamento = %s AND id_servico = %s
    """
    result = execute_query(query, (orcamento_id, servico_id), fetch="one")
    item = dict_to_orcamento_servico(result)
    logger.debug("get_orcamento_servico orcamento=%s servico=%s found=%s", orcamento_id, servico_id, item is not None)
    return item

def get_servicos_by_orcamento(orcamento_id: int):
    """Lista todos os serviços de um orçamento."""
    query = """
    SELECT os.id_orcamento, os.id_servico, os.quantidade,
           s.descricao as servico_descricao, s.preco as servico_preco
    FROM orcamento_servico os
    INNER JOIN servico s ON os.id_servico = s.id_servico
    WHERE os.id_orcamento = %s
    ORDER BY s.descricao ASC
    """
    results = execute_query(query, (orcamento_id,))
    itens = []
    for row in results:
        item = dict_to_orcamento_servico(row)
        # Adiciona informações do serviço
        item.servico_descricao = row['servico_descricao']
        item.servico_preco = row['servico_preco']
        itens.append(item)
    logger.debug("get_servicos_by_orcamento orcamento_id=%s count=%s", orcamento_id, len(itens))
    return itens

def add_servico_to_orcamento(orcamento_servico: OrcamentoServico):
    """Adiciona serviço ao orçamento."""
    query = """
    INSERT INTO orcamento_servico (id_orcamento, id_servico, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_orcamento, id_servico) 
    DO UPDATE SET quantidade = orcamento_servico.quantidade + EXCLUDED.quantidade
    """
    params = (
        orcamento_servico.id_orcamento, orcamento_servico.id_servico, orcamento_servico.quantidade
    )
    execute_command(query, params)
    logger.info("serviço adicionado ao orçamento orcamento=%s servico=%s quantidade=%s", 
                orcamento_servico.id_orcamento, orcamento_servico.id_servico, orcamento_servico.quantidade)
    return orcamento_servico

def update_quantidade_servico(orcamento_id: int, servico_id: int, nova_quantidade: int):
    """Atualiza quantidade de um serviço no orçamento."""
    query = """
    UPDATE orcamento_servico 
    SET quantidade = %s
    WHERE id_orcamento = %s AND id_servico = %s
    """
    params = (nova_quantidade, orcamento_id, servico_id)
    execute_command(query, params)
    logger.info("quantidade atualizada orcamento=%s servico=%s nova_quantidade=%s", 
                orcamento_id, servico_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_orcamento_servico(orcamento_id, servico_id)

def remove_servico_from_orcamento(orcamento_id: int, servico_id: int):
    """Remove serviço do orçamento."""
    query = """
    DELETE FROM orcamento_servico 
    WHERE id_orcamento = %s AND id_servico = %s
    """
    params = (orcamento_id, servico_id)
    execute_command(query, params)
    logger.info("serviço removido do orçamento orcamento=%s servico=%s", orcamento_id, servico_id)

def check_servico_exists_in_orcamento(orcamento_id: int, servico_id: int):
    """Verifica se serviço existe no orçamento."""
    query = """
    SELECT COUNT(*) as count
    FROM orcamento_servico 
    WHERE id_orcamento = %s AND id_servico = %s
    """
    result = execute_query(query, (orcamento_id, servico_id), fetch="one")
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

def calcular_valor_total_servicos(orcamento_id: int):
    """Calcula valor total dos serviços do orçamento."""
    query = """
    SELECT SUM(s.preco * os.quantidade) as valor_total
    FROM orcamento_servico os
    INNER JOIN servico s ON os.id_servico = s.id_servico
    WHERE os.id_orcamento = %s AND s.deleted_at IS NULL
    """
    result = execute_query(query, (orcamento_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
