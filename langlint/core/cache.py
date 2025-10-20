"""
Caching system for LangLint.

This module provides caching functionality for parse results and translations
to improve performance and reduce API calls.
"""

import json
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class CacheEntry:
    """A cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl <= 0:  # No expiration
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self) -> None:
        """Update access information."""
        self.access_count += 1
        self.last_accessed = time.time()


class Cache:
    """
    SQLite-based cache for LangLint.

    This cache stores parse results and translations to improve performance
    and reduce external API calls.
    """

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        max_size: int = 1000,
        default_ttl: int = 3600
    ):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache database
            max_size: Maximum number of entries to store
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".langlint" / "cache"
        else:
            cache_dir = Path(cache_dir)

        cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / "langlint_cache.db"
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise CacheError(f"Database error: {e}") from e
        finally:
            if conn:
                conn.close()

    def _serialize_value(self, value: Any) -> str:
        """Serialize a value for storage."""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            raise CacheError(f"Cannot serialize value: {e}") from e

    def _deserialize_value(self, value_str: str) -> Any:
        """Deserialize a value from storage."""
        try:
            return json.loads(value_str)
        except (TypeError, ValueError) as e:
            raise CacheError(f"Cannot deserialize value: {e}") from e

    def _generate_key(self, *args: Any) -> str:
        """Generate a cache key from arguments."""
        key_data = "|".join(str(arg) for arg in args)
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cache_entries WHERE key = ?", (key,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            entry = CacheEntry(
                key=row['key'],
                value=self._deserialize_value(row['value']),
                created_at=row['created_at'],
                ttl=row['ttl'],
                access_count=row['access_count'],
                last_accessed=row['last_accessed']
            )

            if entry.is_expired():
                # Remove expired entry
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                return None

            # Update access information
            entry.touch()
            conn.execute(
                "UPDATE cache_entries SET access_count = ?, last_accessed = ? WHERE key = ?",
                (entry.access_count, entry.last_accessed, key)
            )

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl

        with self._get_connection() as conn:
            # Check if we need to evict entries
            self._evict_if_needed(conn)

            # Insert or update the entry
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries
                (key, value, created_at, ttl, access_count, last_accessed)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (
                key,
                self._serialize_value(value),
                time.time(),
                ttl,
                time.time()
            ))

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if the key was found and deleted, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            return cursor.rowcount > 0

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM cache_entries")

    def _evict_if_needed(self, conn: sqlite3.Connection) -> None:
        """Evict entries if the cache is full."""
        # Count current entries
        cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
        count = cursor.fetchone()[0]

        if count >= self.max_size:
            # Remove oldest entries (least recently accessed)
            to_remove = count - self.max_size + 1
            conn.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY last_accessed ASC
                    LIMIT ?
                )
            """, (to_remove,))

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from the cache.

        Returns:
            Number of entries removed
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM cache_entries
                WHERE created_at + ttl < ?
            """, (time.time(),))
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            total_entries = cursor.fetchone()[0]

            cursor = conn.execute("""
                SELECT COUNT(*) FROM cache_entries
                WHERE created_at + ttl < ?
            """, (time.time(),))
            expired_entries = cursor.fetchone()[0]

            cursor = conn.execute("""
                SELECT AVG(access_count), MAX(access_count), MIN(access_count)
                FROM cache_entries
            """)
            stats = cursor.fetchone()
            avg_access, max_access, min_access = stats

            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'max_size': self.max_size,
                'utilization': total_entries / self.max_size if self.max_size > 0 else 0,
                'avg_access_count': avg_access or 0,
                'max_access_count': max_access or 0,
                'min_access_count': min_access or 0,
            }

    def close(self) -> None:
        """Close the cache and clean up resources."""
        # SQLite connections are closed automatically in the context manager
        pass


class CacheError(Exception):
    """Exception raised for cache-related errors."""
    pass
