import logging
import os
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_s = get_settings()

safe_password = urllib.parse.quote_plus(_s.db_pass)

if _s.database_url:
    SQLALCHEMY_DATABASE_URL = _s.database_url
    logger.info("engine PostgreSQL: usando DATABASE_URL (override)")
elif _s.instance_connection_name != "conexao_vazia":
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{_s.db_user}:{safe_password}@/{_s.db_name}?"
        f"host=/cloudsql/{_s.instance_connection_name}"
    )
    logger.info("engine PostgreSQL: modo Cloud SQL (socket Unix no Cloud Run)")
else:
    SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/db"
    logger.info(
        "engine PostgreSQL: URL local padrão — defina INSTANCE_CONNECTION_NAME "
        "(Cloud Run) ou DATABASE_URL (dev com proxy/tunel)"
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("sessão DB fechada")
