# Parent Ecosystem Reference

**This package is part of the Ada ecosystem.**

## Quick Pointers

| Need | Location |
|------|----------|
| Full architecture | `../../../.ai/context.md` |
| Extension design | `../../../.ai/ADA-CHAT-ARCHITECTURE.md` |
| Conventions | `../../../.ai/CONVENTIONS.md` |
| Testing patterns | `../../../.ai/TESTING.md` |
| Gotchas | `../../../.ai/GOTCHAS.md` |

## Key Ecosystem Context (Excerpted)

### Ada's Purpose
Conversational AI with RAG, streaming, specialists, and tool transparency. Privacy-first, runs locally.

### Service Topology
```
Ada CLI (terminal)        ┐
Ada Chat (VS Code)        │  ← YOU ARE HERE
Ada Complete (VS Code)    ├→ Ada Brain (fastapi:8000) ⇄ chroma:8000
Ada Nvim (Neovim)         │                           ⇄ ollama:11434
Ada MCP (stdio)           ┘
```

### Adapter Pattern
All interfaces (CLI, Chat, Matrix, MCP) are **adapters** that talk to Brain's REST API. Brain is the core; adapters translate protocols.

### Extension-First Principle (v3.0)
Extension tools are **FUNDAMENTAL** - they work in both modes:
- **Direct Mode:** Extension → Ollama (no Brain needed)
- **Brain Mode:** Extension → Brain → Ollama (adds RAG, memory)

### Communication Pattern
- **Chat endpoint:** `POST /v1/chat/stream` (SSE)
- **Health check:** `GET /v1/healthz`
- **Streaming:** Server-Sent Events with JSON chunks

## When to Read Parent Docs

- Adding new tools → Read `ADA-CHAT-ARCHITECTURE.md`
- Understanding data flow → Read `context.md`
- Writing tests → Read `TESTING.md`
- Avoiding mistakes → Read `GOTCHAS.md`

## Navigation

```bash
# From this package, parent .ai/ is at:
cd ../../../.ai/

# Or use relative paths in code/docs:
../../../.ai/context.md
```
