"""
Controller de páginas HTML (Jinja2).

Responsável por renderizar todas as páginas do frontend.
As rotas de API (/auth/*, /me/*, etc.) continuam nos outros controllers.

Para adicionar uma nova página:
    1. Crie o template em templates/pages/nova_pagina.html
    2. Adicione uma rota aqui com @router.get("/nova-pagina")
    3. Use get_page_user para auth opcional, ou verifique if not user para obrigatória
"""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.settings import get_settings
from app.database.db import execute_query
from app.services.user_service import list_users
from app.services import servico_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Páginas"])

# Caminho dos templates (backend/app/templates/)
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))


# ---------------------------------------------------------------------------
# Dependências de autenticação para páginas
# ---------------------------------------------------------------------------

def get_page_user(request: Request):
    """Auth opcional: retorna dict com dados do usuário ou None.
    
    Lê o JWT do cookie 'access_token'. Se válido, busca o user no banco
    e retorna {user_id, role, nome}. Se inválido ou ausente, retorna None.
    """
    token = request.cookies.get("__session") or request.cookies.get("access_token")
    if not token:
        return None
    # Compatibilidade: remove prefixo 'Bearer ' se presente (cookies antigos)
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = execute_query(
            "SELECT id_usuario, nome, role FROM usuario WHERE id_usuario = %s AND deleted_at IS NULL",
            (int(user_id),),
            fetch="one",
        )
        if not user:
            return None
        return {"user_id": user_id, "role": payload.get("role"), "nome": user["nome"]}
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Rotas de páginas
# ---------------------------------------------------------------------------

@router.get("/", include_in_schema=False)
def home_page(request: Request, user=Depends(get_page_user)):
    """Página inicial — pública, mostra header logado/deslogado."""
    return templates.TemplateResponse("pages/index.html", {
        "request": request,
        "user": user,
        "page": "home",
    })


@router.get("/login", include_in_schema=False)
def login_page(request: Request, user=Depends(get_page_user)):
    """Página de login — redireciona para / se já logado."""
    if user:
        return RedirectResponse(url="/", status_code=302)
    _s = get_settings()
    return templates.TemplateResponse("pages/login.html", {
        "request": request,
        "user": None,
        "error": None,
        "firebase_api_key": _s.firebase_web_api_key,
    })


@router.get("/cadastro", include_in_schema=False)
def cadastro_page(request: Request, user=Depends(get_page_user)):
    """Página de cadastro — redireciona para / se já logado."""
    if user:
        return RedirectResponse(url="/", status_code=302)
    _s = get_settings()
    return templates.TemplateResponse("pages/cadastro.html", {
        "request": request,
        "user": None,
        "firebase_api_key": _s.firebase_web_api_key,
    })


@router.get("/servicos", include_in_schema=False)
def services_page(request: Request, user=Depends(get_page_user)):
    """Página de serviços — pública."""
    return templates.TemplateResponse("pages/services.html", {
        "request": request,
        "user": user,
        "page": "servicos",
    })


@router.get("/logout", include_in_schema=False)
def logout(request: Request):
    """Limpa o cookie de autenticação e redireciona para a home."""
    logger.info("GET /logout — limpando cookie")
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("__session")
    response.delete_cookie("access_token") # Por segurança, limpa o antigo também
    return response

@router.get("/painel", include_in_schema=False)
def painel_page(request: Request, tab: str = None, user=Depends(get_page_user)):
    """Painel unificado — requer autenticação.

    Admin/Mecânico veem abas de gestão (Usuários, Produtos, OS).
    Cliente vê sua própria área (Meus Pedidos, Minhas OS).
    """
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Define a aba padrão conforme o role
    if not tab:
        tab = "usuarios" if user.get("role") in ("admin", "mecanico") else "meu_usuario"

    # Carrega dados apenas para roles que precisam
    usuarios = []
    servicos = []
    if user.get("role") in ("admin", "mecanico"):
        usuarios = list_users()
        servicos = servico_service.list_servicos()

    return templates.TemplateResponse("pages/painel.html", {
        "request": request,
        "user": user,
        "usuarios": usuarios,
        "servicos": servicos,
        "tab": tab,
        "page": "painel",
    })


@router.get("/admin/usuarios", include_in_schema=False)
def admin_usuarios_page(request: Request, user=Depends(get_page_user)):
    """Página de administração de usuários — apenas para ADMIN."""
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/", status_code=302)
    
    usuarios = list_users()
    return templates.TemplateResponse("pages/admin_usuarios.html", {
        "request": request,
        "user": user,
        "usuarios": usuarios,
        "page": "admin",
    })
