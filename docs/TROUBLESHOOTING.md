# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the MCP Homelab Stack.

## Table of Contents

- [General Debugging](#general-debugging)
- [Container Issues](#container-issues)
- [Service-Specific Issues](#service-specific-issues)
- [Network Issues](#network-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)

---

## General Debugging

### Check Container Status

```bash
# View all containers
docker-compose ps

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs mcp-network

# Follow logs in real-time
docker-compose logs -f mcp-homeautomation
```

### Check Container Health

```bash
# Test health endpoints
curl http://localhost:8001/health  # Network
curl http://localhost:8002/health  # Virtualization
curl http://localhost:8003/health  # Home Automation
curl http://localhost:8004/health  # Workflows
curl http://localhost:8005/health  # Containers
curl http://localhost:8006/health  # Gaming
curl http://localhost:8007/health  # Media Server
curl http://localhost:8008/health  # Downloads
curl http://localhost:8009/health  # Media Management
```

### Validate Configuration

```bash
# Check docker-compose configuration
docker-compose config

# This will show any syntax errors in docker-compose.yml or .env
```

---

## Container Issues

### Container Won't Start

**Symptom**: Container exits immediately after starting

**Debug Steps**:

1. Check the logs:
   ```bash
   docker-compose logs [service-name]
   ```

2. Look for common errors:
   - Missing environment variables
   - Invalid credentials
   - Port already in use
   - Permission issues

3. Try starting the container manually:
   ```bash
   docker-compose up [service-name]
   ```

**Common Solutions**:

- **Missing env vars**: Check your `.env` file
- **Port conflict**: Change the port mapping in `docker-compose.yml`
- **Permission denied**: Check file permissions on mounted volumes

### Container Keeps Restarting

**Symptom**: Container status shows "Restarting"

**Debug Steps**:

1. Check logs for crash reason:
   ```bash
   docker-compose logs [service-name]
   ```

2. Check resource usage:
   ```bash
   docker stats
   ```

3. Verify configuration:
   ```bash
   docker-compose config
   ```

**Common Solutions**:

- **API endpoint unreachable**: Check if the target service (Proxmox, Plex, etc.) is running
- **Invalid credentials**: Verify credentials in `.env`
- **Network issues**: Ensure the container can reach your services
- **Resource limits**: Check if the container is running out of memory

### Health Check Failing

**Symptom**: Container shows "unhealthy" status

**Debug Steps**:

1. Test the health endpoint manually:
   ```bash
   curl -v http://localhost:[port]/health
   ```

2. Check container logs:
   ```bash
   docker-compose logs [service-name]
   ```

3. Exec into the container:
   ```bash
   docker-compose exec [service-name] /bin/bash
   curl localhost:8000/health
   ```

**Common Solutions**:

- **Port not exposed**: Check `docker-compose.yml` port mappings
- **Service not listening**: Check if the Python server started correctly
- **Firewall blocking**: Check firewall rules

---

## Service-Specific Issues

### Network (Unifi)

**Error: "Login failed"**

Solutions:
- Verify `UNIFI_USERNAME` and `UNIFI_PASSWORD` in `.env`
- Check if Unifi controller is accessible
- Try accessing Unifi web UI manually
- Check if account is locked due to failed attempts

**Error: "SSL Certificate verification failed"**

Solutions:
- Set `UNIFI_VERIFY_SSL=false` in `.env`
- Or: Add your Unifi certificate to the container's trust store

**Error: "Connection refused"**

Solutions:
- Verify `UNIFI_HOST` is correct
- Check if Unifi controller is running
- Verify port (usually 8443)
- Check firewall rules

### Virtualization (Proxmox)

**Error: "401 Unauthorized"**

Solutions:
- Verify `PROXMOX_TOKEN_NAME` and `PROXMOX_TOKEN_VALUE`
- Recreate the API token in Proxmox
- Ensure "Privilege Separation" is unchecked when creating token
- Check token hasn't expired

**Error: "SSL Certificate verification failed"**

Solutions:
- Set `PROXMOX_VERIFY_SSL=false` in `.env`
- Or: Use a valid SSL certificate on Proxmox

**Error: "Node not found"**

Solutions:
- Check node name (use `pvesh get /nodes` to list nodes)
- Verify node is online in Proxmox web UI

### Home Automation (Home Assistant)

**Error: "401 Unauthorized"**

Solutions:
- Verify `HA_TOKEN` is correct
- Regenerate long-lived access token
- Check token hasn't been revoked

**Error: "Entity not found"**

Solutions:
- Check entity ID is correct (use Developer Tools → States)
- Verify entity exists and is available
- Check entity naming (case-sensitive)

**Error: "Connection refused"**

Solutions:
- Verify `HA_URL` is correct
- Check if Home Assistant is running
- Verify port (usually 8123)
- Check if Home Assistant is in safe mode

### Workflows (N8N)

**Error: "Invalid API key"**

Solutions:
- Verify `N8N_API_KEY` is correct
- Regenerate API key in N8N
- Check API access is enabled in N8N settings

**Error: "Workflow not found"**

Solutions:
- Check workflow ID is correct
- Verify workflow exists and is active
- List workflows first to get correct IDs

### Containers (Docker/Portainer)

**Error: "Cannot connect to Docker daemon"**

Solutions:
- Verify Docker socket is mounted: `/var/run/docker.sock:/var/run/docker.sock:ro`
- Check Docker service is running on host
- Verify permissions on Docker socket

**Error: "Permission denied"**

Solutions:
- Add user to docker group: `usermod -aG docker $USER`
- Check socket permissions: `ls -l /var/run/docker.sock`
- Restart Docker service

### Gaming (Minecraft)

**Error: "RCON connection failed"**

Solutions:
- Verify `MINECRAFT_SERVERS` JSON is valid
- Check RCON is enabled in `server.properties`
- Verify RCON password matches
- Check Minecraft server is running
- Verify port (usually 25575)

**Error: "Invalid JSON in MINECRAFT_SERVERS"**

Solutions:
- Validate JSON syntax
- Example format:
  ```json
  [{"name":"survival","host":"minecraft.local","port":25575,"password":"rcon_pass"}]
  ```

### Media Server (Plex)

**Error: "401 Unauthorized"**

Solutions:
- Verify `PLEX_TOKEN` is correct
- Regenerate Plex token
- Check token hasn't been revoked

**Error: "Library not found"**

Solutions:
- Check library name is exact match (case-sensitive)
- List libraries first to get correct names
- Verify library exists in Plex

### Downloads (qBittorrent)

**Error: "Login failed"**

Solutions:
- Verify `QBITTORRENT_USERNAME` and `QBITTORRENT_PASSWORD`
- Check if Web UI is enabled in qBittorrent
- Verify port (usually 8080)
- Try logging in via web UI manually

**Error: "Connection refused"**

Solutions:
- Verify `QBITTORRENT_HOST` is correct
- Check if qBittorrent is running
- Verify Web UI is enabled
- Check firewall rules

### Media Management (*Arr)

**Error: "Invalid API key"**

Solutions:
- Verify API keys for each *Arr service
- Regenerate API key in service settings
- Check API key hasn't been rotated

**Error: "Service not configured"**

Solutions:
- Verify URL and API key are set in `.env`
- Check service is running and accessible
- Test API manually:
  ```bash
  curl -H "X-Api-Key: YOUR_KEY" http://sonarr:8989/api/v3/system/status
  ```

---

## Network Issues

### Cannot Reach Service from MCP Container

**Debug Steps**:

1. Test from inside container:
   ```bash
   docker-compose exec [service-name] /bin/bash
   curl [service-url]
   ```

2. Check DNS resolution:
   ```bash
   docker-compose exec [service-name] nslookup [hostname]
   ```

3. Check network connectivity:
   ```bash
   docker-compose exec [service-name] ping [host]
   ```

**Solutions**:

- Use IP addresses instead of hostnames
- Check if services are on same Docker network
- Verify firewall isn't blocking traffic
- Use host network mode if needed:
  ```yaml
  network_mode: host
  ```

### Port Already in Use

**Error**: "Port 8001 is already allocated"

**Solutions**:

1. Find what's using the port:
   ```bash
   sudo lsof -i :8001
   ```

2. Either:
   - Stop the conflicting service
   - Change the port in `docker-compose.yml`:
     ```yaml
     ports:
       - "8010:8000"  # Use port 8010 instead
     ```

### DNS Resolution Failed

**Solutions**:

- Use IP addresses instead of hostnames in `.env`
- Add custom DNS to containers:
  ```yaml
  dns:
    - 8.8.8.8
    - 1.1.1.1
  ```
- Add entries to `/etc/hosts` in container

---

## Performance Issues

### Slow Response Times

**Debug Steps**:

1. Check container resource usage:
   ```bash
   docker stats
   ```

2. Check host system resources:
   ```bash
   top
   htop
   ```

3. Check logs for errors:
   ```bash
   docker-compose logs [service-name]
   ```

**Solutions**:

- Increase container memory limits:
  ```yaml
  deploy:
    resources:
      limits:
        memory: 512M
  ```
- Reduce concurrent operations
- Check target service performance (Proxmox, Plex, etc.)
- Enable caching where applicable

### High Memory Usage

**Solutions**:

- Set memory limits in `docker-compose.yml`
- Restart containers periodically
- Check for memory leaks in logs
- Reduce log verbosity

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"

**Solution**:
```bash
# Rebuild the container
docker-compose build [service-name]
docker-compose up -d [service-name]
```

### "Connection timeout"

**Possible Causes**:
- Service is down
- Firewall blocking connection
- Wrong IP/port
- Network routing issues

**Solutions**:
- Verify service is running
- Check firewall rules
- Test connection manually with `curl` or `telnet`
- Check `.env` configuration

### "Permission denied"

**Solutions**:
- Check file permissions
- Run with appropriate user
- Add user to required groups
- Check SELinux/AppArmor settings

### "Invalid credentials"

**Solutions**:
- Verify credentials in `.env`
- Check for typos (especially quotes)
- Regenerate tokens/passwords
- Test credentials manually

### "Service Unavailable (503)"

**Solutions**:
- Service is starting up (wait a bit)
- Service is overwhelmed (check resources)
- Service is in maintenance mode
- Check service-specific logs

---

## Advanced Debugging

### Enable Debug Logging

Add to docker-compose.yml:

```yaml
environment:
  - LOG_LEVEL=DEBUG
```

### Exec Into Container

```bash
docker-compose exec [service-name] /bin/bash
```

### View Container Inspect

```bash
docker inspect [container-name]
```

### Check Network

```bash
docker network ls
docker network inspect mcp-network
```

### Test API Manually

```bash
# Example: Test Proxmox API
curl -k -H "Authorization: PVEAPIToken=root@pam!mcp-token=YOUR_TOKEN" \
  https://proxmox.local:8006/api2/json/nodes

# Example: Test Home Assistant API
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://homeassistant:8123/api/states
```

---

## Getting Additional Help

If you're still stuck:

1. **Check Logs**: Always start with the logs
   ```bash
   docker-compose logs [service-name] > service-logs.txt
   ```

2. **Test Manually**: Try to access the service API directly

3. **Verify Configuration**: Double-check `.env` and `docker-compose.yml`

4. **Search Issues**: Check GitHub issues for similar problems

5. **Create Issue**: Open a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Relevant logs
   - Your configuration (remove sensitive data)
   - Docker and OS versions

---

## Quick Reference

### Restart Everything

```bash
docker-compose down
docker-compose up -d
```

### Rebuild Everything

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Reset Everything

```bash
docker-compose down -v  # WARNING: This removes volumes!
docker-compose build --no-cache
docker-compose up -d
```

### Check Everything

```bash
docker-compose ps
docker-compose logs --tail=50
curl http://localhost:8001/health
# ... test all health endpoints
```

---

Stay calm and debug on! 🐛🔍
