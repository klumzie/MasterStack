#!/usr/bin/env python3
"""
MCP Server for Unifi Network Controller
Provides tools for managing Unifi network devices, clients, and WLANs
"""

import os
import asyncio
import logging
from typing import Any
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from mcp.server.sse import SseServerTransport

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-network")

# Environment variables
UNIFI_HOST = os.getenv("UNIFI_HOST", "https://unifi.local")
UNIFI_USERNAME = os.getenv("UNIFI_USERNAME", "admin")
UNIFI_PASSWORD = os.getenv("UNIFI_PASSWORD")
UNIFI_PORT = os.getenv("UNIFI_PORT", "8443")
UNIFI_VERIFY_SSL = os.getenv("UNIFI_VERIFY_SSL", "false").lower() == "true"

class UnifiClient:
    """Unifi Controller API Client"""

    def __init__(self):
        self.base_url = UNIFI_HOST
        self.username = UNIFI_USERNAME
        self.password = UNIFI_PASSWORD
        self.verify_ssl = UNIFI_VERIFY_SSL
        self.cookies = None

    async def login(self, client: httpx.AsyncClient):
        """Authenticate with Unifi controller"""
        try:
            response = await client.post(
                f"{self.base_url}/api/login",
                json={"username": self.username, "password": self.password},
                verify=self.verify_ssl
            )
            response.raise_for_status()
            self.cookies = response.cookies
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def get_devices(self, client: httpx.AsyncClient, site: str = "default"):
        """Get all network devices"""
        await self.login(client)
        response = await client.get(
            f"{self.base_url}/api/s/{site}/stat/device",
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def get_clients(self, client: httpx.AsyncClient, site: str = "default"):
        """Get all connected clients"""
        await self.login(client)
        response = await client.get(
            f"{self.base_url}/api/s/{site}/stat/sta",
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def block_client(self, client: httpx.AsyncClient, mac: str, site: str = "default"):
        """Block a client by MAC address"""
        await self.login(client)
        response = await client.post(
            f"{self.base_url}/api/s/{site}/cmd/stamgr",
            json={"cmd": "block-sta", "mac": mac},
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def unblock_client(self, client: httpx.AsyncClient, mac: str, site: str = "default"):
        """Unblock a client by MAC address"""
        await self.login(client)
        response = await client.post(
            f"{self.base_url}/api/s/{site}/cmd/stamgr",
            json={"cmd": "unblock-sta", "mac": mac},
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def restart_device(self, client: httpx.AsyncClient, mac: str, site: str = "default"):
        """Restart a network device"""
        await self.login(client)
        response = await client.post(
            f"{self.base_url}/api/s/{site}/cmd/devmgr",
            json={"cmd": "restart", "mac": mac},
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def get_wlans(self, client: httpx.AsyncClient, site: str = "default"):
        """Get all WLAN configurations"""
        await self.login(client)
        response = await client.get(
            f"{self.base_url}/api/s/{site}/rest/wlanconf",
            cookies=self.cookies,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

# Create MCP server
app = Server("mcp-network")
unifi = UnifiClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Unifi network tools"""
    return [
        Tool(
            name="list_devices",
            description="List all Unifi network devices (APs, switches, gateways)",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                }
            }
        ),
        Tool(
            name="list_clients",
            description="List all connected network clients",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                }
            }
        ),
        Tool(
            name="block_client",
            description="Block a client from the network by MAC address",
            inputSchema={
                "type": "object",
                "properties": {
                    "mac": {
                        "type": "string",
                        "description": "MAC address of the client to block"
                    },
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                },
                "required": ["mac"]
            }
        ),
        Tool(
            name="unblock_client",
            description="Unblock a previously blocked client by MAC address",
            inputSchema={
                "type": "object",
                "properties": {
                    "mac": {
                        "type": "string",
                        "description": "MAC address of the client to unblock"
                    },
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                },
                "required": ["mac"]
            }
        ),
        Tool(
            name="restart_device",
            description="Restart a Unifi network device by MAC address",
            inputSchema={
                "type": "object",
                "properties": {
                    "mac": {
                        "type": "string",
                        "description": "MAC address of the device to restart"
                    },
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                },
                "required": ["mac"]
            }
        ),
        Tool(
            name="list_wlans",
            description="List all wireless network (WLAN) configurations",
            inputSchema={
                "type": "object",
                "properties": {
                    "site": {
                        "type": "string",
                        "description": "Unifi site name (default: 'default')",
                        "default": "default"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Unifi network tool"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            site = arguments.get("site", "default")

            if name == "list_devices":
                result = await unifi.get_devices(client, site)
                devices = result.get("data", [])
                summary = f"Found {len(devices)} network devices:\n\n"
                for device in devices:
                    summary += f"- {device.get('name', 'Unknown')} ({device.get('type', 'N/A')})\n"
                    summary += f"  MAC: {device.get('mac', 'N/A')}\n"
                    summary += f"  IP: {device.get('ip', 'N/A')}\n"
                    summary += f"  Model: {device.get('model', 'N/A')}\n"
                    summary += f"  Status: {device.get('state', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "list_clients":
                result = await unifi.get_clients(client, site)
                clients = result.get("data", [])
                summary = f"Found {len(clients)} connected clients:\n\n"
                for cl in clients:
                    summary += f"- {cl.get('hostname', 'Unknown')} ({cl.get('mac', 'N/A')})\n"
                    summary += f"  IP: {cl.get('ip', 'N/A')}\n"
                    summary += f"  Signal: {cl.get('signal', 'N/A')} dBm\n"
                    summary += f"  Connected to: {cl.get('ap_mac', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "block_client":
                mac = arguments["mac"]
                result = await unifi.block_client(client, mac, site)
                return [TextContent(type="text", text=f"Client {mac} has been blocked")]

            elif name == "unblock_client":
                mac = arguments["mac"]
                result = await unifi.unblock_client(client, mac, site)
                return [TextContent(type="text", text=f"Client {mac} has been unblocked")]

            elif name == "restart_device":
                mac = arguments["mac"]
                result = await unifi.restart_device(client, mac, site)
                return [TextContent(type="text", text=f"Device {mac} restart initiated")]

            elif name == "list_wlans":
                result = await unifi.get_wlans(client, site)
                wlans = result.get("data", [])
                summary = f"Found {len(wlans)} WLAN configurations:\n\n"
                for wlan in wlans:
                    summary += f"- {wlan.get('name', 'Unknown')}\n"
                    summary += f"  SSID: {wlan.get('x_iapp_key', 'N/A')}\n"
                    summary += f"  Enabled: {wlan.get('enabled', False)}\n"
                    summary += f"  Security: {wlan.get('security', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def health_check(request):
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
    logger.info("Starting MCP Network Server (Unifi) on port 8000")
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
