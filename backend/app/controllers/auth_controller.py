import logging
import os
from datetime import date as date_type
from pathlib import Path
from typing import Optional

import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

from app.core.roles import CLIENTE
from app.core.security import create_access_token
from app.middlewares.auth_middleware import get_current_user
from app.schemas.auth_schema import FirebaseLoginRequest, ForgotPasswordRequest, ResetPasswordRequest, TokenResponse
from app.schemas.endereco_schema import EnderecoCreate
from app.schemas.user_schema import UserCreate
from app.services import user_service
from app.services.auth_service import login
from app.services.email_service import send_password_reset_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))

_IS_PRODUCTION = bool(os.environ.get("K_SERVICE"))


class RegisterPayloadJSON(BaseModel):
    nome: str
    email: EmailStr
    password: str
    cpf_cnpj: Optional[str] = None
    data_nascimento: Optional[str] = None
    telefone: Optional[str] = None
    # Endereço acoplado no mesmo payload JSON
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

def _set_auth_cookie(response, token: str):
    """Injeta o JWT como cookie HttpOnly no response."""
    response.set_cookie(
        key="__session",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        secure=_IS_PRODUCTION,
    )
    return response

@router.post("/login", response_model=TokenResponse)
def login_user(data: FirebaseLoginRequest):  # Modificado para usar o schema importado de auth_schema
    logger.info("POST /auth/login email=%s", data.email if hasattr(data, 'email') else "Google/Firebase")

    token = login(data.email, data.password)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    response = JSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
        }
    )

    _set_auth_cookie(response, token)

    logger.info("POST /auth/login sucesso")
    return response


@router.post("/register")
def register_user(request: Request, data: RegisterPayloadJSON):
    """Cadastro via JSON Payload. Renderiza Template Jinja em caso de erro."""
    logger.info("POST /auth/register JSON recebido. Email: %s", data.email)

    parsed_date = None
    if data.data_nascimento:
        try:
            parsed_date = date_type.fromisoformat(data.data_nascimento)
        except ValueError:
            parsed_date = None

    user_data = UserCreate(
        nome=data.nome,
        email=data.email,
        password=data.password,
        role=CLIENTE,
        ativo=True,
        telefone=data.telefone or None,
        cpf_cnpj=data.cpf_cnpj or None,
        data_nascimento=parsed_date,
    )

    try:
        user = user_service.create_user(user_data)
    except HTTPException as e:
        # Se falhar, devolve a página Jinja com o erro para o JS tratar
        return _templates.TemplateResponse("pages/cadastro.html", {
            "request": request,
            "user": None,
            "error": e.detail,
            "firebase_api_key": os.environ.get("FIREBASE_WEB_API_KEY", ""),
        }, status_code=e.status_code)
    except Exception as e:
        logger.error("Erro inesperado ao criar usuário: %s", e, exc_info=True)
        return _templates.TemplateResponse("pages/cadastro.html", {
            "request": request,
            "user": None,
            "error": "Erro interno ao criar conta. Tente novamente.",
            "firebase_api_key": os.environ.get("FIREBASE_WEB_API_KEY", ""),
        }, status_code=500)

    # Criação do Endereço caso preenchido
    if data.logradouro or data.cep:
        endereco_data = EnderecoCreate(
            logradouro=data.logradouro or "",
            numero=data.numero or None,
            cep=data.cep or None,
            bairro=data.bairro or None,
            cidade=data.cidade or None,
            estado=data.estado or None,
        )
        try:
            from app.services import endereco_service
            endereco_service.add_endereco_to_user(user.id_usuario, endereco_data)
        except Exception as e:
            logger.error("Erro ao salvar endereço: %s", e, exc_info=True)

    token = login(data.email, data.password)
    if not token:
        return JSONResponse(content={"redirect": "/login"}, status_code=200)

    # Controlado por Fetch API no front-end, passamos a rota de sucesso
    response = JSONResponse(content={"redirect": "/"}, status_code=200)
    _set_auth_cookie(response, token)
    return response

@router.post("/google")
def login_with_google(data: FirebaseLoginRequest):
    logger.info("POST /auth/google - Validando Token com Firebase Admin")

    try:
        from firebase_admin import auth as firebase_auth
    except ImportError:
        logger.error("firebase-admin não instalado")
        raise HTTPException(status_code=500, detail="Serviço Google indisponível")

    try:
        decoded_token = firebase_auth.verify_id_token(data.id_token)
        email = decoded_token.get("email")
        nome = decoded_token.get("name", "Usuário Google")
    except Exception as e:
        logger.error("Falha na validação do Firebase Token: %s", str(e))
        raise HTTPException(status_code=401, detail="Token do Google inválido ou expirado")

    from app.repositories import user_repository
    user = user_repository.get_user_by_email(email)

    if not user:
        generic_secure_password = str(uuid.uuid4()) + "A1@"

        user_data = UserCreate(
            nome=nome,
            email=email,
            password=generic_secure_password,
            role=CLIENTE,
            ativo=True,
        )
        try:
            user = user_service.create_user(user_data)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("Erro ao criar usuário Google: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Erro ao criar conta Google")

        token = login(email, generic_secure_password)
        if not token:
            raise HTTPException(status_code=500, detail="Erro ao gerar token")
    else:
        token = create_access_token(
            {"sub": str(user.id_usuario), "role": user.role}
        )

    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    logger.info("POST /auth/google sucesso — cookie setado")
    return response


@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    """Solicita reset de senha via email."""
    logger.info("POST /auth/forgot-password email=%s", data.email)
    
    from app.repositories import user_repository
    user = user_repository.get_user_by_email(data.email)
    
    if not user:
        logger.warning("Forgot password request for non-existent email: %s", data.email)
        return {
            "message": "Se o email está cadastrado, você receberá um link de recuperação em breve."
        }
    
    from datetime import timedelta
    from app.core.settings import get_settings
    settings = get_settings()
    
    reset_token = create_access_token(
        {"sub": str(user.id_usuario), "action": "password_reset"},
        expires_delta=timedelta(minutes=settings.password_reset_token_expire_minutes)
    )
    
    send_password_reset_email(user.email, reset_token)
    
    return {
        "message": "Se o email está cadastrado, você receberá um link de recuperação em breve."
    }


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(data: ResetPasswordRequest):
    """Reseta a senha usando token de recuperação."""
    logger.info("POST /auth/reset-password")
    
    from jose import JWTError, jwt
    from app.core.config import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        action = payload.get("action")
        
        if action != "password_reset" or not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )
    except JWTError:
        logger.warning("Invalid password reset token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    from app.repositories import user_repository
    from app.core.security import hash_password
    
    user = user_repository.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    hashed_password = hash_password(data.nova_senha)
    user_repository.update_user_password(user.id_usuario, hashed_password)
    
    logger.info("Password reset successful for user_id=%s", user_id)
    
    access_token = create_access_token(
        {"sub": str(user.id_usuario), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/reset-password")
def reset_password_page(request: Request, token: str):
    return _templates.TemplateResponse(
        "pages/reset_password.html",
        {
            "request": request,
            "token": token
        }
    )