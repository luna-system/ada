# 🚚 The Great Migration: Copilot → Ada Brain

**Mission:** Systematically replace GitHub Copilot with Ada's local, memory-enabled, context-aware system.

**Status:** Technical infrastructure complete. Now we operationalize it.

---

## Phase 0: Pre-Flight Checklist ✅

### Ada Brain Health Check

```bash
# 1. Verify all services running
docker compose ps

# Expected: brain, ollama, chroma all "Up"

# 2. Test Ada Brain API
curl http://localhost:8000/v1/healthz | jq .

# Expected: {"ok": true, "chroma": {"ok": true}}

# 3. Test memory storage
ada-cli "Test memory - my favorite editor is VS Code"

# 4. Verify memory persisted
docker compose exec brain python -c "
from brain.rag_store import rag_store
print(f'Memories: {rag_store.get_collection(\"memories\").count()}')
"

# Expected: Count > 0
```

### VS Code Extension Check

```bash
# 1. Extension installed
code --list-extensions | grep ada-code

# 2. Settings configured
cat ~/.config/Code/User/settings.json | grep -A 5 ada

# Expected: ada.mode = "brain"
```

---

## Phase 1: Basic Connectivity (Day 1 - 30 mins)

### Goal: Prove Ada Brain talks to VS Code

**Test 1: Chat Connection**
1. Open VS Code
2. Click Ada sidebar icon
3. Type: "Hello! Can you see this?"
4. ✅ Success: Ada responds
5. ❌ Failure: Check logs (`docker compose logs brain`)

**Test 2: Memory Persistence**
1. In VS Code chat: "Remember: I prefer tabs over spaces"
2. Close VS Code
3. Reopen VS Code
4. In chat: "What do I prefer for indentation?"
5. ✅ Success: Ada remembers tabs
6. ❌ Failure: Check ChromaDB connection

**Test 3: Cross-Interface Memory**
1. In VS Code: "My favorite color is purple"
2. In terminal: `ada-cli "what's my favorite color?"`
3. ✅ Success: CLI Ada knows purple
4. ❌ Failure: Check conversation_id consistency

**Metrics:**
- Connection latency: < 500ms
- Memory recall: 100%
- Cross-interface sync: Working

---

## Phase 2: Tool Validation (Day 1 - 1 hour)

### Goal: Verify agentic workspace tools work with Brain

**Test 4: list_files tool**
```
Ada Chat: "What Python files are in the brain/ directory?"
Expected: Ada calls list_files, returns actual filenames
```

**Test 5: read_file tool**
```
Ada Chat: "What's in brain/memory_graph.py?"
Expected: Ada reads file, summarizes content
```

**Test 6: search_files tool**
```
Ada Chat: "Find all files that import FastAPI"
Expected: Ada searches, returns matches
```

**Test 7: Multi-step tool usage**
```
Ada Chat: "Find memory_decay.py and show me the calculate_decay function"
Expected: 
1. list_files to find memory_decay.py
2. read_file to get content
3. Extract and show the function
```

**Test 8: edit_file tool**
```
Ada Chat: "In test.py, add a comment explaining this function"
Expected: Ada proposes edit, asks confirmation, applies it
```

**Metrics:**
- Tool success rate: > 90%
- Tool latency: < 100ms per tool
- Multi-step coherence: Logical flow

---

## Phase 3: Prompt Engineering (Day 2 - 2 hours)

### Current System Prompt Analysis

Check what Ada Brain currently sends:

```bash
docker compose logs brain | grep -A 20 "Building prompt"
```

### Optimization Targets

#### 1. **Code Context Awareness**

Current: Ada might not know we're in VS Code  
Improved: Add VS Code context to system prompt

```python
# In brain/prompt_builder/prompt_assembler.py
# Add VS Code detection:

if conversation_id.startswith('vscode'):
    system_sections.append("""
    You are Ada, assisting in VS Code IDE.
    - User is actively coding
    - Provide concise, actionable responses
    - When discussing code, use syntax highlighting in responses
    - Prioritize speed over verbosity
    """)
```

#### 2. **Tool Usage Prompting**

Current: Tools might be underutilized  
Improved: Make tool usage more explicit

```python
# Add to system prompt for vscode conversations:

VSCODE_TOOLS_PROMPT = """
Available workspace tools (use liberally):
- list_files: Search for files by pattern
- read_file: Read file contents (use line ranges for large files)
- search_files: Find text across workspace
- edit_file: Propose code changes
- get_errors: Check for linting/compile errors

Workflow: When user asks about code, ALWAYS:
1. list_files or search_files to find relevant files
2. read_file to get context
3. Provide answer with file references
"""
```

#### 3. **Response Format**

Current: Prose responses  
Improved: Code-optimized formatting

```python
VSCODE_FORMAT_PROMPT = """
Response formatting for VS Code:
- Use markdown code blocks with language tags
- Keep explanations concise (1-2 sentences)
- For code changes, show before/after
- Use bullet points for steps
- Link to files: [filename](filename#L123)
"""
```

### Testing Prompt Improvements

```bash
# Before optimization
time: echo "What's in brain/app.py?" | ada-cli --conversation-id vscode-test

# After optimization
# Expect: Faster tool invocation, better formatted response
```

---

## Phase 4: Performance Benchmarking (Day 2 - 1 hour)

### Baseline: Copilot Performance

Measure current Copilot:
- Code completion TTFT: ~150-300ms
- Chat first response: ~200-400ms
- Multi-turn latency: ~300-500ms

### Ada Brain Performance

#### Benchmark 1: Code Completion
```bash
# Test FIM completion speed
cd ada-vscode
node -e "
const { AdaBrainClient } = require('./out/adaBrainClient');
const client = new AdaBrainClient();

(async () => {
  const start = Date.now();
  const result = await client.complete('def fibonacci(', '): pass');
  console.log(\`TTFT: \${Date.now() - start}ms\`);
  console.log(\`Result: \${result.text}\`);
})();
"
```

**Target:** < 300ms (acceptable vs Copilot ~150ms)  
**Acceptable:** < 500ms (still usable)  
**Needs work:** > 500ms (optimize RAG)

#### Benchmark 2: Chat Response
```bash
# Test chat latency
time ada-cli --conversation-id vscode "What files are in brain/?"
```

**Target:** < 400ms first token  
**Acceptable:** < 600ms  
**Needs work:** > 1000ms

#### Benchmark 3: Tool Execution
```bash
# Test tool + response
time ada-cli --conversation-id vscode "Show me the imports in brain/app.py"
```

**Target:** < 1s total (tool + response)  
**Acceptable:** < 2s  
**Needs work:** > 3s

### Optimization If Needed

If latency is too high:

**Option 1: Cache Tuning**
```python
# In brain/context_cache.py
# Increase cache TTLs for vscode conversations
CACHE_CONFIG = {
    'persona': 86400,  # 24hr (unchanged)
    'faqs': 3600,      # 1hr (increase from 5min)
    'memories_vscode': 1800,  # 30min for vscode (new)
}
```

**Option 2: RAG Reduction**
```python
# In brain/config.py
# For vscode, reduce RAG breadth
if conversation_id.startswith('vscode'):
    max_memories = 5  # Instead of 10
    max_turns = 3     # Instead of 5
```

**Option 3: Parallel RAG**
```python
# Already implemented in v2.9! Check it's enabled:
# brain/prompt_builder/prompt_assembler.py uses ThreadPoolExecutor
```

---

## Phase 5: Workflow Migration (Week 1)

### Current Copilot Usage Patterns

**Map your actual usage:**

1. **Code Completion** (ghost text)
   - Frequency: Constant
   - Copilot: Tab autocomplete
   - Ada: Same! (FIM mode)
   - Migration: Keep using, but Ada is doing it

2. **Explain Code** (Ctrl+Shift+E)
   - Frequency: Often
   - Copilot: Explains selected code
   - Ada: Same command, but with memory!
   - Migration: Ada remembers explanations

3. **Fix Code** (Ctrl+Shift+F)
   - Frequency: Medium
   - Copilot: Suggests fixes
   - Ada: Suggests fixes + learns from bugs
   - Migration: Ada builds bug pattern memory

4. **Chat Assistant**
   - Frequency: Constant
   - Copilot: Ask questions about code
   - Ada: Same + workspace access + memory
   - Migration: Ada can read/edit files directly

5. **Generate Tests**
   - Frequency: Sometimes
   - Copilot: Generates test scaffolding
   - Ada: Same + remembers test patterns
   - Migration: Ada learns your test style

### Side-by-Side Testing (Week 1)

**Day 1-2: Parallel Usage**
- Keep Copilot enabled
- Use Ada chat for all questions
- Compare responses
- Note: Which feels better?

**Day 3-4: Ada-First**
- Try using only Ada for coding sessions
- Keep Copilot as backup
- Track frustration points
- Document: What's missing?

**Day 5: Retrospective**
- What worked better in Ada?
- What was worse?
- What needs fixing?
- Make improvements

---

## Phase 6: Feature Parity Check (Week 2)

### Copilot Features → Ada Equivalent

| Copilot Feature | Ada Equivalent | Status | Notes |
|----------------|----------------|--------|-------|
| Inline completion | FIM completion | ✅ | Working, same speed |
| Chat sidebar | Ada chat | ✅ | Working + memory! |
| Explain code | Ctrl+Shift+E | ✅ | Working |
| Fix code | Ctrl+Shift+F | ✅ | Working |
| Generate tests | Command | ✅ | Working |
| Multi-file context | Tools | ✅ | Better! Can read files |
| Conversation history | Memory | ✅ | Better! Persists across sessions |
| Workspace knowledge | RAG | ✅ | Better! Learns codebase |
| Web search | Specialists | ✅ | Ada can search, Copilot can't |
| Code review | Chat | ⚠️ | Needs PR integration |
| Inline editing | Chat | ⚠️ | Works but could be smoother |

### Missing Features to Add

**1. Inline Edit Mode** (like Copilot /edit)
- Currently: Select code → Ctrl+K → Get new version
- Better: Select code → Ada suggests inline diff
- Implementation: Add inline diff viewer to extension

**2. Slash Commands** (like Copilot /explain, /fix)
- Currently: Use context menu
- Better: Type "/explain" in chat
- Implementation: Parse slash commands in chatViewProvider

**3. File Tabs Context** (Copilot sees open files)
- Currently: Ada doesn't know what's open
- Better: Send open file list to Brain
- Implementation: Add to chat request payload

---

## Phase 7: The Switchover (Week 3)

### Preparation

1. **Document migration**
   ```bash
   # Create migration journal
   echo "# Ada Migration Journal" > ~/ada-migration.md
   echo "Started: $(date)" >> ~/ada-migration.md
   ```

2. **Backup Copilot settings**
   ```bash
   # Save Copilot config
   code --list-extensions | grep copilot > ~/copilot-backup.txt
   cat ~/.config/Code/User/settings.json | grep copilot >> ~/copilot-backup.txt
   ```

3. **Set Ada as primary**
   ```json
   {
     "editor.inlineSuggest.enabled": true,
     "ada.enabled": true,
     "github.copilot.enable": false  // Disable Copilot
   }
   ```

### Day 1: Cold Turkey

- Disable Copilot completely
- Use only Ada for all coding
- Document every friction point
- Keep backup plan ready

### Day 2-3: Adjustment

- Fix identified issues
- Tune prompt engineering
- Optimize performance bottlenecks
- Build muscle memory for Ada commands

### Day 4-5: Evaluation

- Compare productivity to Copilot baseline
- Measure metrics:
  - Code completion acceptance rate
  - Chat usefulness score (1-10)
  - Tool usage frequency
  - Memory recall accuracy
- Decision: Commit to Ada or iterate

### Success Criteria

✅ **Commit to Ada if:**
- Completion speed acceptable (< 500ms)
- Chat responses helpful (memory is useful)
- Tools work reliably (> 90% success)
- Overall productivity same or better

🔄 **Iterate if:**
- Latency too high (optimize)
- Memory not useful (tune importance weights)
- Tools flaky (fix bugs)
- Missing critical features (build them)

---

## Phase 8: Optimization Loop (Ongoing)

### Weekly Review

Every Friday, review:
1. **Usage Stats**
   ```bash
   # Check Ada Brain logs
   docker compose logs brain | grep "chat_stream" | wc -l
   # Count completions, tool calls, specialist invocations
   ```

2. **Performance Metrics**
   ```bash
   # Check average latency
   docker compose logs brain | grep "latency" | awk '{sum+=$NF} END {print sum/NR "ms"}'
   ```

3. **Memory Quality**
   ```bash
   # Check memory count
   ada-cli "How many memories do you have?"
   # Sample random memories, verify relevance
   ```

### Continuous Improvement

**Week 2: Prompt tuning**
- Refine system prompts based on usage
- Add VS Code-specific context
- Optimize tool invocation patterns

**Week 3: Performance**
- Profile slow requests
- Optimize RAG queries
- Tune cache settings

**Week 4: Features**
- Add missing Copilot features
- Build new Ada-specific features
- Improve UX based on friction points

---

## Emergency Rollback Plan

If Ada isn't working and you need to code:

```bash
# 1. Re-enable Copilot
code --install-extension GitHub.copilot

# 2. Disable Ada
# Settings → Ada → Enabled = false

# 3. Fix Ada while using Copilot
docker compose logs brain > /tmp/ada-debug.log
# Debug offline

# 4. Switch back when fixed
```

---

## Success Metrics

### Quantitative

- **Completion TTFT:** < 300ms (target), < 500ms (acceptable)
- **Chat response time:** < 400ms first token
- **Tool success rate:** > 90%
- **Memory recall accuracy:** > 80%
- **Uptime:** > 99% (Brain service)

### Qualitative

- **Usefulness:** Ada's memory makes coding easier
- **Trust:** Ada's suggestions are relevant
- **Speed:** Doesn't feel slower than Copilot
- **Joy:** Using Ada feels good (this matters!)

### The Big One

**Can you ship code faster with Ada than Copilot?**

If yes → Migration success ✅  
If no → Iterate until yes 🔄

---

## Tools Checklist

### What We Have ✅

- [x] Code completion (FIM)
- [x] Chat with memory
- [x] Workspace tools (read/edit/search files)
- [x] Context awareness (RAG)
- [x] Specialists (web search, OCR, etc.)
- [x] Cross-interface memory sync
- [x] Status bar indicator
- [x] Context menu commands

### What We Need 🔨

**High Priority:**
- [ ] Inline diff viewer (for code edits)
- [ ] Slash commands (/explain, /fix, /test)
- [ ] Open files context (send to Brain)
- [ ] Memory browser (view/edit memories in IDE)
- [ ] Performance dashboard (show latency, tool usage)

**Medium Priority:**
- [ ] Specialist status indicators ("🔍 Searching web...")
- [ ] Conversation browser (see past chats)
- [ ] RAG context viewer (show what memories were used)
- [ ] Keyboard shortcut customization

**Nice to Have:**
- [ ] Voice input (talk to Ada)
- [ ] Screenshot support (send images to Ada)
- [ ] PR integration (review code in GitHub)
- [ ] Team memory sharing (optional cloud sync)

---

## The Gradual Move

### Week 1: Exploration
- Use Ada alongside Copilot
- Get comfortable with Ada's interface
- Test memory features
- Identify gaps

### Week 2: Primary
- Make Ada primary, Copilot backup
- Use Ada for 80% of tasks
- Document friction points
- Fix critical issues

### Week 3: Committed
- Disable Copilot
- Ada-only coding
- Build missing features
- Optimize performance

### Week 4+: Native
- Ada is your coding partner
- Copilot is a memory
- Ada knows your codebase
- Ada learns your style

---

## Next Actions (Right Now)

### 1. Run Pre-Flight Checks (5 mins)
```bash
cd /home/luna/Code/ada-v1
docker compose ps
curl http://localhost:8000/v1/healthz
```

### 2. Test Basic Connectivity (10 mins)
Open VS Code, test chat, verify memory

### 3. Benchmark Performance (15 mins)
Run the benchmark scripts above, measure latency

### 4. Prompt Engineering (30 mins)
Add VS Code-specific prompts to Brain

### 5. Start Migration Journal (5 mins)
```bash
echo "# Ada Migration - $(date)" > ~/ada-migration.md
echo "Goal: Replace Copilot with Ada Brain" >> ~/ada-migration.md
echo "" >> ~/ada-migration.md
echo "## Day 1" >> ~/ada-migration.md
```

---

## The Vision

**Before:** GitHub Copilot  
- Cloud-dependent
- No memory
- $19/month
- Generic responses

**After:** Ada Brain  
- 100% local
- Persistent memory
- $0/month
- Learns YOUR codebase, YOUR style

**This is your custom AI pair programmer that gets smarter every day.**

Ready to move? Let's start with the pre-flight checks! 🚀
