# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MasterStack is a comprehensive Model Context Protocol (MCP) server stack for managing homelab infrastructure through Claude AI, Ollama, and voice commands via Home Assistant. The stack provides MCP servers that interface with various homelab services (Unifi, Proxmox, Home Assistant, N8N, Docker/Portainer, Minecraft, Plex, qBittorrent, and Arr suite).

## Development Commands

### Docker Compose Operations

The project uses Docker Compose (V1 or V2):
```bash
# Build and start all services
docker-compose up -d
# or
docker compose up -d

# View service status
docker-compose ps

# View logs
docker-compose logs -f                    # All services
docker-compose logs -f mcp-network        # Specific service

# Restart services
docker-compose restart
docker-compose restart mcp-homeautomation # Specific service

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose build
docker-compose up -d --force-recreate
```

### Quick Start Script

Use the provided startup script for initial setup and validation:
```bash
./start.sh
```

This script checks prerequisites, validates configuration, builds containers, starts services, and performs health checks on all 10 services.

### Testing Individual MCP Servers

Each MCP server runs on a dedicated port and exposes a `/health` endpoint:
```bash
# Test health endpoints
curl http://localhost:8001/health  # Network (Unifi)
curl http://localhost:8002/health  # Virtualization (Proxmox)
curl http://localhost:8003/health  # Home Automation (Home Assistant)
curl http://localhost:8004/health  # Workflows (N8N)
curl http://localhost:8005/health  # Containers (Docker/Portainer)
curl http://localhost:8006/health  # Gaming (Minecraft)
curl http://localhost:8007/health  # Media Server (Plex)
curl http://localhost:8008/health  # Downloads (qBittorrent)
curl http://localhost:8009/health  # Media Management (Arr Suite)
curl http://localhost:8010/health  # Ollama MCP Bridge
```

### Working with Individual Servers

To develop or debug a specific MCP server:
```bash
# Navigate to server directory
cd mcp-servers/network  # or any other server

# Install dependencies locally (for development)
pip install -r requirements.txt

# Run server directly (requires environment variables)
python server.py

# Rebuild just one service
docker-compose build mcp-network
docker-compose up -d mcp-network
```

## Architecture

### Multi-Container MCP Stack

The project uses a microservices architecture where each homelab service has its own dedicated MCP server container. All servers share:
- Common base: Python 3.11-slim Docker images
- Common framework: MCP SDK (mcp>=0.9.0)
- Common patterns: FastAPI/Uvicorn for HTTP endpoints, httpx for async HTTP clients
- Common health checks: `/health` endpoint on port 8000 (mapped to 800X externally)
- Common network: `mcp-network` bridge network

### MCP Server Structure

Each MCP server follows this pattern:
```
mcp-servers/<service-name>/
├── server.py         # Main MCP server implementation
├── requirements.txt  # Python dependencies
└── Dockerfile        # Container definition
```

Server implementations use:
- `mcp.server.Server` for MCP protocol handling
- `mcp.server.stdio.stdio_server` for stdio communication
- `mcp.types.Tool` and `TextContent` for tool definitions
- Async client classes for API interaction with target services
- Environment variables for configuration (loaded from `.env`)

### Ollama MCP Bridge

The `ollama-mcp-bridge` service is unique - it aggregates all MCP server tools and exposes them through an Ollama-compatible API at port 8010. This allows local LLMs to control the entire homelab. The bridge:
- Reads `mcp-config.json` to discover all MCP servers
- Mounts `/mcp-servers` as read-only
- Receives all environment variables from all other services
- Provides CORS support for web UIs

### Configuration Management

Environment variables flow from `.env` → `docker-compose.yml` → individual containers. Critical config:
- Service URLs and ports
- API tokens and credentials
- SSL verification flags
- Docker socket mounting for container management
- Minecraft servers as JSON array format

## Key Implementation Details

### Service Integration Patterns

1. **Token-based Auth** (Home Assistant, Plex, Portainer, Arr Suite): Pass `Authorization: Bearer <token>` header
2. **Username/Password** (Unifi, qBittorrent): Login endpoint to get session cookies
3. **API Token** (Proxmox): Token name + value in headers
4. **Docker Socket** (Containers): Mount `/var/run/docker.sock` as read-only

### Health Check Requirements

All services must respond to `GET /health` on port 8000 within:
- 40s start period
- 30s intervals
- 10s timeout
- 3 retries before marking unhealthy

### Common Environment Variables

Required for all services:
- Service-specific host/URL
- API credentials (tokens, usernames, passwords)
- SSL verification flags (default: false for self-signed certs)

Optional flags:
- Port overrides
- Docker host paths
- CORS origins for bridge

### Security Considerations

- Never commit `.env` files (already in `.gitignore`)
- All API credentials stored in environment variables
- SSL verification disabled by default for homelab self-signed certs
- Docker socket mounted read-only where possible
- Services isolated in dedicated bridge network

## Working with This Codebase

### Adding a New MCP Server

1. Create directory under `mcp-servers/<new-service>/`
2. Add `server.py`, `requirements.txt`, `Dockerfile` following existing patterns
3. Add service definition to `docker-compose.yml` with next available port
4. Add environment variables to `.env.example` and documentation
5. Update `mcp-config.json` if needed for Ollama bridge integration
6. Test health endpoint and API integration

### Modifying Existing Servers

1. Update `server.py` with new tools or API methods
2. Add new dependencies to `requirements.txt` if needed
3. Rebuild container: `docker-compose build <service-name>`
4. Restart: `docker-compose up -d <service-name>`
5. Test: `curl http://localhost:800X/health` and tool functionality

### Testing Changes

After code changes:
```bash
# Rebuild affected services
docker-compose build

# Recreate containers with new images
docker-compose up -d --force-recreate

# Verify all services healthy
docker-compose ps
./start.sh  # or manually curl each health endpoint
```

### Debugging

```bash
# View real-time logs
docker-compose logs -f <service-name>

# Check container status
docker-compose ps

# Validate configuration
docker-compose config

# Check environment variable substitution
docker-compose config | grep -A 5 <service-name>

# Shell into running container
docker exec -it <container-name> /bin/bash

# Check if service can reach homelab endpoints
docker exec -it <container-name> curl -v <homelab-service-url>
```

## Project-Specific Conventions

- All MCP servers expose port 8000 internally, mapped to 8001-8010 externally
- Server logging uses Python's `logging` module with INFO level
- Environment variable naming: `<SERVICE>_<PROPERTY>` (e.g., `UNIFI_HOST`, `HA_TOKEN`)
- SSL verification defaults to `false` to support self-signed certificates
- All servers use async/await patterns with httpx for HTTP calls
- Docker healthchecks use curl against `/health` endpoint
- Container names match service names with `mcp-` prefix
