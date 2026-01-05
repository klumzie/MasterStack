#!/bin/bash

# MCP Homelab Stack - Quick Start Script

set -e

echo "🏠 MCP Homelab Stack Setup"
echo "=========================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Detect Docker Compose version (V1 or V2)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚙️  Please edit .env file with your actual credentials:"
    echo "   nano .env"
    echo ""
    echo "Press ENTER when you've configured .env, or Ctrl+C to exit and configure manually."
    read -r
fi

echo "🔧 Validating configuration..."
if $DOCKER_COMPOSE config > /dev/null 2>&1; then
    echo "✅ Configuration is valid"
else
    echo "❌ Configuration has errors. Please check your docker-compose.yml and .env file."
    exit 1
fi

echo ""
echo "🏗️  Building containers..."
$DOCKER_COMPOSE build

echo ""
echo "🚀 Starting services..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "🏥 Checking service health..."
echo ""

services=(
  "8001:Network"
  "8002:Virtualization"
  "8003:HomeAutomation"
  "8004:Workflows"
  "8005:Containers"
  "8006:Gaming"
  "8007:MediaServer"
  "8008:Downloads"
  "8009:MediaManagement"
  "8010:OllamaBridge"
)

all_healthy=true

for service in "${services[@]}"; do
  port="${service%%:*}"
  name="${service##*:}"
  
  if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
    echo "✅ $name (port $port) is healthy"
  else
    echo "❌ $name (port $port) is unhealthy"
    all_healthy=false
  fi
done

echo ""

if [ "$all_healthy" = true ]; then
    echo "🎉 All services are healthy!"
    echo ""
    echo "Next steps:"
    echo "1. Configure Claude AI to use these MCP servers"
    echo "2. Use Ollama at http://localhost:8010 (with all MCP tools)"
    echo "3. Set up Home Assistant voice commands"
    echo "4. Create N8N workflows"
    echo ""
    echo "📚 See docs/SETUP.md for detailed configuration"
    echo "📚 See docs/OLLAMA_INTEGRATION.md for Ollama usage"
else
    echo "⚠️  Some services are unhealthy. Check logs with:"
    echo "   $DOCKER_COMPOSE logs [service-name]"
    echo ""
    echo "📚 See docs/TROUBLESHOOTING.md for help"
fi

echo ""
echo "Useful commands:"
echo "  $DOCKER_COMPOSE ps              - View service status"
echo "  $DOCKER_COMPOSE logs -f         - Follow all logs"
echo "  $DOCKER_COMPOSE logs [service]  - View specific service logs"
echo "  $DOCKER_COMPOSE restart         - Restart all services"
echo "  $DOCKER_COMPOSE down            - Stop all services"
