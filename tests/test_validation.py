"""
Tests for the validation module.
"""

import pytest
from mcp_slate.validation import (
    TicketCreate, TicketResponse, TicketUpdate,
    TodoCreate, TodoResponse, TodoUpdate,
    TicketStatus, TicketPriority, TodoStatus
)


class TestTicketValidation:
    """Test ticket validation models."""
    
    def test_valid_ticket_create(self):
        """Test creating a valid ticket."""
        ticket = TicketCreate(
            project_id="test-project",
            title="Test Ticket",
            description="Test description",
            status="open",
            priority="medium"
        )
        assert ticket.project_id == "test-project"
        assert ticket.title == "Test Ticket"
        assert ticket.description == "Test description"
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.MEDIUM
    
    def test_ticket_create_with_defaults(self):
        """Test creating a ticket with default values."""
        ticket = TicketCreate(
            project_id="test-project",
            title="Test Ticket"
        )
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.MEDIUM
        assert ticket.description is None
    
    def test_invalid_project_id(self):
        """Test validation of invalid project_id."""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            TicketCreate(
                project_id="",
                title="Test Ticket"
            )
    
    def test_invalid_title(self):
        """Test validation of invalid title."""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            TicketCreate(
                project_id="test-project",
                title=""
            )
    
    def test_title_too_long(self):
        """Test validation of title length."""
        long_title = "x" * 256
        with pytest.raises(ValueError):
            TicketCreate(
                project_id="test-project",
                title=long_title
            )
    
    def test_description_too_long(self):
        """Test validation of description length."""
        long_description = "x" * 1001
        with pytest.raises(ValueError):
            TicketCreate(
                project_id="test-project",
                title="Test Ticket",
                description=long_description
            )
    
    def test_invalid_status(self):
        """Test validation of invalid status."""
        with pytest.raises(ValueError):
            TicketCreate(
                project_id="test-project",
                title="Test Ticket",
                status="invalid-status"
            )
    
    def test_invalid_priority(self):
        """Test validation of invalid priority."""
        with pytest.raises(ValueError):
            TicketCreate(
                project_id="test-project",
                title="Test Ticket",
                priority="invalid-priority"
            )
    
    def test_ticket_response(self):
        """Test ticket response model."""
        ticket = TicketResponse(
            id=1,
            project_id="test-project",
            title="Test Ticket",
            description="Test description",
            status="open",
            priority="high",
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-15T10:30:00"
        )
        assert ticket.id == 1
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH


class TestTodoValidation:
    """Test todo validation models."""
    
    def test_valid_todo_create(self):
        """Test creating a valid todo."""
        todo = TodoCreate(
            ticket_id=1,
            description="Test todo",
            status="pending",
            due_date="2024-01-20"
        )
        assert todo.ticket_id == 1
        assert todo.description == "Test todo"
        assert todo.status == TodoStatus.PENDING
        assert todo.due_date == "2024-01-20"
    
    def test_todo_create_with_defaults(self):
        """Test creating a todo with default values."""
        todo = TodoCreate(
            ticket_id=1,
            description="Test todo"
        )
        assert todo.status == TodoStatus.PENDING
        assert todo.due_date is None
    
    def test_invalid_ticket_id(self):
        """Test validation of invalid ticket_id."""
        with pytest.raises(ValueError):
            TodoCreate(
                ticket_id=0,
                description="Test todo"
            )
    
    def test_invalid_description(self):
        """Test validation of invalid description."""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            TodoCreate(
                ticket_id=1,
                description=""
            )
    
    def test_description_too_long(self):
        """Test validation of description length."""
        long_description = "x" * 1001
        with pytest.raises(ValueError):
            TodoCreate(
                ticket_id=1,
                description=long_description
            )
    
    def test_invalid_due_date_format(self):
        """Test validation of invalid due date format."""
        with pytest.raises(ValueError, match="due_date must be in ISO 8601 format"):
            TodoCreate(
                ticket_id=1,
                description="Test todo",
                due_date="20-01-2024"
            )
    
    def test_invalid_due_date_value(self):
        """Test validation of invalid due date value."""
        with pytest.raises(ValueError, match="due_date must be a valid date"):
            TodoCreate(
                ticket_id=1,
                description="Test todo",
                due_date="2024-13-45"
            )
    
    def test_valid_due_date_with_time(self):
        """Test validation of valid due date with time."""
        todo = TodoCreate(
            ticket_id=1,
            description="Test todo",
            due_date="2024-01-20T15:30:00"
        )
        assert todo.due_date == "2024-01-20T15:30:00"
    
    def test_invalid_status(self):
        """Test validation of invalid status."""
        with pytest.raises(ValueError):
            TodoCreate(
                ticket_id=1,
                description="Test todo",
                status="invalid-status"
            )
    
    def test_todo_response(self):
        """Test todo response model."""
        todo = TodoResponse(
            id=1,
            ticket_id=1,
            description="Test todo",
            status="done",
            due_date="2024-01-20",
            created_at="2024-01-15T10:30:00",
            updated_at="2024-01-15T10:30:00"
        )
        assert todo.id == 1
        assert todo.status == TodoStatus.DONE


class TestUpdateModels:
    """Test update validation models."""
    
    def test_valid_ticket_update(self):
        """Test valid ticket update."""
        update = TicketUpdate(
            title="Updated Title",
            status="in-progress"
        )
        assert update.title == "Updated Title"
        assert update.status == TicketStatus.IN_PROGRESS
    
    def test_empty_ticket_update(self):
        """Test that empty update raises error."""
        with pytest.raises(ValueError, match="At least one field must be provided"):
            TicketUpdate()
    
    def test_valid_todo_update(self):
        """Test valid todo update."""
        update = TodoUpdate(
            description="Updated description",
            status="done"
        )
        assert update.description == "Updated description"
        assert update.status == TodoStatus.DONE
    
    def test_empty_todo_update(self):
        """Test that empty update raises error."""
        with pytest.raises(ValueError, match="At least one field must be provided"):
            TodoUpdate() 