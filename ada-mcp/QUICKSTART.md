# Ada MCP Quick Start

## What You're Looking At
This is the Model Context Protocol (MCP) server for Ada - it lets you use Ada in any MCP-compatible editor!

## Quick Test

### 1. Check if it runs
```bash
cd ada-mcp
uv run ada-mcp
```

You should see:
```
🤖 Ada MCP Server starting...
📡 Listening on stdio for MCP protocol messages
🔗 Ada Brain: http://localhost:8000
```

Press Ctrl+C to stop.

### 2. Chat with Ada (CLI)
```bash
./ada_chat.py "Write a Python hello world script"
```

### 3. Test the full stack
```bash
uv run python ../test_mcp_manually.py
```

## How It Works

**MCP Server** (this package) ← stdio → **Editor** (VSCode/Helix/etc)
       ↓ HTTP/REST
**Ada Brain** (Docker container on port 8000)

The MCP server is just a thin protocol adapter - all the AI/memory/tools live in Ada Brain.

## Editor Setup

### VSCode/VSCodium
1. Check `.vscode/mcp.json` - already configured!
2. Install an MCP extension (if available)
3. Reload window

### Helix
Check `examples/helix-config.toml` but note: Helix uses LSP, not MCP (need adapter layer)

### Command Line
Just use `./ada_chat.py` - works right now!

## Troubleshooting

**"Nothing happens when I run uv run ada-mcp"**
→ This is correct! It's waiting for MCP protocol messages on stdin. Use an editor or the CLI tool.

**"404 error from Ollama"**
→ Ada Brain config issue (internal Docker networking). MCP layer is working fine.

**"No tools showing in editor"**
→ Make sure you have an MCP-compatible extension installed.

## Files

- `ada-mcp.sh` - Quick launcher script
- `ada_chat.py` - CLI tool for testing
- `TESTING.md` - Full testing documentation
- `examples/` - Editor configuration examples
