# mcp/server.py
import logging
from mcp_slate.tools import slate

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # stdio transport is required for local Cursor integration
    slate.run(transport="stdio")