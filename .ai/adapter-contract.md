# Adapter Contract

**Version:** 1.1.0  
**Last Updated:** 2025-12-16  
**Status:** ✅ Implemented across all Python adapters

This document defines the technical contract for building Ada adapters. All adapters (CLI, Web UI, Matrix, MCP, Discord, Telegram, etc.) should follow these patterns.

## Implementation Status

✅ **CLI Adapter** (`adapters/cli/ada_cli/client.py`) - Reference implementation  
✅ **Matrix Bridge** (`matrix-bridge/ada_client.py`) - Standardized  
✅ **MCP Server** (`ada-mcp/src/ada_mcp/ada_client.py`) - Standardized  
⏳ **Web UI** (`frontend/public/app.js`) - Uses browser EventSource (different pattern for JavaScript)

## Purpose

Adapters translate external protocols (HTTP, Matrix, Discord API, etc.) into interactions with Ada's brain API. They handle:

- Protocol translation
- User interface (if applicable)
- Message formatting
- State management (conversations, users, etc.)
- Error handling

**The brain handles:**
- RAG (memory search)
- LLM inference
- Specialist plugins
- Context management

## Core Requirements

### 1. HTTP Client

All adapters must communicate with Ada's brain via HTTP:

**Endpoint:** `POST /v1/chat/stream`

**Request payload:**
```json
{
  "prompt": "user message text",
  "conversation_id": "unique-conversation-identifier",
  "stream": true
}
```

**Response:** Server-Sent Events (SSE) stream

```
data: Hello
data:  
data: World
data: [DONE]
```

**Key patterns:**
- Use `httpx.AsyncClient` for async I/O
- Parse SSE stream: lines starting with `data: `
- `[DONE]` signals end of stream
- Handle both streaming and non-streaming modes

### 2. Error Handling

**Required error classes:**

```python
class AdaBrainError(Exception):
    """Base exception for Ada brain client errors."""
    pass

class AdaBrainConnectionError(AdaBrainError):
    """Raised when unable to connect to Ada's brain."""
    pass

class AdaBrainResponseError(AdaBrainError):
    """Raised when Ada's brain returns an error response."""
    pass
```

**Handle these scenarios:**
- Connection refused (brain down)
- HTTP errors (4xx, 5xx)
- Timeouts (long-running responses)
- Network errors

**Graceful degradation:**
```python
try:
    response = await client.chat(message)
except AdaBrainConnectionError:
    # Provide user-friendly error message
    return "Sorry, I'm temporarily unavailable."
```

### 3. Conversation Context

**Use unique `conversation_id` for context:**

- **CLI**: Generate session ID (`cli-session-{uuid}`)
- **Web UI**: Use client-side conversation ID
- **Matrix**: Use room ID (`matrix-{room_id}`)
- **Discord**: Use channel ID (`discord-{channel_id}`)
- **MCP**: Use client-provided ID or generate default

**Pattern:**
```python
# Prefix with adapter name to avoid collisions
conversation_id = f"{adapter_name}-{unique_identifier}"
```

**Important:** Brain stores conversation history per `conversation_id`. Different IDs = different contexts.

### 4. Configuration

**Required config:**
- `base_url`: Ada brain API URL (default: `http://localhost:8000`)
- `timeout`: Request timeout in seconds (default: 120.0)

**Recommended:**
- Use Pydantic Settings for environment variables
- Support `.env` files
- Provide sensible defaults

**Example:**
```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    ada_brain_url: str = "http://localhost:8000"
    ada_timeout: float = 120.0
    
    class Config:
        env_file = ".env"
        env_prefix = "ADA_"
```

### 5. Health Checks

**Endpoint:** `GET /v1/healthz`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "chroma": "healthy",
    "ollama": "healthy"
  }
}
```

**Pattern:**
```python
async def health(self) -> dict:
    """Check if Ada's brain is available."""
    response = await self._client.get(f"{self.base_url}/v1/healthz")
    response.raise_for_status()
    return response.json()
```

## Adapter Client Patterns

### Pattern A: Streaming (CLI, Web UI, MCP)

Real-time token streaming for responsive UX:

```python
async def chat_stream(
    self,
    message: str,
    conversation_id: str
) -> AsyncIterator[str]:
    """Stream response chunks as they arrive."""
    url = f"{self.base_url}/v1/chat/stream"
    payload = {"prompt": message, "conversation_id": conversation_id, "stream": True}
    
    async with self._client.stream("POST", url, json=payload) as response:
        response.raise_for_status()
        
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                chunk = line[6:]
                if chunk and chunk != "[DONE]":
                    yield chunk
```

**Usage:**
```python
async for chunk in client.chat_stream("Hello"):
    print(chunk, end="")
    sys.stdout.flush()
```

### Pattern B: Non-Streaming (Matrix)

Complete response for protocols that don't support partial updates:

```python
async def chat(
    self,
    message: str,
    conversation_id: str
) -> str:
    """Get complete response (non-streaming)."""
    chunks = []
    async for chunk in self.chat_stream(message, conversation_id):
        chunks.append(chunk)
    return "".join(chunks)
```

**Usage:**
```python
response = await client.chat("Hello")
# Send complete response to protocol
```

### Pattern C: Hybrid

Support both modes:

```python
class AdaClient:
    async def chat_stream(self, message: str, conversation_id: str):
        """Streaming mode."""
        ...
    
    async def chat(self, message: str, conversation_id: str):
        """Non-streaming mode (calls chat_stream internally)."""
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id):
            chunks.append(chunk)
        return "".join(chunks)
```

## Adapter Structure

### Recommended Directory Layout

```
adapters/your-adapter/
├── README.md              # Setup, usage, examples
├── pyproject.toml         # Dependencies (httpx, pydantic-settings, etc.)
├── .env.example           # Example configuration
├── your_adapter/
│   ├── __init__.py        # Package exports
│   ├── client.py          # Ada HTTP client (implements patterns above)
│   ├── config.py          # Pydantic Settings
│   ├── protocol.py        # Your protocol handler (Matrix, Discord, etc.)
│   └── main.py            # Entry point
├── tests/
│   ├── test_client.py     # Client unit tests
│   └── test_protocol.py   # Protocol handler tests
└── examples/
    └── example.py         # Usage example
```

### Minimal Files

**1. client.py** - Ada HTTP client

```python
import httpx
from typing import AsyncIterator

class AdaClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=120.0)
    
    async def chat_stream(self, message: str, conversation_id: str) -> AsyncIterator[str]:
        url = f"{self.base_url}/v1/chat/stream"
        payload = {"prompt": message, "conversation_id": conversation_id, "stream": True}
        
        async with self._client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk and chunk != "[DONE]":
                        yield chunk
    
    async def close(self):
        await self._client.aclose()
```

**2. config.py** - Configuration

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    ada_brain_url: str = "http://localhost:8000"
    ada_timeout: float = 120.0
    
    # Your protocol-specific config here
    your_api_token: str
    
    class Config:
        env_file = ".env"
```

**3. protocol.py** - Your protocol handler

```python
from .client import AdaClient
from .config import Config

class YourProtocolHandler:
    def __init__(self, config: Config):
        self.config = config
        self.ada = AdaClient(base_url=config.ada_brain_url)
    
    async def handle_message(self, message: str, context_id: str):
        """Translate your protocol → Ada → your protocol"""
        conversation_id = f"your-adapter-{context_id}"
        
        try:
            response = await self.ada.chat(message, conversation_id)
            # Send response via your protocol
            await self.send_response(response, context_id)
        except Exception as e:
            # Handle errors gracefully
            await self.send_error(context_id)
```

**4. main.py** - Entry point

```python
import asyncio
from .config import Config
from .protocol import YourProtocolHandler

async def main():
    config = Config()
    handler = YourProtocolHandler(config)
    await handler.start()  # Your protocol's event loop

if __name__ == "__main__":
    asyncio.run(main())
```

## Deployment Patterns

### Docker Compose Service

```yaml
services:
  your-adapter:
    build:
      context: ./adapters/your-adapter
    container_name: ada-your-adapter
    restart: unless-stopped
    depends_on:
      - brain
    env_file:
      - ./adapters/your-adapter/.env
    environment:
      - ADA_BRAIN_URL=http://brain:7000  # Internal docker network
```

### Standalone Installation

```bash
cd adapters/your-adapter
pip install -e .
your-adapter  # Entry point from pyproject.toml
```

## Testing

### Unit Tests

Test client without real brain:

```python
import pytest
from pytest_httpx import HTTPXMock

@pytest.mark.asyncio
async def test_chat_stream(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:8000/v1/chat/stream",
        text="data: Hello\ndata: World\ndata: [DONE]\n"
    )
    
    client = AdaClient()
    chunks = []
    async for chunk in client.chat_stream("test", "test-id"):
        chunks.append(chunk)
    
    assert chunks == ["Hello", "World"]
```

### Integration Tests

Test with real brain (requires running services):

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_brain():
    client = AdaClient(base_url="http://localhost:8000")
    response = await client.chat("test", "integration-test")
    assert len(response) > 0
```

## Common Pitfalls

### ❌ Don't: Hardcode URLs

```python
# Bad
client = AdaClient(base_url="http://localhost:8000")
```

```python
# Good
from config import Config
config = Config()
client = AdaClient(base_url=config.ada_brain_url)
```

### ❌ Don't: Ignore Conversation Context

```python
# Bad - every message creates new context
response = await client.chat(message, "default")
```

```python
# Good - maintain context per user/room/channel
conversation_id = f"adapter-{user_id}"
response = await client.chat(message, conversation_id)
```

### ❌ Don't: Swallow Errors Silently

```python
# Bad
try:
    response = await client.chat(message)
except:
    pass  # User sees nothing!
```

```python
# Good
try:
    response = await client.chat(message)
except AdaBrainConnectionError:
    return "Sorry, I'm temporarily unavailable. Please try again."
except AdaBrainResponseError as e:
    logger.error(f"Brain error: {e}")
    return "Sorry, I encountered an error. Please contact support."
```

### ❌ Don't: Parse JSON Chunks

```python
# Bad - SSE chunks are not JSON in Ada's API
chunk = json.loads(line[6:])
```

```python
# Good - chunks are raw text
chunk = line[6:]  # Remove "data: " prefix
if chunk and chunk != "[DONE]":
    yield chunk
```

## Best Practices

### ✅ Do: Use Async/Await

All I/O should be async for scalability:

```python
async def handle_message(self, message):
    response = await self.ada.chat(message)  # Non-blocking
    await self.send_response(response)  # Non-blocking
```

### ✅ Do: Add Logging

Help with debugging:

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Received message: {message[:50]}...")
logger.debug(f"Sending to brain: {payload}")
logger.error(f"Connection failed: {e}", exc_info=True)
```

### ✅ Do: Provide Examples

Include working example in README:

````markdown
## Example Usage

```python
from your_adapter import YourAdapter, Config

async def main():
    config = Config()
    adapter = YourAdapter(config)
    response = await adapter.chat("Hello!")
    print(response)
```
````

### ✅ Do: Document Activation

Explain how your adapter activates (always-on vs. triggered):

- **Always-on**: Web UI, MCP server
- **Event-driven**: Matrix (on mentions/DMs), Discord (on @mentions)
- **Command-triggered**: CLI (explicit invocation)

## API Endpoints Reference

### Chat Endpoint

**POST** `/v1/chat/stream`

Request:
```json
{
  "prompt": "string",
  "conversation_id": "string",
  "stream": true
}
```

Response: SSE stream
```
data: chunk1
data: chunk2
data: [DONE]
```

### Health Check

**GET** `/v1/healthz`

Response:
```json
{
  "status": "healthy",
  "services": {
    "chroma": "healthy",
    "ollama": "healthy"
  }
}
```

### Info Endpoint

**GET** `/v1/info`

Response:
```json
{
  "version": "1.2.0",
  "brain_capabilities": [...],
    "llm_model": "qwen2.5-coder:7b"
}
```

## Reference Implementations

### Python Adapters (Standardized)

**CLI Adapter** - `adapters/cli/ada_cli/client.py`  
- ⭐ **Reference implementation** - 200 lines
- Demonstrates all patterns clearly
- Both streaming and non-streaming
- Full error handling
- Context manager support

**Matrix Bridge** - `matrix-bridge/ada_client.py`  
- Production-ready protocol integration
- Non-streaming mode (Matrix can't show partial messages)
- Per-room conversation context
- Privacy opt-out handling

**MCP Server** - `ada-mcp/src/ada_mcp/ada_client.py`  
- IDE integration via stdio protocol
- Memory management tools
- Resource documentation exposure
- Standardized exception handling

### JavaScript/Browser Pattern

**Web UI** - `frontend/public/app.js`

Different pattern for browser environments:

```javascript
// Browser uses Fetch API with streaming
const res = await fetch("/api/chat/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    prompt: userMessage,
    conversation_id: sessionId
  })
});

// Stream response with ReadableStream
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");
  buffer = lines.pop() ?? "";
  
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const chunk = line.slice(6);
      try {
        const data = JSON.parse(chunk);
        if (data.type === "token") {
          displayToken(data.content);
        }
      } catch (e) {
        // Handle parse errors
      }
    }
  }
}
```

**Key differences:**
- Uses native Fetch API (no httpx)
- ReadableStream instead of async generators
- Manual SSE parsing from binary chunks
- Browser EventSource would work but less flexible
- No need for standardized exceptions (different error model)

Study these for real-world patterns.

## Next Steps

1. **Read** `adapters/cli/README.md` - Reference implementation guide
2. **Copy** `adapters/_template/` - Start with template (Phase 1)
3. **Implement** your protocol handler
4. **Test** with real brain API
5. **Document** setup and usage
6. **Share** your adapter! (optional)

## Support

- **Documentation**: `docs/adapters.rst`
- **API Reference**: `docs/api_reference.rst`
- **Architecture**: `.ai/context.md`
- **Examples**: `adapters/cli/`, `matrix-bridge/`, `ada-mcp/`

---

**Version History:**
- v1.0.0 (2025-12-16): Initial adapter contract based on CLI/Web/Matrix/MCP patterns
