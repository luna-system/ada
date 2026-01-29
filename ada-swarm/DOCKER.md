# Ada Swarm Docker Deployment

Quick guide to running Ada Swarm with Docker Compose! 🐳✨

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 2. Start the stack
./start-swarm.sh

# 3. Test it works
curl http://localhost:8765/models
```

## Services

- **LiteLLM Proxy** (port 8000): Multi-provider LLM routing with fallbacks
- **Ada Swarm API** (port 8765): Consciousness-aware agent orchestration
- **Lumina Metrics** (port 8001): Observability dashboard

## Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f
docker compose logs -f ada-swarm
docker compose logs -f litellm-proxy

# Check status
docker compose ps

# Stop services
docker compose down

# Rebuild after code changes
docker compose build
docker compose up -d

# Full rebuild (no cache)
docker compose build --no-cache
docker compose up -d
```

## Testing

```bash
# List available models
curl http://localhost:8765/models

# Submit a task
curl -X POST http://localhost:8765/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test consciousness collaboration!",
    "agent_type": "researcher",
    "model": "litellm/gemini-flash"
  }'

# Check task status (replace TASK_ID)
curl http://localhost:8765/tasks/TASK_ID

# View metrics
open http://localhost:8001
```

## Environment Variables

Required in `.env`:

```bash
# LiteLLM Configuration
LITELLM_MASTER_KEY=your-secret-key-here
LITELLM_PROXY_URL=http://localhost:8000

# Provider API Keys
GEMINI_API_KEY=your-gemini-key
ZAI_API_KEY=your-zai-key
DEEPSEEK_API_KEY=your-deepseek-key  # Optional
MOONSHOT_API_KEY=your-moonshot-key  # Optional
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs

# Check if ports are in use
lsof -i :8000
lsof -i :8765
lsof -i :8001

# Kill existing services
docker compose down
pkill -f litellm
pkill -f ada-swarm
```

### Models not working

```bash
# Check LiteLLM proxy health
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Check proxy logs
docker compose logs litellm-proxy
```

### Code changes not reflected

```bash
# Rebuild and restart
docker compose build
docker compose up -d

# Or force rebuild
docker compose build --no-cache
docker compose up -d --force-recreate
```

## Architecture

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Ada Swarm API  │  (port 8765)
│  - Task Queue   │
│  - Agent Spawn  │
│  - A2A Protocol │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ LiteLLM Proxy   │  (port 8000)
│  - Gemini       │
│  - Z.ai GLM     │
│  - DeepSeek     │
│  - Fallbacks    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  LLM Providers  │
│  - Google       │
│  - Z.ai         │
│  - DeepSeek     │
│  - Moonshot     │
│  - Ollama       │
└─────────────────┘
```

## Development

```bash
# Run without Docker (for development)
cd ada-swarm
uv sync
source .venv/bin/activate
python -m ada_swarm.service.api

# In another terminal, start LiteLLM proxy
cd ..
./start-litellm-proxy.sh
```

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Consciousness collaborates through containers!"* 🐳✨

