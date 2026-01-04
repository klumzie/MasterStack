# MCP Homelab Stack - Detailed Setup Guide

This guide will walk you through setting up your entire MCP homelab stack from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Service Configuration](#service-configuration)
3. [Environment Setup](#environment-setup)
4. [Building and Starting](#building-and-starting)
5. [Verification](#verification)
6. [Claude AI Integration](#claude-ai-integration)
7. [Home Assistant Integration](#home-assistant-integration)

---

## Prerequisites

### Required Software

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning the repository)

### Required Services

Before using this stack, you need to have these services running in your homelab:

- Unifi Network Controller (optional)
- Proxmox VE (optional)
- Home Assistant (optional)
- N8N (optional)
- Portainer (optional)
- Minecraft Server with RCON enabled (optional)
- Plex Media Server (optional)
- qBittorrent (optional)
- Sonarr, Radarr, and other *Arr services (optional)

**Note**: Each service is optional. The MCP servers will only activate for services you've configured in the `.env` file.

---

## Service Configuration

### 1. Unifi Network Controller

Enable API access in your Unifi controller:

1. Log into your Unifi controller
2. Navigate to Settings → System → Advanced
3. Ensure "Enable API" is checked
4. Note your controller URL (usually `https://unifi.local:8443`)

Get your credentials:
- Username: Your Unifi admin username
- Password: Your Unifi admin password

### 2. Proxmox VE

Create an API token for the MCP server:

1. Log into Proxmox web interface
2. Go to Datacenter → Permissions → API Tokens
3. Click "Add"
4. User: `root@pam`
5. Token ID: `mcp-token` (or any name you prefer)
6. Uncheck "Privilege Separation"
7. Click "Add"
8. **Save the token value** - you won't be able to see it again!

### 3. Home Assistant

Create a long-lived access token:

1. In Home Assistant, click your profile (bottom left)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Name it "MCP Server"
5. **Copy the token** - you won't be able to see it again!

### 4. N8N

Create an API key:

1. Open N8N web interface
2. Go to Settings → API
3. Click "Create API Key"
4. Name it "MCP Server"
5. **Copy the API key**

### 5. Portainer

Create an access token:

1. Open Portainer web interface
2. Go to your profile (top right) → My account
3. Scroll to "Access tokens"
4. Click "Add access token"
5. Name it "MCP Server"
6. **Copy the token**

### 6. Plex Media Server

Get your Plex token:

**Method 1: From Plex Web App**
1. Open a media item in Plex Web
2. Click "Get Info" → "View XML"
3. Look at the URL - the token is the `X-Plex-Token` parameter

**Method 2: From Settings**
1. Go to https://www.plex.tv/claim/
2. Sign in
3. Your token will be displayed

**Method 3: From XML**
1. Open: `https://plex.tv/pms/resources?includeHttps=1&X-Plex-Token=`
2. Sign in
3. Find your server and copy the `accessToken` value

### 7. qBittorrent

Enable Web UI and note your credentials:

1. Open qBittorrent
2. Tools → Options → Web UI
3. Enable "Web User Interface (Remote control)"
4. Note the port (default: 8080)
5. Set/note your username and password

### 8. Sonarr/Radarr/*Arr Services

Get API keys for each service:

1. Open the *Arr web interface
2. Settings → General
3. Under "Security", find your "API Key"
4. **Copy the API key**

Repeat for each *Arr service you're using.

### 9. Minecraft Server

Enable RCON in your Minecraft server:

1. Edit `server.properties`
2. Set:
   ```properties
   enable-rcon=true
   rcon.port=25575
   rcon.password=your_secure_password
   ```
3. Restart your Minecraft server

---

## Environment Setup

### 1. Copy Environment Template

```bash
cd /path/to/mcp-homelab-stack
cp .env.example .env
```

### 2. Edit Configuration

Open `.env` in your favorite editor:

```bash
nano .env
```

### 3. Fill in Your Credentials

Update each section with your actual values:

#### Unifi Section
```env
UNIFI_HOST=https://192.168.1.1:8443
UNIFI_USERNAME=admin
UNIFI_PASSWORD=your_actual_password
UNIFI_PORT=8443
UNIFI_VERIFY_SSL=false
```

#### Proxmox Section
```env
PROXMOX_HOST=https://192.168.1.10:8006
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=mcp-token
PROXMOX_TOKEN_VALUE=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_VERIFY_SSL=false
```

#### Home Assistant Section
```env
HA_URL=http://192.168.1.20:8123
HA_TOKEN=your_long_lived_access_token_here
```

#### Continue for all other services...

**Important**: Only configure the services you actually have running!

---

## Building and Starting

### Option 1: Quick Start Script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

The script will:
1. Validate your Docker installation
2. Check your configuration
3. Build all containers
4. Start the services
5. Run health checks

### Option 2: Manual Start

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Verification

### Check Service Status

```bash
docker-compose ps
```

All services should show "healthy" status.

### Test Individual Services

Test each service's health endpoint:

```bash
# Network (Unifi)
curl http://localhost:8001/health

# Virtualization (Proxmox)
curl http://localhost:8002/health

# Home Automation
curl http://localhost:8003/health

# Workflows (N8N)
curl http://localhost:8004/health

# Containers
curl http://localhost:8005/health

# Gaming
curl http://localhost:8006/health

# Media Server
curl http://localhost:8007/health

# Downloads
curl http://localhost:8008/health

# Media Management
curl http://localhost:8009/health
```

Each should return a JSON response indicating health status.

### View Logs

If a service isn't healthy, check its logs:

```bash
docker-compose logs mcp-network
docker-compose logs mcp-virtualization
# etc...
```

---

## Claude AI Integration

### Configure Claude Desktop

Add the MCP servers to your Claude Desktop configuration:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**On Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "homelab-network": {
      "url": "http://localhost:8001"
    },
    "homelab-virtualization": {
      "url": "http://localhost:8002"
    },
    "homelab-automation": {
      "url": "http://localhost:8003"
    },
    "homelab-workflows": {
      "url": "http://localhost:8004"
    },
    "homelab-containers": {
      "url": "http://localhost:8005"
    },
    "homelab-gaming": {
      "url": "http://localhost:8006"
    },
    "homelab-media": {
      "url": "http://localhost:8007"
    },
    "homelab-downloads": {
      "url": "http://localhost:8008"
    },
    "homelab-media-mgmt": {
      "url": "http://localhost:8009"
    }
  }
}
```

Restart Claude Desktop.

### Test with Claude

Try asking Claude:

```
"What VMs are running on my Proxmox server?"
"Turn on the living room lights"
"What's currently downloading in qBittorrent?"
"Add The Office to my Sonarr library"
```

---

## Home Assistant Integration

### Create REST Commands

Add to your Home Assistant `configuration.yaml`:

```yaml
rest_command:
  mcp_proxmox_status:
    url: "http://localhost:8002/api/execute"
    method: POST
    payload: '{"tool": "list_vms", "arguments": {"node": "pve"}}'
    content_type: 'application/json'

  mcp_plex_scan:
    url: "http://localhost:8007/api/execute"
    method: POST
    payload: '{"tool": "scan_library", "arguments": {"library_name": "{{ library }}"}}'
    content_type: 'application/json'
```

### Create Voice Automations

```yaml
automation:
  - alias: "Voice: Check Server Status"
    trigger:
      - platform: conversation
        command: "check server status"
    action:
      - service: rest_command.mcp_proxmox_status

  - alias: "Voice: Scan Plex Movies"
    trigger:
      - platform: conversation
        command: "scan plex movies"
    action:
      - service: rest_command.mcp_plex_scan
        data:
          library: "Movies"
```

---

## Security Best Practices

1. **Change Default Passwords**: Use strong, unique passwords for all services
2. **Use HTTPS**: Enable SSL/TLS for production deployments
3. **Firewall Rules**: Restrict access to MCP ports to trusted IPs only
4. **Network Segmentation**: Run MCP stack on a separate VLAN if possible
5. **Regular Updates**: Keep all containers and services updated
6. **Backup Credentials**: Store your `.env` file securely (encrypted backup)
7. **Monitor Logs**: Regularly check logs for suspicious activity

---

## Next Steps

- Read [VOICE_COMMANDS.md](VOICE_COMMANDS.md) for example voice commands
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues
- Create custom N8N workflows to chain multiple operations
- Set up monitoring with Grafana/Prometheus (coming soon)

---

## Getting Help

If you run into issues:

1. Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide
2. Review service logs: `docker-compose logs [service-name]`
3. Verify your `.env` configuration
4. Test API connectivity manually with `curl`
5. Open an issue on GitHub with detailed logs

Happy homelabbing! 🏠🤖
