-- mcp_slate/schema.sql
-- Database schema for the Slate MCP server

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