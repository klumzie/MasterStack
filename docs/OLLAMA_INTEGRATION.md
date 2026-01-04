# Ollama Integration Guide

This guide explains how to use your MCP homelab stack with Ollama through the ollama-mcp-bridge.

## What is ollama-mcp-bridge?

The ollama-mcp-bridge creates a transparent proxy layer between Ollama and your MCP servers. It allows you to use all your homelab tools directly within Ollama conversations - locally or through any Ollama-compatible interface.

### Key Features

- **All Tools Available**: Every tool from all 9 MCP servers accessible in Ollama
- **Ollama API Compatible**: Works with any Ollama client or UI
- **Streaming Support**: Real-time streaming responses
- **Zero Configuration**: Auto-loads all tools on startup
- **Local & Remote**: Use Ollama running locally or on a remote server

---

## Quick Start

### Prerequisites

1. **Ollama Installed and Running**
   - Local: `http://localhost:11434`
   - Remote: Update `OLLAMA_URL` in `.env`

   Install Ollama: https://ollama.ai/

2. **MCP Stack Configured**
   - Complete `.env` configuration
   - At least one service configured (Proxmox, Home Assistant, etc.)

### Start the Bridge

The ollama-mcp-bridge is included in the docker-compose stack:

```bash
# Start everything including the bridge
docker-compose up -d

# Or start just the bridge (if other services already running)
docker-compose up -d ollama-mcp-bridge
```

### Verify Bridge is Running

```bash
# Check bridge health
curl http://localhost:8010/health

# Check bridge version
curl http://localhost:8010/version
```

---

## Using Ollama with MCP Tools

### Configuration

The bridge runs on **port 8010** and proxies to your Ollama instance.

**Point your Ollama client to the bridge instead of Ollama directly:**

- **Standard Ollama**: `http://localhost:11434`
- **With MCP Bridge**: `http://localhost:8010`

### Example Usage

#### Command Line

```bash
# Use Ollama through the bridge
curl http://localhost:8010/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {
      "role": "user",
      "content": "What VMs are running on my Proxmox server?"
    }
  ]
}'
```

Ollama will automatically:
1. See the available tools from your MCP servers
2. Choose the appropriate tool (e.g., `list_vms`)
3. Execute it through the MCP server
4. Return the results in the response

#### Ollama Python Library

```python
import ollama

# Point to the bridge instead of Ollama directly
client = ollama.Client(host='http://localhost:8010')

response = client.chat(
    model='llama3.2',
    messages=[
        {
            'role': 'user',
            'content': 'Turn on the living room lights and tell me what\'s new on Plex'
        }
    ]
)

print(response['message']['content'])
```

#### Open WebUI

If you're using Open WebUI:

1. Go to Settings → Connections
2. Set Ollama API URL to: `http://localhost:8010`
3. Save and restart

Now all your conversations have access to your homelab tools!

---

## Available Tools

When connected, Ollama has access to all tools from your MCP servers:

### Network Management (Unifi)
- `list_devices` - List all network devices
- `list_clients` - List connected clients
- `block_client` - Block a client by MAC
- `restart_device` - Restart a network device
- `list_wlans` - List wireless networks

### Virtualization (Proxmox)
- `list_nodes` - List Proxmox nodes
- `list_vms` - List virtual machines
- `start_vm` / `stop_vm` / `reboot_vm` - Control VMs
- `vm_status` - Get VM status
- `create_snapshot` - Create VM snapshot

### Home Automation (Home Assistant)
- `list_entities` - List all entities
- `get_entity_state` - Get entity state
- `turn_on` / `turn_off` - Control devices
- `set_temperature` - Control climate
- `trigger_automation` - Run automations

### Workflows (N8N)
- `list_workflows` - List all workflows
- `trigger_workflow` - Execute a workflow
- `list_executions` - View workflow history

### Container Management (Docker)
- `list_containers` - List all containers
- `start_container` / `stop_container` - Control containers
- `get_logs` - View container logs
- `get_stats` - Container resource usage

### Gaming (Minecraft)
- `list_servers` - List Minecraft servers
- `execute_command` - Run RCON commands
- `list_players` - See online players
- `send_message` - Broadcast messages

### Media Server (Plex)
- `list_libraries` - List Plex libraries
- `scan_library` - Scan for new content
- `get_recently_added` - Recent content
- `get_sessions` - Active playback
- `search` - Search media

### Downloads (qBittorrent)
- `list_torrents` - List all torrents
- `add_torrent` - Add new torrent
- `pause_torrent` / `resume_torrent` - Control torrents
- `get_stats` - Download statistics

### Media Management (*Arr)
- `sonarr_get_series` / `radarr_get_movies` - List content
- `sonarr_search` / `radarr_search` - Search for content
- `*_get_queue` - View download queues
- `*_get_calendar` - Upcoming releases

---

## Example Conversations

### Basic Queries

```
You: What VMs are currently running?
Ollama: [Calls list_vms tool] You have 5 VMs running: web-server, database, mail-server, docker-host, and test-vm.

You: How many people are watching Plex right now?
Ollama: [Calls get_sessions tool] There are 2 active Plex sessions: John is watching The Office on Living Room TV, and Sarah is watching Inception on her iPad.

You: What's downloading?
Ollama: [Calls list_torrents tool] You have 3 active torrents: Ubuntu-24.04.iso (85% complete), Season 3 of Breaking Bad (45% complete), and The Matrix 4K (12% complete).
```

### Complex Operations

```
You: Set up my evening routine: turn on living room lights, set them to 30%, turn on the TV, and start the Plex server VM if it's not running
Ollama: [Calls multiple tools]
1. [turn_on: light.living_room]
2. [turn_on: light.living_room with brightness 30%]
3. [turn_on: media_player.living_room_tv]
4. [vm_status: checks Plex VM]
5. [start_vm: starts Plex VM if needed]

I've set up your evening routine:
- Living room lights are on at 30% brightness
- Living room TV is turned on
- Plex server VM was already running

You're all set for your evening!
```

### Troubleshooting Queries

```
You: Why is my network slow? Check if someone is downloading
Ollama: [Calls list_clients and list_torrents]
I found the issue - you have 3 active torrents downloading at 45 MB/s total. Additionally, there are 12 clients connected to your network. The torrent "Linux ISOs Collection" is using 30 MB/s alone. Would you like me to pause some torrents?
```

---

## Configuration Details

### Environment Variables

Set in `.env`:

```env
# Ollama instance location
OLLAMA_URL=http://host.docker.internal:11434

# CORS origins (for web UIs)
CORS_ORIGINS=*
```

### MCP Configuration File

The bridge uses `mcp-config.json` to know which MCP servers to load:

```json
{
  "mcpServers": {
    "homelab-network": {
      "command": "python",
      "args": ["/mcp-servers/network/server.py"],
      "env": { ... }
    },
    ...
  }
}
```

This file is automatically configured and includes all 9 MCP servers.

### Port Configuration

- **8010**: ollama-mcp-bridge (Ollama API with MCP tools)
- **8001-8009**: Individual MCP servers (for Claude AI)
- **11434**: Ollama (standard, if running locally)

---

## Troubleshooting

### Bridge Won't Start

**Check logs:**
```bash
docker-compose logs ollama-mcp-bridge
```

**Common issues:**
- Ollama not running: Start Ollama first
- Wrong OLLAMA_URL: Check if Ollama is accessible
- MCP servers failing: Check individual server configs in `.env`

### Tools Not Appearing

**Verify MCP servers are loading:**
```bash
docker-compose logs ollama-mcp-bridge | grep "MCP server"
```

You should see startup messages for each configured server.

**Check mcp-config.json:**
```bash
docker-compose exec ollama-mcp-bridge cat /app/config/mcp-config.json
```

### Ollama Not Calling Tools

**Possible causes:**
1. **Model doesn't support tools**: Use models with tool support (llama3.2, mistral, etc.)
2. **Query not clear**: Be specific about what you want to do
3. **Tools not loaded**: Check bridge logs for MCP server errors

**Test manually:**
```bash
curl http://localhost:8010/api/chat -d '{
  "model": "llama3.2",
  "messages": [
    {"role": "user", "content": "List all network devices"}
  ]
}'
```

### CORS Errors

If using a web UI and seeing CORS errors:

1. Update `CORS_ORIGINS` in `.env`:
   ```env
   CORS_ORIGINS=http://localhost:3000,http://localhost:8080
   ```

2. Restart the bridge:
   ```bash
   docker-compose restart ollama-mcp-bridge
   ```

---

## Advanced Usage

### Using Remote Ollama

If Ollama runs on a different machine:

```env
OLLAMA_URL=http://192.168.1.100:11434
```

### Multiple Ollama Instances

Run multiple bridges for different Ollama instances:

```yaml
ollama-mcp-bridge-local:
  # ... config for local Ollama

ollama-mcp-bridge-remote:
  # ... config for remote Ollama
  ports:
    - "8011:8000"
  command: ["ollama-mcp-bridge", "--ollama-url", "http://remote-ollama:11434"]
```

### Custom Tool Filtering

To use only specific MCP servers, edit `mcp-config.json` and remove unwanted servers:

```json
{
  "mcpServers": {
    "homelab-automation": { ... },
    "homelab-media": { ... }
  }
}
```

Then restart:
```bash
docker-compose restart ollama-mcp-bridge
```

---

## Integration Examples

### Chatbot Integration

Use the bridge in your custom chatbot:

```python
import requests

def chat_with_homelab(message):
    response = requests.post('http://localhost:8010/api/chat', json={
        'model': 'llama3.2',
        'messages': [{'role': 'user', 'content': message}]
    })
    return response.json()['message']['content']

# Example usage
print(chat_with_homelab("What's the status of my Proxmox VMs?"))
print(chat_with_homelab("Turn on bedroom lights"))
```

### Slack Bot

```python
from slack_bolt import App
import ollama

app = App(token="xoxb-your-token")
client = ollama.Client(host='http://localhost:8010')

@app.message("homelab")
def handle_homelab(message, say):
    response = client.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': message['text']}]
    )
    say(response['message']['content'])

app.start(port=3000)
```

### Voice Assistant

Integrate with Home Assistant's voice assistant:

```yaml
conversation:
  intents:
    GetServerStatus:
      - "What servers are running"
      - "Check homelab status"

automation:
  - alias: "Voice: Homelab Query"
    trigger:
      platform: conversation
      command:
        - "What servers are running"
    action:
      - service: rest_command.ollama_chat
        data:
          message: "{{ trigger.phrase }}"
```

---

## Performance Tips

1. **Use Fast Models**: For quick responses, use smaller models like `llama3.2:1b`
2. **Limit Tool Scope**: Only enable MCP servers you need
3. **Cache Responses**: Implement caching for repeated queries
4. **Async Processing**: Use async clients for better performance

---

## Security Considerations

1. **Network Isolation**: Run the bridge on a private network
2. **CORS Settings**: Restrict CORS origins in production
3. **Authentication**: Consider adding authentication layer
4. **API Keys**: Protect your `.env` file with proper permissions

---

## Next Steps

- Read [VOICE_COMMANDS.md](VOICE_COMMANDS.md) for command examples
- Explore [SETUP.md](SETUP.md) for detailed configuration
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

## Getting Help

**Bridge Issues:**
- GitHub: https://github.com/flexnst/ollama-mcp-bridge
- Check logs: `docker-compose logs ollama-mcp-bridge`

**MCP Server Issues:**
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Check individual server logs

---

Enjoy controlling your entire homelab through natural conversation with Ollama! 🤖🏠
