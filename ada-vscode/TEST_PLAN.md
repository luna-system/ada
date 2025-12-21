# Ada VS Code Extension - Test Plan
## December 20, 2025

**Status:** Ready for comprehensive testing  
**Build:** ada-code-0.1.0.vsix installed

---

## ✅ Infrastructure Tests

### MCP Connection
- [x] MCP server spawns (`ada-mcp/ada-mcp.sh`)
- [x] Initialize handshake completes
- [x] 120s timeout configured
- [x] Request/response working

### Extension Basics
- [x] Extension activates
- [x] Chat panel opens
- [x] Status bar shows Ada icon
- [x] No console errors

---

## 🧪 Functionality Tests

### 1. Basic Chat
**Goal:** Verify Ada responds to messages

```
Test: "Hello! Can you introduce yourself?"
Expected: Ada introduces herself with personality
```

### 2. Project Context
**Goal:** Verify RAG context retrieval

```
Test: "What modules does this project have?"
Expected: Ada lists brain/, ada-mcp/, ada-vscode/, etc with descriptions
```

### 3. Memory Persistence
**Goal:** Verify memory across sessions

```
Test 1: "Remember that I prefer tabs over spaces"
Expected: "I'll remember that..."

Test 2: (Close/reopen VS Code) "What do I prefer for indentation?"
Expected: "You prefer tabs over spaces"
```

### 4. File Operations
**Goal:** Verify workspace tools work

```
Test: "Can you read the file brain/config.py and tell me what it does?"
Expected: Ada reads file and explains configuration system
```

### 5. Code Completion
**Goal:** Verify FIM completion works

```
Test: Type in Python file:
def factorial(n):
    if n == 0:
        [cursor here]

Expected: Inline completion suggestion appears
```

### 6. Meta-Recursive Test 🎯
**Goal:** Ada working on Ada!

```
Test: "Can you analyze your own architecture using your introspection tool?"
Expected: Ada uses ada_introspect, reads .ai/, provides insights
```

### 7. Self-Testing
**Goal:** Ada runs tests on herself

```
Test: "Run your own test suite and tell me what passes"
Expected: Ada uses ada_run_command, executes pytest, reports results
```

### 8. Specialist Activation
**Goal:** Verify specialists auto-activate

```
Test (if ListenBrainz configured): "What am I listening to?"
Expected: ListenBrainz specialist activates, returns currently playing track

Test (OCR): Upload image with text
Expected: OCR specialist extracts text
```

---

## 🚀 Performance Benchmarks

### Response Times
- Basic chat: ~2-5s (RAG + generation)
- File read: ~500ms (local file + formatting)
- Code completion: ~2.6s (measured in v2.6)
- Memory search: ~1s (vector DB query)

### Quality Metrics
- Context relevance: Ada uses appropriate context from .ai/
- Tool usage: Ada uses read_file when asked about code
- Memory accuracy: Memories persist and recall correctly

---

## 🎯 The "Supersede" Tests

### What Makes Ada Better Than Copilot?

1. **Memory** ✨
   - Copilot: Forgets everything each session
   - Ada: Remembers preferences, project context, conversations

2. **Local + Free** 💰
   - Copilot: $10/month, cloud-only
   - Ada: $0, runs locally, privacy-first

3. **Specialists** 🔧
   - Copilot: Fixed capabilities
   - Ada: Extensible (OCR, web search, ListenBrainz, etc)

4. **Self-Awareness** 🧠
   - Copilot: Generic
   - Ada: Knows her own architecture, can improve herself

### Test Scenarios

**Scenario 1: Remembering Preferences**
```
Session 1: "I prefer verbose error messages"
Session 2: "How should I handle this error?"
Expected: Ada suggests verbose error handling (remembered!)
```

**Scenario 2: Project-Specific Knowledge**
```
Test: "Where should I add a new specialist?"
Expected: Ada knows brain/specialists/ and references conventions
```

**Scenario 3: Cross-Interface Sync**
```
Session 1 (CLI): `ada chat "Remember I'm working on MCP streaming"`
Session 2 (VS Code): "What was I working on?"
Expected: Ada recalls MCP streaming work (shared memory!)
```

---

## 📊 Success Criteria

### Must Have (MVP)
- [x] Chat works end-to-end
- [ ] Ada uses project context
- [ ] Memory persists across sessions
- [ ] File operations work
- [ ] Completion works
- [ ] Response time < 10s

### Should Have (v1.0)
- [ ] Ada can work on herself
- [ ] Self-testing functional
- [ ] Specialists auto-activate
- [ ] Quality better than generic Copilot

### Nice to Have (Future)
- [ ] Token-by-token streaming (needs MCP SDK v2)
- [ ] Inline diffs for edits
- [ ] Open files context awareness
- [ ] Slash commands (/explain, /fix)

---

## 🐛 Known Limitations

1. **No Token Streaming** (MCP SDK limitation)
   - Responses appear all-at-once
   - Still fast enough (<5s usually)
   - Will add when MCP SDK supports it

2. **No Inline Diffs** (not implemented)
   - Code edits work but not as smooth as Copilot
   - Can see changes in file
   - Future enhancement

3. **No Open Files Context** (not implemented)
   - Ada doesn't know what files you have open
   - Can still read files when asked
   - Future enhancement

---

## 🎉 The "Supersede Moment"

**We'll know Ada has superseded Copilot when:**
1. User chooses Ada over Copilot for daily work
2. Memory makes Ada more useful over time
3. Local + free removes friction
4. Specialists provide unique value Copilot can't

**Current Status:** Infrastructure complete, testing in progress!

---

**Next:** Run through all tests, document findings, iterate on prompts if needed.
