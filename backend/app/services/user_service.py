import logging

from fastapi import HTTPException, status, UploadFile
import psycopg2
import os
from uuid import uuid4

from app.core.roles import ADMIN, CLIENTE, MECANICO
from app.core.security import hash_password
from app.models.entities import User
from app.repositories import user_repository as repo
from app.schemas.user_schema import UserCreate, UserUpdate

logger = logging.getLogger(__name__)

def _actor_user_id(actor: dict) -> str:
    return str(actor.get("user_id", ""))

def list_users():
    return repo.get_all_users()

def create_user(data: UserCreate):
    user = User(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.password),
        role=data.role,
        ativo=data.ativo,
        telefone=data.telefone,
        cpf_cnpj=data.cpf_cnpj,
        data_nascimento=data.data_nascimento,
    )
    try:
        return repo.create_user(user)
    except psycopg2.IntegrityError:
        logger.warning("create_user email duplicado email=%s", data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

def get_user_or_404(user_id: int) -> User:
    user = repo.get_user_by_id(user_id)
    if not user:
        logger.info("usuário não encontrado id=%s", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

def get_user_by_role(role: str):
    return repo.get_user_by_role(role)

def assert_can_read(actor: dict, target_id: int):
    if actor["role"] == ADMIN:
        return
    if _actor_user_id(actor) == str(target_id):
        return
    logger.warning(
        "acesso negado leitura usuário actor=%s target=%s",
        actor.get("user_id"),
        target_id,
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

def assert_can_modify(actor: dict, target_id: int, *, admin_only: bool = False):
    if admin_only:
        if actor["role"] != ADMIN:
            logger.warning(
                "acesso negado (só admin) actor=%s target=%s",
                actor.get("user_id"),
                target_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado",
            )
        return
    if actor["role"] == ADMIN:
        return
    if _actor_user_id(actor) == str(target_id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

def assert_can_manage_cliente_data(actor: dict, target_id: int):
    # Verifica se o usuário pode gerenciar dados de cliente (endereços, veículos)
    if actor["role"] == ADMIN:
        return
    if actor["role"] == CLIENTE and _actor_user_id(actor) == str(target_id):
        return
    logger.warning(
        "acesso negado gerenciar dados cliente actor=%s target=%s",
        actor.get("user_id"),
        target_id,
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso não autorizado")

def update_user(
    user_id: int,
    data: UserUpdate,
    *,
    actor: dict,
):
    user = get_user_or_404(user_id)
    assert_can_modify(actor, user_id, admin_only=False)

    is_admin = actor["role"] == ADMIN
    if data.nome is not None:
        user.nome = data.nome
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.senha_hash = hash_password(data.password)
    if data.telefone is not None:
        user.telefone = data.telefone
    if data.cpf_cnpj is not None:
        user.cpf_cnpj = data.cpf_cnpj
    if data.data_nascimento is not None:
        user.data_nascimento = data.data_nascimento
    if data.ativo is not None and is_admin:
        user.ativo = data.ativo
    elif data.ativo is not None and not is_admin:
        logger.warning("tentativa de alterar ativo sem ser admin user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente administrador pode alterar o campo ativo",
        )
    if data.role is not None:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Somente administrador pode alterar o papel",
            )
        user.role = data.role

    try:
        return repo.update_user(user)
    except psycopg2.IntegrityError:
        logger.warning("update_user conflito de e-mail user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

def delete_user(user_id: int, *, actor: dict):
    user = get_user_or_404(user_id)
    assert_can_modify(actor, user_id, admin_only=True)

    try:
        return repo.delete_user(user)
    except psycopg2.IntegrityError:
        logger.error("delete_user erro de integridade user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir usuário",
        )

def save_user_photo(user_id: int, file: UploadFile) -> str:
    """Salva a foto do usuário no sistema de arquivos."""
    upload_dir = os.path.join("uploads", "users")
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = file.filename.split(".")[-1]
    file_name = f"{user_id}_{uuid4().hex}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path
