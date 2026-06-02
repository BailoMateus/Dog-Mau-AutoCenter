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
from app.core.file_storage import normalize_stored_image_url
from app.repositories import produto_repository as produto_repo
from app.repositories import servico_repository as servico_repo
from app.services import produto_service
from app.services import servico_service
from app.services import pedido_service
from app.services import veiculo_service
from app.services import modelo_service
from app.services import marca_service

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
    e retorna {user_id, role, nome, avatar}. Se inválido ou ausente, retorna None.
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
            "SELECT id_usuario, nome, role, foto_perfil FROM usuario WHERE id_usuario = %s AND deleted_at IS NULL",
            (int(user_id),),
            fetch="one",
        )
        if not user:
            return None
        avatar = normalize_stored_image_url(user.get("foto_perfil")) if user.get("foto_perfil") else None
        return {
            "user_id": user_id,
            "role": payload.get("role"),
            "nome": user["nome"],
            "avatar": avatar,
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Rotas de páginas
# ---------------------------------------------------------------------------

@router.get("/", include_in_schema=False)
def home_page(request: Request, user=Depends(get_page_user)):
    """Página inicial — pública, mostra header logado/deslogado e destaques."""
    todos_servicos = servico_service.list_servicos()
    todos_produtos = produto_service.list_produtos()
    
    # Pegar apenas os 3 primeiros para destaque na Home
    servicos_destaque = todos_servicos[:3]
    produtos_destaque = todos_produtos[:3]

    return templates.TemplateResponse("pages/index.html", {
        "request": request,
        "user": user,
        "page": "home",
        "servicos_destaque": servicos_destaque,
        "produtos_destaque": produtos_destaque,
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
    servicos = servico_service.list_servicos()
    marcas = marca_service.list_marcas()
    modelos = modelo_service.list_modelos()
    
    # We map modelos by marca to easily build the frontend select
    modelos_por_marca = {}
    for mod in modelos:
        if mod.id_marca not in modelos_por_marca:
            modelos_por_marca[mod.id_marca] = []
        modelos_por_marca[mod.id_marca].append({
            "id": mod.id_modelo,
            "nome": mod.nome_modelo
        })
    
    return templates.TemplateResponse("pages/services.html", {
        "request": request,
        "user": user,
        "page": "servicos",
        "servicos": servicos,
        "marcas": marcas,
        "modelos_por_marca": modelos_por_marca,
    })


@router.get("/produtos", include_in_schema=False)
@router.get("/loja", include_in_schema=False)
def loja_page(request: Request, user=Depends(get_page_user)):
    """Página pública de e-commerce (Loja de Produtos)."""
    produtos = produto_service.list_produtos()
    pedidos = []

    return templates.TemplateResponse("pages/loja.html", {
        "request": request,
        "user": user,
        "produtos": produtos,
        "pedidos": pedidos,
        "page": "produtos",
    })


@router.get("/api/busca", include_in_schema=False)
def busca_global(q: str = ""):
    """Busca pública de produtos e serviços (autocomplete parcial)."""
    term = (q or "").strip()
    if len(term) < 1:
        return {"produtos": [], "servicos": []}

    produtos = produto_repo.buscar_produtos(term, limit=8)
    servicos = servico_repo.buscar_servicos(term, limit=8)

    produtos_out = []
    for p in produtos:
        img = normalize_stored_image_url(getattr(p, "imagem_produto", None))
        produtos_out.append({
            "id": p.id_produto,
            "nome": p.nome or "",
            "descricao": p.descricao or "",
            "preco": float(p.preco or 0),
            "imagem": img,
            "tipo": "produto",
        })

    servicos_out = []
    for s in servicos:
        nome = (getattr(s, "nome_servico", None) or s.descricao or "").strip()
        servicos_out.append({
            "id": s.id_servico,
            "nome": nome,
            "preco": float(s.preco or 0),
            "tipo": "servico",
        })

    return {"produtos": produtos_out, "servicos": servicos_out}


@router.get("/logout", include_in_schema=False)
def logout(request: Request):
    """Limpa o cookie de autenticação e redireciona para a home."""
    logger.info("GET /logout — limpando cookie")
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("__session")
    response.delete_cookie("access_token") # Por segurança, limpa o antigo também
    return response

@router.get("/checkout", include_in_schema=False)
def checkout_page(request: Request, user=Depends(get_page_user)):
    """Página de checkout — requer autenticação (cliente)."""
    if not user:
        return RedirectResponse(url="/login?next=/checkout", status_code=302)

    # Busca email e telefone para preenchimento automático do formulário
    user_extra = execute_query(
        "SELECT email, telefone FROM usuario WHERE id_usuario = %s AND deleted_at IS NULL",
        (int(user["user_id"]),),
        fetch="one",
    )
    user_email = user_extra["email"] if user_extra else ""
    user_phone = user_extra.get("telefone", "") if user_extra else ""

    return templates.TemplateResponse("pages/checkout.html", {
        "request": request,
        "user": user,
        "user_email": user_email,
        "user_phone": user_phone or "",
        "page": "checkout",
    })


@router.get("/painel", include_in_schema=False)
def painel_page(request: Request, tab: str = None, user=Depends(get_page_user)):
    """Painel unificado — requer autenticação.

    Admin/Mecânico veem abas de gestão (Usuários, Produtos, OS).
    Cliente vê sua própria área (Meus Pedidos, Minhas OS).
    """
    try:
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        # Define a aba padrão conforme o role
        if not tab:
            tab = "usuarios" if user.get("role") in ("admin", "mecanico") else "meu_usuario"

        # Carrega dados apenas para roles que precisam
        usuarios = []
        servicos = []
        produtos = []
        marcas = []
        if user.get("role") in ("admin", "mecanico"):
            usuarios = list_users()
            servicos = servico_service.list_servicos()
            produtos = produto_service.list_produtos()
            marcas = marca_service.list_marcas()

        # Pedidos
        if user.get("role") in ("admin", "mecanico"):
            pedidos_db = pedido_service.list_pedidos_detalhados()
        else:
            pedidos_db = pedido_service.get_pedidos_detalhados_by_usuario(int(user["user_id"]))
            
        pedidos = []
        for p in pedidos_db:
            if isinstance(p, dict):
                id_pedido = p.get('id_pedido')
                created_at = p.get('created_at')
                valor_total = p.get('valor_total')
                status = p.get('status')
                itens = p.get('itens', [])
                usuario_nome = p.get('usuario_nome')
            else:
                id_pedido = p.id_pedido
                created_at = p.created_at
                valor_total = p.valor_total
                status = p.status
                itens = getattr(p, 'itens', [])
                usuario_nome = getattr(p, 'usuario_nome', None)
                
            qtd_itens = sum(i.quantidade for i in itens) if itens else 0
            
            pedidos.append({
                "id_pedido": id_pedido,
                "data_pedido": created_at.strftime('%Y-%m-%d') if created_at else "",
                "valor_total": valor_total,
                "status": status,
                "qtd_itens": qtd_itens,
                "itens": itens,
                "usuario_nome": usuario_nome
            })

        # Veículos (Admin vê todos com nome do proprietário, cliente vê os seus)
        if user.get("role") in ("admin", "mecanico"):
            veiculos = execute_query(
                "SELECT v.id_veiculo, v.placa, v.ano_fabricacao, v.cor, v.id_usuario, v.id_modelo, "
                "u.nome AS proprietario_nome "
                "FROM veiculo v "
                "JOIN usuario u ON v.id_usuario = u.id_usuario "
                "WHERE v.deleted_at IS NULL "
                "ORDER BY v.created_at DESC",
                fetch="all",
            ) or []
        else:
            veiculos = veiculo_service.list_veiculos_by_user(int(user["user_id"]))
            
        modelos = modelo_service.list_modelos()

        orcamentos = []
        ordens_servico = []
        mecanicos = []

        if user.get("role") == "admin":
            orcamentos = execute_query(
                "SELECT o.*, v.placa, m.nome_modelo, u.nome as usuario_nome FROM orcamento o "
                "JOIN veiculo v ON o.id_veiculo = v.id_veiculo "
                "JOIN modelo m ON v.id_modelo = m.id_modelo "
                "JOIN usuario u ON o.id_usuario = u.id_usuario "
                "WHERE o.deleted_at IS NULL ORDER BY o.created_at DESC", fetch="all"
            )
            ordens_servico = execute_query(
                "SELECT os.*, o.valor_total, v.placa, m.nome_modelo, u.nome as cliente_nome, mec.nome as mecanico_nome "
                "FROM ordem_servico os "
                "JOIN orcamento o ON os.id_orcamento = o.id_orcamento "
                "JOIN veiculo v ON o.id_veiculo = v.id_veiculo "
                "JOIN modelo m ON v.id_modelo = m.id_modelo "
                "JOIN usuario u ON o.id_usuario = u.id_usuario "
                "LEFT JOIN usuario mec ON os.id_usuario = mec.id_usuario "
                "WHERE os.deleted_at IS NULL ORDER BY os.created_at DESC", fetch="all"
            )
            mecanicos = execute_query("SELECT id_usuario, nome FROM usuario WHERE role = 'mecanico' AND deleted_at IS NULL", fetch="all")
        elif user.get("role") == "mecanico":
            ordens_servico = execute_query(
                "SELECT os.*, o.valor_total, v.placa, m.nome_modelo, u.nome as cliente_nome "
                "FROM ordem_servico os "
                "JOIN orcamento o ON os.id_orcamento = o.id_orcamento "
                "JOIN veiculo v ON o.id_veiculo = v.id_veiculo "
                "JOIN modelo m ON v.id_modelo = m.id_modelo "
                "JOIN usuario u ON o.id_usuario = u.id_usuario "
                "WHERE os.deleted_at IS NULL AND os.id_usuario = %s ORDER BY os.created_at DESC", 
                (int(user["user_id"]),), fetch="all"
            )
        else: # Cliente
            orcamentos = execute_query(
                "SELECT o.*, v.placa, m.nome_modelo FROM orcamento o "
                "JOIN veiculo v ON o.id_veiculo = v.id_veiculo "
                "JOIN modelo m ON v.id_modelo = m.id_modelo "
                "WHERE o.deleted_at IS NULL AND o.id_usuario = %s ORDER BY o.created_at DESC", 
                (int(user["user_id"]),), fetch="all"
            )
            ordens_servico = execute_query(
                "SELECT os.*, o.valor_total, v.placa, m.nome_modelo "
                "FROM ordem_servico os "
                "JOIN orcamento o ON os.id_orcamento = o.id_orcamento "
                "JOIN veiculo v ON o.id_veiculo = v.id_veiculo "
                "JOIN modelo m ON v.id_modelo = m.id_modelo "
                "WHERE os.deleted_at IS NULL AND o.id_usuario = %s ORDER BY os.created_at DESC", 
                (int(user["user_id"]),), fetch="all"
            )

        return templates.TemplateResponse("pages/painel.html", {
            "request": request,
            "user": user,
            "usuarios": usuarios,
            "servicos": servicos,
            "produtos": produtos,
            "pedidos": pedidos,
            "veiculos": veiculos,
            "modelos": modelos,
            "marcas": marcas,
            "orcamentos": orcamentos,
            "ordens_servico": ordens_servico,
            "mecanicos": mecanicos,
            "tab": tab,
            "page": "painel",
        })
    except Exception as e:
        import traceback
        logger.error("Error in painel_page: %s", traceback.format_exc())
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": traceback.format_exc()}
        )



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


@router.get("/relatorios", include_in_schema=False)
def relatorios_page(request: Request, user=Depends(get_page_user)):
    """Página de relatórios executivos — apenas para ADMIN."""
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("pages/relatorios.html", {
        "request": request,
        "user": user,
        "page": "relatorios",
    })


@router.get("/movimentacoes-estoque", include_in_schema=False)
def movimentacoes_estoque_page(request: Request, user=Depends(get_page_user)):
    """Página de movimentações de estoque — Admin/Mecânico."""
    if not user or user.get("role") not in ("admin", "mecanico"):
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("pages/movimentacoes_estoque.html", {
        "request": request,
        "user": user,
        "page": "movimentacoes_estoque",
    })


@router.get("/movimentacoes-financeiras", include_in_schema=False)
def movimentacoes_financeiras_page(request: Request, user=Depends(get_page_user)):
    """Página de movimentações financeiras — apenas para ADMIN."""
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/", status_code=302)
    
    return templates.TemplateResponse("pages/movimentacoes_financeiras.html", {
        "request": request,
        "user": user,
        "page": "movimentacoes_financeiras",
    })


@router.get("/ordem-servico/{os_id}", include_in_schema=False)
def ordem_servico_detail_page(request: Request, os_id: int, user=Depends(get_page_user)):
    """Página de detalhes de uma ordem de serviço."""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("pages/ordem_servico_detail.html", {
        "request": request,
        "user": user,
        "os_id": os_id,
        "page": "ordem_servico",
    })
