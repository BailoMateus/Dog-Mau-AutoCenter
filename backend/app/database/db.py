"""
Módulo de conexão com banco de dados usando psycopg2 (PostgreSQL).
Substitui completamente o SQLAlchemy.
"""
import logging
import os
import urllib.parse
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor

from app.core.settings import get_settings

logger = logging.getLogger(__name__)

_settings = get_settings()

# Construção da URL de conexão PostgreSQL (sem SQLAlchemy)
def _get_connection_string() -> str:
    """Retorna a string de conexão PostgreSQL."""
    safe_password = urllib.parse.quote_plus(_settings.db_pass)
    
    if _settings.database_url:
        # Remove o prefixo 'postgresql+psycopg2://' se existir
        db_url = _settings.database_url.replace('postgresql+psycopg2://', 'postgresql://')
        logger.info("Conexão PostgreSQL: usando DATABASE_URL (override)")
        return db_url
    elif _settings.instance_connection_name != "conexao_vazia":
        # Conexão Cloud SQL via socket Unix
        conn_str = (
            f"postgresql://{_settings.db_user}:{safe_password}@/{_settings.db_name}?"
            f"host=/cloudsql/{_settings.instance_connection_name}"
        )
        logger.info("Conexão PostgreSQL: modo Cloud SQL (socket Unix)")
        return conn_str
    else:
        # Conexão local padrão
        conn_str = f"postgresql://{_settings.db_user}:{safe_password}@localhost/{_settings.db_name}"
        logger.info("Conexão PostgreSQL: modo local")
        return conn_str

@contextmanager
def get_db_connection():
    """
    Context manager para obter uma conexão com o banco de dados.
    Garante commit/rollback e fechamento da conexão.
    """
    conn = None
    try:
        conn = psycopg2.connect(_get_connection_string())
        conn.autocommit = False
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro de banco de dados: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Conexão com banco fechada")

def execute_query(query: str, params: Optional[Tuple] = None, fetch: str = "all") -> List[Dict[str, Any]]:
    """
    Executa uma query SELECT e retorna os resultados.
    
    Args:
        query: Query SQL com placeholders %s
        params: Tupla de parâmetros para a query
        fetch: 'all' para retornar todos os resultados, 'one' para um resultado
        
    Returns:
        Lista de dicionários com os resultados
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            if fetch == "one":
                result = cur.fetchone()
                return dict(result) if result else None
            elif fetch == "all":
                results = cur.fetchall()
                return [dict(row) for row in results]
            else:
                raise ValueError("Parâmetro fetch deve ser 'all' ou 'one'")

def execute_command(query: str, params: Optional[Tuple] = None) -> int:
    """
    Executa uma query INSERT, UPDATE ou DELETE.
    
    Args:
        query: Query SQL com placeholders %s
        params: Tupla de parâmetros para a query
        
    Returns:
        Número de linhas afetadas
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.rowcount

def execute_insert(query: str, params: Optional[Tuple] = None) -> int:
    """
    Executa uma query INSERT e retorna o ID gerado.
    
    Args:
        query: Query SQL INSERT com placeholders %s
        params: Tupla de parâmetros para a query
        
    Returns:
        ID do registro inserido
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if cur.lastrowid:
                return cur.lastrowid
            else:
                # Para PostgreSQL, usar RETURNING id
                cur.execute("SELECT lastval()")
                return cur.fetchone()[0]

def execute_batch(query: str, params_list: List[Tuple]) -> int:
    """
    Executa múltiplas queries em batch (performance).
    
    Args:
        query: Query SQL com placeholders %s
        params_list: Lista de tuplas de parâmetros
        
    Returns:
        Número total de linhas afetadas
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, query, params_list)
            return cur.rowcount

# Função de compatibilidade para FastAPI (substitui get_db do SQLAlchemy)
def get_db():
    """
    Dependency function para FastAPI.
    Substitui a função get_db do SQLAlchemy.
    """
    with get_db_connection() as conn:
        yield conn
