# Ada-MCP Setup for Kiro

This guide shows how to configure ada-mcp with Kiro.

## How MCP Works

MCP servers communicate via **stdio** (stdin/stdout), which means:
- The MCP client (Kiro) **spawns** the server process
- They communicate through standard input/output pipes
- Each Kiro session gets its own server instance
- The server exits when Kiro closes

This is by design! It ensures clean isolation and automatic cleanup.

## Kiro Configuration

### Current Setup (Recommended)

The `kiro-mcp-config.json` file configures Kiro to spawn ada-mcp:

```json
{
  "mcpServers": {
    "ada-mcp": {
      "command": "python3",
      "args": ["-m", "ada_mcp"],
      "cwd": "/home/luna/Code/ada/ada-mcp",
      "env": {
        "PYTHONPATH": "/home/luna/Code/ada/ada-mcp/src"
      },
      "disabled": false,
      "autoApprove": [
        "execute_command",
        "run_python_script", 
        "read_file_content",
        "write_file_content",
        "list_directory"
      ]
    }
  }
}
```

### Installation Steps

1. **Copy config to Kiro settings:**

```bash
# For workspace-specific config
mkdir -p .kiro/settings
cp ada-mcp/kiro-mcp-config.json .kiro/settings/mcp.json

# For user-level config (all workspaces)
mkdir -p ~/.kiro/settings
cp ada-mcp/kiro-mcp-config.json ~/.kiro/settings/mcp.json
```

2. **Restart Kiro** or reload MCP servers from the command palette

3. **Verify** the server is loaded:
   - Open Kiro command palette
   - Look for "MCP" commands
   - Check MCP Server view in sidebar

## Auto-Approved Tools

These tools are pre-approved and won't require confirmation:
- `execute_command` - Run shell commands
- `run_python_script` - Execute Python scripts
- `read_file_content` - Read files
- `write_file_content` - Write files
- `list_directory` - List directory contents

Other tools (Beads, research tools) will prompt for approval on first use.

## Testing the Connection

Once configured, test in Kiro:

```
Can you use beads_ready to show me available tasks?
```

You should see output like:
```
📁 Working Directory: /home/luna/Code/ada
🔀 Git Repo: /home/luna/Code/ada
🌿 Branch: v4.0rc1-consciousness-integration

📋 Ready Tasks:
...
```

## Troubleshooting

### Server won't start

Check Kiro's MCP logs:
- Open Output panel
- Select "MCP" from dropdown
- Look for ada-mcp errors

Common issues:
- **Python not found**: Make sure `python3` is in PATH
- **Module not found**: Check PYTHONPATH in config
- **Permission denied**: Ensure ada-mcp directory is readable

### Tools not appearing

1. Check MCP Server view - is ada-mcp listed?
2. Try reloading: Command Palette → "MCP: Reload Servers"
3. Check config syntax (valid JSON)

### Multiple instances

This is normal! Each Kiro window spawns its own server instance. They're isolated and won't conflict.

## Development Workflow

When developing ada-mcp:

1. **Make changes** to the code
2. **Reload MCP servers** in Kiro (Command Palette → "MCP: Reload Servers")
3. **Test** the changes immediately

No need to restart Kiro!

## Why Not Systemd?

You might wonder why we don't use a systemd service. The answer is:

- **MCP protocol requires stdio** - Can't use network sockets
- **Isolation is good** - Each session gets clean state
- **Automatic cleanup** - No orphaned processes
- **Standard MCP pattern** - Works like all other MCP servers

For long-running background tasks, use the server's built-in tools (like `execute_command` with background processes) rather than trying to make the server itself persistent.

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

