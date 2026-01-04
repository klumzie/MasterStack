#!/usr/bin/env python3
"""
MCP Server for Proxmox VE
Provides tools for managing VMs, containers, and nodes
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
logger = logging.getLogger("mcp-virtualization")

# Environment variables
PROXMOX_HOST = os.getenv("PROXMOX_HOST", "https://proxmox.local:8006")
PROXMOX_USER = os.getenv("PROXMOX_USER", "root@pam")
PROXMOX_TOKEN_NAME = os.getenv("PROXMOX_TOKEN_NAME")
PROXMOX_TOKEN_VALUE = os.getenv("PROXMOX_TOKEN_VALUE")
PROXMOX_VERIFY_SSL = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"

class ProxmoxClient:
    """Proxmox VE API Client"""

    def __init__(self):
        self.base_url = PROXMOX_HOST
        self.headers = {
            "Authorization": f"PVEAPIToken={PROXMOX_USER}!{PROXMOX_TOKEN_NAME}={PROXMOX_TOKEN_VALUE}"
        }
        self.verify_ssl = PROXMOX_VERIFY_SSL

    async def get_nodes(self, client: httpx.AsyncClient):
        """Get all Proxmox nodes"""
        response = await client.get(
            f"{self.base_url}/api2/json/nodes",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def get_vms(self, client: httpx.AsyncClient, node: str):
        """Get all VMs on a node"""
        response = await client.get(
            f"{self.base_url}/api2/json/nodes/{node}/qemu",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def get_containers(self, client: httpx.AsyncClient, node: str):
        """Get all LXC containers on a node"""
        response = await client.get(
            f"{self.base_url}/api2/json/nodes/{node}/lxc",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def start_vm(self, client: httpx.AsyncClient, node: str, vmid: int):
        """Start a VM"""
        response = await client.post(
            f"{self.base_url}/api2/json/nodes/{node}/qemu/{vmid}/status/start",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def stop_vm(self, client: httpx.AsyncClient, node: str, vmid: int):
        """Stop a VM"""
        response = await client.post(
            f"{self.base_url}/api2/json/nodes/{node}/qemu/{vmid}/status/stop",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def reboot_vm(self, client: httpx.AsyncClient, node: str, vmid: int):
        """Reboot a VM"""
        response = await client.post(
            f"{self.base_url}/api2/json/nodes/{node}/qemu/{vmid}/status/reboot",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def vm_status(self, client: httpx.AsyncClient, node: str, vmid: int):
        """Get VM status"""
        response = await client.get(
            f"{self.base_url}/api2/json/nodes/{node}/qemu/{vmid}/status/current",
            headers=self.headers,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

    async def create_snapshot(self, client: httpx.AsyncClient, node: str, vmid: int, snapname: str):
        """Create a VM snapshot"""
        response = await client.post(
            f"{self.base_url}/api2/json/nodes/{node}/qemu/{vmid}/snapshot",
            headers=self.headers,
            data={"snapname": snapname},
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()

# Create MCP server
app = Server("mcp-virtualization")
proxmox = ProxmoxClient()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Proxmox tools"""
    return [
        Tool(
            name="list_nodes",
            description="List all Proxmox nodes in the cluster",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_vms",
            description="List all virtual machines on a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    }
                },
                "required": ["node"]
            }
        ),
        Tool(
            name="list_containers",
            description="List all LXC containers on a node",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    }
                },
                "required": ["node"]
            }
        ),
        Tool(
            name="start_vm",
            description="Start a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    },
                    "vmid": {
                        "type": "integer",
                        "description": "VM ID"
                    }
                },
                "required": ["node", "vmid"]
            }
        ),
        Tool(
            name="stop_vm",
            description="Stop a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    },
                    "vmid": {
                        "type": "integer",
                        "description": "VM ID"
                    }
                },
                "required": ["node", "vmid"]
            }
        ),
        Tool(
            name="reboot_vm",
            description="Reboot a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    },
                    "vmid": {
                        "type": "integer",
                        "description": "VM ID"
                    }
                },
                "required": ["node", "vmid"]
            }
        ),
        Tool(
            name="vm_status",
            description="Get current status of a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    },
                    "vmid": {
                        "type": "integer",
                        "description": "VM ID"
                    }
                },
                "required": ["node", "vmid"]
            }
        ),
        Tool(
            name="create_snapshot",
            description="Create a snapshot of a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "node": {
                        "type": "string",
                        "description": "Proxmox node name"
                    },
                    "vmid": {
                        "type": "integer",
                        "description": "VM ID"
                    },
                    "snapname": {
                        "type": "string",
                        "description": "Snapshot name"
                    }
                },
                "required": ["node", "vmid", "snapname"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Proxmox tool"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if name == "list_nodes":
                result = await proxmox.get_nodes(client)
                nodes = result.get("data", [])
                summary = f"Found {len(nodes)} Proxmox nodes:\n\n"
                for node in nodes:
                    summary += f"- {node.get('node', 'Unknown')}\n"
                    summary += f"  Status: {node.get('status', 'N/A')}\n"
                    summary += f"  CPU: {node.get('cpu', 0)*100:.1f}%\n"
                    summary += f"  Memory: {node.get('mem', 0)/(1024**3):.1f}GB / {node.get('maxmem', 0)/(1024**3):.1f}GB\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "list_vms":
                node = arguments["node"]
                result = await proxmox.get_vms(client, node)
                vms = result.get("data", [])
                summary = f"Found {len(vms)} VMs on node {node}:\n\n"
                for vm in vms:
                    summary += f"- VM {vm.get('vmid', 'N/A')}: {vm.get('name', 'Unknown')}\n"
                    summary += f"  Status: {vm.get('status', 'N/A')}\n"
                    summary += f"  CPU: {vm.get('cpus', 0)} cores\n"
                    summary += f"  Memory: {vm.get('maxmem', 0)/(1024**3):.1f}GB\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "list_containers":
                node = arguments["node"]
                result = await proxmox.get_containers(client, node)
                containers = result.get("data", [])
                summary = f"Found {len(containers)} containers on node {node}:\n\n"
                for ct in containers:
                    summary += f"- CT {ct.get('vmid', 'N/A')}: {ct.get('name', 'Unknown')}\n"
                    summary += f"  Status: {ct.get('status', 'N/A')}\n"
                    summary += f"  CPU: {ct.get('cpus', 0)} cores\n"
                    summary += f"  Memory: {ct.get('maxmem', 0)/(1024**3):.1f}GB\n\n"
                return [TextContent(type="text", text=summary)]

            elif name == "start_vm":
                node = arguments["node"]
                vmid = arguments["vmid"]
                await proxmox.start_vm(client, node, vmid)
                return [TextContent(type="text", text=f"VM {vmid} on node {node} is starting")]

            elif name == "stop_vm":
                node = arguments["node"]
                vmid = arguments["vmid"]
                await proxmox.stop_vm(client, node, vmid)
                return [TextContent(type="text", text=f"VM {vmid} on node {node} is stopping")]

            elif name == "reboot_vm":
                node = arguments["node"]
                vmid = arguments["vmid"]
                await proxmox.reboot_vm(client, node, vmid)
                return [TextContent(type="text", text=f"VM {vmid} on node {node} is rebooting")]

            elif name == "vm_status":
                node = arguments["node"]
                vmid = arguments["vmid"]
                result = await proxmox.vm_status(client, node, vmid)
                data = result.get("data", {})
                summary = f"VM {vmid} Status:\n"
                summary += f"  Status: {data.get('status', 'N/A')}\n"
                summary += f"  CPU: {data.get('cpu', 0)*100:.1f}%\n"
                summary += f"  Memory: {data.get('mem', 0)/(1024**3):.1f}GB / {data.get('maxmem', 0)/(1024**3):.1f}GB\n"
                summary += f"  Uptime: {data.get('uptime', 0)}s\n"
                return [TextContent(type="text", text=summary)]

            elif name == "create_snapshot":
                node = arguments["node"]
                vmid = arguments["vmid"]
                snapname = arguments["snapname"]
                await proxmox.create_snapshot(client, node, vmid, snapname)
                return [TextContent(type="text", text=f"Snapshot '{snapname}' created for VM {vmid}")]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Virtualization Server (Proxmox)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
