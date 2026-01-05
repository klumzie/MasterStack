#!/usr/bin/env python3
"""
MCP Server for qBittorrent
Provides tools for managing torrents and downloads
"""

import os
import asyncio
import logging
from typing import Any
from qbittorrentapi import Client
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-downloads")

# Environment variables
QBITTORRENT_HOST = os.getenv("QBITTORRENT_HOST", "http://qbittorrent.local:8080")
QBITTORRENT_USERNAME = os.getenv("QBITTORRENT_USERNAME", "admin")
QBITTORRENT_PASSWORD = os.getenv("QBITTORRENT_PASSWORD")

class QBittorrentClient:
    """qBittorrent API Client"""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy-load qBittorrent client connection"""
        if self._client is None:
            logger.info(f"Connecting to qBittorrent at {QBITTORRENT_HOST}")
            self._client = Client(
                host=QBITTORRENT_HOST,
                username=QBITTORRENT_USERNAME,
                password=QBITTORRENT_PASSWORD
            )
        return self._client

    def get_torrents(self, filter_status: str = None):
        """Get all torrents"""
        return self.client.torrents_info(status_filter=filter_status)

    def add_torrent(self, url: str, save_path: str = None):
        """Add a torrent by URL or magnet link"""
        return self.client.torrents_add(urls=url, save_path=save_path)

    def pause_torrent(self, torrent_hash: str):
        """Pause a torrent"""
        self.client.torrents_pause(torrent_hashes=torrent_hash)

    def resume_torrent(self, torrent_hash: str):
        """Resume a torrent"""
        self.client.torrents_resume(torrent_hashes=torrent_hash)

    def delete_torrent(self, torrent_hash: str, delete_files: bool = False):
        """Delete a torrent"""
        self.client.torrents_delete(
            delete_files=delete_files,
            torrent_hashes=torrent_hash
        )

    def get_global_stats(self):
        """Get global transfer statistics"""
        return self.client.transfer_info()

# Create MCP server and client (lazy-loaded)
app = Server("mcp-downloads")
qbit = QBittorrentClient()  # Won't connect until first use

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available qBittorrent tools"""
    return [
        Tool(
            name="list_torrents",
            description="List all torrents",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "Filter by status (downloading, seeding, completed, paused, active, inactive)",
                        "enum": ["downloading", "seeding", "completed", "paused", "active", "inactive", "all"]
                    }
                }
            }
        ),
        Tool(
            name="add_torrent",
            description="Add a torrent by URL or magnet link",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Torrent URL or magnet link"
                    },
                    "save_path": {
                        "type": "string",
                        "description": "Optional save path for the torrent"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="pause_torrent",
            description="Pause a torrent",
            inputSchema={
                "type": "object",
                "properties": {
                    "torrent_hash": {
                        "type": "string",
                        "description": "Torrent hash"
                    }
                },
                "required": ["torrent_hash"]
            }
        ),
        Tool(
            name="resume_torrent",
            description="Resume a paused torrent",
            inputSchema={
                "type": "object",
                "properties": {
                    "torrent_hash": {
                        "type": "string",
                        "description": "Torrent hash"
                    }
                },
                "required": ["torrent_hash"]
            }
        ),
        Tool(
            name="delete_torrent",
            description="Delete a torrent",
            inputSchema={
                "type": "object",
                "properties": {
                    "torrent_hash": {
                        "type": "string",
                        "description": "Torrent hash"
                    },
                    "delete_files": {
                        "type": "boolean",
                        "description": "Also delete downloaded files (default: false)",
                        "default": False
                    }
                },
                "required": ["torrent_hash"]
            }
        ),
        Tool(
            name="get_stats",
            description="Get global download/upload statistics",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute qBittorrent tool"""
    try:
        if name == "list_torrents":
            filter_status = arguments.get("filter")
            torrents = qbit.get_torrents(filter_status)
            summary = f"Found {len(torrents)} torrents:\n\n"
            for torrent in torrents:
                summary += f"- {torrent.name}\n"
                summary += f"  Hash: {torrent.hash}\n"
                summary += f"  Status: {torrent.state}\n"
                summary += f"  Progress: {torrent.progress*100:.1f}%\n"
                summary += f"  Size: {torrent.size/(1024**3):.2f}GB\n"
                summary += f"  DL Speed: {torrent.dlspeed/(1024**2):.2f}MB/s\n"
                summary += f"  UP Speed: {torrent.upspeed/(1024**2):.2f}MB/s\n\n"
            return [TextContent(type="text", text=summary)]

        elif name == "add_torrent":
            url = arguments["url"]
            save_path = arguments.get("save_path")
            result = qbit.add_torrent(url, save_path)
            return [TextContent(type="text", text=f"Torrent added successfully: {result}")]

        elif name == "pause_torrent":
            torrent_hash = arguments["torrent_hash"]
            qbit.pause_torrent(torrent_hash)
            return [TextContent(type="text", text=f"Torrent {torrent_hash} has been paused")]

        elif name == "resume_torrent":
            torrent_hash = arguments["torrent_hash"]
            qbit.resume_torrent(torrent_hash)
            return [TextContent(type="text", text=f"Torrent {torrent_hash} has been resumed")]

        elif name == "delete_torrent":
            torrent_hash = arguments["torrent_hash"]
            delete_files = arguments.get("delete_files", False)
            qbit.delete_torrent(torrent_hash, delete_files)
            action = "and files deleted" if delete_files else "removed"
            return [TextContent(type="text", text=f"Torrent {torrent_hash} has been {action}")]

        elif name == "get_stats":
            stats = qbit.get_global_stats()
            summary = "Global Statistics:\n"
            summary += f"  Download Speed: {stats.dl_info_speed/(1024**2):.2f}MB/s\n"
            summary += f"  Upload Speed: {stats.up_info_speed/(1024**2):.2f}MB/s\n"
            summary += f"  Downloaded (session): {stats.dl_info_data/(1024**3):.2f}GB\n"
            summary += f"  Uploaded (session): {stats.up_info_data/(1024**3):.2f}GB\n"
            return [TextContent(type="text", text=summary)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    logger.info("Starting MCP Downloads Server (qBittorrent)")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
