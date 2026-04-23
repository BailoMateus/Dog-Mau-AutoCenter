import logging
import firebase_admin
from firebase_admin import auth

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse, FirebaseLoginRequest
from app.services.auth_service import login
from app.services import user_service
from app.schemas.user_schema import UserCreate
from app.schemas.endereco_schema import EnderecoCreate
from app.middlewares.auth_middleware import get_current_user
from app.core.roles import CLIENTE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest):
    logger.info("POST /auth/login email=%s", data.email)
    token = login(data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    return {"access_token": token}

@router.post("/register", response_model=TokenResponse)
def register_user(data: RegisterRequest):
    logger.info("POST /auth/register nome=%s email=%s", data.nome, data.email)
    
    # Criar usuário unificado
    user_data = UserCreate(
        nome=data.nome,
        email=data.email,
        password=data.password,
        role=CLIENTE,
        ativo=True,
        telefone=data.telefone,
        cpf_cnpj=data.cpf_cnpj,
        data_nascimento=data.data_nascimento
    )
    
    try:
        user = user_service.create_user(user_data)
    except HTTPException as e:
        raise e
        
    # Salvar Endereço se fornecido
    if data.logradouro or data.cep:
        endereco_data = EnderecoCreate(
            logradouro=data.logradouro or "",
            numero=data.numero,
            cep=data.cep,
            bairro=data.bairro,
            cidade=data.cidade,
            estado=data.estado
        )
        try:
            from app.services import endereco_service
            endereco_service.add_endereco(user.id_usuario, endereco_data)
        except Exception as e:
            logger.error(f"Erro ao salvar endereco: {e}")
            # Fails silently for address, allow user login to continue
    
    # Fazer login automático
    token = login(data.email, data.password)
    if not token:
        logger.error("registro: falha ao gerar token user_id=%s", user.id_usuario)
        raise HTTPException(status_code=500, detail="Erro ao gerar token")
    
    logger.info("POST /auth/register sucesso user_id=%s", user.id_usuario)
    return {"access_token": token}

@router.post("/google", response_model=TokenResponse)
def login_with_google(data: FirebaseLoginRequest):
    logger.info("POST /auth/google - Validando Token com Firebase Admin")
    
    # 1. Validação da Autenticidade no Firebase Admin
    try:
        decoded_token = auth.verify_id_token(data.id_token)
        email = decoded_token.get("email")
        nome = decoded_token.get("name", "Usuário Google")
    except Exception as e:
        logger.error("Falha na validação do Firebase Token: %s", str(e))
        raise HTTPException(status_code=401, detail="Token do Google inválido ou expirado")

    # 2. Lógica de Banco de Dados: Verifica se usuário já existe pelo e-mail
    from app.repositories import user_repository
    user = user_repository.get_user_by_email(email)

    if not user:
        # Se não existe, cria o usuário e o cliente automaticamente
        # Geramos uma senha aleatória de alta segurança (bypassando a senha)
        import uuid
        generic_secure_password = str(uuid.uuid4()) + "A1@"
        
        user_data = UserCreate(
            nome=nome,
            email=email,
            password=generic_secure_password,
            role=CLIENTE,
            ativo=True
        )
        user = user_service.create_user(user_data)

        # Autentica pelo DB local agora para gerar nosso próprio JWT
        token = login(email, generic_secure_password)
    else:
        # Se já existe, geramos o token JWT da nossa API diretamente sem pedir senha
        from app.services.auth_service import create_access_token
        from datetime import timedelta
        from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.email, "role": user.role, "user_id": user.id_usuario},
            expires_delta=access_token_expires
        )
        
    return {"access_token": token}


@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current
