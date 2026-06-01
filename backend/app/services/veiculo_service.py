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
        raise HTTPException(status_code=404, detail="Modelo não encontrado")

def find_or_create_veiculo_for_user(user_id: int, data: VeiculoCreate):
    """Reutiliza veículo existente pela placa do usuário ou cria um novo."""
    user_service.get_user_or_404(user_id)
    get_modelo_or_404(data.id_modelo)
    existing = repo.get_veiculo_by_placa_for_user(data.placa, user_id)
    if existing:
        if data.id_modelo is not None:
            existing.id_modelo = data.id_modelo
        if data.ano_fabricacao is not None:
            existing.ano_fabricacao = data.ano_fabricacao
        if data.cor is not None:
            existing.cor = data.cor
        return repo.update_veiculo(existing)
    return create_veiculo_for_user(user_id, data)


def create_veiculo_for_user(user_id: int, data: VeiculoCreate):
    user_service.get_user_or_404(user_id)
    get_modelo_or_404(data.id_modelo)

    veiculo = Veiculo(
        id_usuario=user_id,
        id_modelo=data.id_modelo,
        placa=data.placa,
        ano_fabricacao=data.ano_fabricacao,
        cor=data.cor,
    )

    try:
        return repo.create_veiculo(veiculo)
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=409, detail="Placa já cadastrada")


def list_all_veiculos():
    return repo.get_all_veiculos()


def list_veiculos_by_user(user_id: int):
    user_service.get_user_or_404(user_id)
    return repo.list_veiculos_by_user(user_id)


def get_veiculo_by_id_or_404(veiculo_id: int):
    veiculo = repo.get_veiculo_by_id(veiculo_id)

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    return veiculo


def update_veiculo(veiculo_id: int, data: VeiculoUpdate):
    veiculo = get_veiculo_by_id_or_404(veiculo_id)

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
        raise HTTPException(status_code=409, detail="Placa já cadastrada")

def delete_veiculo(veiculo_id: int):
    veiculo = get_veiculo_by_id_or_404(veiculo_id)
    return repo.soft_delete_veiculo(veiculo)