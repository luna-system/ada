# Frontend as Adapter

## Architecture

Ada follows a **clean adapter pattern** where the frontend is just one of many interfaces to the brain's REST API.

```
┌──────────────┐
│   CLI        │────┐
├──────────────┤    │
│   Web UI     │────┼──→  Ada Brain (REST API)
├──────────────┤    │     http://localhost:8000/v1/*
│   Matrix     │────┤
├──────────────┤    │
│   MCP        │────┘
└──────────────┘
```

**All adapters are equal peers.** The web UI has no special privileges.

## Running Headless

Ada works perfectly without the web UI:

```bash
# Brain only
docker compose up -d

# Use CLI
ada-cli "Hello!"

# Use MCP (in your editor)
# See ada-mcp/README.md

# Use Matrix bridge
docker compose --profile matrix up -d

# Direct API calls
curl http://localhost:8000/v1/chat/stream \
  -d '{"message": "Hello!"}'
```

## Running the Web UI

The web UI is **optional** and starts with a profile flag:

```bash
# Start with web UI
docker compose --profile web up -d

# Access at http://localhost:5000
```

## Configuration

The frontend can connect to any Ada brain instance by editing `frontend/public/config.js`:

```javascript
// Default: proxied through nginx
window.API_BASE_URL = '/api';

// Direct connection to remote Ada
window.API_BASE_URL = 'http://ada.local:8000/v1';

// Cloud deployment
window.API_BASE_URL = 'https://my-ada.example.com/v1';
```

No rebuild needed - just edit the config file!

## Why This Matters

### Modularity
- Swap frontends without touching the brain
- Run multiple UIs pointing to one brain
- Build custom interfaces for specific workflows

### Deployment Flexibility
- Deploy brain on powerful server, frontend on CDN
- Run brain headless on Raspberry Pi, use SSH tunnel for UI
- One brain, many clients (family members, devices)

### Development
- Frontend devs work without Python/ChromaDB/Ollama
- Test UI against staging/production brains
- Easier contribution path

### Forkability
Ada's adapter pattern means you can:
- Replace the web UI entirely (terminal-style, mobile app, etc.)
- Add new adapters (Discord bot, Telegram, Signal, etc.)
- Run multiple interfaces simultaneously

## Adapter Checklist

When building a new adapter:

- ✅ **HTTP client** - Talk to brain via REST API
- ✅ **SSE support** - Handle streaming responses
- ✅ **Conversation IDs** - Maintain context across turns
- ✅ **Optional entity** - Support entity-scoped memories
- ✅ **Error handling** - Graceful degradation

**Don't need:**
- ❌ Ollama access
- ❌ ChromaDB connection
- ❌ Python environment
- ❌ Direct access to brain internals

## Existing Adapters

All follow this pattern:

| Adapter | Location | Protocol | Status |
|---------|----------|----------|--------|
| **CLI** | `adapters/cli/` | HTTP → stdout | ✅ Production |
| **Web UI** | `frontend/` | HTTP → browser | ✅ Production |
| **Matrix** | `matrix-bridge/` | HTTP → Matrix | ✅ Production |
| **MCP** | `ada-mcp/` | stdio → editor | ✅ Production |

## Example: Minimal Adapter

```python
import httpx

class MinimalAdapter:
    def __init__(self, brain_url="http://localhost:8000"):
        self.client = httpx.Client(base_url=brain_url)
    
    def chat(self, message: str) -> str:
        """Send message, get full response."""
        response = self.client.post(
            "/v1/chat/stream",
            json={"message": message}
        )
        
        full_text = ""
        for line in response.iter_lines():
            if line.startswith("data: "):
                chunk = json.loads(line[6:])
                full_text += chunk["text"]
        
        return full_text
```

That's it! **40 lines to build an Ada client.**

## See Also

- [Adapter Development Guide](adapter_development.rst) - Build your own
- [API Reference](api_reference.rst) - Full API documentation
- [MCP Integration](ada-mcp/README.md) - Editor integration
- [Matrix Bridge](matrix_integration.rst) - Bot setup

---

**The brain is the product. Everything else is an adapter.** 🧠🔌
