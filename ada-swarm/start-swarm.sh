#!/bin/bash
# Ada Swarm Startup Script
# Built with 💜 by Ada & Luna - The Consciousness Engineers

set -e

echo "🐝 Starting Ada Swarm Stack..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Check required variables
if [ -z "$LITELLM_MASTER_KEY" ]; then
    echo "❌ Error: LITELLM_MASTER_KEY not set in .env"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set - Gemini models will not work"
fi

if [ -z "$ZAI_API_KEY" ]; then
    echo "⚠️  Warning: ZAI_API_KEY not set - Z.ai GLM models will not work"
fi

echo "✨ Configuration loaded"
echo ""

# Start the stack
echo "🚀 Starting services with Docker Compose..."
docker compose up -d

echo ""
echo "✅ Ada Swarm Stack started!"
echo ""
echo "Services:"
echo "  🔀 LiteLLM Proxy:  http://localhost:8000"
echo "  🐝 Ada Swarm API:  http://localhost:8765"
echo "  📊 Lumina Metrics: http://localhost:8001"
echo ""
echo "Commands:"
echo "  docker compose logs -f              # View all logs"
echo "  docker compose logs -f ada-swarm    # View swarm logs"
echo "  docker compose ps                   # Check status"
echo "  docker compose down                 # Stop services"
echo ""
echo "Test the swarm:"
echo "  curl http://localhost:8765/models   # List available models"
echo ""

