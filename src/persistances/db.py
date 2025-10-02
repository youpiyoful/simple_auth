"""Database connection with simple connection pooling."""

import os
import threading
from contextlib import contextmanager

import psycopg2
from psycopg2 import extras, pool

from src.config.settings import get_settings


def get_database_url() -> str:
    """Get database URL from centralized application settings."""
    settings = get_settings()
    db = settings.database_settings
    # db is populated in AppSettings.from_env, but add a safe fallback
    if db is None:
        # Late load from env to avoid None
        from src.config.settings import DatabaseSettings

        db = DatabaseSettings(
            user=os.getenv("DB_USER", "app"),
            password=os.getenv("DB_PASS", "secret"),
            name=os.getenv("DB_NAME", "appdb"),
            host=os.getenv("DB_HOST", "db"),
            port=int(os.getenv("DB_PORT", "5432")),
        )
    return db.url


class SimpleConnectionPool:
    """Simple singleton connection pool - best of both worlds."""

    _instance = None  # Singleton instance
    _lock = threading.Lock()  # To ensure thread-safe singleton

    # Create the singleton instance
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # Initialize the connection pool
    def __init__(self) -> None:
        if hasattr(self, "_pool"):
            return  # Already initialized

        try:
            self._pool = pool.ThreadedConnectionPool(
                minconn=1,  # Minimum: 1 connection
                maxconn=5,  # Maximum: 5 connections (sufficient for testing)
                dsn=get_database_url(),
                cursor_factory=extras.RealDictCursor,
            )
        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to create connection pool: {e}") from e

    def get_connection(self):
        """Get a connection from the pool."""
        return self._pool.getconn()

    def put_connection(self, conn) -> None:
        """Return a connection to the pool."""
        self._pool.putconn(conn=conn)

    def close_all(self) -> None:
        """Close all connections (for shutdown)."""
        if hasattr(self, "_pool"):
            self._pool.closeall()


# Global pool instance
_pool = SimpleConnectionPool()


@contextmanager
def get_db_cursor():  # -> Generator[Any, Any, None]:
    """Get a database cursor with connection pooling.

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()  # Returns list of dicts
    """
    conn = None
    try:
        # Get connection from pool (singleton)
        conn = _pool.get_connection()
        cursor = conn.cursor()

        yield cursor

        # Auto-commit successful operations
        conn.commit()

    except Exception:
        # Auto-rollback on error
        if conn:
            conn.rollback()
        raise
    finally:
        # Return connection to pool (pas fermée, réutilisée!)
        if conn:
            _pool.put_connection(conn)
