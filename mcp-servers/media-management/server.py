#!/usr/bin/env python3
"""
MCP Server for *Arr Suite (Sonarr, Radarr, Lidarr, Prowlarr, Readarr)
Provides tools for managing media libraries and downloads
"""

import os
import asyncio
import logging
from typing import Any
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-media-management")

# Environment variables
SONARR_URL = os.getenv("SONARR_URL", "")
SONARR_API_KEY = os.getenv("SONARR_API_KEY", "")
RADARR_URL = os.getenv("RADARR_URL", "")
RADARR_API_KEY = os.getenv("RADARR_API_KEY", "")
LIDARR_URL = os.getenv("LIDARR_URL", "")
LIDARR_API_KEY = os.getenv("LIDARR_API_KEY", "")
PROWLARR_URL = os.getenv("PROWLARR_URL", "")
PROWLARR_API_KEY = os.getenv("PROWLARR_API_KEY", "")
READARR_URL = os.getenv("READARR_URL", "")
READARR_API_KEY = os.getenv("READARR_API_KEY", "")

class ArrClient:
    """Generic *Arr API Client"""

    def __init__(self, service_name: str, base_url: str, api_key: str):
        self.service_name = service_name
        self.base_url = base_url.rstrip('/')
        self.headers = {"X-Api-Key": api_key}

    async def get(self, client: httpx.AsyncClient, endpoint: str):
        """Generic GET request"""
        response = await client.get(
            f"{self.base_url}/api/v3/{endpoint}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def post(self, client: httpx.AsyncClient, endpoint: str, data: dict):
        """Generic POST request"""
        response = await client.post(
            f"{self.base_url}/api/v3/{endpoint}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def get_calendar(self, client: httpx.AsyncClient):
        """Get calendar/upcoming items"""
        return await self.get(client, "calendar")

    async def get_queue(self, client: httpx.AsyncClient):
        """Get download queue"""
        return await self.get(client, "queue")

    async def search(self, client: httpx.AsyncClient, query: str):
        """Search for media"""
        return await self.get(client, f"search?term={query}")

# Initialize *Arr clients
arr_services = {}

if SONARR_URL and SONARR_API_KEY:
    arr_services["sonarr"] = ArrClient("Sonarr", SONARR_URL, SONARR_API_KEY)

if RADARR_URL and RADARR_API_KEY:
    arr_services["radarr"] = ArrClient("Radarr", RADARR_URL, RADARR_API_KEY)

if LIDARR_URL and LIDARR_API_KEY:
    arr_services["lidarr"] = ArrClient("Lidarr", LIDARR_URL, LIDARR_API_KEY)

if PROWLARR_URL and PROWLARR_API_KEY:
    arr_services["prowlarr"] = ArrClient("Prowlarr", PROWLARR_URL, PROWLARR_API_KEY)

if READARR_URL and READARR_API_KEY:
    arr_services["readarr"] = ArrClient("Readarr", READARR_URL, READARR_API_KEY)

# Create MCP server
app = Server("mcp-media-management")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available *Arr tools"""
    tools = [
        Tool(
            name="list_services",
            description="List all configured *Arr services",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

    # Add service-specific tools
    if "sonarr" in arr_services:
        tools.extend([
            Tool(
                name="sonarr_get_series",
                description="Get all TV series in Sonarr",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="sonarr_get_calendar",
                description="Get Sonarr calendar (upcoming episodes)",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="sonarr_search",
                description="Search for TV series in Sonarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            )
        ])

    if "radarr" in arr_services:
        tools.extend([
            Tool(
                name="radarr_get_movies",
                description="Get all movies in Radarr",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="radarr_get_calendar",
                description="Get Radarr calendar (upcoming movies)",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="radarr_search",
                description="Search for movies in Radarr",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            )
        ])

    # Add generic queue tool for all services
    for service_name in arr_services.keys():
        tools.append(
            Tool(
                name=f"{service_name}_get_queue",
                description=f"Get {service_name.capitalize()} download queue",
                inputSchema={"type": "object", "properties": {}}
            )
        )

    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute *Arr tool"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if name == "list_services":
                if not arr_services:
                    return [TextContent(type="text", text="No *Arr services configured")]

                summary = "Configured *Arr services:\n\n"
                for service_name, service in arr_services.items():
                    summary += f"- {service.service_name}\n"
                    summary += f"  URL: {service.base_url}\n\n"
                return [TextContent(type="text", text=summary)]

            # Sonarr tools
            elif name == "sonarr_get_series":
                series = await arr_services["sonarr"].get(client, "series")
                summary = f"Found {len(series)} TV series:\n\n"
                for show in series[:20]:  # Limit to 20
                    summary += f"- {show.get('title', 'Unknown')}\n"
                    summary += f"  Year: {show.get('year', 'N/A')}\n"
                    summary += f"  Status: {show.get('status', 'N/A')}\n"
                    summary += f"  Seasons: {show.get('seasonCount', 0)}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "sonarr_get_calendar":
                calendar = await arr_services["sonarr"].get_calendar(client)
                summary = f"Upcoming episodes ({len(calendar)}):\n\n"
                for episode in calendar[:20]:
                    summary += f"- {episode.get('series', {}).get('title', 'Unknown')}\n"
                    summary += f"  Episode: S{episode.get('seasonNumber', 0):02d}E{episode.get('episodeNumber', 0):02d}\n"
                    summary += f"  Title: {episode.get('title', 'Unknown')}\n"
                    summary += f"  Air Date: {episode.get('airDate', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "sonarr_search":
                query = arguments["query"]
                results = await arr_services["sonarr"].search(client, query)
                summary = f"Search results for '{query}':\n\n"
                for show in results[:10]:
                    summary += f"- {show.get('title', 'Unknown')} ({show.get('year', 'N/A')})\n"
                return [TextContent(type="text", text=summary)]

            # Radarr tools
            elif name == "radarr_get_movies":
                movies = await arr_services["radarr"].get(client, "movie")
                summary = f"Found {len(movies)} movies:\n\n"
                for movie in movies[:20]:  # Limit to 20
                    summary += f"- {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})\n"
                    summary += f"  Status: {movie.get('status', 'N/A')}\n"
                    summary += f"  Quality: {movie.get('hasFile', False) and 'Downloaded' or 'Missing'}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "radarr_get_calendar":
                calendar = await arr_services["radarr"].get_calendar(client)
                summary = f"Upcoming movies ({len(calendar)}):\n\n"
                for movie in calendar[:20]:
                    summary += f"- {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})\n"
                    summary += f"  Release Date: {movie.get('physicalRelease', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "radarr_search":
                query = arguments["query"]
                results = await arr_services["radarr"].search(client, query)
                summary = f"Search results for '{query}':\n\n"
                for movie in results[:10]:
                    summary += f"- {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})\n"
                return [TextContent(type="text", text=summary)]

            # Generic queue tools
            elif name.endswith("_get_queue"):
                service_name = name.replace("_get_queue", "")
                if service_name in arr_services:
                    queue = await arr_services[service_name].get_queue(client)
                    records = queue.get("records", [])
                    summary = f"{arr_services[service_name].service_name} download queue ({len(records)} items):\n\n"
                    for item in records:
                        summary += f"- {item.get('title', 'Unknown')}\n"
                        summary += f"  Status: {item.get('status', 'N/A')}\n"
                        summary += f"  Progress: {item.get('sizeleft', 0)/(1024**3):.2f}GB remaining\n\n"
                    return [TextContent(type="text", text=summary)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Media Management Server (*Arr Suite)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
