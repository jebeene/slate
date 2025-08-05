# Slate MCP Server

A Model Context Protocol (MCP) server for managing tickets and todos, backed by SQLite.

## Overview

Slate is an MCP server that provides tools for creating and managing tickets and todos through a simple SQLite database. It's designed to integrate with AI assistants and development tools that support the MCP protocol.

### Features

- **Type-safe validation** using Pydantic models for all data operations
- **Comprehensive field validation** including length limits and format checking
- **Enum-based status and priority values** for consistent data
- **ISO 8601 date format validation** for due dates
- **SQLite backend** with proper foreign key relationships
- **MCP protocol support** for integration with AI assistants

## Prerequisites

- Python 3.10+
- UV (for dependency management)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd slate
```

2. Install dependencies:
```bash
uv sync
```

3. Create and initialize the database:
```bash
# Create the database directory
mkdir -p ~/.slate

# Set the database path environment variable
export SQLITE_DB=~/.slate/slate.db

# Initialize the database with schema (creates the file and tables)
uv run python -c "from mcp_slate.db import init_db; init_db('$SQLITE_DB')"
```

## Development

### Running Tests
```bash
# Run all tests
uv run python -m pytest

# Run specific test file
uv run python -m pytest tests/test_validation.py

# Run tests with verbose output
uv run python -m pytest -v
```

### Adding Dependencies
```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Running the MCP Server Locally
```bash
# Run the server directly
uv run python mcp_slate/server.py

# Or run with specific database path
SQLITE_DB=./test.db uv run python mcp_slate/server.py
```

## Cursor Integration

Add this to your global Cursor MCP configuration inside the `mcpServers` object (usually at `~/.cursor/mcp.json`):

```json
"slate": {
      "command": "uv",
      "args": [
        "--directory",
        "<ABS_PATH>/slate",
        "run",
        "mcp_slate/server.py"
      ],
      "env": {
        "SQLITE_DB": "<ABS_PATH>/<DATABASE_NAME>.db"
      }
    }
```

Make sure to update the `ABS_PATH` and `DATABASE_NAME` placeholder paths to match your machine's configurations.

## Tools

### Tickets
- `add_ticket(project_id, title, description, status, priority)`: Create a new ticket
- `list_tickets()`: List all tickets
- `get_ticket(id)`: Get ticket details

### Todos
- `add_todo(ticket_id, description, status, due_date)`: Create a new todo
- `list_todos(ticket_id)`: List todos for a ticket
- `update_todo_status(id, status)`: Update todo status

### Database Operations
- `list_tables()`: List all database tables
- `schema(table)`: Get table schema information
- `run_select(sql, params, limit)`: Execute SELECT queries (with safety limits)

## Table Structure

### Tickets Table
```sql
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,                  -- simple label for project
    title TEXT NOT NULL,                       -- short summary
    description TEXT,                          -- details
    status TEXT CHECK(status IN (
        'open', 'in-progress', 'blocked', 'closed'
    )) DEFAULT 'open',
    priority TEXT CHECK(priority IN (
        'low', 'medium', 'high', 'urgent'
    )) DEFAULT 'medium',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Todos Table
```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,                -- link to parent ticket
    description TEXT NOT NULL,                 -- todo text
    status TEXT CHECK(status IN (
        'pending', 'in-progress', 'done'
    )) DEFAULT 'pending',
    due_date TEXT,                              -- optional deadline
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
);
``` 