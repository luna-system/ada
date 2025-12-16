# Testing Ada MCP in VSCode

## Prerequisites
- Ada Brain running: `docker compose up brain -d`
- VSCode with MCP support (or GitHub Copilot with MCP)

## Testing Steps

### Option 1: With MCP Extension
If you have an MCP extension installed:
1. Open VSCode in this workspace: `code /home/luna/Code/ada-v1`
2. Check the MCP status in the status bar
3. Try asking Ada to "write a Python hello world script"

### Option 2: Test MCP Server Directly
Test the MCP server works before trying VSCode integration:

```bash
cd /home/luna/Code/ada-v1/ada-mcp

# Quick test
uv run python ../test_mcp_manually.py

# Or start MCP server
uv run ada-mcp
# Or use wrapper script
./ada-mcp.sh
```

Expected output:
- ✓ Health check passes
- ✓ Tools are accessible
- Note about Ollama 404 is OK (internal Docker issue)

### Option 3: Simple CLI Chat
Use the CLI tool to chat with Ada:

```bash
cd /home/luna/Code/ada-v1/ada-mcp

# Simple chat
uv run python ada_chat.py "Write a Python hello world script"

# Or make it executable and run directly
./ada_chat.py "What is the meaning of life?"
```

## Known Issues
- Helix: Uses LSP not MCP (need adapter layer)
- Ollama 404: Internal Docker network (doesn't affect MCP)
- VSCode MCP: Experimental feature, may need specific extension

## What Works
✅ MCP server starts and runs
✅ Health checks pass
✅ Tool definitions exposed
✅ Ada client can communicate with Ada Brain
✅ Proper stdio protocol handling

## Next Steps
1. Install VSCode MCP extension (if available)
2. Or use GitHub Copilot with MCP support
3. Or build LSP wrapper for Helix
4. Or create standalone CLI tool
