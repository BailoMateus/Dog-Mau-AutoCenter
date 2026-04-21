import logging
import os
import time

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.settings import get_settings

_settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if _settings.debug_log else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

from app.controllers.auth_controller import router as auth_router
from app.controllers.me_controller import router as me_router
from app.controllers.user_controller import router as users_router
from app.controllers.endereco_controller import router as enderecos_router
from app.controllers.marca_controller import router as marcas_router
from app.controllers.modelo_controller import router as modelos_router
from app.controllers.veiculo_controller import router as veiculos_router
from app.controllers.servico_controller import router as servicos_router
from app.core.roles import ADMIN
from app.core.security import require_role
from app.database.database import get_db

app = FastAPI(title="Dog Mau AutoCenter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(me_router)
app.include_router(enderecos_router)
app.include_router(marcas_router)
app.include_router(modelos_router)
app.include_router(veiculos_router)
app.include_router(servicos_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("%s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
    except Exception:
        logger.exception("erro ao processar %s %s", request.method, request.url.path)
        raise

@app.on_event("startup")
async def on_startup():
    from app.core.firebase import init_firebase
    init_firebase()
    logger.info("API iniciada (FastAPI) e Firebase Configurado!")


@app.get("/testar-banco")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("testar-banco: SELECT 1 ok")
        return {"status": "Sucesso", "mensagem": "Conectado ao Cloud SQL!"}
    except Exception as e:
        logger.exception("testar-banco falhou")
        return {"status": "Erro", "detalhes": str(e)}

@app.get("/")
def root():
    return {"message": "Dog Mau AutoCenter API - Backend", "status": "Online"}

@app.get("/saude")
def health_check():
    return {"message": "API Online"}

@app.get("/admin/ping")
def admin_only(_=Depends(require_role([ADMIN]))):
    """Exemplo de rota só para role admin (autorização por papel)."""
    logger.info("GET /admin/ping autorizado (admin)")
    return {"ok": True, "scope": "admin"}

if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    import traceback

    port = int(os.environ.get("PORT", 8080))
    try:
        # Passar o objeto 'app' diretamente (e não a string) evita que o uvicorn faça 
        # recarregamentos dinâmicos que quebram o path no Docker/Cloud Run
        uvicorn.run(app, host="0.0.0.0", port=port)
    except BaseException as e:
        print(f"=== STARTUP CRASH: {type(e).__name__} ===", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.stderr.flush()
        sys.exit(1)
