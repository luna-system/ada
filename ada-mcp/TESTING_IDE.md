# Testing Ada's MCP Server in VS Code

## Prerequisites

1. **MCP Server Running:**
   ```bash
   cd ada-mcp
   python -m ada_mcp.server
   ```

2. **VS Code Extensions:**
   - GitHub Copilot Chat (includes MCP support)
   - Or: Cline extension (dedicated MCP client)

## Configuration

### For GitHub Copilot

Add to VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcp.servers": {
    "ada": {
      "command": "python",
      "args": ["-m", "ada_mcp.server"],
      "cwd": "/home/luna/Code/ada-v1/ada-mcp",
      "env": {
        "ADA_BRAIN_URL": "http://localhost:8000"
      }
    }
  }
}
```

### For Cline

Add to Cline MCP settings:

```json
{
  "mcpServers": {
    "ada": {
      "command": "python",
      "args": ["-m", "ada_mcp.server"],
      "cwd": "/home/luna/Code/ada-v1/ada-mcp",
      "env": {
        "ADA_BRAIN_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Testing Commands

### 1. Basic Chat

In VS Code chat (Cmd+I or Ctrl+I):

```
@ada what's the current time?
```

Expected: Ada responds with time in Central timezone

### 2. Now Playing Specialist

```
@ada what am i listening to?
```

Expected: Ada uses now_playing_specialist → MPRIS → contextual response

### 3. Memory Operations

```
@ada remember that i prefer techno and house music
```

Then later:

```
@ada search your memory for my music preferences
```

Expected: Ada stores and retrieves memory

### 4. Health Check

```
@ada check your health status
```

Expected: Status report of brain, chroma, ollama services

## Troubleshooting

### MCP Server Not Found

**Symptom:** VS Code says "MCP server 'ada' not found"

**Solution:**
1. Check server runs standalone: `cd ada-mcp && python -m ada_mcp.server`
2. Verify path in settings.json is absolute
3. Restart VS Code after config change

### Connection Errors

**Symptom:** `AdaBrainConnectionError: Connection failed`

**Solution:**
1. Ensure brain service running: `docker compose ps brain`
2. Check brain port: `curl http://localhost:8000/v1/healthz`
3. Verify `ADA_BRAIN_URL` environment variable

### Specialist Not Activating

**Symptom:** Ada doesn't use now_playing_specialist

**Solution:**
1. Check music is actually playing: `playerctl status`
2. Try more explicit query: "what track is currently playing?"
3. Check brain logs: `docker compose logs brain`

## What Makes This Cool

### Tool Use in IDE

When you ask Ada about your music, VS Code will show:

```
🔧 Using tool: ada_chat
📝 Query: what am i listening to?
✅ Response received
```

### Context Awareness

Ada has access to:
- Your workspace files (via IDE context)
- Her own memory (via MCP tools)
- Current system state (via specialists)
- Documentation (via docs_specialist)

### Streaming Responses

If using Cline, you'll see Ada's response stream in real-time, just like the CLI!

## Advanced Usage

### Chaining Context

```
@ada what am i listening to, and can you find similar artists?
```

Expected: now_playing → web_search → synthesized response

### Documentation Lookup

```
@ada how do i add a new specialist to your system?
```

Expected: docs_specialist activates → searches Ada's own docs → explains

### Memory + Context

```
@ada based on what you remember about my music taste, recommend something
```

Expected: search_memory → contextual recommendation

## Next: MPRIS Control Commands

See `MPRIS_CONTROL_IDEAS.md` for bidirectional specialist patterns!

---

**Last Updated:** 2025-12-16  
**Test Status:** ✅ MCP client works, IDE integration pending user test

