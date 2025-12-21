# MCP Debugging Session - December 20, 2025

## Timeline of Issues & Fixes

### Issue 1: MCP Server Not Found
**Symptom:** VS Code couldn't spawn MCP server  
**Root Cause:** `ada-mcp` not in PATH  
**Fix:** Changed default from `ada-mcp` to `ada-mcp/ada-mcp.sh` (relative path)

### Issue 2: Request Timeout (30s)
**Symptom:** MCP connected but chat requests timed out after 30s  
**Root Cause:** Ada brain responses can take longer than 30s (RAG + specialists)  
**Fix:** Increased timeout from 30s → 120s to match AdaClient default

### Issue 3: venv PATH Resolution
**Symptom:** Kept hitting "command not found" issues  
**Root Cause:** Tools installed in `.venv/bin/` not in system PATH  
**Fix:** Standardized on `uv run` via ada-mcp.sh wrapper

## Final Architecture

```
VS Code Extension
  ↓ spawn(workspace/ada-mcp/ada-mcp.sh)
  ↓
ada-mcp.sh wrapper
  ↓ exec uv run ada-mcp
  ↓
uv (auto-detects .venv)
  ↓ runs
ada-mcp stdio server
  ↓ calls
Ada Brain (localhost:8000)
```

## Key Learnings

1. **uv is magic** - Auto-detects venvs, no PATH needed
2. **Wrapper scripts** - Better than trying to manage PATH
3. **Relative paths** - Resolve from workspace root for portability
4. **Timeout alignment** - Match timeouts across layers
5. **stdio testing** - Hard to debug, use logging liberally

## Files Modified

1. `ada-vscode/package.json` - Default mcpServerPath
2. `ada-vscode/src/mcpClient.ts` - Workspace path resolution + 120s timeout + logging
3. `.ai/UV-STANDARDIZATION.md` - Documentation of uv-first approach

## Testing Steps

1. **Restart VS Code** (full quit Cmd+Q, not reload)
2. **Open ada-v1 workspace**
3. **Check MCP connection** in dev console
4. **Try chat** - should work now!

## What to Look For in Logs

✅ Good:
```
[ADA MCP] Spawning MCP server: /path/to/workspace/ada-mcp/ada-mcp.sh
[ADA MCP] Connected successfully!
[ADA MCP] Sending request 1: tools/call
[ADA MCP] Request 1 completed successfully
```

❌ Bad:
```
[ADA MCP] stderr: command not found
[ADA MCP] Request timeout
Process exited with code: 1
```

## Next: Full Integration Test

With MCP working, the next phase is:
1. Test all MCP tools (ada_chat, ada_read_file, ada_write_file)
2. Test bidirectional specialists
3. Test code completion via MCP
4. Benchmark TTFT (target: <300ms)

## UV Standardization Rabbit Hole

Created comprehensive plan in `.ai/UV-STANDARDIZATION.md`:
- All tools use `uv run`
- All docs use `uv` commands
- Wrappers handle PATH issues
- Consistent across CLI/web/matrix/vscode

**Status:** Phase 1 complete (VS Code MCP)
**Next:** Update all READMEs and dev docs
