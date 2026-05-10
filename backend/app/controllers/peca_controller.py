from fastapi import APIRouter, HTTPException
from app.services.peca_service import (
    listar_pecas,
    buscar_peca_por_id,
    criar_peca,
    atualizar_peca,
    remover_peca,
)

router = APIRouter(prefix="/pecas", tags=["Peças"])

@router.get("/", response_model=list)
def listar():
    """Lista todas as peças."""
    return listar_pecas()

@router.get("/{peca_id}", response_model=dict)
def buscar_por_id(peca_id: int):
    """Busca uma peça pelo ID."""
    try:
        return buscar_peca_por_id(peca_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=dict)
def criar(nome: str, preco_unitario: float, quantidade_estoque: int = 0):
    """Cria uma nova peça."""
    try:
        return criar_peca(nome, preco_unitario, quantidade_estoque)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{peca_id}", response_model=dict)
def atualizar(peca_id: int, nome: str, preco_unitario: float, quantidade_estoque: int):
    """Atualiza os dados de uma peça."""
    try:
        return atualizar_peca(peca_id, nome, preco_unitario, quantidade_estoque)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e

@router.delete("/{peca_id}", response_model=dict)
def remover(peca_id: int):
    """Remove uma peça (soft delete)."""
    try:
        return remover_peca(peca_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))