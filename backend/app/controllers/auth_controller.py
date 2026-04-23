import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse, FirebaseLoginRequest
from app.services.auth_service import login
from app.services import user_service
from app.schemas.user_schema import UserCreate
from app.schemas.endereco_schema import EnderecoCreate
from app.middlewares.auth_middleware import get_current_user
from app.core.roles import CLIENTE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_auth_cookie(response: JSONResponse, token: str) -> JSONResponse:
    """Injeta o JWT como cookie HttpOnly no response."""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        secure=True,
    )
    return response


@router.post("/login")
def login_user(data: LoginRequest):
    logger.info("POST /auth/login email=%s", data.email)
    token = login(data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    # Retorna JSON e seta o cookie HttpOnly no mesmo response
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    _set_auth_cookie(response, token)
    logger.info("POST /auth/login sucesso — cookie setado")
    return response


@router.post("/register")
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
    except Exception as e:
        logger.error("Erro inesperado ao criar usuário: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno ao criar conta")
        
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
            endereco_service.add_endereco_to_user(user.id_usuario, endereco_data)
        except Exception as e:
            logger.error("Erro ao salvar endereco: %s", e, exc_info=True)
            # Fails silently for address, allow user login to continue
    
    # Fazer login automático
    token = login(data.email, data.password)
    if not token:
        logger.error("registro: falha ao gerar token user_id=%s", user.id_usuario)
        raise HTTPException(status_code=500, detail="Erro ao gerar token")
    
    logger.info("POST /auth/register sucesso user_id=%s — cookie setado", user.id_usuario)
    response = JSONResponse(
        content={"access_token": token, "token_type": "bearer"},
        status_code=201,
    )
    _set_auth_cookie(response, token)
    return response


@router.post("/google")
def login_with_google(data: FirebaseLoginRequest):
    logger.info("POST /auth/google - Validando Token com Firebase Admin")
    
    # 1. Importação lazy do Firebase (evita crash no import do módulo inteiro)
    try:
        from firebase_admin import auth as firebase_auth
    except ImportError:
        logger.error("firebase-admin não instalado")
        raise HTTPException(status_code=500, detail="Serviço Google indisponível")

    # 2. Validação da Autenticidade no Firebase Admin
    try:
        decoded_token = firebase_auth.verify_id_token(data.id_token)
        email = decoded_token.get("email")
        nome = decoded_token.get("name", "Usuário Google")
    except Exception as e:
        logger.error("Falha na validação do Firebase Token: %s", str(e))
        raise HTTPException(status_code=401, detail="Token do Google inválido ou expirado")

    # 3. Lógica de Banco de Dados: Verifica se usuário já existe pelo e-mail
    from app.repositories import user_repository
    user = user_repository.get_user_by_email(email)

    if not user:
        # Se não existe, cria o usuário automaticamente
        # Senha aleatória de alta segurança (usuário Google nunca usa essa senha)
        import uuid
        generic_secure_password = str(uuid.uuid4()) + "A1@"
        
        user_data = UserCreate(
            nome=nome,
            email=email,
            password=generic_secure_password,
            role=CLIENTE,
            ativo=True,
            # telefone, cpf_cnpj, data_nascimento ficam None (opcionais agora)
        )
        try:
            user = user_service.create_user(user_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("Erro ao criar usuário Google: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Erro ao criar conta Google")

        # Autentica pelo DB local para gerar nosso JWT
        token = login(email, generic_secure_password)
        if not token:
            logger.error("Google login: falha ao gerar token para novo user email=%s", email)
            raise HTTPException(status_code=500, detail="Erro ao gerar token")
    else:
        # Se já existe, geramos o token JWT diretamente sem pedir senha
        from app.core.security import create_access_token
        
        token = create_access_token(
            {"sub": str(user.id_usuario), "role": user.role}
        )
    
    # Setar cookie HttpOnly e retornar
    response = JSONResponse(content={"access_token": token, "token_type": "bearer"})
    _set_auth_cookie(response, token)
    logger.info("POST /auth/google sucesso — cookie setado")
    return response


@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current
