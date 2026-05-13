import logging

from fastapi import APIRouter, HTTPException, status

from app.services import orcamento_item_service
from app.schemas.orcamento_item_schema import (
    OrcamentoPecaCreate, OrcamentoPecaUpdate, OrcamentoPecaPublic,
    OrcamentoServicoCreate, OrcamentoServicoUpdate, OrcamentoServicoPublic
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orcamentos/{orcamento_id}/itens", tags=["Itens do Orçamento"])

# Endpoints para Peças
@router.post("/pecas", response_model=OrcamentoPecaPublic, status_code=status.HTTP_201_CREATED)
def add_peca_to_orcamento(orcamento_id: int, data: OrcamentoPecaCreate):
    """Adiciona uma peça ao orçamento."""
    logger.info("POST /orcamentos/%s/itens/pecas peca=%s quantidade=%s", orcamento_id, data.id_peca, data.quantidade)
    item = orcamento_item_service.add_peca_to_orcamento(orcamento_id, data)
    return OrcamentoPecaPublic(
        id_orcamento=item.id_orcamento,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco
    )

@router.get("/pecas", response_model=list[OrcamentoPecaPublic])
def get_pecas_orcamento(orcamento_id: int):
    """Lista todas as peças de um orçamento."""
    logger.info("GET /orcamentos/%s/itens/pecas", orcamento_id)
    itens = orcamento_item_service.get_itens_orcamento(orcamento_id, "peca")
    return [
        OrcamentoPecaPublic(
            id_orcamento=item.id_orcamento,
            id_peca=item.id_peca,
            quantidade=item.quantidade,
            peca_nome=item.peca_nome,
            peca_preco=item.peca_preco
        )
        for item in itens
    ]

@router.put("/pecas/{peca_id}", response_model=OrcamentoPecaPublic)
def update_quantidade_peca(orcamento_id: int, peca_id: int, data: OrcamentoPecaUpdate):
    """Atualiza quantidade de uma peça no orçamento."""
    logger.info("PUT /orcamentos/%s/itens/pecas/%s quantidade=%s", orcamento_id, peca_id, data.quantidade)
    item = orcamento_item_service.update_quantidade_peca(orcamento_id, peca_id, data)
    return OrcamentoPecaPublic(
        id_orcamento=item.id_orcamento,
        id_peca=item.id_peca,
        quantidade=item.quantidade,
        peca_nome=item.peca_nome,
        peca_preco=item.peca_preco
    )

@router.delete("/pecas/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_peca_from_orcamento(orcamento_id: int, peca_id: int):
    """Remove uma peça do orçamento."""
    logger.info("DELETE /orcamentos/%s/itens/pecas/%s", orcamento_id, peca_id)
    orcamento_item_service.remove_peca_from_orcamento(orcamento_id, peca_id)
    return None

# Endpoints para Serviços
@router.post("/servicos", response_model=OrcamentoServicoPublic, status_code=status.HTTP_201_CREATED)
def add_servico_to_orcamento(orcamento_id: int, data: OrcamentoServicoCreate):
    """Adiciona um serviço ao orçamento."""
    logger.info("POST /orcamentos/%s/itens/servicos servico=%s quantidade=%s", orcamento_id, data.id_servico, data.quantidade)
    item = orcamento_item_service.add_servico_to_orcamento(orcamento_id, data)
    return OrcamentoServicoPublic(
        id_orcamento=item.id_orcamento,
        id_servico=item.id_servico,
        quantidade=item.quantidade,
        servico_descricao=item.servico_descricao,
        servico_preco=item.servico_preco
    )

@router.get("/servicos", response_model=list[OrcamentoServicoPublic])
def get_servicos_orcamento(orcamento_id: int):
    """Lista todos os serviços de um orçamento."""
    logger.info("GET /orcamentos/%s/itens/servicos", orcamento_id)
    itens = orcamento_item_service.get_itens_orcamento(orcamento_id, "servico")
    return [
        OrcamentoServicoPublic(
            id_orcamento=item.id_orcamento,
            id_servico=item.id_servico,
            quantidade=item.quantidade,
            servico_descricao=item.servico_descricao,
            servico_preco=item.servico_preco
        )
        for item in itens
    ]

@router.put("/servicos/{servico_id}", response_model=OrcamentoServicoPublic)
def update_quantidade_servico(orcamento_id: int, servico_id: int, data: OrcamentoServicoUpdate):
    """Atualiza quantidade de um serviço no orçamento."""
    logger.info("PUT /orcamentos/%s/itens/servicos/%s quantidade=%s", orcamento_id, servico_id, data.quantidade)
    item = orcamento_item_service.update_quantidade_servico(orcamento_id, servico_id, data)
    return OrcamentoServicoPublic(
        id_orcamento=item.id_orcamento,
        id_servico=item.id_servico,
        quantidade=item.quantidade,
        servico_descricao=item.servico_descricao,
        servico_preco=item.servico_preco
    )

@router.delete("/servicos/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_servico_from_orcamento(orcamento_id: int, servico_id: int):
    """Remove um serviço do orçamento."""
    logger.info("DELETE /orcamentos/%s/itens/servicos/%s", orcamento_id, servico_id)
    orcamento_item_service.remove_servico_from_orcamento(orcamento_id, servico_id)
    return None
