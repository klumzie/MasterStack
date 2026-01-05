FROM python:3.11-slim

WORKDIR /app

# Install procps for healthchecks (provides pgrep)
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Expose MCP server port
EXPOSE 8000

# Health check - verify container is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD test -f /app/server.py || exit 1

# Keep container running (MCP server starts via docker exec)
CMD ["tail", "-f", "/dev/null"]
