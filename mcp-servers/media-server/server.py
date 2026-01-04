#!/usr/bin/env python3
"""
MCP Server for Plex Media Server
Provides tools for managing libraries, scans, and playback
"""

import os
import asyncio
import logging
from typing import Any
from plexapi.server import PlexServer
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-media-server")

# Environment variables
PLEX_URL = os.getenv("PLEX_URL", "http://plex.local:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")

class PlexClient:
    """Plex Media Server Client"""

    def __init__(self):
        self.plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    def get_libraries(self):
        """Get all libraries"""
        return self.plex.library.sections()

    def get_library(self, library_name: str):
        """Get specific library"""
        return self.plex.library.section(library_name)

    def scan_library(self, library_name: str):
        """Scan a library for new content"""
        library = self.plex.library.section(library_name)
        library.update()
        return f"Library '{library_name}' scan initiated"

    def get_recently_added(self, library_name: str = None, limit: int = 10):
        """Get recently added content"""
        if library_name:
            library = self.plex.library.section(library_name)
            return library.recentlyAdded(maxresults=limit)
        else:
            return self.plex.library.recentlyAdded(maxresults=limit)

    def get_sessions(self):
        """Get active playback sessions"""
        return self.plex.sessions()

    def search(self, query: str):
        """Search for media"""
        return self.plex.library.search(query)

# Create MCP server
app = Server("mcp-media-server")
plex = PlexClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Plex tools"""
    return [
        Tool(
            name="list_libraries",
            description="List all Plex libraries",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="scan_library",
            description="Scan a Plex library for new content",
            inputSchema={
                "type": "object",
                "properties": {
                    "library_name": {
                        "type": "string",
                        "description": "Library name to scan"
                    }
                },
                "required": ["library_name"]
            }
        ),
        Tool(
            name="get_recently_added",
            description="Get recently added media",
            inputSchema={
                "type": "object",
                "properties": {
                    "library_name": {
                        "type": "string",
                        "description": "Library name to filter (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of items to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_sessions",
            description="Get active playback sessions",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="search",
            description="Search for media in Plex",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Plex tool"""
    try:
        if name == "list_libraries":
            libraries = plex.get_libraries()
            summary = f"Found {len(libraries)} libraries:\n\n"
            for lib in libraries:
                summary += f"- {lib.title} ({lib.type})\n"
                summary += f"  Items: {lib.totalSize}\n"
                summary += f"  Agent: {lib.agent}\n\n"
            return [TextContent(type="text", text=summary)]

        elif name == "scan_library":
            library_name = arguments["library_name"]
            result = plex.scan_library(library_name)
            return [TextContent(type="text", text=result)]

        elif name == "get_recently_added":
            library_name = arguments.get("library_name")
            limit = arguments.get("limit", 10)
            items = plex.get_recently_added(library_name, limit)
            summary = f"Recently added ({len(items)} items):\n\n"
            for item in items:
                summary += f"- {item.title}"
                if hasattr(item, 'year') and item.year:
                    summary += f" ({item.year})"
                summary += f"\n  Type: {item.type}\n"
                if hasattr(item, 'addedAt') and item.addedAt:
                    summary += f"  Added: {item.addedAt}\n"
                summary += "\n"
            return [TextContent(type="text", text=summary)]

        elif name == "get_sessions":
            sessions = plex.get_sessions()
            if not sessions:
                return [TextContent(type="text", text="No active playback sessions")]

            summary = f"Active sessions ({len(sessions)}):\n\n"
            for session in sessions:
                summary += f"- {session.title}\n"
                summary += f"  User: {session.usernames[0] if session.usernames else 'Unknown'}\n"
                summary += f"  Player: {session.player.title if session.player else 'Unknown'}\n"
                summary += f"  State: {session.player.state if session.player else 'Unknown'}\n\n"
            return [TextContent(type="text", text=summary)]

        elif name == "search":
            query = arguments["query"]
            results = plex.search(query)
            summary = f"Search results for '{query}' ({len(results)} items):\n\n"
            for item in results[:20]:  # Limit to 20
                summary += f"- {item.title}"
                if hasattr(item, 'year') and item.year:
                    summary += f" ({item.year})"
                summary += f"\n  Type: {item.type}\n\n"
            return [TextContent(type="text", text=summary)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Media Server (Plex)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
