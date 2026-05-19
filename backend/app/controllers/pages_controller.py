"""
Controller para páginas públicas de produtos e checkout
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import os

router = APIRouter(tags=["Pages"])

# Setup Jinja2 environment
templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
env = Environment(loader=FileSystemLoader(templates_dir))


@router.get("/produtos", response_class=HTMLResponse)
async def produtos_page():
    """Página de catálogo de produtos"""
    template = env.get_template("pages/produtos.html")
    return template.render(page="produtos")


@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page():
    """Página de checkout"""
    template = env.get_template("pages/checkout.html")
    return template.render(page="checkout")
