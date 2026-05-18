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

# Schema unificado
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
    response.set_cookie(
        key="__session",
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
        secure=_IS_PRODUCTION,
    )
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
        # Se falhar no Pydantic interno ou na regra de negócio, devolve a página Jinja com o erro !!!!!
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

    # Em requisições JSON controladas por Fetch API, retornamos o destino no corpo
    response = JSONResponse(content={"redirect": "/"}, status_code=200)
    _set_auth_cookie(response, token)
    return response