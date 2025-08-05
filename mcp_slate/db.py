# mcp_slate/db.py
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

def _get_db_path():
    return os.getenv("SQLITE_DB")

def _get_schema_path():
    """Get the path to the schema.sql file"""
    return Path(__file__).parent / "schema.sql"

def init_db(db_path: str):
    """Initialize database with schema"""
    schema_path = _get_schema_path()
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with sqlite3.connect(db_path) as conn:
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        # Set busy timeout
        conn.execute("PRAGMA busy_timeout = 5000")
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()

@contextmanager
def get_conn():
    db_path = _get_db_path()
    if not db_path:
        raise RuntimeError("Environment variable SQLITE_DB is not set")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode = WAL")
    # Set busy timeout
    conn.execute("PRAGMA busy_timeout = 5000")
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()