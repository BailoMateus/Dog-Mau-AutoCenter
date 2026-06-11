import logging
import os

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Body
from fastapi.responses import JSONResponse, RedirectResponse

from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.services.auth_service import login
from app.services import user_service
from app.schemas.user_schema import UserCreate
from app.schemas.endereco_schema import EnderecoCreate
from app.middlewares.auth_middleware import get_current_user
from app.core.roles import CLIENTE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])
api_router = APIRouter(prefix="/api/auth", tags=["Auth API"])

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
        }, status_code=e.status_code)
    except Exception as e:
        logger.error("Erro inesperado ao criar usuário: %s", e, exc_info=True)
        from app.controllers.page_controller import templates
        return templates.TemplateResponse("pages/cadastro.html", {
            "request": request,
            "user": None,
            "error": "Erro interno ao criar conta. Tente novamente.",
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



@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current


# ---------------------------------------------------------------------------
# API JSON: Login com JSON (para Postman, Swagger, testes, e frontend com fetch)
# ---------------------------------------------------------------------------
@api_router.post("/login", response_model=dict)
def login_user_api(credentials: LoginRequest = Body(...)):
    """Login API: recebe JSON, retorna token JWT em JSON."""
    logger.info("POST /api/auth/login email=%s", credentials.email)
    
    token = login(credentials.email, credentials.password)

    if not token:
        logger.warning("POST /api/auth/login falha — credenciais inválidas email=%s", credentials.email)
        raise HTTPException(
            status_code=401, 
            detail="Usuário ou senha incorretos."
        )

    logger.info("POST /api/auth/login sucesso — token gerado")
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# API JSON: Registro com JSON (para Postman, Swagger, testes, e frontend com fetch)
# ---------------------------------------------------------------------------
@api_router.post("/register", response_model=dict)
def register_user_api(user_data: RegisterRequest = Body(...)):
    """Registro API: recebe JSON, cria user, retorna token JWT em JSON."""
    logger.info("POST /api/auth/register nome=%s email=%s", user_data.nome, user_data.email)

    # Preparar dados do usuário
    user_create = UserCreate(
        nome=user_data.nome,
        email=user_data.email,
        password=user_data.password,
        role=CLIENTE,
        ativo=True,
        telefone=user_data.telefone,
        cpf_cnpj=user_data.cpf_cnpj,
        data_nascimento=user_data.data_nascimento,
    )

    try:
        user = user_service.create_user(user_create)
    except HTTPException as e:
        logger.warning("POST /api/auth/register falha — %s", e.detail)
        raise e
    except Exception as e:
        logger.error("Erro inesperado ao criar usuário: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao criar conta. Tente novamente."
        )

    # Salvar Endereço se fornecido
    if user_data.logradouro or user_data.cep:
        endereco_data = EnderecoCreate(
            logradouro=user_data.logradouro or "",
            numero=user_data.numero,
            cep=user_data.cep,
            bairro=user_data.bairro,
            cidade=user_data.cidade,
            estado=user_data.estado,
        )
        try:
            from app.services import endereco_service
            endereco_service.add_endereco_to_user(user.id_usuario, endereco_data)
        except Exception as e:
            logger.error("Erro ao salvar endereco: %s", e, exc_info=True)

    # Login automático e retornar token
    token = login(user_data.email, user_data.password)
    if not token:
        logger.error("registro: falha ao gerar token user_id=%s", user.id_usuario)
        raise HTTPException(
            status_code=500, 
            detail="Erro ao gerar token de autenticação"
        )

    logger.info("POST /api/auth/register sucesso user_id=%s — token gerado", user.id_usuario)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id_usuario}


# Export dos routers
__all__ = ["router", "api_router"]
