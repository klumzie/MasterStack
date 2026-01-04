#!/usr/bin/env python3
"""
MCP Server for Docker/Portainer
Provides tools for managing containers, images, and stacks
"""

import os
import asyncio
import logging
from typing import Any
import httpx
import docker
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-containers")

# Environment variables
DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
PORTAINER_URL = os.getenv("PORTAINER_URL", "http://portainer.local:9000")
PORTAINER_API_KEY = os.getenv("PORTAINER_API_KEY")

class ContainerClient:
    """Docker/Portainer API Client"""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.portainer_url = PORTAINER_URL
        self.portainer_headers = {
            "X-API-Key": PORTAINER_API_KEY
        }

    def get_containers(self, all_containers=True):
        """Get all containers"""
        return self.docker_client.containers.list(all=all_containers)

    def get_container(self, container_id: str):
        """Get specific container"""
        return self.docker_client.containers.get(container_id)

    def start_container(self, container_id: str):
        """Start a container"""
        container = self.docker_client.containers.get(container_id)
        container.start()

    def stop_container(self, container_id: str):
        """Stop a container"""
        container = self.docker_client.containers.get(container_id)
        container.stop()

    def restart_container(self, container_id: str):
        """Restart a container"""
        container = self.docker_client.containers.get(container_id)
        container.restart()

    def get_logs(self, container_id: str, tail: int = 100):
        """Get container logs"""
        container = self.docker_client.containers.get(container_id)
        return container.logs(tail=tail).decode('utf-8')

    def get_stats(self, container_id: str):
        """Get container stats"""
        container = self.docker_client.containers.get(container_id)
        stats = container.stats(stream=False)
        return stats

# Create MCP server
app = Server("mcp-containers")
container_client = ContainerClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available container management tools"""
    return [
        Tool(
            name="list_containers",
            description="List all Docker containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Include stopped containers (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="start_container",
            description="Start a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    }
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="stop_container",
            description="Stop a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    }
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="restart_container",
            description="Restart a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    }
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="get_logs",
            description="Get container logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to tail (default: 100)",
                        "default": 100
                    }
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="get_stats",
            description="Get container resource usage statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {
                        "type": "string",
                        "description": "Container ID or name"
                    }
                },
                "required": ["container_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute container management tool"""
    try:
        if name == "list_containers":
            all_containers = arguments.get("all", True)
            containers = container_client.get_containers(all_containers)
            summary = f"Found {len(containers)} containers:\n\n"
            for container in containers:
                summary += f"- {container.name} ({container.short_id})\n"
                summary += f"  Image: {container.image.tags[0] if container.image.tags else 'N/A'}\n"
                summary += f"  Status: {container.status}\n"
                summary += f"  Ports: {container.ports}\n\n"
            return [TextContent(type="text", text=summary)]

        elif name == "start_container":
            container_id = arguments["container_id"]
            container_client.start_container(container_id)
            return [TextContent(type="text", text=f"Container {container_id} has been started")]

        elif name == "stop_container":
            container_id = arguments["container_id"]
            container_client.stop_container(container_id)
            return [TextContent(type="text", text=f"Container {container_id} has been stopped")]

        elif name == "restart_container":
            container_id = arguments["container_id"]
            container_client.restart_container(container_id)
            return [TextContent(type="text", text=f"Container {container_id} has been restarted")]

        elif name == "get_logs":
            container_id = arguments["container_id"]
            tail = arguments.get("tail", 100)
            logs = container_client.get_logs(container_id, tail)
            return [TextContent(type="text", text=f"Logs for {container_id}:\n\n{logs}")]

        elif name == "get_stats":
            container_id = arguments["container_id"]
            stats = container_client.get_stats(container_id)
            # Parse CPU and memory stats
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0

            mem_usage = stats['memory_stats']['usage']
            mem_limit = stats['memory_stats']['limit']
            mem_percent = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0

            summary = f"Stats for {container_id}:\n"
            summary += f"  CPU: {cpu_percent:.2f}%\n"
            summary += f"  Memory: {mem_usage/(1024**2):.1f}MB / {mem_limit/(1024**2):.1f}MB ({mem_percent:.1f}%)\n"
            return [TextContent(type="text", text=summary)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Containers Server (Docker/Portainer)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
