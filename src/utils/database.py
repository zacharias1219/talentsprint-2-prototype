"""
Database connection and utility module.

Provides database connection pooling and utility functions for PostgreSQL.
"""

from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Global connection pool
_connection_pool: Optional[pool.SimpleConnectionPool] = None


def init_connection_pool() -> None:
    """Initialize database connection pool."""
    global _connection_pool

    if _connection_pool is not None:
        return

    config = get_config()
    db_url = config.get("database.url")

    try:
        # Parse database URL or use individual config values
        if db_url:
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,
                config.get("database.pool_size", 10),
                dsn=db_url,
            )
        else:
            # Use individual config values if URL not provided
            _connection_pool = psycopg2.pool.SimpleConnectionPool(
                1,
                config.get("database.pool_size", 10),
                host=config.get("database.host", "localhost"),
                port=config.get("database.port", 5432),
                database=config.get("database.name", "financial_advisor"),
                user=config.get("database.user"),
                password=config.get("database.password"),
            )

        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}")
        raise


def get_connection_pool() -> pool.SimpleConnectionPool:
    """
    Get database connection pool.

    Returns:
        Connection pool instance.
    """
    global _connection_pool

    if _connection_pool is None:
        init_connection_pool()

    return _connection_pool


@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Get a database connection from the pool.

    Yields:
        Database connection.

    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    pool = get_connection_pool()
    conn = pool.getconn()

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        pool.putconn(conn)


def execute_query(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
    fetch_one: bool = False,
    fetch_all: bool = True,
) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a database query.

    Args:
        query: SQL query string.
        params: Query parameters for parameterized queries.
        fetch_one: If True, fetch only one row.
        fetch_all: If True, fetch all rows.

    Returns:
        Query results as list of dictionaries, or None if no results.
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)

            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                return None


def execute_update(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """
    Execute an UPDATE, INSERT, or DELETE query.

    Args:
        query: SQL query string.
        params: Query parameters for parameterized queries.

    Returns:
        Number of affected rows.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount


def close_connection_pool() -> None:
    """Close all database connections in the pool."""
    global _connection_pool

    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Database connection pool closed")

