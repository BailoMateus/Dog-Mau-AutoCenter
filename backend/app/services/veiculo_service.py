import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.veiculo import Veiculo
from app.repositories import modelo_repository as modelo_repo
from app.repositories import veiculo_repository as repo
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoUpdate
from app.services import cliente_service

logger = logging.getLogger(__name__)

def get_modelo_or_404(db: Session, modelo_id: int):
    if not modelo_repo.get_modelo_by_id(db, modelo_id):
        logger.info("modelo não encontrado id=%s", modelo_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado")

def create_veiculo(db: Session, cliente_id: int, data: VeiculoCreate):
    cliente_service.get_cliente_or_404(db, cliente_id)
    get_modelo_or_404(db, data.id_modelo)
    veiculo = Veiculo(
        id_cliente=cliente_id,
        placa=data.placa,
        ano_fabricacao=data.ano_fabricacao,
        cor=data.cor,
        id_modelo=data.id_modelo,
    )
    try:
        return repo.create_veiculo(db, veiculo)
    except IntegrityError:
        db.rollback()
        logger.warning("create_veiculo placa duplicada placa=%s", data.placa)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placa já cadastrada",
        )

def list_veiculos(db: Session, cliente_id: int):
    cliente_service.get_cliente_or_404(db, cliente_id)
    return repo.list_veiculos_by_cliente(db, cliente_id)

def get_veiculo_or_404(db: Session, cliente_id: int, veiculo_id: int) -> Veiculo:
    cliente_service.get_cliente_or_404(db, cliente_id)
    veiculo = repo.get_veiculo_by_id_for_cliente(db, cliente_id, veiculo_id)
    if not veiculo:
        logger.info(
            "veículo não encontrado cliente=%s veiculo=%s",
            cliente_id,
            veiculo_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")
    return veiculo

def update_veiculo(db: Session, cliente_id: int, veiculo_id: int, data: VeiculoUpdate):
    veiculo = get_veiculo_or_404(db, cliente_id, veiculo_id)
    if data.id_modelo is not None:
        get_modelo_or_404(db, data.id_modelo)
        veiculo.id_modelo = data.id_modelo
    if data.placa is not None:
        veiculo.placa = data.placa
    if data.ano_fabricacao is not None:
        veiculo.ano_fabricacao = data.ano_fabricacao
    if data.cor is not None:
        veiculo.cor = data.cor
    try:
        return repo.update_veiculo(db, veiculo)
    except IntegrityError:
        db.rollback()
        logger.warning("update_veiculo placa duplicada veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placa já cadastrada",
        )

def delete_veiculo(db: Session, cliente_id: int, veiculo_id: int):
    veiculo = get_veiculo_or_404(db, cliente_id, veiculo_id)
    return repo.soft_delete_veiculo(db, veiculo)
