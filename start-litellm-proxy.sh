#!/usr/bin/env bash
# Start LiteLLM Proxy Server
# Built with 💜 by Ada & Luna - The Consciousness Engineers

set -euo pipefail

# Load environment variables from ada-swarm/.env
if [ -f "ada-swarm/.env" ]; then
    set -a
    source ada-swarm/.env
    set +a
fi

# Activate venv
source /home/luna/Code/ada/.venv/bin/activate

# Set default port
PORT="${LITELLM_PORT:-8000}"

# Force asyncio loop for Python 3.14 compatibility (uvloop not supported yet)
export UVICORN_LOOP=asyncio

# Start proxy
echo "🚀 Starting LiteLLM Proxy on port $PORT..."
litellm --config litellm-proxy-config.yaml --port "$PORT" --host 0.0.0.0
