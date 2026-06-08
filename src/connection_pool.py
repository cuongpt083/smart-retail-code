"""
SQLite Connection Pool - Manage database connections efficiently

Implements:
- Maximum concurrent connections (default 2 for SQLite)
- WAL mode for better concurrency
- Connection timeout and reuse
- Automatic cleanup
"""

import sqlite3
import queue
import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ConnectionPoolExhausted(Exception):
    """Raised when connection pool is exhausted"""
    pass


class SQLiteConnectionPool:
    """
    SQLite connection pool with WAL mode support

    Features:
    - Max 2 concurrent connections (SQLite limitation)
    - WAL mode for concurrent read/write
    - Connection timeout
    - Thread-safe operations
    """

    def __init__(
        self,
        db_path: str,
        max_connections: int = 2,
        timeout: float = 5.0,
        check_same_thread: bool = False
    ):
        """
        Initialize connection pool

        Args:
            db_path: Path to SQLite database
            max_connections: Max concurrent connections (2 for SQLite)
            timeout: Connection acquisition timeout in seconds
            check_same_thread: SQLite thread safety check
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.check_same_thread = check_same_thread

        # Connection pool queue
        self.available = queue.Queue(maxsize=max_connections)
        self.connections = []
        self.lock = threading.Lock()

        # Initialize pool
        self._init_pool()

        logger.info(
            f"Connection pool initialized: max={max_connections}, "
            f"timeout={timeout}s, db={db_path}"
        )

    def _init_pool(self):
        """Create initial connections"""
        for _ in range(self.max_connections):
            conn = self._create_connection()
            self.connections.append(conn)
            self.available.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """Create and configure SQLite connection"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=self.check_same_thread
        )

        # Enable WAL mode for concurrent access
        conn.execute("PRAGMA journal_mode=WAL")

        # Set reasonable timeouts
        conn.execute("PRAGMA busy_timeout=5000")  # 5 second timeout

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")

        return conn

    def get_connection(self, timeout: Optional[float] = None) -> sqlite3.Connection:
        """
        Get connection from pool

        Args:
            timeout: Override default timeout (seconds)

        Returns:
            SQLite connection

        Raises:
            ConnectionPoolExhausted: If no connection available
        """
        timeout = timeout or self.timeout

        try:
            conn = self.available.get(timeout=timeout)
            logger.debug("Connection acquired from pool")
            return conn
        except queue.Empty:
            logger.error(f"Connection pool exhausted (timeout={timeout}s)")
            raise ConnectionPoolExhausted(
                f"No connections available (timeout={timeout}s)"
            )

    def return_connection(self, conn: sqlite3.Connection):
        """
        Return connection to pool for reuse

        Args:
            conn: SQLite connection to return
        """
        if conn and conn in self.connections:
            self.available.put(conn)
            logger.debug("Connection returned to pool")

    def close_all(self):
        """Close all connections in pool"""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
        logger.info("All connections closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()


# Global pool instance
_pool = None

def init_pool(db_path: str = "retail.db", max_conn: int = 2) -> SQLiteConnectionPool:
    """Initialize global connection pool"""
    global _pool
    if _pool is None:
        _pool = SQLiteConnectionPool(db_path, max_connections=max_conn)
    return _pool

def get_pool() -> SQLiteConnectionPool:
    """Get global connection pool"""
    global _pool
    if _pool is None:
        _pool = init_pool()
    return _pool
