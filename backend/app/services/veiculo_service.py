import logging

from fastapi import HTTPException, status
import psycopg2

from app.models.entities import Veiculo
from app.repositories import modelo_repository as modelo_repo
from app.repositories import veiculo_repository as repo
from app.schemas.veiculo_schema import VeiculoCreate, VeiculoUpdate
from app.services import user_service

logger = logging.getLogger(__name__)

def get_modelo_or_404(modelo_id: int):
    if not modelo_repo.get_modelo_by_id(modelo_id):
        logger.info("modelo não encontrado id=%s", modelo_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado")

def create_veiculo_for_user(user_id: int, data: VeiculoCreate):
    user_service.get_user_or_404(user_id)
    get_modelo_or_404(data.id_modelo)
    veiculo = Veiculo(
        id_cliente=user_id,
        placa=data.placa,
        ano_fabricacao=data.ano_fabricacao,
        cor=data.cor,
        id_modelo=data.id_modelo,
    )
    try:
        return repo.create_veiculo(veiculo)
    except psycopg2.IntegrityError:
        logger.warning("create_veiculo placa duplicada placa=%s", data.placa)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placa já cadastrada",
        )

def list_veiculos_by_user(user_id: int):
    user_service.get_user_or_404(user_id)
    return repo.list_veiculos_by_user(user_id)

def get_veiculo_by_user_or_404(user_id: int, veiculo_id: int) -> Veiculo:
    user_service.get_user_or_404(user_id)
    veiculo = repo.get_veiculo_by_id_for_user(user_id, veiculo_id)
    if not veiculo:
        logger.info(
            "veículo não encontrado user=%s veiculo=%s",
            user_id,
            veiculo_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")
    return veiculo

def update_veiculo_by_user(user_id: int, veiculo_id: int, data: VeiculoUpdate):
    veiculo = get_veiculo_by_user_or_404(user_id, veiculo_id)
    if data.id_modelo is not None:
        get_modelo_or_404(data.id_modelo)
        veiculo.id_modelo = data.id_modelo
    if data.placa is not None:
        veiculo.placa = data.placa
    if data.ano_fabricacao is not None:
        veiculo.ano_fabricacao = data.ano_fabricacao
    if data.cor is not None:
        veiculo.cor = data.cor
    try:
        return repo.update_veiculo(veiculo)
    except psycopg2.IntegrityError:
        logger.warning("update_veiculo placa duplicada veiculo_id=%s", veiculo_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placa já cadastrada",
        )

def delete_veiculo_by_user(user_id: int, veiculo_id: int):
    veiculo = get_veiculo_by_user_or_404(user_id, veiculo_id)
    return repo.soft_delete_veiculo(veiculo)
