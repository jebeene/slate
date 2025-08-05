"""
Validation module for Slate MCP server using Pydantic models.
Provides type-safe validation for Ticket and Todo entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re


class TicketStatus(str, Enum):
    """Valid ticket status values."""
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Valid ticket priority values."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TodoStatus(str, Enum):
    """Valid todo status values."""
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    DONE = "done"


class BaseTicket(BaseModel):
    """Base ticket model with common validation."""
    project_id: str = Field(..., min_length=1, max_length=100, description="Project identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Ticket title")
    description: Optional[str] = Field(None, max_length=1000, description="Ticket description")
    status: TicketStatus = Field(TicketStatus.OPEN, description="Ticket status")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="Ticket priority")

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        """Validate project_id format."""
        if not v.strip():
            raise ValueError("project_id cannot be empty or whitespace")
        return v.strip()

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title format."""
        if not v.strip():
            raise ValueError("title cannot be empty or whitespace")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description format."""
        if v is not None and not v.strip():
            return None  # Convert empty strings to None
        return v.strip() if v else None


class BaseTodo(BaseModel):
    """Base todo model with common validation."""
    ticket_id: int = Field(..., gt=0, description="Parent ticket ID")
    description: str = Field(..., min_length=1, max_length=1000, description="Todo description")
    status: TodoStatus = Field(TodoStatus.PENDING, description="Todo status")
    due_date: Optional[str] = Field(None, description="Due date in ISO 8601 format")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate description format."""
        if not v.strip():
            raise ValueError("description cannot be empty or whitespace")
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Validate ISO 8601 date format."""
        if v is None:
            return v
        
        # ISO 8601 pattern: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
        iso_pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?)?$'
        if not re.match(iso_pattern, v):
            raise ValueError("due_date must be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
        
        try:
            # Validate that it's a real date
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("due_date must be a valid date")
        
        return v


# Input models for creation
class TicketCreate(BaseTicket):
    """Model for creating new tickets."""
    pass


class TodoCreate(BaseTodo):
    """Model for creating new todos."""
    pass


# Input models for updates
class TicketUpdate(BaseModel):
    """Model for updating tickets."""
    project_id: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError("project_id cannot be empty or whitespace")
        return v.strip() if v else None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError("title cannot be empty or whitespace")
        return v.strip() if v else None

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        """Ensure at least one field is provided for update."""
        if not any([self.project_id, self.title, self.description, self.status, self.priority]):
            raise ValueError("At least one field must be provided for update")
        return self


class TodoUpdate(BaseModel):
    """Model for updating todos."""
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[TodoStatus] = None
    due_date: Optional[str] = None

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError("description cannot be empty or whitespace")
        return v.strip() if v else None

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v
        
        iso_pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?)?$'
        if not re.match(iso_pattern, v):
            raise ValueError("due_date must be in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
        
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("due_date must be a valid date")
        
        return v

    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        """Ensure at least one field is provided for update."""
        if not any([self.description, self.status, self.due_date]):
            raise ValueError("At least one field must be provided for update")
        return self


# Response models
class TicketResponse(BaseTicket):
    """Model for ticket responses."""
    id: int = Field(..., description="Ticket ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "project_id": "my-project",
                "title": "Implement user authentication",
                "description": "Add OAuth2 authentication to the application",
                "status": "open",
                "priority": "high",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    )


class TodoResponse(BaseTodo):
    """Model for todo responses."""
    id: int = Field(..., description="Todo ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "ticket_id": 1,
                "description": "Set up OAuth2 provider configuration",
                "status": "pending",
                "due_date": "2024-01-20",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    ) 