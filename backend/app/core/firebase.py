import os
import logging
import firebase_admin
from firebase_admin import credentials, storage

from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def _resolve_bucket_name() -> str | None:
    """Nome do bucket do Firebase Storage.

    Prioriza a configuração explícita (FIREBASE_STORAGE_BUCKET); caso contrário
    deriva do project_id do app inicializado (<project_id>.appspot.com).
    """
    configured = get_settings().firebase_storage_bucket
    if configured:
        return configured
    try:
        app = firebase_admin.get_app()
        project_id = getattr(app, "project_id", None)
        if project_id:
            return f"{project_id}.appspot.com"
    except Exception:
        pass
    return None


def init_firebase():
    """Inicializa o SDK do Firebase Admin usando o arquivo de credencial local."""
    if not firebase_admin._apps:
        try:
            # Caminho esperado do JSON baixado na raiz do /backend/
            cred_path = "firebase-credentials.json"

            options = {}
            bucket_name = get_settings().firebase_storage_bucket
            if bucket_name:
                options["storageBucket"] = bucket_name

            if os.path.exists(cred_path):
                logger.info(f"Inicializando Firebase com arquivo de credencial: {cred_path}")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, options or None)
            else:
                logger.warning(f"Arquivo {cred_path} não encontrado. Tentando inicialização default.")
                firebase_admin.initialize_app(options=options or None)

            logger.info("Firebase Admin inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase Admin: {e}")


def get_bucket():
    """Retorna o bucket do Firebase Storage, ou None se indisponível.

    Usado para persistir imagens de forma durável (compatível com o filesystem
    efêmero do Cloud Run). Se o Firebase/Storage não estiver disponível
    (ex.: ambiente local sem credenciais), retorna None e o chamador usa o
    armazenamento em disco como fallback.
    """
    try:
        if not firebase_admin._apps:
            init_firebase()
        if not firebase_admin._apps:
            return None
        name = _resolve_bucket_name()
        if name:
            return storage.bucket(name)
        return storage.bucket()
    except Exception as e:
        logger.warning("Firebase Storage indisponível: %s", e)
        return None
