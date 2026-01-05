#!/usr/bin/env python3
"""
Script to fix all MCP servers to use HTTP/SSE instead of stdio
"""

import os
import re
from pathlib import Path

SERVERS = [
    "virtualization",
    "workflows",
    "containers",
    "gaming",
    "media-server",
    "downloads",
    "media-management"
]

IMPORTS_OLD = '''from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent'''

IMPORTS_NEW = '''from mcp.server import Server
from mcp.types import Tool, TextContent
from fastapi.responses import JSONResponse
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport'''

MAIN_TEMPLATE = '''async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy"})

async def handle_sse(request):
    """Handle SSE connections for MCP"""
    transport = SseServerTransport("/messages")
    async with transport.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def create_app():
    """Create Starlette app"""
    return Starlette(
        debug=True,
        routes=[
            Route("/health", health_check),
            Route("/sse", handle_sse),
        ],
    )

if __name__ == "__main__":
    logger.info("Starting MCP Server on port 8000")
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
'''

REQS_OLD = '''mcp>=0.9.0'''

REQS_NEW = '''mcp>=0.9.0
httpx>=0.27.0
fastapi>=0.115.0
uvicorn>=0.32.0
pydantic>=2.0.0
starlette>=0.27.0
sse-starlette>=1.6.5'''

def fix_server(server_name):
    """Fix a single server"""
    server_path = Path(f"mcp-servers/{server_name}")
    server_file = server_path / "server.py"
    reqs_file = server_path / "requirements.txt"

    print(f"Fixing {server_name}...")

    # Fix server.py
    if server_file.exists():
        content = server_file.read_text()

        # Replace imports
        content = content.replace('from mcp.server.stdio import stdio_server\n', '')
        if 'from fastapi.responses import JSONResponse' not in content:
            content = content.replace(
                'from mcp.server import Server',
                'from mcp.server import Server\nfrom fastapi.responses import JSONResponse\nimport uvicorn\nfrom starlette.applications import Starlette\nfrom starlette.routing import Route\nfrom mcp.server.sse import SseServerTransport'
            )

        # Replace main function
        # Find and replace the async def main() and if __name__ == "__main__" blocks
        main_pattern = r'async def main\(\):.*?asyncio\.run\(main\(\)\)'
        if re.search(main_pattern, content, re.DOTALL):
            content = re.sub(main_pattern, MAIN_TEMPLATE.strip(), content, flags=re.DOTALL)

        server_file.write_text(content)
        print(f"  ✓ Updated {server_file}")

    # Fix requirements.txt
    if reqs_file.exists():
        content = reqs_file.read_text()
        if 'starlette' not in content:
            lines = content.strip().split('\n')
            # Add new dependencies
            if 'starlette>=0.27.0' not in content:
                lines.append('starlette>=0.27.0')
            if 'sse-starlette>=1.6.5' not in content:
                lines.append('sse-starlette>=1.6.5')
            content = '\n'.join(lines) + '\n'
            reqs_file.write_text(content)
        print(f"  ✓ Updated {reqs_file}")

if __name__ == "__main__":
    print("Fixing MCP servers to use HTTP/SSE transport...\n")
    for server in SERVERS:
        try:
            fix_server(server)
        except Exception as e:
            print(f"  ✗ Error fixing {server}: {e}")
    print("\nDone! Rebuild containers with: docker-compose build")
