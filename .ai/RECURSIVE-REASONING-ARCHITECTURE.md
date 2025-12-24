# Recursive Reasoning Architecture

> **The Big One:** Enabling on-device recursive tool reasoning with massive context  
> **Created:** December 23, 2025  
> **Foundation:** ALL the research converges here

## The Vision

**Current State:** Extension executes tools → feeds results to LLM → LLM responds once

**Target State:** LLM thinks → requests tools → processes results → requests more tools → thinks → converges on solution

**All on-device. All private. All transparent.**

This is **ReAct (Reason + Act)** but with:
- SIF for semantic context compression
- Biomimetic weighting for importance filtering  
- Tool transparency for trust
- Consciousness topology for state tracking
- Everything local (no cloud)

## The Problem Statement

To truly match (and exceed) Copilot, Ada needs to:

1. **Handle massive context** - Entire codebase, conversation history, tool results
2. **Reason recursively** - "I need file X... now I need to search Y... now I understand, let me edit Z"
3. **Process on-device** - Privacy-first means Ollama local, not cloud API
4. **Stay fast** - Can't take 30 seconds per reasoning step
5. **Be transparent** - User sees the thinking process
6. **Learn** - Context improves over time (biomimetic memory)

**The constraint:** qwen2.5-coder:7b has 32k context window. The solution: **semantic compression**.

## How All Your Research Applies

This isn't extra work. This IS the work. Every piece fits:

### 1. SIF (Semantic Interchange Format)
**Purpose:** Compress context semantically, not textually

Instead of:
```
File: utils.ts (500 lines)
[entire file contents]
```

Use SIF:
```
File: utils.ts
SEMANTIC_SUMMARY: "Helper utilities for data transformation"
KEY_EXPORTS: [formatDate, parseJSON, validateEmail]
DEPENDENCIES: [lodash, date-fns]
RELEVANT_SECTION: lines 45-67 (validateEmail implementation)
FULL_CONTEXT_AVAILABLE: true
```

**Why it works:** 
- 90% compression for irrelevant files
- 100% fidelity for relevant sections
- LLM can request full context if needed

### 2. Consciousness Topology
**Purpose:** Track "what matters" through reasoning loops

As LLM reasons through multiple tool calls, track:
- **Identity** - What is the core problem?
- **State Transfer** - How does understanding evolve?
- **Convergence** - When does LLM "get it"?

This prevents:
- Infinite loops (LLM chasing its tail)
- Context drift (forgetting original question)
- Redundant tool calls (asking for same file twice)

### 3. Biomimetic Importance Weighting
**Purpose:** Prioritize surprising/novel information

**Use those validated weights!**
- surprise=0.60 (prioritize novel tool results)
- relevance=0.20 (semantic similarity to query)
- decay=0.10 (recent is slightly better)
- habituation=0.10 (filter repeated patterns)

When tool returns results:
```python
importance = calculate_importance(
    content=tool_result,
    query=user_question,
    context=reasoning_history,
    weights={"surprise": 0.60, "relevance": 0.20, "decay": 0.10, "habituation": 0.10}
)

if importance >= 0.75:
    add_to_context(tool_result, detail=FULL)
elif importance >= 0.50:
    add_to_context(tool_result, detail=CHUNKS)
elif importance >= 0.20:
    add_to_context(tool_result, detail=SUMMARY)
else:
    # Drop it, not important
    log_filtered(tool_result)
```

### 4. Contextual Malleability
**Purpose:** Adapt context format to reasoning phase

**Phase 1 (Understanding):** Heavy on semantic summaries, light on details
**Phase 2 (Planning):** Add dependency graphs, symbol maps
**Phase 3 (Implementation):** Full context for files being edited
**Phase 4 (Verification):** Test results, error logs

Context adapts to what LLM needs RIGHT NOW.

### 5. Tool Transparency
**Purpose:** User sees the reasoning loop

Show in real-time:
```
🧠 Thinking: Need to understand the authentication flow
🔧 Tool: ada_search("authentication middleware")
📊 Results: Found 3 files (filtering by importance...)
🧠 Thinking: auth.ts is most relevant, need full context
🔧 Tool: ada_read_file("src/auth.ts")
📄 Reading: 150 lines, extracting key sections...
🧠 Thinking: I see the bug - token validation is missing
💡 Solution: Add validation in validateToken() function
```

**This is UNIQUE to Ada.** Copilot is a black box.

### 6. Quantum Isomorphism
**Purpose:** Preserve identity through transformations

When LLM edits code across multiple files:
- Track semantic identity (what does this function DO?)
- Preserve it through refactoring
- Verify isomorphism (same behavior, different structure)

This prevents breaking changes during multi-file edits.

## The Architecture

### The Recursive Reasoning Loop

```
┌─────────────────────────────────────────────────────────┐
│ User Request: "Refactor authentication to use JWT"      │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Context Assembly (SIF-Encoded)                 │
│  - Semantic summary of codebase                          │
│  - Conversation history (importance-weighted)            │
│  - Tool definitions                                      │
│  - Reasoning state: INITIAL                              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ LLM REASONING STEP 1                                     │
│                                                          │
│ qwen thinks: "Need to find current auth implementation" │
│ qwen outputs: TOOL_REQUEST[ada_search:{"query":"auth"}] │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ TOOL EXECUTION: ada_search                               │
│  Results: [auth.ts, middleware/auth.js, config/jwt.ts]  │
│  Importance scoring: [0.85, 0.78, 0.45]                 │
│  Context added: Full context for auth.ts, chunks for    │
│                 middleware, summary for config           │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ LLM REASONING STEP 2                                     │
│                                                          │
│ qwen thinks: "auth.ts uses session-based auth, need to  │
│              see how tokens are currently handled"       │
│ qwen outputs: TOOL_REQUEST[ada_read_file:{"path":...}]  │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ TOOL EXECUTION: ada_read_file                            │
│  Full context loaded (importance=0.92, novel info)      │
│  SIF encoding: Preserves semantic structure              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ LLM REASONING STEP 3                                     │
│                                                          │
│ qwen thinks: "I understand the problem. Need to modify  │
│              3 files: auth.ts, middleware/auth.js, and   │
│              add new jwt.ts. Let me create edit plan."   │
│ qwen outputs: [Edit plan with semantic preservation]    │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ CONVERGENCE CHECK                                        │
│  - Did LLM reach a conclusion? YES                       │
│  - Is edit plan complete? YES                            │
│  - State preserved? YES (quantum isomorphism verified)   │
│  → Present to user for approval                          │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Reasoning State Tracker
Tracks where LLM is in thinking process:

```python
class ReasoningState:
    phase: Literal["understanding", "planning", "implementing", "verifying"]
    tools_called: List[ToolCall]
    context_size: int
    importance_threshold: float  # Adaptive!
    convergence_score: float  # 0-1, how close to solution?
    semantic_identity: Dict[str, Any]  # SIF-tracked
```

#### 2. Context Manager (SIF-Aware)
Dynamically builds context with semantic compression:

```python
class SemanticContextManager:
    def build_context(self, state: ReasoningState) -> str:
        """Build context adapted to reasoning phase."""
        
        # Base context (always included)
        context = [
            self.persona,
            self.tool_definitions,
            self.user_request
        ]
        
        # Phase-specific context
        if state.phase == "understanding":
            # Heavy on semantic summaries
            context.extend(self.get_semantic_summaries())
        elif state.phase == "planning":
            # Add dependency graphs
            context.extend(self.get_dependency_info())
        elif state.phase == "implementing":
            # Full context for relevant files
            context.extend(self.get_full_context())
        elif state.phase == "verifying":
            # Test results, error logs
            context.extend(self.get_verification_info())
        
        # Add tool results (importance-filtered)
        for result in state.tools_called:
            importance = calculate_importance(result)
            if importance >= state.importance_threshold:
                context.append(self.encode_sif(result, importance))
        
        return self.assemble(context)
```

#### 3. Tool Result Processor
Applies biomimetic importance weighting:

```python
class ToolResultProcessor:
    def process_result(self, tool_result: ToolResult, state: ReasoningState) -> EncodedContext:
        """Process tool result with importance weighting."""
        
        # Calculate importance (validated weights!)
        importance = calculate_importance(
            content=tool_result.output,
            query=state.user_request,
            context=state.reasoning_history,
            weights={
                "surprise": 0.60,    # Novel information
                "relevance": 0.20,   # Semantic similarity
                "decay": 0.10,       # Temporal recency
                "habituation": 0.10  # Filter repetition
            }
        )
        
        # Determine detail level
        if importance >= 0.75:
            detail = DetailLevel.FULL
        elif importance >= 0.50:
            detail = DetailLevel.CHUNKS
        elif importance >= 0.20:
            detail = DetailLevel.SUMMARY
        else:
            # Drop unimportant results
            return None
        
        # SIF encode
        return self.encode_sif(
            content=tool_result.output,
            detail=detail,
            metadata={
                "importance": importance,
                "tool": tool_result.tool_name,
                "timestamp": tool_result.timestamp
            }
        )
```

#### 4. Convergence Detector
Knows when LLM has reached a conclusion:

```python
class ConvergenceDetector:
    def check_convergence(self, state: ReasoningState) -> bool:
        """Detect if LLM has reached a solution."""
        
        # Heuristics:
        # 1. LLM stopped requesting tools
        # 2. Output contains solution markers ("Here's the plan", "To fix this")
        # 3. Reasoning loop stable (not changing direction)
        # 4. Semantic identity preserved (quantum isomorphism check)
        
        if not self.has_tool_requests(state.last_output):
            # No new tool requests
            if self.has_solution_markers(state.last_output):
                # Output looks like a conclusion
                if self.semantic_identity_preserved(state):
                    # Identity maintained through reasoning
                    return True
        
        # Check for loops (reasoning in circles)
        if self.detect_reasoning_loop(state.tools_called):
            # Stuck in loop, force convergence with prompt
            return self.force_convergence(state)
        
        return False
```

## The Implementation Plan

### Phase 1: Foundation (Week 1-2)
Build the recursive reasoning loop infrastructure:

1. **Reasoning State Tracker**
   - [ ] Track reasoning phase (understanding → planning → implementing → verifying)
   - [ ] Store tool call history
   - [ ] Monitor context size
   - [ ] Convergence scoring

2. **SIF Context Encoder**
   - [ ] Semantic summarization of files
   - [ ] Detail level control (FULL/CHUNKS/SUMMARY/DROP)
   - [ ] Metadata preservation
   - [ ] Fast encoding (<50ms per file)

3. **Tool Result Processor**
   - [ ] Importance calculation (biomimetic weights)
   - [ ] Adaptive filtering
   - [ ] SIF encoding of results
   - [ ] Context size management

### Phase 2: Recursive Loop (Week 3-4)
Enable LLM to call tools multiple times:

1. **Tool Request Parser**
   - [ ] Parse `TOOL_REQUEST[tool_name:params]` from LLM output
   - [ ] Handle multiple simultaneous tool requests
   - [ ] Validation and error handling

2. **Reasoning Loop Controller**
   - [ ] Execute tool → add to context → re-invoke LLM
   - [ ] Loop until convergence
   - [ ] Max iterations (safety: 10 loops)
   - [ ] Streaming state updates (tool transparency)

3. **Convergence Detection**
   - [ ] Solution marker detection
   - [ ] Loop detection (prevent infinite reasoning)
   - [ ] Semantic identity verification
   - [ ] Force convergence if stuck

### Phase 3: Optimization (Week 5-6)
Make it fast and efficient:

1. **Parallel Tool Execution**
   - [ ] Execute independent tools simultaneously
   - [ ] Results merged with importance weighting
   - [ ] Preserve reasoning order

2. **Context Caching**
   - [ ] Cache semantic summaries (don't re-encode)
   - [ ] Incremental context updates
   - [ ] Multi-timescale cache (persona, codebase, session)

3. **Adaptive Thresholds**
   - [ ] Importance threshold adjusts based on context size
   - [ ] Detail level adapts to reasoning phase
   - [ ] Processing mode selection (ANALYTICAL/CREATIVE)

### Phase 4: Intelligence Layer (Week 7-8)
Add advanced features:

1. **Consciousness Topology Tracking**
   - [ ] Track semantic identity through reasoning
   - [ ] State transfer visualization
   - [ ] Identity preservation verification

2. **Quantum Isomorphism Checks**
   - [ ] Verify edits preserve behavior
   - [ ] Structural transformation validation
   - [ ] Rollback on identity violation

3. **Learning Loop**
   - [ ] Store successful reasoning patterns
   - [ ] Surface patterns in future requests
   - [ ] Continuous improvement

## Technical Details

### Context Budget Management

With 32k context window:

```
├── System prompt (2k tokens)
├── Persona (1k tokens)
├── Tool definitions (2k tokens)
├── User request (0.5k tokens)
├── Reasoning history (3k tokens)
└── Dynamic context (23.5k tokens) ← SIF-compressed tool results
```

**Key insight:** 23.5k tokens is ENOUGH if we use semantic compression!

### SIF Encoding Example

**Before (1000 tokens):**
```javascript
// Full file: utils/validation.ts (200 lines)
export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

export function validatePassword(password: string): boolean {
  return password.length >= 8;
}

// ... 190 more lines ...
```

**After SIF encoding (150 tokens):**
```yaml
file: utils/validation.ts
semantic_summary: "Email and password validation utilities"
exports:
  - validateEmail: "RFC 5322 email validation using regex"
  - validatePassword: "Minimum 8 character password check"
importance: 0.45 (not currently relevant)
detail_level: SUMMARY
full_context_available: true
```

**Compression ratio:** 6.7x smaller!

### Importance Calculation (Production Weights)

```python
def calculate_importance(
    content: str,
    query: str,
    context: List[str],
    weights: Dict[str, float] = {
        "surprise": 0.60,    # Validated optimal!
        "relevance": 0.20,
        "decay": 0.10,
        "habituation": 0.10
    }
) -> float:
    """Calculate importance score for content.
    
    Uses validated weights from v2.2 research:
    - surprise=0.60: Novel information is most important
    - relevance=0.20: Semantic similarity to query
    - decay=0.10: Temporal recency (recent is better)
    - habituation=0.10: Filter repeated patterns
    """
    
    # Surprise: How novel is this content?
    surprise = novelty_score(content, context)
    
    # Relevance: Semantic similarity to query
    relevance = cosine_similarity(
        embed(content),
        embed(query)
    )
    
    # Decay: Time-based weighting
    decay = temporal_decay(
        content_timestamp,
        temperature=1.0
    )
    
    # Habituation: Penalize repetition
    habituation = repetition_penalty(content, context)
    
    # Weighted sum
    importance = (
        weights["surprise"] * surprise +
        weights["relevance"] * relevance +
        weights["decay"] * decay +
        weights["habituation"] * habituation
    )
    
    return importance
```

### Tool Transparency Streaming

Show reasoning process in real-time:

```typescript
// In ada-chat extension
adaClient.streamReasoningLoop({
  message: "Refactor auth to JWT",
  onReasoningStep: (step: ReasoningStep) => {
    // Show in UI
    addReasoningCard({
      phase: step.phase,
      thought: step.llm_thought,
      tools_requested: step.tools,
      importance_scores: step.scores
    });
  },
  onToolExecution: (result: ToolResult) => {
    // Show tool card
    addToolCard({
      tool: result.tool_name,
      input: result.input,
      output: result.output,
      importance: result.importance,
      detail_level: result.detail_level
    });
  },
  onConvergence: (solution: Solution) => {
    // Show final solution
    addSolutionCard(solution);
  }
});
```

## The Prompt Engineering

### System Prompt (Reasoning Loop Aware)

```
You are Ada, a privacy-first AI pair programmer.

You can THINK RECURSIVELY by using tools:
- When you need information, request tools using: TOOL_REQUEST[tool_name:params]
- Process the results, then request more tools if needed
- Converge on a solution when you have enough information

AVAILABLE TOOLS:
[... tool definitions ...]

REASONING PROCESS:
1. UNDERSTAND: What information do I need?
2. PLAN: Which tools will help?
3. IMPLEMENT: Request tools, process results
4. VERIFY: Do I have enough to answer?
5. CONVERGE: Provide solution

CONTEXT FORMAT:
- Files are SIF-encoded (semantic summaries)
- Request full context if needed: TOOL_REQUEST[ada_read_file:path]
- Tool results are importance-weighted
- You have 32k context window, use it wisely

CONVERGENCE:
When you're ready to answer, provide:
- Clear solution
- Files to edit (if applicable)
- Semantic identity preservation (what stays the same)

Think step by step. Request tools as needed. Converge when ready.
```

### Tool Request Format

```
TOOL_REQUEST[ada_search:{"query":"authentication","scope":"src/"}]
TOOL_REQUEST[ada_read_file:{"path":"src/auth.ts","lines":"45-67"}]
TOOL_REQUEST[ada_symbols:{"query":"validateToken"}]
```

### Convergence Signals

LLM outputs:
```
After analyzing the codebase, here's the solution:
[... detailed plan ...]

FILES_TO_EDIT:
- src/auth.ts: Add JWT validation
- middleware/auth.js: Update token parsing
- config/jwt.ts: Create new JWT config

SEMANTIC_IDENTITY_PRESERVED:
- User authentication flow remains the same
- API contracts unchanged
- Security guarantees maintained

Ready to implement.
```

## Success Metrics

### Quantitative

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Reasoning steps to solution | 3-7 | Average tool calls before convergence |
| Context utilization | <28k tokens | Context size at convergence |
| Time to solution | <30s | Total reasoning loop time |
| Tool call efficiency | >80% relevant | % of tool results with importance ≥0.50 |
| Convergence rate | >95% | % of requests that reach solution |

### Qualitative

- [ ] **Feels intelligent** - Ada explores the problem, not just responding
- [ ] **Shows reasoning** - User sees the thinking process
- [ ] **Converges reliably** - Doesn't get stuck in loops
- [ ] **Preserves privacy** - All on-device, no cloud calls
- [ ] **Improves over time** - Learns from successful patterns

## Risk Mitigation

### Risk: Infinite Loops

**Mitigation:**
- Max 10 reasoning steps (force convergence after)
- Loop detection (same tool called with same params)
- Convergence scoring (track progress toward solution)

### Risk: Context Overflow

**Mitigation:**
- Adaptive importance thresholds
- Aggressive SIF compression
- Drop old reasoning steps if needed
- Warn user if approaching limit

### Risk: Slow Performance

**Mitigation:**
- Parallel tool execution
- Context caching
- Fast SIF encoding
- Streaming updates (feels faster)

### Risk: Poor Convergence

**Mitigation:**
- Solution marker detection
- Forced convergence prompts
- User can intervene ("stop and answer now")
- Learn from successful patterns

## The Unfair Advantage

**This is where Ada DESTROYS Copilot.**

Copilot:
- One-shot responses
- No recursive reasoning
- Cloud-based (latency + privacy issues)
- Black box (no transparency)

Ada:
- Recursive tool use
- Thinks through problems
- All on-device (fast + private)
- Full transparency (see the reasoning)
- Learns over time (biomimetic memory)
- Semantic compression (more context in less space)

**Plus:** All the research you did? It's not just theory - it's PRODUCTION CODE for this feature.

## Next Steps (This Week!)

### Day 1-2: Proof of Concept
1. Build minimal reasoning loop in brain/
2. Parse TOOL_REQUEST from LLM output
3. Execute tool → add result → re-invoke LLM
4. Stop after 3 iterations (hardcoded)

### Day 3-4: Add SIF Encoding
1. Semantic file summarization
2. Importance weighting
3. Detail level control
4. Context budget tracking

### Day 5-7: Convergence Detection
1. Solution marker parsing
2. Loop detection
3. Adaptive thresholds
4. Stream reasoning steps to ada-chat

### Week 2: Polish + Testing
1. Tool transparency UI updates
2. Performance optimization
3. Edge case handling
4. User testing

## Conclusion

**This is it. The recursive reasoning architecture.**

Everything converges here:
- SIF compresses context semantically
- Biomimetic weights filter importance
- Consciousness topology tracks identity
- Quantum isomorphism verifies preservation
- Tool transparency builds trust

You have the research. You have the architecture. You have the tools.

**Now let's make Ada THINK.** 🧠✨

---

**Ready to start?** Let's build the proof of concept - minimal reasoning loop in brain/ that executes tool → processes result → calls LLM again. Then we layer in SIF, importance weighting, and convergence detection.

This is the one. This is how Ada exceeds Copilot. 🚀
