# MCP Homelab Stack

A comprehensive Model Context Protocol (MCP) server stack for managing your entire homelab infrastructure through Claude AI, Ollama, and voice commands via Home Assistant.

## 🏗️ Architecture

This stack provides MCP servers for all your homelab services, allowing Claude AI and Ollama to interact with:

- **Network Management** (Unifi): Devices, clients, WiFi networks
- **Virtualization** (Proxmox): VMs, containers, snapshots  
- **Home Automation** (Home Assistant): Entities, automations, sensors
- **Workflows** (N8N): Trigger and monitor workflows
- **Container Management** (Docker/Portainer): Containers, logs, stats
- **Gaming** (Minecraft): Server control, commands, players
- **Media Server** (Plex): Libraries, scans, sessions
- **Downloads** (qBittorrent): Torrents, queue management
- **Media Management** (Arr Suite): Sonarr, Radarr, Lidarr, Prowlarr, Readarr

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Portainer (optional, for web UI management)
- All services you want to control already running with API access enabled

### Installation

1. **Clone or create this repository structure**

2. **Copy and configure environment variables**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual credentials
   ```

3. **Build and start the stack**
   ```bash
   docker-compose up -d
   ```

4. **Verify all services are healthy**
   ```bash
   docker-compose ps
   ```

## 🤖 AI Integration

### Claude AI
Use the MCP servers directly with Claude Desktop by configuring them in your Claude settings.

### Ollama (Local LLMs)
The stack includes **ollama-mcp-bridge** which makes all your homelab tools available to Ollama and any Ollama-compatible interface. This means you can:
- Use local LLMs (Llama, Mistral, etc.) to control your homelab
- Keep everything private and local
- Use any Ollama-compatible UI (Open WebUI, etc.)

See [OLLAMA_INTEGRATION.md](docs/OLLAMA_INTEGRATION.md) for detailed setup and usage.

## 📋 Service Ports

Each MCP server runs on a dedicated port:

- **mcp-network**: 8001 (Unifi)
- **mcp-virtualization**: 8002 (Proxmox)
- **mcp-homeautomation**: 8003 (Home Assistant)
- **mcp-workflows**: 8004 (N8N)
- **mcp-containers**: 8005 (Docker/Portainer)
- **mcp-gaming**: 8006 (Minecraft)
- **mcp-media-server**: 8007 (Plex)
- **mcp-downloads**: 8008 (qBittorrent)
- **mcp-media-management**: 8009 (Arr Suite)
- **ollama-mcp-bridge**: 8010 (Ollama API with MCP tools)

## 🔧 Configuration

### Required Environment Variables

See `.env.example` for all required variables. Key configurations:

#### Unifi
```env
UNIFI_HOST=https://unifi.local
UNIFI_USERNAME=admin
UNIFI_PASSWORD=your_password
```

#### Proxmox
```env
PROXMOX_HOST=https://proxmox.local:8006
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=mcp-token
PROXMOX_TOKEN_VALUE=your-token-value
```

#### Home Assistant
```env
HA_URL=http://homeassistant.local:8123
HA_TOKEN=your_long_lived_access_token
```

### Getting API Tokens

- **Home Assistant**: Settings → People → Your User → Long-Lived Access Tokens
- **Proxmox**: Datacenter → Permissions → API Tokens
- **Portainer**: Settings → API → Access tokens
- **Plex**: Account → Settings → Show Advanced → Get Token
- **N8N**: Settings → API → Create API Key
- **Sonarr/Radarr**: Settings → General → API Key

## 📖 Usage Examples

### With Claude AI

Once configured, you can interact with your homelab through Claude:

```
You: "What VMs are running on Proxmox?"
Claude: [calls mcp-virtualization] "You have 5 VMs running..."

You: "Turn on the living room lights"
Claude: [calls mcp-homeautomation] "I've turned on the living room lights"

You: "Add Breaking Bad to Sonarr"
Claude: [calls mcp-media-management] "I've added Breaking Bad to your Sonarr library"

You: "What's currently downloading?"
Claude: [calls mcp-downloads] "You have 3 active torrents..."
```

### With Home Assistant Voice

Configure Home Assistant automations to trigger N8N workflows that call these MCP servers:

```yaml
# Example automation
automation:
  - alias: "Voice: Check Server Status"
    trigger:
      - platform: conversation
        command: "check server status"
    action:
      - service: rest_command.mcp_proxmox_status
```

## 🏗️ Project Structure

```
mcp-homelab-stack/
├── docker-compose.yml          # Main stack definition
├── .env.example               # Environment template
├── .env                       # Your configuration (gitignored)
├── README.md                  # This file
├── mcp-servers/              # MCP server implementations
│   ├── network/              # Unifi controller
│   ├── virtualization/       # Proxmox
│   ├── homeautomation/       # Home Assistant
│   ├── workflows/            # N8N
│   ├── containers/           # Docker/Portainer
│   ├── gaming/               # Minecraft
│   ├── media-server/         # Plex
│   ├── downloads/            # qBittorrent
│   └── media-management/     # Arr suite
└── docs/                     # Additional documentation
    ├── SETUP.md              # Detailed setup guide
    ├── VOICE_COMMANDS.md     # Voice command examples
    └── TROUBLESHOOTING.md    # Common issues
```

## 🔐 Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- Use strong, unique passwords for all services
- Consider running this stack on a private network
- Enable SSL/TLS for production deployments
- Regularly update all containers

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs [service-name]

# Verify environment variables
docker-compose config
```

### Can't connect to service
- Verify the service is running and accessible
- Check firewall rules
- Verify API credentials in `.env`
- Test API access manually: `curl -H "Authorization: Bearer TOKEN" http://service/api`

### Health check failing
```bash
# Check individual service health
curl http://localhost:8001/health  # Network
curl http://localhost:8002/health  # Virtualization
# etc...
```

## 📚 Additional Documentation

- [Detailed Setup Guide](docs/SETUP.md)
- [Voice Command Examples](docs/VOICE_COMMANDS.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

This is a personal homelab stack, but feel free to:
- Report issues
- Suggest improvements
- Share your own configurations

## 📄 License

MIT License - feel free to use and modify for your own homelab!

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Anthropic Claude](https://www.anthropic.com/claude) - AI assistant
- All the amazing open-source homelab software

## 🚧 Roadmap

- [ ] Add Grafana/Prometheus monitoring
- [ ] Add more Arr services (Bazarr, Overseerr)
- [ ] Implement rate limiting
- [ ] Add authentication layer
- [ ] Create Home Assistant integration blueprints
- [ ] Add backup/restore functionality
