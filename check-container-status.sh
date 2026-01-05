#!/bin/bash
# Script to diagnose MCP container issues

echo "=== Checking container status ==="
ssh klumzie@192.168.1.204 "docker ps -a | grep mcp-homeautomation"

echo ""
echo "=== Checking container logs (last 50 lines) ==="
ssh klumzie@192.168.1.204 "docker logs --tail 50 mcp-homeautomation 2>&1"

echo ""
echo "=== Checking if container is restarting ==="
ssh klumzie@192.168.1.204 "docker inspect mcp-homeautomation --format='{{.State.Status}} - Restarts: {{.RestartCount}}'"

echo ""
echo "=== Checking healthcheck status ==="
ssh klumzie@192.168.1.204 "docker inspect mcp-homeautomation --format='{{json .State.Health}}' | python3 -m json.tool"
