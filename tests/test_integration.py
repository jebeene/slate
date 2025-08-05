"""
Integration tests for validation with database operations.
"""

import os
import tempfile
import pytest
from mcp_slate.db import get_conn, init_db
from mcp_slate.tools import _add_ticket, _add_todo, _get_ticket, _list_todos
from mcp_slate.validation import TicketCreate, TodoCreate


@pytest.fixture(autouse=True)
def db_env(tmp_path, monkeypatch):
    """Set up test database."""
    db = tmp_path / "test.db"
    init_db(str(db))
    monkeypatch.setenv("SQLITE_DB", str(db))


def test_add_ticket_with_validation():
    """Test that ticket creation works with validation."""
    result = _add_ticket(
        project_id="test-project",
        title="Test Ticket",
        description="Test description",
        status="open",
        priority="high"
    )
    assert "id" in result
    assert result["id"] > 0


def test_add_ticket_with_invalid_data():
    """Test that invalid data is caught by validation."""
    with pytest.raises(ValueError):
        _add_ticket(
            project_id="",  # Empty project_id should fail
            title="Test Ticket"
        )


def test_add_todo_with_validation():
    """Test that todo creation works with validation."""
    # First create a ticket
    ticket_result = _add_ticket(
        project_id="test-project",
        title="Test Ticket"
    )
    
    # Then create a todo
    todo_result = _add_todo(
        ticket_id=ticket_result["id"],
        description="Test todo",
        status="pending",
        due_date="2024-01-20"
    )
    assert "id" in todo_result
    assert todo_result["id"] > 0


def test_add_todo_with_invalid_date():
    """Test that invalid date format is caught."""
    # First create a ticket
    ticket_result = _add_ticket(
        project_id="test-project",
        title="Test Ticket"
    )
    
    # Try to create a todo with invalid date
    with pytest.raises(ValueError, match="due_date must be in ISO 8601 format"):
        _add_todo(
            ticket_id=ticket_result["id"],
            description="Test todo",
            due_date="20-01-2024"  # Invalid format
        )


def test_get_ticket_with_validation():
    """Test that ticket retrieval includes validation."""
    # Create a ticket
    ticket_result = _add_ticket(
        project_id="test-project",
        title="Test Ticket",
        description="Test description",
        status="in-progress",
        priority="medium"
    )
    
    # Retrieve the ticket
    ticket = _get_ticket(ticket_result["id"])
    assert ticket is not None
    assert ticket["project_id"] == "test-project"
    assert ticket["title"] == "Test Ticket"
    assert ticket["status"] == "in-progress"
    assert ticket["priority"] == "medium"


def test_list_todos_with_validation():
    """Test that todo listing includes validation."""
    # Create a ticket
    ticket_result = _add_ticket(
        project_id="test-project",
        title="Test Ticket"
    )
    
    # Create multiple todos
    _add_todo(
        ticket_id=ticket_result["id"],
        description="Todo 1",
        status="pending"
    )
    _add_todo(
        ticket_id=ticket_result["id"],
        description="Todo 2",
        status="done"
    )
    
    # List todos
    todos = _list_todos(ticket_result["id"])
    assert len(todos) == 2
    assert todos[0]["description"] == "Todo 1"
    assert todos[0]["status"] == "pending"
    assert todos[1]["description"] == "Todo 2"
    assert todos[1]["status"] == "done" 