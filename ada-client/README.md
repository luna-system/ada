# Ada Client Library

**Shared Python client for Ada brain REST API**

This package provides a standardized HTTP client used by all Ada adapters (CLI, Matrix, MCP, etc.), eliminating code duplication and ensuring consistent behavior.

## Features

- ✨ **Streaming & Non-Streaming** - Real-time or complete responses
- 🔄 **Async/Await** - Built on httpx for async Python
- 🛡️ **Type Hints** - Full type annotations for IDE support
- 🎯 **Error Handling** - Structured exception hierarchy
- 🧪 **Well Tested** - Comprehensive test coverage
- 📦 **Zero Config** - Works with Ada brain defaults

## Installation

```bash
# From local path (development)
pip install -e /path/to/ada-v1/ada-client

# Or with uv
uv add ../ada-client
```

## Quick Start

### Streaming Chat (Real-time)

```python
from ada_client import AdaClient

async def stream_example():
    async with AdaClient() as client:
        async for chunk in client.chat_stream("Hello Ada!"):
            print(chunk, end="", flush=True)
        print()  # Newline after response

# Run it
import asyncio
asyncio.run(stream_example())
```

### Non-Streaming Chat (Complete Response)

```python
from ada_client import AdaClient

async def chat_example():
    async with AdaClient() as client:
        response = await client.chat("Explain quantum computing in simple terms")
        print(response)

asyncio.run(chat_example())
```

### Memory Operations

```python
from ada_client import AdaClient

async def memory_example():
    async with AdaClient() as client:
        # Add a memory
        await client.add_memory(
            "Luna prefers techno music",
            importance=0.8,
            scope="user"
        )
        
        # Search memories
        results = await client.search_memories("music preferences")
        for memory in results:
            print(f"- {memory['content']}")

asyncio.run(memory_example())
```

### Health Check

```python
from ada_client import AdaClient, AdaBrainConnectionError

async def health_example():
    client = AdaClient()
    try:
        health = await client.health()
        print(f"Brain: {health['brain']['status']}")
        print(f"Ollama: {health['ollama']['status']}")
        print(f"ChromaDB: {health['chroma']['status']}")
    except AdaBrainConnectionError as e:
        print(f"Ada is not responding: {e}")
    finally:
        await client.close()

asyncio.run(health_example())
```

## Configuration

```python
from ada_client import AdaClient

# Custom brain URL and timeout
client = AdaClient(
    base_url="http://ada-brain.example.com:7000",
    timeout=60.0  # seconds
)
```

## Exception Handling

```python
from ada_client import (
    AdaClient,
    AdaBrainError,           # Base exception
    AdaBrainConnectionError, # Network/connection errors
    AdaBrainResponseError,   # API error responses
)

async def safe_chat():
    async with AdaClient() as client:
        try:
            response = await client.chat("Hello!")
            print(response)
        except AdaBrainConnectionError as e:
            print(f"Cannot reach Ada: {e}")
        except AdaBrainResponseError as e:
            print(f"Ada returned error {e.status_code}: {e}")
        except AdaBrainError as e:
            print(f"Unexpected error: {e}")

asyncio.run(safe_chat())
```

## API Reference

### `AdaClient`

**Constructor:**
- `base_url` (str): Brain API URL (default: `http://localhost:7000`)
- `timeout` (float): Request timeout in seconds (default: `120.0`)

**Methods:**

#### `async chat_stream(message, conversation_id="default", include_thinking=False)`
Stream response chunks as they arrive.

**Returns:** `AsyncIterator[str]`

#### `async chat(message, conversation_id="default", include_thinking=False)`
Get complete response (non-streaming).

**Returns:** `str`

#### `async search_memories(query, limit=5, scope="user")`
Search Ada's memory store.

**Returns:** `list[dict]`

#### `async add_memory(content, importance=0.5, scope="user", memory_type="note")`
Add memory to Ada's store.

**Returns:** `dict`

#### `async health()`
Check health of all services.

**Returns:** `dict`

#### `async close()`
Close HTTP client and cleanup resources.

## Context Manager Support

The client supports async context managers for automatic cleanup:

```python
# Automatic cleanup
async with AdaClient() as client:
    response = await client.chat("Hello!")

# Manual cleanup
client = AdaClient()
try:
    response = await client.chat("Hello!")
finally:
    await client.close()
```

## Used By

This shared client is used by:

- **CLI Adapter** (`adapters/cli/`) - Terminal interface
- **Matrix Bridge** (`matrix-bridge/`) - Matrix bot
- **MCP Server** (`ada-mcp/`) - IDE integration
- **Web UI** (uses JavaScript Fetch API)

## Development

```bash
# Install with dev dependencies
cd ada-client
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=ada_client --cov-report=html

# Type checking
mypy src/ada_client
```

## Requirements

- Python >= 3.13
- httpx >= 0.27.0

## License

MIT License - See main Ada project for details.

## Contributing

This package is part of the [Ada project](https://github.com/luna-system/ada). Contributions welcome!

## See Also

- [Ada Documentation](https://ada.luna-system.dev)
- [Adapter Development Guide](../docs/adapter_development.rst)
- [API Reference](../docs/api_reference.rst)
