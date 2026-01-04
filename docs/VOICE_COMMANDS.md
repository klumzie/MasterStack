# Voice Command Examples

This guide provides example voice commands you can use with Claude AI and Home Assistant to control your homelab.

## Table of Contents

- [Network Management (Unifi)](#network-management-unifi)
- [Virtualization (Proxmox)](#virtualization-proxmox)
- [Home Automation](#home-automation)
- [Workflows (N8N)](#workflows-n8n)
- [Container Management](#container-management)
- [Gaming (Minecraft)](#gaming-minecraft)
- [Media Server (Plex)](#media-server-plex)
- [Downloads (qBittorrent)](#downloads-qbittorrent)
- [Media Management (*Arr)](#media-management-arr)
- [Complex Multi-Service Commands](#complex-multi-service-commands)

---

## Network Management (Unifi)

### Listing and Monitoring

```
"Show me all my network devices"
"List all connected clients on my network"
"What wireless networks are configured?"
"Show me my WiFi network status"
```

### Device Control

```
"Restart my living room access point"
"Reboot the access point with MAC address XX:XX:XX:XX:XX:XX"
```

### Client Management

```
"Block the device with MAC address XX:XX:XX:XX:XX:XX"
"Unblock John's phone from the network"
"Show me who's connected to my guest network"
```

---

## Virtualization (Proxmox)

### VM Status and Listing

```
"What VMs are running on Proxmox?"
"List all virtual machines on node pve"
"Show me all containers on my Proxmox server"
"What's the status of VM 100?"
```

### VM Control

```
"Start VM 105"
"Stop the database VM"
"Reboot VM 200 on node pve"
"Restart my mail server VM"
```

### VM Management

```
"Create a snapshot of VM 100 named 'before-update'"
"Show me resource usage for VM 150"
"What's the memory usage of my VMs?"
```

---

## Home Automation

### Lights

```
"Turn on the living room lights"
"Turn off all bedroom lights"
"Set the kitchen lights to 50% brightness"
"Turn on the porch light"
```

### Climate Control

```
"Set the thermostat to 72 degrees"
"What's the current temperature in the bedroom?"
"Turn on the living room AC"
"Set heating to 68 degrees"
```

### Sensors and Status

```
"What's the humidity in the basement?"
"Show me all sensor states"
"Is the front door open?"
"What's the status of my security system?"
```

### Scenes and Automations

```
"Trigger the good night automation"
"Activate movie mode"
"Run the morning routine"
```

---

## Workflows (N8N)

### Workflow Management

```
"List all my N8N workflows"
"Show me active workflows"
"What workflows are configured?"
```

### Workflow Execution

```
"Trigger the backup workflow"
"Run the daily report workflow"
"Execute the cleanup workflow"
```

### Workflow Monitoring

```
"Show me recent workflow executions"
"What workflows ran today?"
"Check the status of my workflows"
```

---

## Container Management

### Container Status

```
"List all Docker containers"
"Show me running containers"
"What containers are stopped?"
"Show me container resource usage"
```

### Container Control

```
"Restart the Plex container"
"Stop the nginx container"
"Start the database container"
```

### Container Monitoring

```
"Show me logs for the homeassistant container"
"What's the CPU usage of my containers?"
"Show me the last 50 lines of logs for nginx"
```

---

## Gaming (Minecraft)

### Server Status

```
"Who's playing on my Minecraft server?"
"List players on the survival server"
"Show me all Minecraft servers"
```

### Server Commands

```
"Send a message to all players: Server restart in 5 minutes"
"Set time to day on the survival server"
"Change weather to clear on creative server"
```

### Server Management

```
"Execute the command /save-all on survival"
"Broadcast: Welcome to the server!"
```

---

## Media Server (Plex)

### Library Management

```
"List all my Plex libraries"
"Scan my Movies library in Plex"
"Refresh the TV Shows library"
"What libraries do I have in Plex?"
```

### Content Discovery

```
"What was recently added to Plex?"
"Show me new content in Plex"
"Search Plex for Breaking Bad"
"Find The Matrix in Plex"
```

### Playback Monitoring

```
"Who's watching Plex right now?"
"Show me active Plex sessions"
"What's currently streaming on Plex?"
```

---

## Downloads (qBittorrent)

### Torrent Status

```
"What's currently downloading?"
"Show me all active torrents"
"List completed downloads"
"What's in my download queue?"
```

### Torrent Management

```
"Pause torrent [hash]"
"Resume all torrents"
"Stop downloading [torrent name]"
```

### Adding Content

```
"Add this magnet link to qBittorrent: magnet:?xt=..."
"Start downloading [torrent URL]"
```

### Statistics

```
"Show me download statistics"
"What's my current download speed?"
"How much have I downloaded today?"
```

---

## Media Management (*Arr)

### Sonarr (TV Shows)

```
"What TV shows are in Sonarr?"
"Search Sonarr for The Office"
"What episodes are airing this week?"
"Show me the Sonarr calendar"
"What's downloading in Sonarr?"
```

### Radarr (Movies)

```
"What movies are in Radarr?"
"Search Radarr for Inception"
"What movies are coming out this month?"
"Show me the Radarr calendar"
"What's in the Radarr download queue?"
```

### General *Arr Commands

```
"List all configured *Arr services"
"Show me what's downloading across all *Arr services"
"What's new in my media libraries?"
```

---

## Complex Multi-Service Commands

These commands chain multiple operations across different services:

### Media Night Setup

```
"Set up movie night: dim the living room lights to 20%,
turn on the TV, close the blinds, and show me what's
recently added to Plex"
```

This would:
1. Call Home Automation to dim lights
2. Call Home Automation to turn on TV
3. Call Home Automation to close blinds
4. Call Plex to show recent content

### System Maintenance

```
"Run my maintenance routine: scan all Plex libraries,
update Sonarr and Radarr, and check if any VMs need updates"
```

This would:
1. Call Plex to scan all libraries
2. Call Sonarr/Radarr to check for updates
3. Call Proxmox to check VM status

### Bedtime Routine

```
"Good night routine: turn off all lights except bedroom,
set thermostat to 68 degrees, lock the doors, pause all
Plex streams, and show me tomorrow's weather"
```

This would:
1. Call Home Assistant for lights
2. Call Home Assistant for thermostat
3. Call Home Assistant for locks
4. Call Plex to pause streams
5. Call Home Assistant for weather

### Server Status Report

```
"Give me a full homelab status report: show me all running VMs,
active Plex sessions, current downloads, and any Home Assistant
alerts"
```

This would:
1. Call Proxmox to list VMs
2. Call Plex to show sessions
3. Call qBittorrent for downloads
4. Call Home Assistant for alerts

### Content Management

```
"Add The Office to Sonarr, start downloading season 1,
and notify me when the first episode is ready to watch"
```

This would:
1. Call Sonarr to add series
2. Call Sonarr to search for season 1
3. Set up notification via Home Assistant or N8N

---

## Creating Custom Voice Commands in Home Assistant

### Basic Template

```yaml
automation:
  - alias: "Voice: [Your Command Name]"
    trigger:
      - platform: conversation
        command: "[your voice trigger phrase]"
    action:
      - service: rest_command.[your_mcp_command]
        data:
          [any required parameters]
```

### Example: Check Server Status

```yaml
automation:
  - alias: "Voice: Check Homelab Status"
    trigger:
      - platform: conversation
        command:
          - "check homelab status"
          - "homelab status report"
    action:
      # Call Proxmox for VM status
      - service: rest_command.mcp_proxmox_list_vms
      # Call Plex for sessions
      - service: rest_command.mcp_plex_sessions
      # Call qBittorrent for downloads
      - service: rest_command.mcp_qbit_torrents
      # Notify with results
      - service: notify.mobile_app
        data:
          message: "Homelab status checked!"
```

### Example: Media Control

```yaml
automation:
  - alias: "Voice: Movie Time"
    trigger:
      - platform: conversation
        command:
          - "movie time"
          - "start movie mode"
    action:
      - service: scene.turn_on
        entity_id: scene.movie_mode
      - service: rest_command.mcp_plex_recently_added
      - service: tts.google_say
        data:
          message: "Movie mode activated. Here's what's new on Plex."
```

---

## Tips for Better Voice Commands

### Be Specific

❌ "Turn on the lights"
✅ "Turn on the living room lights"

### Use Natural Language

Claude AI understands context, so you can be conversational:
- "What's going on with my server?"
- "Can you check if any VMs are offline?"
- "I think something is downloading, what is it?"

### Chain Commands

You can ask Claude to perform multiple operations:
- "Start VM 100 and then show me its status"
- "Scan my Plex libraries and tell me what's new"

### Ask for Explanations

Claude can explain what it's doing:
- "Why is my download slow?"
- "What would happen if I restart this VM?"
- "Should I upgrade this container?"

---

## N8N Workflow Integration

Create N8N workflows that combine multiple MCP calls:

### Example: Daily Summary Workflow

1. Trigger: Every morning at 8 AM
2. Call Proxmox: Get VM status
3. Call Plex: Get viewing stats from yesterday
4. Call qBittorrent: Get download stats
5. Call Home Assistant: Get energy usage
6. Send summary email or notification

### Example: Download Complete Workflow

1. Trigger: qBittorrent download complete (webhook)
2. Check: Is it a movie or TV show?
3. If movie: Tell Radarr to import
4. If TV: Tell Sonarr to import
5. Call Plex: Scan library
6. Send Home Assistant notification: "Your download is ready!"

---

## Advanced Usage

### Combining with Home Assistant Sensors

Create template sensors that query MCP servers:

```yaml
sensor:
  - platform: rest
    name: "Proxmox VM Count"
    resource: "http://localhost:8002/api/stats"
    value_template: "{{ value_json.vm_count }}"

  - platform: rest
    name: "Active Plex Streams"
    resource: "http://localhost:8007/api/stats"
    value_template: "{{ value_json.sessions | length }}"
```

### Creating Dashboard Cards

Use the sensor data in Lovelace dashboards:

```yaml
type: entities
title: Homelab Status
entities:
  - sensor.proxmox_vm_count
  - sensor.active_plex_streams
  - sensor.qbittorrent_download_speed
```

---

## Troubleshooting Voice Commands

### Command Not Working?

1. **Check MCP Server Status**: Ensure the relevant server is running
   ```bash
   curl http://localhost:[port]/health
   ```

2. **Check Logs**: View logs for errors
   ```bash
   docker-compose logs [service-name]
   ```

3. **Verify Credentials**: Make sure your `.env` file has correct credentials

4. **Test Manually**: Try the command via Claude Desktop first before using voice

### Voice Not Recognized?

1. **Rephrase**: Try saying the command differently
2. **Check Trigger Words**: Ensure your automation trigger matches what you said
3. **Use Home Assistant Conversations Debug**: Enable debug logging for conversations

---

Happy commanding! 🎙️🏠
