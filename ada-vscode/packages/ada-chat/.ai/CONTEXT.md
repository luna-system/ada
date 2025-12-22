# Ada Chat - VS Code Extension Context

**Package:** `ada-chat`  
**Type:** VS Code Extension (Adapter)  
**Parent Ecosystem:** [Ada](../../../.ai/context.md)

## Purpose

Local AI chat assistant with tool transparency. Implements the "Extension-first" architecture where tools work in both Direct Mode (Ollama only) and Brain Mode (full RAG/memory).

## Architecture

See [ADA-CHAT-ARCHITECTURE.md](../../../.ai/ADA-CHAT-ARCHITECTURE.md) for full design.

```
┌─────────────────────────────────────────────────┐
│              Ada Chat Extension                  │
│  ┌──────────────┐    ┌───────────────────────┐  │
│  │ Pre-Router   │    │   Extension Tools     │  │
│  │ (patterns)   │    │   (always available)  │  │
│  └──────┬───────┘    └───────────┬───────────┘  │
│         │                        │              │
│         ▼                        ▼              │
│  ┌──────────────────────────────────────────┐   │
│  │         Tool Handler (MCP-style)         │   │
│  └──────────────────┬───────────────────────┘   │
│                     │                           │
└─────────────────────┼───────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
   Direct Mode               Brain Mode
   (Ollama only)        (localhost:8000)
```

## Key Files

| File | Purpose |
|------|---------|
| `src/extension.ts` | Entry point, BrainClient, OllamaClient |
| `src/chatViewProvider.ts` | Chat UI, tool routing, bidirectional handling |
| `src/mcpToolHandler.ts` | 7 extension tools (introspect, read_file, etc.) |
| `resources/webview/` | Chat UI (HTML/CSS/JS) |

## Extension Tools (Always Available)

1. `ada_introspect` - Scan workspace for TODOs/FIXMEs
2. `ada_read_file` - Read file contents
3. `ada_list_directory` - List folder contents
4. `ada_search_files` - Grep search
5. `ada_get_diagnostics` - VS Code problems
6. `ada_get_selection` - Current editor selection
7. `ada_get_open_files` - List open editors

## Current Bug (Dec 21, 2025)

**Brain streaming broken:** `fetch()` hangs when calling Brain API.
- Pre-routing/tools work ✅
- curl to Brain works ✅
- Extension fetch() hangs ❌

See [HANDOFF.md](./HANDOFF.md) for debug state.

## Development

```bash
# Extension Development Host (fast iteration!)
code .
# Press F5 to launch
# Ctrl+Shift+F5 to reload
# Debug Console shows all logs

# Or manual build
pnpm build
pnpm package
code --install-extension ada-chat-*.vsix --force
```

## Dependencies

- **Runtime:** VS Code 1.85+
- **Optional:** Ada Brain at localhost:8000
- **Optional:** Ollama at localhost:11434

## Parent Ecosystem Reference

For full Ada architecture, conventions, and cross-cutting concerns:
- **Architecture:** `../../../.ai/context.md`
- **Extension Design:** `../../../.ai/ADA-CHAT-ARCHITECTURE.md`
- **Conventions:** `../../../.ai/CONVENTIONS.md`
- **Testing:** `../../../.ai/TESTING.md`
