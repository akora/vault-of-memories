"""
Database Manager
Handles SQLite database setup and schema management.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """Manages SQLite database setup and schema operations."""

    def __init__(self):
        self.connection: Optional[sqlite3.Connection] = None
        self.db_path: Optional[Path] = None

    def initialize(self, db_path: Path) -> None:
        """
        Initialize database connection and create schema.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(str(db_path))
        self.connection.execute("PRAGMA journal_mode=WAL")  # Better concurrency
        self.connection.execute("PRAGMA foreign_keys=ON")   # Enforce constraints

        self._create_schema()

    def _create_schema(self) -> None:
        """Create database schema."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS file_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            checksum TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            modification_time REAL NOT NULL,
            created_at REAL NOT NULL DEFAULT (strftime('%s', 'now')),
            status TEXT NOT NULL DEFAULT 'pending'
        );

        CREATE INDEX IF NOT EXISTS idx_checksum ON file_records(checksum);
        CREATE INDEX IF NOT EXISTS idx_status ON file_records(status);
        CREATE INDEX IF NOT EXISTS idx_created_at ON file_records(created_at);
        """

        self.connection.executescript(schema_sql)
        self.connection.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.connection is None:
            raise RuntimeError("Database not initialized")
        return self.connection

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()