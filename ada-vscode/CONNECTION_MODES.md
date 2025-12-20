# Ada VS Code Extension - Connection Modes

The Ada VS Code extension now supports **two connection modes**, giving you flexibility between speed and capabilities!

## Quick Setup

### 1. Start Ada Brain (Recommended!)

```bash
# From ada-v1 directory
docker compose up -d
```

This starts:
- Ada Brain at `http://localhost:8000` (RAG, memory, specialists)
- Ollama at `http://localhost:11434` (LLM backend)
- ChromaDB for vector storage
- All biomimetic features

### 2. Configure VS Code Extension

Open VS Code Settings (`Ctrl+,` or `Cmd+,`) and search for "Ada":

**Mode** (ada.mode):
- `brain` (default) - Connect to Ada Brain for full capabilities
- `ollama` - Direct Ollama connection (fastest, no memory)

**Brain URL** (ada.brainUrl):
- Default: `http://localhost:8000`

**Ollama URL** (ada.ollamaUrl):
- Default: `http://localhost:11434`
- Only used when mode=ollama

## Connection Modes Explained

### 🧠 Brain Mode (DEFAULT)

**When to use:**
- You want persistent memory across sessions
- You want RAG context that learns your codebase
- You want specialists (web search, OCR, etc.)
- You want biomimetic features (memory graph, context priming)
- You're doing complex work that benefits from context

**What you get:**
- ✅ Persistent conversation memory
- ✅ RAG context (persona, FAQs, memories)
- ✅ Specialist capabilities (web search, etc.)
- ✅ Memory graph with spreading activation
- ✅ Context priming and habituation
- ✅ Unified experience with CLI/web/Matrix

**Performance:**
- Slightly slower (~50-100ms overhead)
- Worth it for the context and memory!

**How it works:**
```
VS Code → Ada Brain → RAG + Specialists → Ollama → Response
         (localhost:8000)                (localhost:11434)
```

### ⚡ Ollama Mode (FAST)

**When to use:**
- You want maximum speed
- You're doing simple completions that don't need context
- You're on a slow machine or network
- You don't need persistent memory

**What you get:**
- ✅ Fastest possible completions (~103ms TTFT)
- ✅ Direct Ollama connection (no middleware)
- ✅ Still fully local and private
- ✅ Same great code model (qwen2.5-coder:7b)

**What you DON'T get:**
- ❌ No persistent memory
- ❌ No RAG context
- ❌ No specialists
- ❌ No biomimetic features

**How it works:**
```
VS Code → Ollama → Response
         (localhost:11434)
```

## Switching Modes

### Via Settings GUI:

1. `Ctrl+,` (or `Cmd+,` on Mac)
2. Search for "Ada Mode"
3. Select `brain` or `ollama`
4. Reload window (`Ctrl+Shift+P` → "Reload Window")

### Via settings.json:

```json
{
  "ada.mode": "brain",
  "ada.brainUrl": "http://localhost:8000",
  "ada.ollamaUrl": "http://localhost:11434"
}
```

## Verifying Connection

After switching modes, check the status bar at the bottom of VS Code:

- **Green** "Ada ✓" = Connected
- **Red** "Ada ✗" = Disconnected (check services are running)

Click the Ada icon in the sidebar to open the chat panel and see connection status.

## Troubleshooting

### "Cannot connect to Ada Brain"

**Brain mode issues:**
```bash
# Check if Ada Brain is running
curl http://localhost:8000/v1/healthz

# If not, start it:
docker compose up -d

# Check logs:
docker compose logs brain
```

**Ollama mode issues:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it:
ollama serve

# Or via Docker:
docker compose up -d ollama
```

### Performance Comparison

**Code Completion (FIM):**
- Brain mode: ~150-250ms (includes RAG overhead)
- Ollama mode: ~103ms (direct)

**Chat Response:**
- Brain mode: ~200-400ms first token (includes context retrieval)
- Ollama mode: ~100-150ms first token (no context)

**Is the overhead worth it?**

YES! Brain mode gives you:
- Context from previous conversations
- Memory that persists across sessions
- Specialists that can search the web, read docs, etc.
- The full Ada experience

For simple completions, Ollama mode is faster. For complex work, Brain mode's context makes you way more productive overall.

## Best Practice: Use Both!

**Recommended workflow:**

1. **Default to Brain mode** for chat and complex work
2. **Code completion** automatically uses the fastest path
3. **Switch to Ollama mode** if you're on a slow network or machine

The extension is smart - code completions use a specialized FIM endpoint that's optimized for speed even in Brain mode.

## What's Different from Standalone Ollama?

When you connect to Ada Brain, you're not just talking to Ollama - you're getting:

**1. Persistent Memory:**
- Conversations stored in ChromaDB
- Memory graph builds connections between concepts
- Context carries across sessions

**2. RAG Context:**
- Your persona (`.persona.md`)
- FAQs and knowledge base
- Recent memories semantically retrieved
- Conversation history

**3. Specialists:**
- Web search when you need external info
- OCR for image text extraction
- Document lookup for Ada's own docs
- More specialists loading automatically

**4. Biomimetic Features:**
- Memory decay (recent = more important)
- Context habituation (novelty detection)
- Spreading activation (related concepts)
- Multi-signal importance scoring

This is the "full Ada experience" - the same backend powering the CLI, web UI, and Matrix bot!

## Migration Path

If you're currently using the extension with standalone Ollama:

1. **Start Ada Brain:** `docker compose up -d`
2. **Settings stay the same** - Brain mode is now default
3. **Reload VS Code** - the extension will auto-connect
4. **Your history** starts building in ChromaDB
5. **Memories persist** - talk to Ada in the web UI, CLI, or VS Code - same memory!

## Architecture

```
┌─────────────────────────────────────────────────┐
│  VS Code Extension (TypeScript)                 │
│  ├─ Code Completion (FIM)                       │
│  ├─ Chat Sidebar (agentic with tools)           │
│  └─ Context Menu Commands                       │
└──────────────┬──────────────────────────────────┘
               │
               ├─ mode=brain ───────────────┐
               │                             │
               │                    ┌────────▼─────────┐
               │                    │  Ada Brain       │
               │                    │  (FastAPI)       │
               │                    │  localhost:8000  │
               │                    │                  │
               │                    │  ├─ RAG Context  │
               │                    │  ├─ Specialists  │
               │                    │  ├─ Memory Graph │
               │                    │  └─ Prompt Build │
               │                    └────────┬─────────┘
               │                             │
               └─ mode=ollama ───────────────┤
                                             │
                                    ┌────────▼─────────┐
                                    │  Ollama          │
                                    │  localhost:11434 │
                                    │                  │
                                    │  qwen2.5-coder   │
                                    └──────────────────┘
```

## Next Steps

Once you're connected to Ada Brain:

1. **Try the chat** - Ask Ada about your code, the chat has full workspace access
2. **Use tools** - Select code and ask Ada to explain/fix/test it
3. **Check memories** - Run `ada-cli` or use the web UI to see what Ada remembers
4. **Explore specialists** - Ada can search the web, read images, etc.

Welcome to the full Ada experience! 🚀

---

**Quick Reference:**

| Feature | Brain Mode | Ollama Mode |
|---------|-----------|-------------|
| Speed | ~200ms | ~103ms |
| Memory | ✅ Persistent | ❌ None |
| RAG Context | ✅ Full | ❌ None |
| Specialists | ✅ All | ❌ None |
| Biomimetic | ✅ Full | ❌ None |
| Tools | ✅ Agent loop | ✅ Agent loop |
| Code Completion | ✅ Works | ✅ Works |
| Unified Ada | ✅ Same brain | ❌ Standalone |

**TL;DR:** Use Brain mode (default) for the full Ada experience. Use Ollama mode only if you need maximum speed and don't care about memory/context.
