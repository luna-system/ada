#!/usr/bin/env bash
# Start LiteLLM Proxy Server
# Built with 💜 by Ada & Luna - The Consciousness Engineers

set -euo pipefail

# Activate venv
source /home/luna/Code/ada/.venv/bin/activate

# Set default port
PORT="${LITELLM_PORT:-8000}"

# Start proxy
echo "🚀 Starting LiteLLM Proxy on port $PORT..."
litellm --config litellm-proxy-config.yaml --port "$PORT" --host 0.0.0.0
