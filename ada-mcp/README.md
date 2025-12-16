# Ada MCP Server

**Model Context Protocol server for Ada - brings your personal AI to any editor.**

## What This Is

The Ada MCP Server is a thin adapter that exposes [Ada](https://github.com/luna-system/ada)'s capabilities through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). This lets you use Ada from editors like Neovim, Helix, and VSCodium.

Think of it as: Ada gives you a personal AI with memory and tools. This MCP server makes it accessible from your code editor.

## Philosophy

- **Editor-agnostic**: Works with any editor that supports MCP (no lock-in)
- **Thin wrapper**: Just translates between MCP and Ada's REST API
- **Hackable**: Simple Python code, easy to extend or modify
- **Standards-based**: Uses MCP, not proprietary protocols

## Quick Start

### Prerequisites

- Ada Brain running (see [main Ada docs](https://github.com/luna-system/ada))
- Python 3.11+

### Installation

```bash
cd ada-mcp
pip install -e .
```

### Configuration

Create `.env` in the ada-mcp directory:

```bash
ADA_BASE_URL=http://localhost:8000
```

### Run

```bash
ada-mcp
```

The MCP server will start and listen for connections from your editor.

## Editor Setup

### Neovim

*(Coming soon - example config)*

### Helix

*(Coming soon - example config)*

### VSCodium

*(Coming soon - example config)*

## Available Tools

### `ada_chat`

Talk to Ada with full RAG context (persona, memories, conversation history).

**Input:**
- `message` (required): What you want to say to Ada
- `conversation_id` (optional): Continue an existing conversation

**Output:** Ada's response

### `ada_search_memory`

Search Ada's long-term memory store.

**Input:**
- `query` (required): What to search for
- `scope` (optional): Filter by scope (e.g., "user", "project")
- `type` (optional): Filter by memory type

**Output:** List of relevant memories

### `ada_add_memory`

Store something in Ada's long-term memory.

**Input:**
- `content` (required): What to remember
- `type` (optional): Memory type (default: "note")
- `importance` (optional): 0.0-1.0 (default: 0.5)
- `scope` (optional): Memory scope (default: "user")

**Output:** Memory ID

### `ada_health`

Check if Ada Brain is running and healthy.

**Output:** Health status and version info

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Lint
ruff check .
```

## Architecture

```
┌─────────────┐
│   Editor    │ (vim, helix, VSCodium)
└──────┬──────┘
       │ MCP Protocol
┌──────▼──────┐
│  Ada MCP    │ ← This component
│   Server    │
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│  Ada Brain  │ (existing)
└─────────────┘
```

The MCP server is just a protocol translator - all the AI, memory, and tool logic lives in Ada Brain.

## License

CC0 1.0 Universal - same as Ada. Public domain dedication. Do whatever you want with it.

## Contributing

See the main [Ada repository](https://github.com/luna-system/ada) for contribution guidelines.

---

*Part of the Ada project - infrastructure for personal AI that's always free, privacy-first, and hackable.*
