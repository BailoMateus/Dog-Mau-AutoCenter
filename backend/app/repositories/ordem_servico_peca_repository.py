import logging

from app.database.db import execute_query, execute_command
from app.models.entities import OrdemServicoPeca, dict_to_ordem_servico_peca, ordem_servico_peca_to_dict

logger = logging.getLogger(__name__)

def get_ordem_servico_peca(ordem_servico_id: int, peca_id: int):
    """Busca peça da ordem de serviço por IDs."""
    query = """
    SELECT id_ordem_servico, id_peca, quantidade
    FROM ordem_servico_peca 
    WHERE id_ordem_servico = %s AND id_peca = %s
    """
    result = execute_query(query, (ordem_servico_id, peca_id), fetch="one")
    item = dict_to_ordem_servico_peca(result)
    logger.debug("get_ordem_servico_peca ordem=%s peca=%s found=%s", ordem_servico_id, peca_id, item is not None)
    return item

def get_pecas_by_ordem_servico(ordem_servico_id: int):
    """Lista todas as peças de uma ordem de serviço."""
    query = """
    SELECT osp.id_ordem_servico, osp.id_peca, osp.quantidade,
           p.nome as peca_nome, p.preco_unitario as peca_preco
    FROM ordem_servico_peca osp
    INNER JOIN peca p ON osp.id_peca = p.id_peca
    WHERE osp.id_ordem_servico = %s
    ORDER BY p.nome ASC
    """
    results = execute_query(query, (ordem_servico_id,))
    itens = []
    for row in results:
        item = dict_to_ordem_servico_peca(row)
        # Adiciona informações da peça
        item.peca_nome = row['peca_nome']
        item.peca_preco = row['peca_preco']
        itens.append(item)
    logger.debug("get_pecas_by_ordem_servico ordem_servico_id=%s count=%s", ordem_servico_id, len(itens))
    return itens

def add_peca_to_ordem_servico(ordem_servico_peca: OrdemServicoPeca):
    """Adiciona peça à ordem de serviço."""
    query = """
    INSERT INTO ordem_servico_peca (id_ordem_servico, id_peca, quantidade)
    VALUES (%s, %s, %s)
    ON CONFLICT (id_ordem_servico, id_peca) 
    DO UPDATE SET quantidade = ordem_servico_peca.quantidade + EXCLUDED.quantidade
    """
    params = (
        ordem_servico_peca.id_ordem_servico, ordem_servico_peca.id_peca, ordem_servico_peca.quantidade
    )
    execute_command(query, params)
    logger.info("peça adicionada à ordem de serviço ordem=%s peca=%s quantidade=%s", 
                ordem_servico_peca.id_ordem_servico, ordem_servico_peca.id_peca, ordem_servico_peca.quantidade)
    return ordem_servico_peca

def update_quantidade_peca(ordem_servico_id: int, peca_id: int, nova_quantidade: int):
    """Atualiza quantidade de uma peça na ordem de serviço."""
    query = """
    UPDATE ordem_servico_peca 
    SET quantidade = %s
    WHERE id_ordem_servico = %s AND id_peca = %s
    """
    params = (nova_quantidade, ordem_servico_id, peca_id)
    execute_command(query, params)
    logger.info("quantidade atualizada ordem=%s peca=%s nova_quantidade=%s", 
                ordem_servico_id, peca_id, nova_quantidade)
    
    # Retorna o item atualizado
    return get_ordem_servico_peca(ordem_servico_id, peca_id)

def remove_peca_from_ordem_servico(ordem_servico_id: int, peca_id: int):
    """Remove peça da ordem de serviço."""
    query = """
    DELETE FROM ordem_servico_peca 
    WHERE id_ordem_servico = %s AND id_peca = %s
    """
    params = (ordem_servico_id, peca_id)
    execute_command(query, params)
    logger.info("peça removida da ordem de serviço ordem=%s peca=%s", ordem_servico_id, peca_id)

def check_peca_exists_in_ordem_servico(ordem_servico_id: int, peca_id: int):
    """Verifica se peça existe na ordem de serviço."""
    query = """
    SELECT COUNT(*) as count
    FROM ordem_servico_peca 
    WHERE id_ordem_servico = %s AND id_peca = %s
    """
    result = execute_query(query, (ordem_servico_id, peca_id), fetch="one")
    return result['count'] > 0 if result else False

def calcular_valor_total_pecas(ordem_servico_id: int):
    """Calcula valor total das peças da ordem de serviço."""
    query = """
    SELECT SUM(p.preco_unitario * osp.quantidade) as valor_total
    FROM ordem_servico_peca osp
    INNER JOIN peca p ON osp.id_peca = p.id_peca
    WHERE osp.id_ordem_servico = %s AND p.deleted_at IS NULL
    """
    result = execute_query(query, (ordem_servico_id,), fetch="one")
    return result['valor_total'] if result and result['valor_total'] else 0.0
