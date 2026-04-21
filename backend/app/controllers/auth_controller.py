import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import login
from app.services import user_service
from app.schemas.user_schema import UserCreate
from app.database.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.core.roles import CLIENTE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    logger.info("POST /auth/login email=%s", data.email)
    token = login(db, data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")

    return {"access_token": token}

@router.post("/register", response_model=TokenResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
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
        user = user_service.create_user(db, user_data)
    except HTTPException as e:
        raise e
    
    # Fazer login automático
    token = login(db, data.email, data.password)
    if not token:
        logger.error("registro: falha ao gerar token user_id=%s", user.id_usuario)
        raise HTTPException(status_code=500, detail="Erro ao gerar token")
    
    logger.info("POST /auth/register sucesso user_id=%s", user.id_usuario)
    return {"access_token": token}

@router.get("/me")
def me(current=Depends(get_current_user)):
    logger.info("GET /auth/me user_id=%s role=%s", current["user_id"], current["role"])
    return current
