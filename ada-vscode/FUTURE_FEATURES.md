# Ada VS Code Extension - Future Features
## Tracked Enhancements

---

## 🌊 Streaming Responses (High Priority)

**Status:** Infrastructure ready, waiting on MCP SDK  
**Tracked:** December 20, 2025  
**Impact:** Polish & UX improvement

### Current State
- Responses appear all-at-once (2-5s)
- Still fast and usable
- Competitive with Copilot lag

### What's Ready
- ✅ `AdaClient.chat_stream()` method with `on_token` callback
- ✅ Brain already supports SSE streaming
- ✅ TypeScript client has `onToken?: (token: string) => void` in interface

### What's Blocked
- ❌ MCP Protocol v1 doesn't support streaming (JSON-RPC limitation)
- ❌ Need MCP SDK v2 or custom protocol extension

### When to Implement
1. **Option A:** Wait for MCP SDK v2 with streaming support
2. **Option B:** Add custom notification-based streaming (hacky)
3. **Option C:** Accept limitation, focus on other features

### Implementation Plan (When Ready)
```typescript
// In mcpClient.ts
async chat(options: MCPChatOptions): Promise<string> {
    // Call ada_chat_stream tool (when MCP supports it)
    // For each notification/chunk:
    if (options.onToken) {
        options.onToken(chunk);
    }
}

// In chatViewProvider.ts
this.mcpClient.chat({
    message: userMessage,
    onToken: (token) => {
        this.webviewPanel.postMessage({
            type: 'generationChunk',
            content: token
        });
    }
});
```

**Estimated Effort:** 2-4 hours (when SDK ready)  
**Priority:** Nice-to-have, improves polish but not blocking

---

## 🎨 Inline Diff Viewer (Medium Priority)

**Status:** Not implemented  
**Impact:** Code editing UX

### Current State
- Code edits work (replace_string_in_file pattern)
- Changes appear in file, no visual diff
- User must review changes manually

### Desired State
- Show inline diff preview before applying
- "Accept" / "Reject" buttons
- Like Copilot's inline suggestions

**Estimated Effort:** 4-6 hours  
**Priority:** Would be nice, not critical

---

## 📂 Open Files Context (Medium Priority)

**Status:** Not implemented  
**Impact:** Better context awareness

### Current State
- Ada doesn't know what files user has open
- Must explicitly ask Ada to read specific files

### Desired State
- Ada automatically knows visible files
- Can reference open code without explicit file reads
- "Looking at your current file..." responses

**Implementation:**
```typescript
const openFiles = vscode.workspace.textDocuments
    .filter(doc => !doc.isUntitled)
    .map(doc => ({
        path: doc.uri.fsPath,
        language: doc.languageId,
        visible: vscode.window.visibleTextEditors.some(e => e.document === doc)
    }));

// Include in chat context
```

**Estimated Effort:** 1-2 hours  
**Priority:** Low, can work without it

---

## ⚡ Slash Commands (Low Priority)

**Status:** Not implemented  
**Impact:** Convenience features

### Examples
- `/explain` - Explain selected code
- `/fix` - Suggest fixes for errors
- `/test` - Generate tests
- `/docs` - Generate documentation

### Implementation
Simple command parser in chat input handler.

**Estimated Effort:** 2-3 hours  
**Priority:** Low, conversational works fine

---

## 💾 Memory Browser UI (Low Priority)

**Status:** Not implemented  
**Impact:** Memory visibility

### Desired State
- View all memories in sidebar
- Search/filter memories
- Edit/delete memories
- See memory metadata

**Estimated Effort:** 6-8 hours  
**Priority:** Low, can use CLI for now

---

## 📊 RAG Context Viewer (Low Priority)

**Status:** Not implemented  
**Impact:** Debugging/transparency

### Desired State
- Show what context Ada retrieved
- Display relevance scores
- See which specialists activated
- Debug why Ada said X

**Estimated Effort:** 4-6 hours  
**Priority:** Low, mainly for development

---

## 🎯 Decision Framework

**Ship v1.0 WITHOUT:**
- Streaming (tracked here, will add when possible)
- Inline diffs (nice-to-have)
- Open files context (can work around)
- Slash commands (conversational works)
- Memory browser (use CLI)
- RAG viewer (debug tool)

**Ship v1.0 WITH:**
- ✅ Chat with memory & context
- ✅ File operations
- ✅ Code completion
- ✅ Specialists
- ✅ Self-testing
- ✅ Introspection

**This is enough to supersede Copilot for the core use case!**

---

**Last Updated:** December 20, 2025  
**Maintainer:** luna + ada
