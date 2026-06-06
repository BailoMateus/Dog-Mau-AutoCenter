import logging
import os
from typing import Annotated

from app.schemas.password_schema import PasswordChangeRequest
from fastapi import HTTPException, status, UploadFile
import psycopg2

from app.core.file_storage import save_image_upload
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
        senha_hash=hash_password(data.password.strip()),
        role=data.role,
        ativo=data.ativo,
        telefone=data.telefone,
        cpf_cnpj=data.cpf_cnpj,
        data_nascimento=data.data_nascimento,
        foto_perfil=data.foto_perfil
    )
    try:
        return repo.create_user(user)
    except psycopg2.IntegrityError:
        logger.warning("create_user email duplicado email=%s", data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )
    except Exception as e:
        logger.error("create_user erro inesperado email=%s: %s", data.email, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar conta. Tente novamente.",
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
        user.senha_hash = hash_password(data.password.strip())
    if data.telefone is not None:
        user.telefone = data.telefone
    
    # Proteger CPF/CNPJ após criação
    if data.cpf_cnpj is not None:
        if user.cpf_cnpj is not None and user.cpf_cnpj != data.cpf_cnpj:
            logger.warning(
                "tentativa de alterar cpf_cnpj protegido user_id=%s actor=%s",
                user_id,
                actor.get("user_id")
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CPF/CNPJ não pode ser alterado após o cadastro"
            )
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


def change_user_password(user_id: int, data: PasswordChangeRequest, *, actor: dict):
    """Altera senha do usuário após verificação de senha atual."""
    user = get_user_or_404(user_id)
    assert_can_update(actor, user_id)
    
    from app.core.security import verify_password, hash_password
    
    if not verify_password(data.old_password, user.senha_hash):
        logger.warning("change_password senha incorreta user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ser diferente da atual"
        )
    
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Novas senhas não coincidem"
        )
    
    user.senha_hash = hash_password(data.new_password.strip())
    
    try:
        updated = repo.update_user(user)
        logger.info("change_password sucesso user_id=%s", user_id)
        return updated
    except Exception as e:
        logger.error("change_password erro user_id=%s: %s", user_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao alterar senha"
        )
    

def delete_user(user_id: int, *, actor: dict):
    user = get_user_or_404(user_id)
    assert_can_modify(actor, user_id, admin_only=True)

    try:
        return repo.soft_delete_user(user)
    except psycopg2.IntegrityError:
        logger.error("delete_user erro de integridade user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir usuário",
        )

def assert_can_update(actor: dict, target_id: int):
    assert_can_modify(actor, target_id, admin_only=False)


def upload_user_photo(user_id: int, file: UploadFile, *, actor: dict):
    """
    REQUISITO 6: Realiza o upload da nova foto e remove o arquivo antigo 
    da pasta local para mitigar o acúmulo de arquivos órfãos.
    """
    user = get_user_or_404(user_id)
    assert_can_update(actor, user_id)
    
    # Guardamos o caminho do arquivo anterior antes do novo processamento
    old_photo_url = getattr(user, "foto_perfil", None)
    
    # Executa o salvamento físico da nova foto através do core utilitário
    photo_url = save_image_upload("perfil", user_id, file)
    
    # Atualiza a referência no repositório de banco de dados
    repo.update_user_photo(user_id, photo_url)
    
    # Se existia uma foto anterior e ela for diferente da nova, realiza o expurgo
    if old_photo_url and old_photo_url != photo_url:
        try:
            # Converte a URL relativa (/uploads/perfil/...) para o caminho real no disco
            # Remove a barra inicial se existir para não quebrar a junção de caminhos do OS
            relative_path = old_photo_url.lstrip("/")
            
            if os.path.exists(relative_path) and os.path.isfile(relative_path):
                os.remove(relative_path)
                logger.info("REQUISITO 6: Arquivo de foto antigo expurgado com sucesso: %s", relative_path)
        except Exception as e:
            # Falhas na remoção do arquivo antigo não devem travar o fluxo principal do usuário
            logger.error("Falha ao remover arquivo órfão antigo de perfil %s: %s", old_photo_url, e)

    return get_user_or_404(user_id)