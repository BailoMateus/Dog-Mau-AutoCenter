import os

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY deve ser configurada nas variáveis de ambiente")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60