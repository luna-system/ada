# Ada CLI - Reference Implementation Adapter

**Command-line interface adapter for Ada's brain**

This is the **reference implementation** for building Ada adapters. It demonstrates the core patterns needed to integrate with Ada's brain API in the simplest possible way.

## Features

- ✅ **Interactive REPL mode** - Chat with Ada in your terminal
- ✅ **One-shot query mode** - Single queries for scripting
- ✅ **Streaming responses** - Real-time token streaming
- ✅ **Non-streaming mode** - Wait for complete responses (like Matrix bridge)
- ✅ **JSON output** - Machine-readable responses for automation
- ✅ **Conversation context** - Maintains context across messages
- ✅ **Health checks** - Verifies brain connectivity
- ✅ **Clean error handling** - Clear error messages and exit codes

## Why This Exists

The CLI adapter serves as:

1. **Reference implementation** - "Here's how to build an adapter"
2. **Documentation** - Working code showing all the patterns
3. **Utility** - Actually useful for scripting and testing
4. **Foundation** - The `client.py` will become the shared library in Phase 2

## Installation

```bash
# From the ada-v1 root directory
cd adapters/cli
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Usage

### Interactive Mode

Start a conversation with Ada:

```bash
$ ada-cli

🤖 Ada CLI - Interactive Mode

Commands: /help, /history, /clear, /exit
Ctrl+C to interrupt, Ctrl+D or 'exit' to quit

You: What's the weather like?
Ada: I don't have access to real-time weather data, but I can help you...

You: /history
Conversation History:
  1. You: What's the weather like?
  Ada: I don't have access to real-time weather data...

You: /clear
✓ Conversation cleared. Starting fresh!

You: exit
Goodbye! 👋
```

### One-Shot Mode

Single query for scripting:

```bash
# Simple query
$ ada-cli "What is 2+2?"
4

# JSON output (for scripting)
$ ada-cli --format json "Hello Ada"
{
  "response": "Hello! How can I help you today?",
  "conversation_id": "cli-oneshot"
}

# Pipe input
$ echo "Summarize this README" | ada-cli

# Use in scripts
$ ada-cli --format json "analyze this" | jq '.response'
```

### Advanced Options

```bash
# Custom brain URL
$ ada-cli --brain-url http://ada.example.com:7000

# Specific conversation ID (maintain context across calls)
$ ada-cli --conversation-id "my-session" "First message"
$ ada-cli --conversation-id "my-session" "Follow-up question"

# Non-streaming mode (wait for complete response)
$ ada-cli --no-stream "Tell me a story"

# Increase timeout for long responses
$ ada-cli --timeout 300 "Write a long essay"

# Environment variable for brain URL
$ export ADA_BRAIN_URL=http://ada.example.com:7000
$ ada-cli "Hello"
```

## Architecture

### Module Structure

```
ada_cli/
├── __init__.py          # Package exports
├── client.py            # HTTP client (will become shared library)
└── cli.py               # Interactive REPL and CLI interface
```

### Key Components

#### 1. AdaClient (`client.py`)

The HTTP client that communicates with Ada's brain:

```python
from ada_cli import AdaClient

async with AdaClient(base_url="http://localhost:7000") as client:
    # Streaming (real-time tokens)
    async for chunk in client.chat_stream("Hello"):
        print(chunk, end="")
    
    # Non-streaming (complete response)
    response = await client.chat("What is Ada?")
    print(response)
    
    # Health check
    health = await client.health()
    print(health)
```

**Key patterns demonstrated:**
- Async/await with httpx
- SSE (Server-Sent Events) stream parsing
- Error handling (connection errors, response errors)
- Context manager for cleanup
- Both streaming and non-streaming modes

#### 2. CLI Interface (`cli.py`)

Two modes of operation:

**Interactive Mode:**
- REPL-style conversation
- Commands: `/help`, `/history`, `/clear`, `/exit`
- Streaming display of responses
- Conversation context maintained

**One-Shot Mode:**
- Single query and exit
- JSON output for scripting
- Markdown rendering option
- Exit codes for error handling

### Protocol Flow

```
User Input
    ↓
AdaClient
    ↓
POST /v1/chat/stream
    ↓
Brain (FastAPI)
    ↓
SSE Stream
    ↓
Parse Chunks
    ↓
Display/Return
```

## Building Your Own Adapter

Use this CLI as a template! Here's the minimal pattern:

### 1. Create HTTP Client

```python
import httpx

class YourAdaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._client = httpx.AsyncClient()
    
    async def chat(self, message: str) -> str:
        """Send message to brain, return response."""
        url = f"{self.base_url}/v1/chat/stream"
        payload = {"prompt": message, "conversation_id": "your-id", "stream": True}
        
        chunks = []
        async with self._client.stream("POST", url, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk and chunk != "[DONE]":
                        chunks.append(chunk)
        
        return "".join(chunks)
```

### 2. Add Protocol Handler

Adapt the Ada client to your protocol:

- **Matrix**: Translate Matrix events → Ada client → Matrix responses
- **Discord**: Discord events → Ada client → Discord messages
- **Telegram**: Telegram updates → Ada client → Telegram replies
- **Web UI**: EventSource → Ada client → DOM updates

### 3. Handle State

Manage conversation context:

```python
# Use room ID, channel ID, or user ID as conversation_id
conversation_id = f"discord-{channel_id}"
response = await client.chat(message, conversation_id)
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=ada_cli --cov-report=term-missing

# Test against live brain
ADA_BRAIN_URL=http://localhost:7000 pytest
```

## Comparison with Other Adapters

| Feature | CLI | Web UI | Matrix | MCP |
|---------|-----|--------|--------|-----|
| Complexity | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Complex | ⭐⭐ Medium |
| Streaming | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| Interactive | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| Dependencies | 3 | Many | Many | 2 |
| Lines of Code | ~400 | ~1000 | ~800 | ~300 |
| Use Case | Terminal, scripting | Browser chat | Federated chat | IDE integration |

**Start here** if you want to build a new adapter!

## Environment Variables

- `ADA_BRAIN_URL` - Ada brain API URL (default: `http://localhost:7000`)

## Error Handling

The CLI uses exit codes for scripting:

- `0` - Success
- `1` - Connection error or brain error

Errors are printed to stderr, responses to stdout:

```bash
$ ada-cli "hello" 2>/dev/null  # Suppress errors
$ ada-cli "hello" 1>/dev/null  # Suppress output
```

## Docker Usage

Run CLI in Docker:

```bash
# From ada-v1 root
docker compose run --rm scripts bash
cd /app/adapters/cli
pip install -e .
ada-cli
```

## Future Enhancements

See `INTEGRATION_PLUGINS_PLAN.md` for:

- Phase 2: Extract `client.py` as shared `ada-client` library
- Phase 3: All adapters use shared library
- Additional adapters: Discord, Telegram, Slack

## Contributing

This is a reference implementation! If you:

- Find bugs → Fix them (helps everyone)
- Add features → Keep it simple (it's a reference)
- Build new adapters → Use this as a template

## License

MIT License - See LICENSE file

---

**Remember:** This CLI is intentionally simple. It's a teaching tool and reference implementation. For production adapters with complex requirements, see the Matrix bridge or MCP server examples.
