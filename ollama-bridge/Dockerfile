FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y git curl && \
    rm -rf /var/lib/apt/lists/*

# Install ollama-mcp-bridge
RUN pip install --no-cache-dir ollama-mcp-bridge

# Install Python packages needed by MCP servers
RUN pip install --no-cache-dir \
    mcp>=0.9.0 \
    httpx>=0.27.0 \
    docker>=7.0.0 \
    PlexAPI>=4.15.0 \
    qbittorrent-api>=2024.1.0 \
    mcrcon>=0.7.0 \
    fastapi>=0.115.0 \
    uvicorn>=0.32.0 \
    pydantic>=2.0.0

# Create config directory
RUN mkdir -p /app/config

# Expose bridge port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["ollama-mcp-bridge", "--host", "0.0.0.0", "--port", "8000", "--config", "/app/config/mcp-config.json"]
