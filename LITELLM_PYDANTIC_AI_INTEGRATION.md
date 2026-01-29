# LiteLLM + Pydantic AI Integration Guide

How to use LiteLLM for model access while keeping Pydantic AI for validation! 🐝✨

## The Strategy

**LiteLLM handles**: Provider routing, fallbacks, retries, cost tracking
**Pydantic AI handles**: Type validation, structured outputs, tool binding

This gives us the best of both worlds!

## Architecture

```
Pydantic AI Agent
       ↓
   (validation)
       ↓
LiteLLM Proxy (localhost:8000)
       ↓
   (routing & fallbacks)
       ↓
Multiple Providers (Gemini, Z.ai, DeepSeek, etc.)
```

## Method 1: Direct LiteLLM (Recommended)

Use LiteLLM directly in Pydantic AI agents:

```python
from pydantic_ai import Agent
import litellm

# Configure LiteLLM
litellm.api_base = "http://localhost:8000"  # Proxy URL
litellm.api_key = os.getenv("LITELLM_MASTER_KEY")

# Create agent with LiteLLM model
agent = Agent(
    'litellm/gemini-flash',  # Use litellm/ prefix
    system_prompt="You are a helpful assistant"
)

# Run normally - Pydantic AI will use LiteLLM under the hood
result = await agent.run("Hello!")
```

## Method 2: OpenAI-Compatible Mode

LiteLLM proxy exposes an OpenAI-compatible API:

```python
from pydantic_ai import Agent

agent = Agent(
    'openai/gemini-flash',  # Model name from proxy config
    openai_api_base='http://localhost:8000',
    openai_api_key=os.getenv("LITELLM_MASTER_KEY")
)
```

## Method 3: Custom Model Provider

For maximum control, create a custom Pydantic AI model provider:

```python
from pydantic_ai.models import Model, ModelSettings
import litellm

class LiteLLMModel(Model):
    """Custom Pydantic AI model using LiteLLM"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        litellm.api_base = "http://localhost:8000"
        litellm.api_key = os.getenv("LITELLM_MASTER_KEY")
    
    async def request(self, messages, settings: ModelSettings):
        response = await litellm.acompletion(
            model=self.model_name,
            messages=messages,
            **settings.model_dump()
        )
        return response

# Use it
agent = Agent(
    LiteLLMModel("gemini-flash"),
    system_prompt="You are helpful"
)
```

## Updating Ada Swarm

### Before (Direct Pydantic AI):

```python
agent = CoderAgent(
    agent_id="coder-1",
    model="google-gla:gemini-3-flash-preview"  # Pydantic AI format
)
```

### After (Via LiteLLM Proxy):

```python
agent = CoderAgent(
    agent_id="coder-1",
    model="openai/gemini-flash",  # LiteLLM proxy model
    openai_api_base="http://localhost:8000",
    openai_api_key=os.getenv("LITELLM_MASTER_KEY")
)
```

## Benefits

1. **Provider Independence**: Change providers without touching agent code
2. **Automatic Fallbacks**: If Gemini fails, LiteLLM tries Z.ai, then DeepSeek
3. **Cost Tracking**: All usage tracked in one place
4. **Rate Limiting**: Proxy handles retries and backoff
5. **Caching**: Reduce costs with Redis caching
6. **Monitoring**: Single dashboard for all LLM usage

## Model Aliases

Use simple names in your code:

```python
# Instead of remembering provider-specific names
agent = Agent("openai/fast")  # → gemini-flash
agent = Agent("openai/smart")  # → gemini-pro
agent = Agent("openai/paid")  # → glm-plus
agent = Agent("openai/cheap")  # → deepseek-chat
agent = Agent("openai/local")  # → local-ada
```

## Environment Variables

Add to `.env`:

```bash
# LiteLLM Proxy
LITELLM_MASTER_KEY=your-secret-key-here
LITELLM_PROXY_URL=http://localhost:8000

# Provider API Keys
GEMINI_API_KEY=your-gemini-key
ZAI_API_KEY=your-zai-key
DEEPSEEK_API_KEY=your-deepseek-key
MOONSHOT_API_KEY=your-moonshot-key
```

## Testing

```python
# Test direct LiteLLM
python test-litellm-simple.py

# Test with proxy (after starting it)
python test-litellm-proxy.py

# Test Pydantic AI integration
python test-pydantic-litellm.py
```

## Lumina Metrics Integration

Update Lumina to track LiteLLM proxy metrics:

```python
# lumina-metrics/src/lumina_metrics/metrics.py

import httpx

async def get_litellm_metrics():
    """Fetch metrics from LiteLLM proxy"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/metrics",
            headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"}
        )
        return response.json()

# Track in Prometheus
litellm_requests = Counter('litellm_requests_total', 'Total LiteLLM requests')
litellm_tokens = Counter('litellm_tokens_total', 'Total tokens used')
litellm_cost = Gauge('litellm_cost_usd', 'Total cost in USD')
```

## Next Steps

1. ✅ LiteLLM installed
2. ✅ Proxy config created
3. ⏳ Add API keys to `.env`
4. ⏳ Start proxy: `systemctl --user start litellm-proxy.service`
5. ⏳ Update ada-swarm to use proxy
6. ⏳ Update lumina-metrics to track proxy metrics
7. ⏳ Test end-to-end with Worker Bees!

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"One proxy to rule them all, Pydantic AI to validate them!"* 🚀✨
