import logging
from datetime import datetime, timezone

from app.database.db import execute_query, execute_command, execute_insert
from app.models.entities import User, dict_to_user, user_to_dict
from app.core.roles import ADMIN, MECANICO, CLIENTE

logger = logging.getLogger(__name__)

def get_user_by_email(email: str):
    """Busca usuário por email."""
    query = """
    SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, 
           data_nascimento, created_at, updated_at, deleted_at
    FROM usuario 
    WHERE email = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (email,), fetch="one")
    user = dict_to_user(result)
    logger.debug("get_user_by_email email=%s found=%s", email, user is not None)
    return user

def get_user_by_id(user_id: int):
    """Busca usuário por ID."""
    query = """
    SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, 
           data_nascimento, created_at, updated_at, deleted_at
    FROM usuario 
    WHERE id_usuario = %s AND deleted_at IS NULL
    """
    result = execute_query(query, (user_id,), fetch="one")
    user = dict_to_user(result)
    logger.debug("get_user_by_id id=%s found=%s", user_id, user is not None)
    return user

def create_user(user: User):
    """Cria um novo usuário."""
    query = """
    INSERT INTO usuario (nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, data_nascimento)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id_usuario
    """
    params = (
        user.nome, user.email, user.senha_hash, user.role, 
        user.ativo, user.telefone, user.cpf_cnpj, user.data_nascimento
    )
    user_id = execute_insert(query, params)
    user.id_usuario = user_id
    logger.info("usuário criado id=%s email=%s", user.id_usuario, user.email)
    return user

def get_all_users():
    """Lista todos os usuários."""
    query = """
    SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, 
           data_nascimento, created_at, updated_at, deleted_at
    FROM usuario 
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query)
    users = [dict_to_user(row) for row in results]
    logger.debug("get_all_users count=%s", len(users))
    return users

def update_user(user: User):
    """Atualiza um usuário."""
    query = """
    UPDATE usuario 
    SET nome = %s, email = %s, role = %s, ativo = %s, telefone = %s, 
        cpf_cnpj = %s, data_nascimento = %s, senha_hash = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_usuario = %s AND deleted_at IS NULL
    """
    params = (
        user.nome, user.email, user.role, user.ativo, user.telefone,
        user.cpf_cnpj, user.data_nascimento, user.senha_hash, user.id_usuario
    )
    execute_command(query, params)
    logger.info("usuário atualizado id=%s", user.id_usuario)
    return user

def soft_delete_user(user: User):
    """Soft delete de usuário."""
    query = """
    UPDATE usuario 
    SET deleted_at = %s, ativo = FALSE, updated_at = CURRENT_TIMESTAMP
    WHERE id_usuario = %s
    """
    params = (datetime.now(timezone.utc), user.id_usuario)
    execute_command(query, params)
    user.deleted_at = datetime.now(timezone.utc)
    user.ativo = False
    logger.info("usuário soft-delete id=%s", user.id_usuario)
    return user

def get_user_by_role(role: str):
    """Busca usuário por role."""
    query = """
    SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, 
           data_nascimento, created_at, updated_at, deleted_at
    FROM usuario 
    WHERE role = %s AND deleted_at IS NULL
    LIMIT 1
    """
    result = execute_query(query, (role,), fetch="one")
    user = dict_to_user(result)
    logger.debug("get_user_by_role role=%s found=%s", role, user is not None)
    return user

def get_users_by_role(role: str):
    """Lista usuários por role."""
    query = """
    SELECT id_usuario, nome, email, senha_hash, role, ativo, telefone, cpf_cnpj, 
           data_nascimento, created_at, updated_at, deleted_at
    FROM usuario 
    WHERE role = %s AND deleted_at IS NULL
    ORDER BY created_at DESC
    """
    results = execute_query(query, (role,))
    users = [dict_to_user(row) for row in results]
    logger.debug("get_users_by_role role=%s count=%s", role, len(users))
    return users

def get_clientes():
    """Lista todos os clientes."""
    return get_users_by_role(CLIENTE)

def get_mecanicos():
    """Lista todos os mecânicos."""
    return get_users_by_role(MECANICO)

def get_admins():
    """Lista todos os administradores."""
    return get_users_by_role(ADMIN)

def update_user_photo(user_id: int, photo_path: str):
    """Atualiza a foto de perfil do usuário."""
    query = """
    UPDATE usuario
    SET foto_perfil = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_usuario = %s AND deleted_at IS NULL
    """
    params = (photo_path, user_id)
    execute_command(query, params)
    logger.info("Foto de perfil atualizada para o usuário id=%s", user_id)

def update_user_password(user_id: int, hashed_password: str):
    """Atualiza a senha do usuário."""
    query = """
    UPDATE usuario
    SET senha_hash = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id_usuario = %s AND deleted_at IS NULL
    """
    params = (hashed_password, user_id)
    execute_command(query, params)
    logger.info("Senha atualizada para o usuário id=%s", user_id)
