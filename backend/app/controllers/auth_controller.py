import logging
import os

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.schemas.auth_schema import FirebaseLoginRequest, ForgotPasswordRequest, ResetPasswordRequest, TokenResponse
from app.services.auth_service import login
from app.services import user_service
from app.schemas.user_schema import UserCreate
from app.schemas.endereco_schema import EnderecoCreate
from app.middlewares.auth_middleware import get_current_user
from app.core.roles import CLIENTE
from app.core.security import create_access_token
from app.services.email_service import send_password_reset_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

# Detecta se estamos em produção (HTTPS) ou local (HTTP)
_IS_PRODUCTION = bool(os.environ.get("K_SERVICE"))


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


# ---------------------------------------------------------------------------
# SSR: Login via formulário HTML (POST direto, sem JS/fetch)
# ---------------------------------------------------------------------------
@router.post("/login")
def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login SSR: recebe dados do formulário, seta cookie e redireciona."""
    logger.info("POST /auth/login email=%s", email)
    token = login(email, password)

    if not token:
        # Re-renderiza a página de login com mensagem de erro
        from app.controllers.page_controller import templates
        return templates.TemplateResponse("pages/login.html", {
            "request": request,
            "user": None,
            "error": "Usuário ou senha incorretos.",
            "firebase_api_key": os.environ.get("FIREBASE_WEB_API_KEY", ""),
        }, status_code=401)

    # Sucesso: redireciona para / com cookie setado (303 = POST → GET)
    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    logger.info("POST /auth/login sucesso — cookie setado, redirect 303")
    return response


# ---------------------------------------------------------------------------
# SSR: Cadastro via formulário HTML (POST direto, sem JS/fetch)
# ---------------------------------------------------------------------------
@router.post("/register")
def register_user(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cpf_cnpj: str = Form(""),
    data_nascimento: str = Form(""),
    telefone: str = Form(""),
    cep: str = Form(""),
    logradouro: str = Form(""),
    numero: str = Form(""),
    bairro: str = Form(""),
    cidade: str = Form(""),
    estado: str = Form(""),
):
    """Cadastro SSR: recebe dados do formulário, cria user, seta cookie e redireciona."""
    logger.info("POST /auth/register nome=%s email=%s", nome, email)

    # Preparar dados do usuário
    from datetime import date as date_type
    parsed_date = None
    if data_nascimento:
        try:
            parsed_date = date_type.fromisoformat(data_nascimento)
        except ValueError:
            parsed_date = None

    user_data = UserCreate(
        nome=nome,
        email=email,
        password=password,
        role=CLIENTE,
        ativo=True,
        telefone=telefone or None,
        cpf_cnpj=cpf_cnpj or None,
        data_nascimento=parsed_date,
    )

    try:
        user = user_service.create_user(user_data)
    except HTTPException as e:
        # Re-renderiza a página de cadastro com erro
        from app.controllers.page_controller import templates
        return templates.TemplateResponse("pages/cadastro.html", {
            "request": request,
            "user": None,
            "error": e.detail,
            "firebase_api_key": os.environ.get("FIREBASE_WEB_API_KEY", ""),
        }, status_code=e.status_code)
    except Exception as e:
        logger.error("Erro inesperado ao criar usuário: %s", e, exc_info=True)
        from app.controllers.page_controller import templates
        return templates.TemplateResponse("pages/cadastro.html", {
            "request": request,
            "user": None,
            "error": "Erro interno ao criar conta. Tente novamente.",
            "firebase_api_key": os.environ.get("FIREBASE_WEB_API_KEY", ""),
        }, status_code=500)

    # Salvar Endereço se fornecido
    if logradouro or cep:
        endereco_data = EnderecoCreate(
            logradouro=logradouro or "",
            numero=numero or None,
            cep=cep or None,
            bairro=bairro or None,
            cidade=cidade or None,
            estado=estado or None,
        )
        try:
            from app.services import endereco_service
            endereco_service.add_endereco_to_user(user.id_usuario, endereco_data)
        except Exception as e:
            logger.error("Erro ao salvar endereco: %s", e, exc_info=True)

    # Login automático e redirect
    token = login(email, password)
    if not token:
        logger.error("registro: falha ao gerar token user_id=%s", user.id_usuario)
        response = RedirectResponse(url="/login", status_code=303)
        return response

    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    logger.info("POST /auth/register sucesso user_id=%s — redirect 303", user.id_usuario)
    return response


# ---------------------------------------------------------------------------
# API JSON: Login com Google (Firebase Auth) — mantém fetch/JSON
# porque o popup do Google é client-side por natureza
# ---------------------------------------------------------------------------
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
        import uuid
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
        from app.core.security import create_access_token
        token = create_access_token(
            {"sub": str(user.id_usuario), "role": user.role}
        )

    # Sucesso: redireciona para / com cookie setado (303 = POST → GET)
    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    logger.info("POST /auth/google sucesso — cookie setado")
    return response


@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current

# Recuperação de Senha

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    """Solicita reset de senha via email.
    
    Envia link com token JWT válido por 30 minutos.
    """
    logger.info("POST /auth/forgot-password email=%s", data.email)
    
    # Verificar se usuário existe
    from app.repositories import user_repository
    user = user_repository.get_user_by_email(data.email)
    
    if not user:
        # Não revelar se email existe ou não (segurança)
        logger.warning("Forgot password request for non-existent email: %s", data.email)
        return {
            "message": "Se o email está cadastrado, você receberá um link de recuperação em breve."
        }
    
    # Gerar token de reset (válido por 30 minutos)
    from datetime import timedelta
    from app.core.settings import get_settings
    settings = get_settings()
    
    reset_token = create_access_token(
        {"sub": str(user.id_usuario), "action": "password_reset"},
        expires_delta=timedelta(minutes=settings.password_reset_token_expire_minutes)
    )
    
    # Enviar email
    send_password_reset_email(user.email, reset_token)
    
    return {
        "message": "Se o email está cadastrado, você receberá um link de recuperação em breve."
    }


@router.post("/reset-password", response_model=TokenResponse)
def reset_password(data: ResetPasswordRequest):
    """Reseta a senha usando token de recuperação.
    
    Body:
        - token: JWT token recebido no email
        - nova_senha: nova senha (min 8 chars, uppercase, lowercase, número, caractere especial)
    """
    logger.info("POST /auth/reset-password")
    
    # Validar token
    from jose import JWTError, jwt
    from app.core.config import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        action = payload.get("action")
        
        if action != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido ou expirado"
            )
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )
    except JWTError:
        logger.warning("Invalid password reset token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado"
        )
    
    # Atualizar senha do usuário
    from app.repositories import user_repository
    from app.core.security import hash_password
    
    user = user_repository.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Hash a nova senha
    hashed_password = hash_password(data.nova_senha)
    user_repository.update_user_password(user.id_usuario, hashed_password)
    
    logger.info("Password reset successful for user_id=%s", user_id)
    
    # Gerar novo token de acesso para o usuário
    access_token = create_access_token(
        {"sub": str(user.id_usuario), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/reset-password")
def reset_password_page(
    request: Request,
    token: str
):
    from app.controllers.page_controller import templates

    return templates.TemplateResponse(
        "pages/reset_password.html",
        {
            "request": request,
            "token": token
        }
    )