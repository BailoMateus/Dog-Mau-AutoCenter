import logging

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import Mecanico, dict_to_mecanico, mecanico_to_dict

logger = logging.getLogger(__name__)

def get_mecanico_by_id(mecanico_id: int):
    """Busca mecânico por ID."""
    query = """
    SELECT id_mecanico, nome, especialidade, telefone, email, ativo,
           created_at, updated_at, deleted_at
    FROM mecanico 
    WHERE id_mecanico = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (mecanico_id,), fetch="one")
    mecanico = dict_to_mecanico(result)
    logger.debug("get_mecanico_by_id id=%s found=%s", mecanico_id, mecanico is not None)
    return mecanico

def get_all_mecanicos():
    """Lista todos os mecânicos."""
    query = """
    SELECT id_mecanico, nome, especialidade, telefone, email, ativo,
           created_at, updated_at, deleted_at
    FROM mecanico 
    WHERE deleted_at IS NULL
    ORDER BY nome ASC
    """
    results = execute_query(query)
    mecanicos = [dict_to_mecanico(row) for row in results]
    logger.debug("get_all_mecanicos count=%s", len(mecanicos))
    return mecanicos

def get_mecanicos_ativos():
    """Lista apenas mecânicos ativos."""
    query = """
    SELECT id_mecanico, nome, especialidade, telefone, email, ativo,
           created_at, updated_at, deleted_at
    FROM mecanico 
    WHERE ativo = true AND deleted_at IS NULL
    ORDER BY nome ASC
    """
    results = execute_query(query)
    mecanicos = [dict_to_mecanico(row) for row in results]
    logger.debug("get_mecanicos_ativos count=%s", len(mecanicos))
    return mecanicos

def create_mecanico(mecanico: Mecanico):
    """Cria um novo mecânico."""
    query = """
    INSERT INTO mecanico (nome, especialidade, telefone, email, ativo)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id_mecanico
    """
    params = (
        mecanico.nome, mecanico.especialidade, 
        mecanico.telefone, mecanico.email, mecanico.ativo
    )
    mecanico_id = execute_insert(query, params)
    mecanico.id_mecanico = mecanico_id
    logger.info("mecânico criado id=%s nome=%s", mecanico.id_mecanico, mecanico.nome)
    return mecanico

def update_mecanico(mecanico: Mecanico):
    """Atualiza um mecânico."""
    query = """
    UPDATE mecanico 
    SET nome = %s, especialidade = %s, telefone = %s, email = %s, ativo = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id_mecanico = %s AND deleted_at IS NULL
    """
    params = (
        mecanico.nome, mecanico.especialidade, mecanico.telefone, 
        mecanico.email, mecanico.ativo, mecanico.id_mecanico
    )
    execute_command(query, params)
    logger.info("mecânico atualizado id=%s", mecanico.id_mecanico)
    return mecanico

def soft_delete_mecanico(mecanico: Mecanico):
    """Soft delete de mecânico."""
    query = """
    UPDATE mecanico 
    SET deleted_at = CURRENT_TIMESTAMP, ativo = false, updated_at = CURRENT_TIMESTAMP
    WHERE id_mecanico = %s
    """
    execute_command(query, (mecanico.id_mecanico,))
    logger.info("mecânico soft-delete id=%s", mecanico.id_mecanico)
    return mecanico

def check_email_exists(email: str, exclude_id: int = None):
    """Verifica se email já existe (excluindo ID específico)."""
    if exclude_id:
        query = """
        SELECT COUNT(*) as count
        FROM mecanico 
        WHERE email = %s AND id_mecanico != %s AND deleted_at IS NULL
        """
        result = execute_query(query, (email, exclude_id), fetch="one")
    else:
        query = """
        SELECT COUNT(*) as count
        FROM mecanico 
        WHERE email = %s AND deleted_at IS NULL
        """
        result = execute_query(query, (email,), fetch="one")
    
    return result['count'] > 0 if result else False
