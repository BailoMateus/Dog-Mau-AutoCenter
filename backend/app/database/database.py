import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Coleta das variáveis (com proteção para valores nulos)
DB_USER = os.getenv("DB_USER", "usuario_vazio")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "banco_vazio")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME", "conexao_vazia")


safe_password = urllib.parse.quote_plus(DB_PASS)


if INSTANCE_CONNECTION_NAME != "conexao_vazia":
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{safe_password}@/{DB_NAME}?"
        f"host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
    )
else:
    
    SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
