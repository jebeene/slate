# mcp_slate/tools.py
from typing import Any, Optional, Dict, List
from fastmcp import FastMCP
from mcp_slate.db import get_conn
from mcp_slate.validation import (
    TicketCreate, TicketResponse, TicketUpdate,
    TodoCreate, TodoResponse, TodoUpdate
)

slate = FastMCP("slate")

# Business logic functions (testable)
def _list_tables() -> List[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return [r[0] for r in rows]

def _schema(table: str) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return [dict(r) for r in rows]

def _run_select(sql: str, params: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
    q = sql.strip().lower()
    if not q.startswith("select"):
        raise ValueError("Only SELECT queries allowed")
    if " limit " not in q:
        sql = f"{sql.rstrip(';')} LIMIT {limit}"
    with get_conn() as conn:
        rows = conn.execute(sql, params or {}).fetchall()
        return [dict(r) for r in rows]

def _add_ticket(project_id: str, title: str, description: str = "", status: str = "open", priority: str = "medium") -> Dict[str, int]:
    # Validate input using Pydantic model
    ticket_data = TicketCreate(
        project_id=project_id,
        title=title,
        description=description,
        status=status,
        priority=priority
    )
    
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tickets (project_id, title, description, status, priority) VALUES (?, ?, ?, ?, ?)",
            (ticket_data.project_id, ticket_data.title, ticket_data.description, ticket_data.status, ticket_data.priority)
        )
        conn.commit()
        return {"id": cur.lastrowid}

def _list_tickets() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
        # Validate and format responses using Pydantic models
        tickets = []
        for row in rows:
            ticket_dict = dict(row)
            ticket_response = TicketResponse(**ticket_dict)
            tickets.append(ticket_response.model_dump())
        return tickets

def _get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not row:
            return None
        
        # Validate and format response using Pydantic model
        ticket_dict = dict(row)
        ticket_response = TicketResponse(**ticket_dict)
        return ticket_response.model_dump()

def _add_todo(ticket_id: int, description: str, status: str = "pending", due_date: Optional[str] = None) -> Dict[str, int]:
    # Validate input using Pydantic model
    todo_data = TodoCreate(
        ticket_id=ticket_id,
        description=description,
        status=status,
        due_date=due_date
    )
    
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO todos (ticket_id, description, status, due_date) VALUES (?, ?, ?, ?)",
            (todo_data.ticket_id, todo_data.description, todo_data.status, todo_data.due_date)
        )
        conn.commit()
        return {"id": cur.lastrowid}

def _list_todos(ticket_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM todos WHERE ticket_id = ? ORDER BY created_at", (ticket_id,)).fetchall()
        # Validate and format responses using Pydantic models
        todos = []
        for row in rows:
            todo_dict = dict(row)
            todo_response = TodoResponse(**todo_dict)
            todos.append(todo_response.model_dump())
        return todos

def _update_todo_status(todo_id: int, status: str) -> bool:
    # Validate status using Pydantic model
    from mcp_slate.validation import TodoStatus
    try:
        validated_status = TodoStatus(status)
    except ValueError:
        raise ValueError(f"Invalid status: {status}. Must be one of: {', '.join([s.value for s in TodoStatus])}")
    
    with get_conn() as conn:
        result = conn.execute("UPDATE todos SET status = ? WHERE id = ?", (validated_status, todo_id))
        conn.commit()
        return result.rowcount > 0

# MCP tool wrappers
@slate.tool()
def list_tables() -> List[str]:
    return _list_tables()

@slate.tool()
def schema(table: str) -> List[Dict[str, Any]]:
    return _schema(table)

@slate.tool()
def run_select(sql: str, params: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
    return _run_select(sql, params, limit)

@slate.tool()
def add_ticket(project_id: str, title: str, description: str = "", status: str = "open", priority: str = "medium") -> Dict[str, int]:
    return _add_ticket(project_id, title, description, status, priority)

@slate.tool()
def list_tickets() -> List[Dict[str, Any]]:
    return _list_tickets()

@slate.tool()
def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    return _get_ticket(ticket_id)

@slate.tool()
def add_todo(ticket_id: int, description: str, status: str = "pending", due_date: Optional[str] = None) -> Dict[str, int]:
    return _add_todo(ticket_id, description, status, due_date)

@slate.tool()
def list_todos(ticket_id: int) -> List[Dict[str, Any]]:
    return _list_todos(ticket_id)

@slate.tool()
def update_todo_status(todo_id: int, status: str) -> bool:
    return _update_todo_status(todo_id, status)