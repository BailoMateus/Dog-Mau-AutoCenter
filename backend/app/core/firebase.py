import os
import logging
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger(__name__)

def init_firebase():
    """Inicializa o SDK do Firebase Admin usando o arquivo de credencial local."""
    if not firebase_admin._apps:
        try:
            # Caminho esperado do JSON baixado na raiz do /backend/
            cred_path = "firebase-credentials.json"
            
            if os.path.exists(cred_path):
                logger.info(f"Inicializando Firebase com arquivo de credencial: {cred_path}")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                logger.warning(f"Arquivo {cred_path} não encontrado. Tentando inicialização default.")
                firebase_admin.initialize_app()
                
            logger.info("Firebase Admin inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase Admin: {e}")
