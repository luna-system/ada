# Testing Code Completion

Quick reference for testing the Phase 1 code completion MVP.

## Quick Start

### 1. Start Ada Brain
```bash
docker compose up -d brain chroma ollama
```

Wait ~30 seconds for services to be healthy:
```bash
docker compose ps
curl http://localhost:8000/v1/healthz
```

### 2. Run Integration Tests
```bash
./test_completion_integration.py
```

Expected output:
```
🤖 Ada Code Completion - Manual Test Suite
...
📊 Results: 3/3 tests passed
✅ All tests passed! Code completion is working! 🎉
```

### 3. Test via MCP (if MCP server running)
```bash
# Start MCP server
cd ada-mcp && uv run ada-mcp

# In another terminal, use MCP client
echo '{"method": "tools/call", "params": {"name": "ada_complete_code", "arguments": {"code_before": "def hello():\n    ", "code_after": "", "language": "python"}}}' | mcp-cli
```

## What's Being Tested

### Test 1: Simple Function
```python
def greet(name):
    message = <COMPLETE>
    return message
```

Should complete with something like: `f"Hello, {name}!"`

### Test 2: Class Method
```python
class Calculator:
    def add(self, a, b):
        <COMPLETE>
```

Should complete with: `return a + b`

### Test 3: Import Statement
```python
from pathlib import <COMPLETE>
```

Should complete with: `Path` or `Path, PurePath`

## Expected Behavior

✅ **Good completions:**
- Respects `code_after` (doesn't duplicate)
- No markdown artifacts (clean code only)
- Appropriate length (~1-3 tokens)
- Syntactically valid

❌ **Bad completions:**
- Ignores context
- Includes markdown ```python blocks
- Too long or verbose
- Syntactically invalid

## Troubleshooting

### "Connection error" or "Cannot connect"
- Check Ada brain is running: `curl http://localhost:8000/v1/healthz`
- Check Docker containers: `docker compose ps`
- Check logs: `docker compose logs brain`

### "Completion failed" or empty responses
- Check Ollama has model: `docker compose exec ollama ollama list`
- Check model in config: Should match `OLLAMA_MODEL` (default: `qwen2.5-coder:7b`)
- Try manual chat: `curl -X POST http://localhost:8000/v1/chat/stream -d '{"message": "test"}'`

### Slow completions (>2s)
- Normal on first request (model loading)
- Should be <500ms after warmup
- Check system load: `docker stats`
- Consider smaller model if too slow

## Performance Expectations

| Metric | Expected | Notes |
|--------|----------|-------|
| First completion | 2-10s | Model loading |
| Subsequent | <500ms | Warm cache |
| Token usage | 30-80 | Terse prompts |
| Accuracy | ~80% | Good enough for MVP |

## Next Steps After Tests Pass

1. ✅ Foundation working
2. Add Neovim integration (`ada.nvim/lua/ada/completion.lua`)
3. Add keybinding (`<C-x><C-a>` or auto-trigger)
4. Test in real editing workflow
5. Iterate on prompt engineering for better completions

## Files Involved

- `ada-mcp/src/ada_mcp/tools/complete_code.py` - Core completion logic
- `ada-mcp/src/ada_mcp/tools.py` - MCP server integration
- `ada-mcp/src/ada_mcp/client.py` - HTTP client singleton
- `tests/test_code_completion.py` - Unit tests (prompt building)
- `test_completion_integration.py` - Integration tests (this script)

## See Also

- Phase 1 Progress: `PHASE1_PROGRESS.md`
- Full Roadmap: `.ai/ROADMAP_COPILOT_PARITY.md`
- MCP Protocol: https://modelcontextprotocol.io/

---

**Status:** Foundation complete, ready for real-world testing! 🚀
