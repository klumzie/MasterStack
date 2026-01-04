#!/usr/bin/env python3
"""
MCP Server for Minecraft (via RCON)
Provides tools for managing Minecraft servers
"""

import os
import asyncio
import logging
import json
from typing import Any
from mcrcon import MCRcon
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-gaming")

# Environment variables
MINECRAFT_SERVERS = json.loads(os.getenv("MINECRAFT_SERVERS", "[]"))

class MinecraftClient:
    """Minecraft RCON Client"""

    def __init__(self, servers: list):
        self.servers = {server["name"]: server for server in servers}

    def execute_command(self, server_name: str, command: str):
        """Execute an RCON command on a Minecraft server"""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not found")

        server = self.servers[server_name]
        with MCRcon(
            server["host"],
            server["password"],
            port=server.get("port", 25575)
        ) as mcr:
            response = mcr.command(command)
            return response

    def list_players(self, server_name: str):
        """List online players"""
        return self.execute_command(server_name, "list")

    def send_message(self, server_name: str, message: str):
        """Send a message to all players"""
        return self.execute_command(server_name, f"say {message}")

    def give_item(self, server_name: str, player: str, item: str, amount: int = 1):
        """Give an item to a player"""
        return self.execute_command(server_name, f"give {player} {item} {amount}")

    def teleport(self, server_name: str, player: str, x: int, y: int, z: int):
        """Teleport a player"""
        return self.execute_command(server_name, f"tp {player} {x} {y} {z}")

    def set_time(self, server_name: str, time: str):
        """Set world time (day, night, etc)"""
        return self.execute_command(server_name, f"time set {time}")

    def set_weather(self, server_name: str, weather: str):
        """Set weather (clear, rain, thunder)"""
        return self.execute_command(server_name, f"weather {weather}")

# Create MCP server
app = Server("mcp-gaming")
minecraft = MinecraftClient(MINECRAFT_SERVERS)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Minecraft tools"""
    return [
        Tool(
            name="list_servers",
            description="List all configured Minecraft servers",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="execute_command",
            description="Execute a raw RCON command on a Minecraft server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Minecraft server name"
                    },
                    "command": {
                        "type": "string",
                        "description": "RCON command to execute"
                    }
                },
                "required": ["server_name", "command"]
            }
        ),
        Tool(
            name="list_players",
            description="List online players on a Minecraft server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Minecraft server name"
                    }
                },
                "required": ["server_name"]
            }
        ),
        Tool(
            name="send_message",
            description="Send a message to all players on a Minecraft server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Minecraft server name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    }
                },
                "required": ["server_name", "message"]
            }
        ),
        Tool(
            name="set_time",
            description="Set the world time (day, night, etc)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Minecraft server name"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time to set (day, night, noon, midnight, or tick value)"
                    }
                },
                "required": ["server_name", "time"]
            }
        ),
        Tool(
            name="set_weather",
            description="Set the weather (clear, rain, thunder)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "Minecraft server name"
                    },
                    "weather": {
                        "type": "string",
                        "description": "Weather to set (clear, rain, thunder)"
                    }
                },
                "required": ["server_name", "weather"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Minecraft tool"""
    try:
        if name == "list_servers":
            if not minecraft.servers:
                return [TextContent(type="text", text="No Minecraft servers configured")]

            summary = f"Configured Minecraft servers:\n\n"
            for server_name, server_info in minecraft.servers.items():
                summary += f"- {server_name}\n"
                summary += f"  Host: {server_info['host']}:{server_info.get('port', 25575)}\n\n"
            return [TextContent(type="text", text=summary)]

        elif name == "execute_command":
            server_name = arguments["server_name"]
            command = arguments["command"]
            result = minecraft.execute_command(server_name, command)
            return [TextContent(type="text", text=f"Command result:\n{result}")]

        elif name == "list_players":
            server_name = arguments["server_name"]
            result = minecraft.list_players(server_name)
            return [TextContent(type="text", text=result)]

        elif name == "send_message":
            server_name = arguments["server_name"]
            message = arguments["message"]
            result = minecraft.send_message(server_name, message)
            return [TextContent(type="text", text=f"Message sent: {result}")]

        elif name == "set_time":
            server_name = arguments["server_name"]
            time = arguments["time"]
            result = minecraft.set_time(server_name, time)
            return [TextContent(type="text", text=f"Time set: {result}")]

        elif name == "set_weather":
            server_name = arguments["server_name"]
            weather = arguments["weather"]
            result = minecraft.set_weather(server_name, weather)
            return [TextContent(type="text", text=f"Weather set: {result}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Gaming Server (Minecraft)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
