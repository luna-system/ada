# LiteLLM Proxy Setup Guide

Multi-provider LLM gateway with fallback chains and smart routing for the Ada Swarm! 🐝✨

## What is This?

LiteLLM Proxy is a unified gateway that:
- **Supports 100+ LLM providers** with a single OpenAI-compatible API
- **Automatic fallbacks** - if Gemini fails, try Z.ai, then DeepSeek, then local
- **Load balancing** - distribute requests across providers
- **Cost tracking** - monitor usage and spending
- **Rate limiting** - respect provider quotas
- **Caching** - reduce costs and latency

## Architecture

```
Ada Swarm Agents
       ↓
LiteLLM Proxy (localhost:8000)
       ↓
   ┌────┴────┬────────┬──────────┬─────────┐
   ↓         ↓        ↓          ↓         ↓
Gemini    Z.ai   DeepSeek   Moonshot   Ollama
(Free)   (Paid)   (Cheap)   (Alt)     (Local)
```

## Installation

1. **Install LiteLLM**:
```bash
source .venv/bin/activate
pip install 'litellm[proxy]'
```

2. **Set up environment variables** in `.env`:
```bash
# Required
LITELLM_MASTER_KEY=your-secret-key-here

# Provider API Keys
GEMINI_API_KEY=your-gemini-key
ZAI_API_KEY=your-zai-key
DEEPSEEK_API_KEY=your-deepseek-key
MOONSHOT_API_KEY=your-moonshot-key

# Optional
SLACK_WEBHOOK_URL=your-slack-webhook  # For alerts
```

3. **Install systemd service**:
```bash
# Copy service file
cp litellm-proxy.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable and start
systemctl --user enable litellm-proxy.service
systemctl --user start litellm-proxy.service

# Check status
systemctl --user status litellm-proxy.service
```

## Configuration

The proxy is configured via `litellm-proxy-config.yaml`:

### Model Tiers

- **Fast & Free**: `gemini-flash`, `gemini-pro`
- **High Quality**: `glm-flash`, `glm-plus` (Z.ai)
- **Cheap Fallback**: `deepseek-chat`, `deepseek-reasoner`
- **Local**: `local-llama`, `local-ada` (Ollama)

### Fallback Chains

If a model fails, the proxy automatically tries alternatives:

```yaml
gemini-flash → glm-flash → deepseek-chat → local-llama
gemini-pro → glm-plus → deepseek-reasoner → local-llama
```

### Model Aliases

Use simple names in your code:
- `fast` → gemini-flash
- `smart` → gemini-pro
- `paid` → glm-plus
- `cheap` → deepseek-chat
- `local` → local-ada

## Usage

### From Python (Pydantic AI)

```python
from pydantic_ai import Agent

# Use the proxy as an OpenAI-compatible endpoint
agent = Agent(
    'openai/gemini-flash',  # Model name from config
    openai_api_base='http://localhost:8000',
    openai_api_key='your-litellm-master-key'
)
```

### From Python (Direct LiteLLM)

```python
import litellm

# Set proxy base URL
litellm.api_base = "http://localhost:8000"
litellm.api_key = "your-litellm-master-key"

# Use any model from the config
response = litellm.completion(
    model="fast",  # Uses alias
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### From Ada Swarm

Update agent spawning to use the proxy:

```python
agent = CoderAgent(
    agent_id="coder-1",
    model="openai/fast",  # Proxy will route to gemini-flash
    openai_api_base="http://localhost:8000",
    openai_api_key=os.getenv("LITELLM_MASTER_KEY")
)
```

## Monitoring

### Check Proxy Status

```bash
# Service status
systemctl --user status litellm-proxy.service

# View logs
journalctl --user -u litellm-proxy.service -f

# Check if proxy is responding
curl http://localhost:8000/health
```

### Dashboard

LiteLLM includes a web UI for monitoring:

```bash
# Access at http://localhost:8000/ui
# Login with your LITELLM_MASTER_KEY
```

### Cost Tracking

The proxy tracks usage in `litellm_proxy.db`:

```bash
# View database
sqlite3 litellm_proxy.db "SELECT * FROM spend_logs LIMIT 10;"
```

## Troubleshooting

### Proxy won't start

```bash
# Check logs
journalctl --user -u litellm-proxy.service -n 50

# Test config manually
source .venv/bin/activate
litellm --config litellm-proxy-config.yaml --test
```

### Provider failing

```bash
# Check which provider is being used
curl http://localhost:8000/model/info

# Test specific provider
curl -X POST http://localhost:8000/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-flash",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### Fallbacks not working

Check the config fallback chains and ensure all provider API keys are set.

## Advanced Features

### Custom Routing

Add custom routing logic in `litellm-proxy-config.yaml`:

```yaml
router_settings:
  routing_strategy: "cost-based-routing"  # Route to cheapest provider
  # or "latency-based-routing"  # Route to fastest provider
```

### Rate Limiting

Add per-user rate limits:

```yaml
general_settings:
  max_parallel_requests: 100
  max_user_budget: 100.0  # $100 per user
```

### Caching

Enable Redis caching for faster responses:

```yaml
litellm_settings:
  cache: true
  cache_params:
    type: "redis"
    host: "localhost"
    port: 6379
    ttl: 3600  # 1 hour
```

## Integration with Ada Swarm

The proxy gives us:

1. **Provider Independence**: Switch providers without changing agent code
2. **Automatic Failover**: If Gemini is down, agents keep working
3. **Cost Optimization**: Route cheap tasks to free models, complex tasks to paid
4. **Unified Monitoring**: Track all LLM usage in one place
5. **Rate Limit Protection**: Proxy handles retries and backoff

## Next Steps

1. Test the proxy with a simple request
2. Update ada-swarm to use the proxy
3. Monitor usage and costs
4. Tune fallback chains based on real-world performance
5. Add more providers as needed!

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"One API to rule them all, one proxy to route them!"* 🚀✨
