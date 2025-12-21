# Ada Chat Architecture

> Extension-first tool architecture for VS Code integration
> 
> Created: December 2025 (v3.0.0)

## Core Principle

**Extension tools are FUNDAMENTAL. Brain is ADDITIVE.**

Ada Chat must work in two modes:
- **Brain Mode:** Extension → Brain → Ollama (full RAG, memory, persona)
- **Direct Mode:** Extension → Ollama (fast, stateless, tools only)

Therefore: **Extension owns tool injection, always.**

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│ VS Code Extension (ada-chat)                        │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ ALWAYS (both modes):                        │   │
│  │  - Inject VS Code tool instructions         │   │
│  │  - Intent classification (pre-routing)      │   │
│  │  - Intercept TOOL_REQUEST patterns          │   │
│  │  - Execute: read, search, git, symbols      │   │
│  │  - Tool transparency UI                     │   │
│  └─────────────────────────────────────────────┘   │
│                    ↓                                │
│         ┌─────────┴─────────┐                      │
│         ▼                   ▼                      │
│   [Brain Mode]        [Direct Mode]                │
│         │                   │                      │
│         ▼                   │                      │
│   ┌───────────┐             │                      │
│   │  Brain    │             │                      │
│   │  +RAG     │             │                      │
│   │  +memory  │             │                      │
│   │  +persona │             │                      │
│   │  +Brain   │             │                      │
│   │  specialists            │                      │
│   └─────┬─────┘             │                      │
│         │                   │                      │
│         └─────────┬─────────┘                      │
│                   ▼                                │
│              [Ollama]                              │
└─────────────────────────────────────────────────────┘
```

## Tool Ownership

### Extension Tools (VS Code APIs)
These MUST work in both modes:

| Tool | Purpose | API |
|------|---------|-----|
| `ada_introspect` | Workspace analysis, TODOs | `vscode.workspace.findFiles` |
| `ada_read_file` | File contents | `vscode.workspace.fs.readFile` |
| `ada_search` | Text search | `vscode.workspace.findTextInFiles` |
| `ada_list_files` | Directory listing | `vscode.workspace.fs.readDirectory` |
| `ada_symbols` | Code symbols | `vscode.commands.executeCommand('vscode.executeWorkspaceSymbolProvider')` |
| `ada_git_status` | Git status | `vscode.extensions.getExtension('vscode.git')` |
| `ada_edit_file` | File editing | `vscode.WorkspaceEdit` (planned) |
| `ada_run_terminal` | Command execution | `vscode.window.createTerminal` (planned) |

### Brain Specialists (Server-side)
These only work in Brain Mode:

| Specialist | Purpose | Requires |
|------------|---------|----------|
| `web_search` | Live web queries | SearxNG |
| `wiki_lookup` | Wikipedia/Fandom | HTTP |
| `codebase` | Self-introspection | Local files |
| `ocr` | Image text extraction | Tesseract |
| `vision` | Image analysis | Ollama vision |

## Tool Invocation Patterns

### 1. Pre-routing (Intent Classification)
Extension identifies tool need BEFORE sending to LLM:

```typescript
// User says "search for handleMessage"
const intent = toolHandler.classifyIntent(message);
if (intent.tool === 'ada_search') {
  // Execute immediately, then send results to Brain for reasoning
}
```

**When:** User intent is obvious from keywords/patterns
**Benefit:** Fast, deterministic, no LLM roundtrip wasted

### 2. Bidirectional (LLM-initiated)
LLM requests tools mid-response using pattern:

```
TOOL_REQUEST[tool_name:{"param":"value"}]
```

Extension watches stream, intercepts pattern, executes tool, re-injects result.

**When:** Complex queries where LLM needs to explore
**Benefit:** LLM chooses what it needs based on reasoning

### 3. Unified Syntax
Both Brain specialists and Extension tools use same pattern:
- `TOOL_REQUEST[ada_read_file:{"path":"src/index.ts"}]`
- `SPECIALIST_REQUEST[web_search:{"query":"..."}]`

Extension intercepts `TOOL_REQUEST`, Brain intercepts `SPECIALIST_REQUEST`.
No collision because namespaces are different.

## Tool Instruction Injection

Extension injects tool instructions into every message:

```typescript
const augmentedMessage = `${toolInstructions}

---

User request: ${userMessage}`;
```

This happens in BOTH modes:
- Brain Mode: Brain receives augmented message, passes to Ollama
- Direct Mode: Ollama receives augmented message directly

~500 tokens overhead, but required for bidirectional to work.

## Stream Interception Flow

```
1. User sends message
2. Extension injects tool instructions
3. Send to Brain (or Ollama direct)
4. Stream response chunks
5. Accumulate text, watch for TOOL_REQUEST pattern
6. On match:
   a. Send text-before-pattern to UI
   b. Show tool transparency card
   c. Execute tool via VS Code API
   d. Build continuation prompt with tool result
   e. Restart stream with new prompt
7. Continue until no more tool requests
8. Send final response to UI
```

## Configuration

### Extension Settings
```json
{
  "ada.brainUrl": "http://localhost:8000",
  "ada.connectionMode": "brain",  // or "direct"
  "ada.ollamaUrl": "http://localhost:11434",
  "ada.model": "qwen2.5-coder:7b"
}
```

### Mode Behavior

| Feature | Brain Mode | Direct Mode |
|---------|------------|-------------|
| VS Code tools | ✅ | ✅ |
| Tool transparency | ✅ | ✅ |
| RAG context | ✅ | ❌ |
| Memory/persona | ✅ | ❌ |
| Brain specialists | ✅ | ❌ |
| Speed | ~200ms TTFT | ~100ms TTFT |

## Future: Native Tool Calling

If Ollama model supports native tool calling (structured JSON output):
1. Define tools as JSON schema
2. Model outputs `{"tool": "name", "params": {...}}`
3. Extension parses JSON instead of regex patterns
4. Same execution flow, cleaner invocation

Architecture supports this transition - tool definitions are already structured.

## Key Design Decisions

### Why Extension owns tools?
- Must work without Brain (Direct Mode)
- VS Code APIs only available in extension context
- Keeps Brain focused on RAG/memory

### Why inject instructions every message?
- Bidirectional requires LLM awareness of tools
- No persistent context between messages (stateless)
- ~500 tokens is acceptable overhead

### Why two routing approaches?
- Pre-routing: Fast for obvious intents
- Bidirectional: Flexible for complex reasoning
- Best of both worlds

### Why same pattern syntax?
- Brain already uses `SPECIALIST_REQUEST`
- Extension mirrors with `TOOL_REQUEST`
- Future unification possible

## Metrics

### v3.0.0 Baseline
- 7 working tools
- ~137ms TTFT (Brain Mode)
- Pre-routing: 100% reliable
- Bidirectional: Testing in progress

### v3.1 Goals
- Add `ada_edit_file`, `ada_run_terminal`, `ada_create_file`
- Active file context injection
- Bidirectional validation complete
- Direct Mode fully functional

---

*This architecture enables Ada Chat to be a complete Copilot alternative that works with OR without the full Ada stack.*
