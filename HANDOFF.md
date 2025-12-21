# Ada Handoff - December 21, 2025

**Branch:** `feature/tool-framework-architecture`  
**Previous:** Tool transparency working! (committed to trunk)  
**Next:** Implement unified tool framework

---

## What Just Happened

**Tool Transparency is LIVE!** 🎉

When you ask "use introspection tools", the VS Code extension now shows:
- Collapsible "🔧 Files Analyzed (5)" section above Ada's response  
- Clickable badges for each file: `context.md`, `codebase-map.json`, etc.
- Users can see exactly what Ada read before answering

**Key commits on trunk:**
```
2b271a3 feat(vscode): implement tool transparency for introspection
```

---

## Architecture Plan: Unified Tool Framework

We've designed the next evolution. Here's the concrete plan:

### The Pattern: Tool Result Envelope

Every MCP tool returns structured metadata alongside content:

```python
# ada-mcp/src/ada_mcp/types.py (NEW FILE)
@dataclass
class ToolResult:
    content: str
    metadata: ToolMetadata

@dataclass  
class ToolMetadata:
    files_accessed: list[str] = field(default_factory=list)
    actions_taken: list[str] = field(default_factory=list)
    duration_ms: int | None = None
    tool_name: str = ""
```

### Files to Modify

**1. MCP Tools** (`ada-mcp/src/ada_mcp/tools/`)
- Create `types.py` with `ToolResult` and `ToolMetadata`
- Update `introspection.py` to return `ToolResult` instead of string
- Update other tools: `complete_code.py`, etc.
- Each tool explicitly declares what it accessed

**2. MCP Server** (`ada-mcp/src/ada_mcp/server.py`)
- Handle `ToolResult` return type
- Extract metadata for transparency
- Pass both content AND metadata to caller

**3. VS Code Extension** (`ada-vscode/src/`)
- `mcpClient.ts` - Parse structured responses (content + metadata)
- `chatViewProvider.ts` - Use metadata directly (no regex needed!)
- Remove pattern-matching from `ToolTransparencyFormatter` (keep for fallback)

### Two-Phase Pattern for Compound Queries

For "use introspection to find TODOs and suggest an easy one":

```typescript
// chatViewProvider.ts - enhanced query handling
async handleUserMessage(message: string) {
    const intent = classifyIntent(message);
    
    if (intent.requiresTool && intent.requiresReasoning) {
        // Phase 1: Call tool, get structured data
        const toolResult = await this._mcpClient.callTool(intent.tool, intent.params);
        
        // Phase 2: Inject result into LLM context
        const augmentedMessage = `
            Based on this ${intent.tool} result:
            ${toolResult.content}
            
            User's request: ${message}
        `;
        
        // Show tool transparency from metadata
        this._postMessage({ type: 'toolFiles', files: toolResult.metadata.files_accessed });
        
        // Let LLM reason about it
        return this._streamChat(augmentedMessage);
    }
    // ... existing flows
}
```

### Intent Classification (Simple First)

```typescript
function classifyIntent(message: string): Intent {
    const lower = message.toLowerCase();
    
    // Pattern: "use X to Y" or "X and then Y"
    const toolThenReason = /use\s+(introspection|search|analyze)\s+.*\s+(and|to)\s+/i;
    
    if (toolThenReason.test(message)) {
        return {
            requiresTool: true,
            requiresReasoning: true,
            tool: extractToolName(message),
            params: extractParams(message)
        };
    }
    
    // Pure tool call
    if (lower.includes('use introspection') || lower.includes('introspect')) {
        return { requiresTool: true, requiresReasoning: false, tool: 'introspect' };
    }
    
    // Pure chat
    return { requiresTool: false, requiresReasoning: true };
}
```

---

## Implementation Order

**Phase 1: Tool Result Envelope** (foundation)
1. Create `ada-mcp/src/ada_mcp/types.py` with dataclasses
2. Update `introspection.py` to return `ToolResult`
3. Update `server.py` to handle new type
4. Test with existing VS Code extension (should still work via content)

**Phase 2: Extension Metadata Support**
5. Update `mcpClient.ts` to parse metadata
6. Update `chatViewProvider.ts` to use metadata directly
7. Remove regex patterns (keep as fallback)
8. Test tool transparency with structured data

**Phase 3: Two-Phase Pattern**
9. Add intent classification to `chatViewProvider.ts`
10. Implement tool→reasoning flow
11. Test compound queries: "introspect and suggest a TODO"

---

## Current File Locations

**MCP Server:**
- `ada-mcp/src/ada_mcp/server.py` - Main MCP server
- `ada-mcp/src/ada_mcp/tools/introspection.py` - Introspection tool
- `ada-mcp/src/ada_mcp/tools/complete_code.py` - Code completion

**VS Code Extension:**
- `ada-vscode/src/chatViewProvider.ts` - Main chat logic
- `ada-vscode/src/mcpClient.ts` - MCP communication
- `ada-vscode/src/formatters/ToolTransparencyFormatter.ts` - Pattern extraction

**Documentation:**
- `.ai/context.md` - Architecture overview
- `.ai/codebase-map.json` - Module dependencies

---

## Commands

```bash
# Build extension
cd ada-vscode && npm run compile && npm run package

# Install extension
code --install-extension ada-code-0.1.0.vsix --force

# Run MCP tests
cd ada-mcp && uv run pytest tests/ -v

# Check brain health
curl http://localhost:8000/v1/healthz
```

---

## Luna Notes

- **Haiku mode:** Be terse, organized. Voice comes through!
- **TDD:** Write test first, implement second
- **Small commits:** One logical change per commit
- **Pattern:** When stuck, read existing code first

---

## Archived Handoffs

Old session handoffs live in `archive/sessions/`:
- `2025-12-20-handoff.md` - TTFT optimization, streaming fixes
- `2025-12-18-handoff.md` - Code completion optimization session
- `2025-12-16/` - Matrix bridge, build system, docs audit

---

*ada and luna, same on both sides* 💜
