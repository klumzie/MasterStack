#!/usr/bin/env python3
"""
MCP Server for Home Assistant
Provides tools for managing entities, automations, and services
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
logger = logging.getLogger("mcp-homeautomation")

# Environment variables
HA_URL = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN")

class HomeAssistantClient:
    """Home Assistant API Client"""

    def __init__(self):
        self.base_url = HA_URL
        self.headers = {
            "Authorization": f"Bearer {HA_TOKEN}",
            "Content-Type": "application/json"
        }

    async def get_states(self, client: httpx.AsyncClient):
        """Get all entity states"""
        response = await client.get(
            f"{self.base_url}/api/states",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def get_entity_state(self, client: httpx.AsyncClient, entity_id: str):
        """Get specific entity state"""
        response = await client.get(
            f"{self.base_url}/api/states/{entity_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def call_service(self, client: httpx.AsyncClient, domain: str, service: str, data: dict):
        """Call a Home Assistant service"""
        response = await client.post(
            f"{self.base_url}/api/services/{domain}/{service}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def get_services(self, client: httpx.AsyncClient):
        """Get all available services"""
        response = await client.get(
            f"{self.base_url}/api/services",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def trigger_automation(self, client: httpx.AsyncClient, automation_id: str):
        """Trigger an automation"""
        return await self.call_service(client, "automation", "trigger", {
            "entity_id": automation_id
        })

# Create MCP server
app = Server("mcp-homeautomation")
ha = HomeAssistantClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Home Assistant tools"""
    return [
        Tool(
            name="list_entities",
            description="List all Home Assistant entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filter by domain (e.g., 'light', 'switch', 'sensor')"
                    }
                }
            }
        ),
        Tool(
            name="get_entity_state",
            description="Get the current state of a specific entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID (e.g., 'light.living_room')"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="turn_on",
            description="Turn on a light, switch, or other device",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to turn on"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="turn_off",
            description="Turn off a light, switch, or other device",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to turn off"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="set_temperature",
            description="Set temperature for climate devices",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Climate entity ID"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Target temperature"
                    }
                },
                "required": ["entity_id", "temperature"]
            }
        ),
        Tool(
            name="trigger_automation",
            description="Trigger a Home Assistant automation",
            inputSchema={
                "type": "object",
                "properties": {
                    "automation_id": {
                        "type": "string",
                        "description": "Automation entity ID"
                    }
                },
                "required": ["automation_id"]
            }
        ),
        Tool(
            name="list_services",
            description="List all available Home Assistant services",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Home Assistant tool"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if name == "list_entities":
                states = await ha.get_states(client)
                domain_filter = arguments.get("domain")

                if domain_filter:
                    states = [s for s in states if s.get("entity_id", "").startswith(f"{domain_filter}.")]

                summary = f"Found {len(states)} entities:\n\n"
                for state in states[:50]:  # Limit to 50 for readability
                    entity_id = state.get("entity_id", "Unknown")
                    current_state = state.get("state", "N/A")
                    friendly_name = state.get("attributes", {}).get("friendly_name", entity_id)
                    summary += f"- {entity_id}: {current_state}\n"
                    summary += f"  Name: {friendly_name}\n\n"

                if len(states) > 50:
                    summary += f"\n... and {len(states) - 50} more entities"

                return [TextContent(type="text", text=summary)]

            elif name == "get_entity_state":
                entity_id = arguments["entity_id"]
                state = await ha.get_entity_state(client, entity_id)
                summary = f"Entity: {entity_id}\n"
                summary += f"State: {state.get('state', 'N/A')}\n"
                summary += f"Last Changed: {state.get('last_changed', 'N/A')}\n"
                summary += f"Attributes:\n"
                for key, value in state.get("attributes", {}).items():
                    summary += f"  {key}: {value}\n"
                return [TextContent(type="text", text=summary)]

            elif name == "turn_on":
                entity_id = arguments["entity_id"]
                domain = entity_id.split(".")[0]
                await ha.call_service(client, domain, "turn_on", {"entity_id": entity_id})
                return [TextContent(type="text", text=f"{entity_id} has been turned on")]

            elif name == "turn_off":
                entity_id = arguments["entity_id"]
                domain = entity_id.split(".")[0]
                await ha.call_service(client, domain, "turn_off", {"entity_id": entity_id})
                return [TextContent(type="text", text=f"{entity_id} has been turned off")]

            elif name == "set_temperature":
                entity_id = arguments["entity_id"]
                temperature = arguments["temperature"]
                await ha.call_service(client, "climate", "set_temperature", {
                    "entity_id": entity_id,
                    "temperature": temperature
                })
                return [TextContent(type="text", text=f"Temperature set to {temperature}°C for {entity_id}")]

            elif name == "trigger_automation":
                automation_id = arguments["automation_id"]
                await ha.trigger_automation(client, automation_id)
                return [TextContent(type="text", text=f"Automation {automation_id} has been triggered")]

            elif name == "list_services":
                services = await ha.get_services(client)
                summary = "Available Services:\n\n"
                for domain, domain_services in services.items():
                    summary += f"Domain: {domain}\n"
                    for service_name in domain_services.keys():
                        summary += f"  - {service_name}\n"
                    summary += "\n"
                return [TextContent(type="text", text=summary)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Home Automation Server (Home Assistant)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
