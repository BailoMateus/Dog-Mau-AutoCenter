import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.core.roles import CLIENTE
from app.core.security import require_role
from app.database.database import get_db
from app.middlewares.auth_middleware import get_current_user
from app.schemas.cliente_schema import ClientePublic, ClienteUpdate
from app.schemas.endereco_schema import EnderecoCreate, EnderecoPublic, EnderecoUpdate
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoPublic, VeiculoUpdate
from app.services import cliente_service, endereco_service, veiculo_service, user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["Minha Conta"])

# Middleware para garantir que é cliente
def require_cliente(current=Depends(get_current_user)):
    if current["role"] != CLIENTE:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para clientes"
        )
    return current

@router.post("/cliente", response_model=ClientePublic, status_code=201)
def create_my_cliente_data(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente cria seus dados completos (após cadastro de usuário)"""
    logger.info("POST /me/cliente user_id=%s", current["user_id"])
    
    user_id = current["user_id"]
    user = user_service.get_user_or_404(db, user_id)
    
    # Verifica se já existe cliente para este usuário
    existing_cliente = cliente_service.get_cliente_by_email(db, user.email)
    if existing_cliente:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dados do cliente já existem"
        )
    
    # Cria cliente com email do usuário
    cliente_data = ClienteCreate(
        nome=data.nome,
        telefone=data.telefone,
        email=user.email,  # Usa o email do usuário
        cpf_cnpj=data.cpf_cnpj,
        data_nascimento=data.data_nascimento,
    )
    
    return cliente_service.create_cliente(db, cliente_data)

@router.get("/cliente", response_model=ClientePublic)
def get_my_cliente_data(
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente vê seus próprios dados"""
    logger.info("GET /me/cliente user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return cliente

@router.patch("/cliente", response_model=ClientePublic)
def update_my_cliente_data(
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente atualiza seus próprios dados"""
    logger.info("PATCH /me/cliente user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return cliente_service.update_cliente(db, cliente.id_cliente, data)

# Endereços do cliente
@router.get("/enderecos", response_model=list[EnderecoPublic])
def list_my_enderecos(
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente lista seus endereços"""
    logger.info("GET /me/enderecos user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return endereco_service.list_enderecos(db, cliente.id_cliente)

@router.post("/enderecos", response_model=EnderecoPublic, status_code=201)
def create_my_endereco(
    data: EnderecoCreate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente adiciona endereço"""
    logger.info("POST /me/enderecos user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return endereco_service.add_endereco(db, cliente.id_cliente, data)

@router.get("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def get_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente vê um endereço específico"""
    logger.info("GET /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    cliente = get_my_cliente(db, current)
    return endereco_service.get_endereco_or_404(db, cliente.id_cliente, endereco_id)

@router.patch("/enderecos/{endereco_id}", response_model=EnderecoPublic)
def update_my_endereco(
    endereco_id: Annotated[int, Path(ge=1)],
    data: EnderecoUpdate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente atualiza um endereço"""
    logger.info("PATCH /me/enderecos/%s user_id=%s", endereco_id, current["user_id"])
    cliente = get_my_cliente(db, current)
    return endereco_service.update_endereco(db, cliente.id_cliente, endereco_id, data)

# Veículos do cliente
@router.get("/veiculos", response_model=list[VeiculoPublic])
def list_my_veiculos(
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente lista seus veículos"""
    logger.info("GET /me/veiculos user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return veiculo_service.list_veiculos(db, cliente.id_cliente)

@router.post("/veiculos", response_model=VeiculoPublic, status_code=201)
def create_my_veiculo(
    data: VeiculoCreate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente adiciona veículo"""
    logger.info("POST /me/veiculos user_id=%s", current["user_id"])
    cliente = get_my_cliente(db, current)
    return veiculo_service.create_veiculo(db, cliente.id_cliente, data)

@router.get("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def get_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente vê um veículo específico"""
    logger.info("GET /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    cliente = get_my_cliente(db, current)
    return veiculo_service.get_veiculo_or_404(db, cliente.id_cliente, veiculo_id)

@router.patch("/veiculos/{veiculo_id}", response_model=VeiculoPublic)
def update_my_veiculo(
    veiculo_id: Annotated[int, Path(ge=1)],
    data: VeiculoUpdate,
    db: Session = Depends(get_db),
    current=Depends(require_cliente),
):
    """Cliente atualiza um veículo"""
    logger.info("PATCH /me/veiculos/%s user_id=%s", veiculo_id, current["user_id"])
    cliente = get_my_cliente(db, current)
    return veiculo_service.update_veiculo(db, cliente.id_cliente, veiculo_id, data)