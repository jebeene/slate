# tests/test_tools.py
import os
import tempfile
import sqlite3
import pytest
from mcp_slate.db import get_conn, init_db
from mcp_slate.tools import _add_ticket, _list_tables

@pytest.fixture(autouse=True)
def db_env(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    
    # Initialize database using the schema file
    init_db(str(db))
    
    monkeypatch.setenv("SQLITE_DB", str(db))

def test_add_and_list():
    _add_ticket(project_id="test-project", title="Test Ticket")
    tables = _list_tables()
    assert "tickets" in tables
    assert "todos" in tables