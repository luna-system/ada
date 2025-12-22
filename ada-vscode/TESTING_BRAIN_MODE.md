# Testing Ada Brain Mode

Quick test scenarios to verify Brain mode is working correctly.

## Prerequisites

```bash
# Start Ada Brain
cd /home/luna/Code/ada-v1
docker compose up -d

# Verify Ada Brain is running
curl http://localhost:8000/v1/healthz
```

## Test 1: Connection Status

1. Open VS Code
2. Check status bar (bottom right):
   - Should say "Ada ✓" (green) if connected
   - Should say "Ada ✗" (red) if disconnected

3. If disconnected, check settings:
   - `Ctrl+,` → Search "Ada Mode"
   - Should be set to `brain`
   - `ada.brainUrl` should be `http://localhost:8000`

## Test 2: Chat with Memory

1. Click Ada icon in sidebar (left panel)
2. Type: "Hi! My name is luna and I work on Ada."
3. Wait for response
4. Type: "What's my name?"
5. Expected: Ada should remember "luna" from previous message

**What this tests:**
- Conversation history tracking
- Memory persistence within session

## Test 3: RAG Context

1. In chat, ask: "What's in memory_graph.py?"
2. Expected: Ada should:
   - Call `list_files` tool to find the file
   - Call `read_file` tool to read it
   - Summarize the biomimetic memory graph implementation

**What this tests:**
- Tool execution (workspace access)
- RAG context from actual file content

## Test 4: Persistent Memory Across Sessions

1. In chat, tell Ada: "Remember that I prefer Python over JavaScript"
2. Close VS Code
3. Reopen VS Code
4. Open Ada chat
5. Ask: "What language do I prefer?"
6. Expected: Ada should remember your preference

**What this tests:**
- Memory storage in ChromaDB
- Cross-session persistence

## Test 5: Specialist Activation

1. In chat, ask: "Search the web for the latest qwen2.5-coder model"
2. Expected: Ada should:
   - Detect web search request
   - Invoke web_search_specialist
   - Return real results from the web

**What this tests:**
- Specialist detection and invocation
- External data retrieval

## Test 6: Code Completion (FIM)

1. Open a Python file
2. Type: `def fibonacci(`
3. Wait ~200ms
4. Expected: Ghost text completion appears

**What this tests:**
- FIM code completion still works in Brain mode
- Latency is acceptable (~150-250ms)

## Test 7: Verify RAG Pipeline

Check logs to see RAG context being assembled:

```bash
docker compose logs brain | grep -A 5 "Building prompt"
```

Expected output should show:
- Persona loading
- Memory retrieval
- FAQ loading
- Context assembly

## Test 8: Cross-Interface Memory

1. In VS Code chat, say: "My favorite color is purple"
2. Open terminal
3. Run: `ada-cli "what's my favorite color?"`
4. Expected: Ada should remember "purple"

**What this tests:**
- Unified memory across all Ada interfaces
- ChromaDB storage working correctly

## Test 9: Switch to Ollama Mode

1. `Ctrl+,` → Search "Ada Mode"
2. Change to `ollama`
3. `Ctrl+Shift+P` → "Reload Window"
4. Check status bar: Should say "Ada ✓" (connected to Ollama)
5. Try chat: Should work but won't have memory from Brain mode

**What this tests:**
- Mode switching works
- Ollama fallback is functional
- No errors when switching modes

## Test 10: Switch Back to Brain Mode

1. `Ctrl+,` → Search "Ada Mode"
2. Change to `brain`
3. Reload window
4. Previous memories should still be accessible

**What this tests:**
- Brain mode re-connection
- Memory persistence (not lost when switching modes)

## Debugging

If tests fail:

### Ada Brain not responding:
```bash
docker compose ps
docker compose logs brain
curl http://localhost:8000/v1/info
```

### Tools not executing:
Check `ada.enableTools` setting is `true`

### No memory:
```bash
# Check ChromaDB is running
curl http://localhost:8000/v1/healthz | jq .chroma

# Check memory storage
docker compose exec brain python -c "from brain.rag_store import rag_store; print(rag_store.get_collection('memories').count())"
```

### Ollama errors:
```bash
docker compose logs ollama
curl http://localhost:11434/api/tags
```

## Success Criteria

✅ All tests pass  
✅ Status bar shows "Ada ✓"  
✅ Chat responds with context  
✅ Memories persist across sessions  
✅ Tools execute correctly  
✅ Code completion works  
✅ Mode switching is smooth  

## Performance Benchmarks

Expected latencies in Brain mode:

- **Code completion (FIM)**: 150-250ms
- **Chat first token**: 200-400ms
- **Tool execution**: +50-100ms per tool
- **Memory retrieval**: ~50ms (cached after first use)

If you're seeing much higher latency:
1. Check Docker resource limits
2. Check if GPU is being used: `docker compose logs ollama | grep -i gpu`
3. Consider switching to Ollama mode for speed-critical work

## What Success Looks Like

When Brain mode is working correctly:

1. Ada remembers context from previous conversations
2. Ada can access and modify workspace files
3. Ada can search the web when needed
4. Ada's responses are contextually aware
5. Memories sync across CLI, web UI, Matrix, and VS Code
6. The experience feels unified and intelligent

This is what we built! 🎉

---

**Quick Test:**
```bash
# Start Ada Brain
docker compose up -d

# Test from terminal
ada-cli "Test message - my name is $(whoami)"

# Then in VS Code chat
# Ask: "What did I just tell you in the CLI?"
# Ada should know!
```

If that works, **Brain mode is fully operational!** 🧠✨
