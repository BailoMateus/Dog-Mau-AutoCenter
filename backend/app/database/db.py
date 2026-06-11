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

def _get_connection_string() -> str:
    if _settings.database_url:
        return _settings.database_url.replace(
            "postgresql+psycopg2://",
            "postgresql://"
        )
    return "postgresql://postgres:password@localhost:5432/dogmau"


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
    Executa uma query INSERT com RETURNING e retorna o ID gerado.
    
    A query DEVE conter uma cláusula RETURNING (ex: RETURNING id_usuario).
    Usa fetchone() no mesmo cursor para ler o valor retornado.
    
    Args:
        query: Query SQL INSERT com placeholders %s e cláusula RETURNING
        params: Tupla de parâmetros para a query
        
    Returns:
        ID do registro inserido
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            row = cur.fetchone()
            if row:
                return row[0]
            raise RuntimeError("INSERT não retornou ID. Verifique a cláusula RETURNING na query.")

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
