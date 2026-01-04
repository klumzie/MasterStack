#!/usr/bin/env python3
"""
MCP Server for N8N Workflows
Provides tools for triggering and monitoring N8N workflows
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
logger = logging.getLogger("mcp-workflows")

# Environment variables
N8N_HOST = os.getenv("N8N_HOST", "http://n8n.local:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY")

class N8NClient:
    """N8N API Client"""

    def __init__(self):
        self.base_url = N8N_HOST
        self.headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }

    async def get_workflows(self, client: httpx.AsyncClient):
        """Get all workflows"""
        response = await client.get(
            f"{self.base_url}/api/v1/workflows",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def get_workflow(self, client: httpx.AsyncClient, workflow_id: str):
        """Get specific workflow details"""
        response = await client.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    async def trigger_workflow(self, client: httpx.AsyncClient, workflow_id: str, data: dict = None):
        """Trigger a workflow execution"""
        response = await client.post(
            f"{self.base_url}/api/v1/workflows/{workflow_id}/activate",
            headers=self.headers,
            json=data or {}
        )
        response.raise_for_status()
        return response.json()

    async def get_executions(self, client: httpx.AsyncClient, workflow_id: str = None):
        """Get workflow executions"""
        url = f"{self.base_url}/api/v1/executions"
        if workflow_id:
            url += f"?workflowId={workflow_id}"

        response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Create MCP server
app = Server("mcp-workflows")
n8n = N8NClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available N8N workflow tools"""
    return [
        Tool(
            name="list_workflows",
            description="List all N8N workflows",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_workflow",
            description="Get details of a specific workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="trigger_workflow",
            description="Trigger a workflow execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow ID to trigger"
                    },
                    "data": {
                        "type": "object",
                        "description": "Optional data to pass to the workflow"
                    }
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="list_executions",
            description="List workflow executions",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Filter by workflow ID (optional)"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute N8N workflow tool"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if name == "list_workflows":
                result = await n8n.get_workflows(client)
                workflows = result.get("data", [])
                summary = f"Found {len(workflows)} workflows:\n\n"
                for wf in workflows:
                    summary += f"- {wf.get('name', 'Unknown')} (ID: {wf.get('id', 'N/A')})\n"
                    summary += f"  Active: {wf.get('active', False)}\n"
                    summary += f"  Updated: {wf.get('updatedAt', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "get_workflow":
                workflow_id = arguments["workflow_id"]
                workflow = await n8n.get_workflow(client, workflow_id)
                summary = f"Workflow: {workflow.get('name', 'Unknown')}\n"
                summary += f"ID: {workflow.get('id', 'N/A')}\n"
                summary += f"Active: {workflow.get('active', False)}\n"
                summary += f"Nodes: {len(workflow.get('nodes', []))}\n"
                summary += f"Created: {workflow.get('createdAt', 'N/A')}\n"
                summary += f"Updated: {workflow.get('updatedAt', 'N/A')}\n"
                return [TextContent(type="text", text=summary)]

            elif name == "trigger_workflow":
                workflow_id = arguments["workflow_id"]
                data = arguments.get("data")
                result = await n8n.trigger_workflow(client, workflow_id, data)
                return [TextContent(type="text", text=f"Workflow {workflow_id} has been triggered")]

            elif name == "list_executions":
                workflow_id = arguments.get("workflow_id")
                result = await n8n.get_executions(client, workflow_id)
                executions = result.get("data", [])
                summary = f"Found {len(executions)} executions:\n\n"
                for exe in executions[:20]:  # Limit to 20
                    summary += f"- Execution {exe.get('id', 'N/A')}\n"
                    summary += f"  Workflow: {exe.get('workflowId', 'N/A')}\n"
                    summary += f"  Status: {exe.get('finished', 'running')}\n"
                    summary += f"  Started: {exe.get('startedAt', 'N/A')}\n\n"
                return [TextContent(type="text", text=summary)]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Workflows Server (N8N)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
