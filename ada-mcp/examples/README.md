# Editor Configuration Examples

This directory contains example configurations for integrating Ada MCP Server with various editors.

## Quick Setup

1. **Install Ada MCP Server:**
   ```bash
   cd ada-mcp
   pip install -e .
   ```

2. **Start Ada Brain** (if not already running):
   ```bash
   docker compose up brain
   ```

3. **Configure your editor** using the examples below.

## Neovim

See [neovim-config.lua](./neovim-config.lua)

**Requirements:**
- Neovim 0.9+
- MCP client plugin (e.g., `anthropics/mcp.nvim`)

**Setup:**
1. Install the MCP plugin via your package manager
2. Copy the config to your Neovim configuration
3. Adjust paths if needed
4. Restart Neovim

**Testing:**
```vim
:McpListTools
:McpCallTool ada_health {}
```

## Helix

See [helix-config.toml](./helix-config.toml)

**Requirements:**
- Helix editor with MCP support (experimental as of 2025)
- Check Helix docs for current MCP status

**Setup:**
1. Add config to `~/.config/helix/languages.toml`
2. Restart Helix
3. MCP tools should appear in LSP actions

**Testing:**
```
# Open a file, then:
:lsp-workspace-command
# Look for Ada tools
```

## VSCodium

See [vscodium-settings.json](./vscodium-settings.json)

**Requirements:**
- VSCodium (or VS Code)
- MCP extension (install from marketplace if available)

**Setup:**
1. Open Settings (Ctrl+,)
2. Click "Open Settings (JSON)" in top right
3. Add the MCP server configuration
4. Reload window (Ctrl+Shift+P -> "Reload Window")

**Testing:**
```
Ctrl+Shift+P -> "MCP: List Tools"
```

## Manual Testing (All Editors)

You can test the MCP server directly without an editor:

```bash
# Start Ada Brain first
docker compose up brain

# In another terminal:
cd ada-mcp
pip install -e .
ada-mcp
```

The server will start and wait for stdio input. You can send MCP protocol messages manually (though this is mainly for debugging).

## Troubleshooting

### "Command not found: ada-mcp"

The `ada-mcp` command isn't in PATH. Options:
1. Activate the virtualenv: `source ada-mcp/.venv/bin/activate`
2. Use absolute path in editor config: `/full/path/to/ada-mcp/.venv/bin/ada-mcp`
3. Install globally: `pip install -e ada-mcp` (not recommended)

### "Connection refused" or "Ada Brain not responding"

Make sure Ada Brain is running:
```bash
docker compose up brain
curl http://localhost:8000/health
```

### "No tools available" or MCP not connecting

Check logs:
1. Editor logs (usually in editor config directory)
2. Ada Brain logs: `docker compose logs brain`
3. Test MCP server manually: `ADA_BASE_URL=http://localhost:8000 ada-mcp`

## Configuration Options

All editors support these environment variables:

- `ADA_BASE_URL`: Ada Brain API URL (default: `http://localhost:8000`)

You can also create an `.env` file in the `ada-mcp` directory:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Next Steps

Once connected:
1. Try `:McpCallTool ada_health {}` to verify connection
2. Chat with Ada: `:McpCallTool ada_chat {"message": "Hello!"}`
3. Search memories: `:McpCallTool ada_search_memory {"query": "project"}`
4. Add a memory: `:McpCallTool ada_add_memory {"content": "Testing MCP"}`

## Contributing Editor Configs

Have a working config for another editor? PRs welcome! We're especially interested in:
- Emacs
- Zed
- Sublime Text
- Any editor with MCP support

See main Ada repo for contribution guidelines.
