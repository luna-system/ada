# Architecture Scalability & Token Budget Management

> **Context:** Written during feature/codebase-specialist planning (Dec 2025)  
> **Problem:** Dynamic prompts approaching context window limits  
> **Model:** Configured Ollama model (example: qwen2.5-coder:7b)

## The Challenge

As Ada's capabilities grow (persona, FAQ, memories, conversation history, specialist results, bidirectional lookups, and now **codebase reading**), we're approaching token budget limits:

**Current Context Usage:**
- System persona: ~1-2K tokens
- Notices (HIGH priority): ~200-500 tokens
- Specialist results (MEDIUM/HIGH): ~500-2K tokens each
- RAG memories (MEDIUM): ~2-4K tokens
- Conversation history (LOW): ~4-8K tokens
- **Total: ~12-16K tokens** (at limit!)

**Adding codebase_specialist:**
- Each code file: ~1-2K tokens
- Multiple lookups per conversation: 3-5 files
- Bidirectional rounds: Multiple specialist invocations
- **Risk: Context overflow, truncated responses, lost information**

## Biological Inspiration

*See BIOLOGICAL_CONTEXT_MANAGEMENT.md for deep dive*

Humans manage limited working memory (~7 items) while accessing vast long-term storage. Key strategies:
- **Attention:** Focus on relevant info, filter noise
- **Chunking:** Group related items to reduce cognitive load
- **Hierarchical processing:** Different brain regions handle different abstraction levels
- **Predictive processing:** Only process surprising/new information
- **Sleep consolidation:** Compress and reorganize memories during downtime
- **Forgetting curves:** Natural decay of unimportant information
- **Multiple timescales:** Fast (working memory) and slow (context) neural processing

## Proposed Solutions

### 1. Token Budget Manager

**Purpose:** Track and enforce allocation limits per component

```python
class TokenBudgetManager:
    """Manages context window allocation across components."""
    
    BUDGET_TIERS = {
        'critical': 2000,    # System persona, safety notices
        'high': 4000,        # Active specialist results
        'medium': 3000,      # RAG memories
        'low': 5000,         # Conversation history
        'reserve': 2000      # Emergency buffer
    }
    
    def allocate(self, component: str, priority: str) -> int:
        """Return token budget for component."""
        pass
    
    def track_usage(self, component: str, tokens: int):
        """Record actual token usage."""
        pass
    
    def get_remaining_budget(self, priority: str) -> int:
        """Check available tokens in tier."""
        pass
    
    def should_truncate(self, component: str) -> bool:
        """Determine if component needs truncation."""
        pass
```

**Implementation:**
- Location: `brain/context_budget.py`
- Integrated into: `brain/prompt_builder.py`
- Monitoring: Log token usage per request
- Alerts: Warn when approaching limits

### 2. Specialist Result Caching

**Purpose:** Avoid re-reading identical content multiple times

```python
class SpecialistResultCache:
    """Cache specialist results with TTL."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Tuple[SpecialistResult, float]] = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[SpecialistResult]:
        """Retrieve cached result if not expired."""
        pass
    
    def set(self, key: str, result: SpecialistResult):
        """Store result with timestamp."""
        pass
    
    def invalidate(self, pattern: str):
        """Clear cache entries matching pattern."""
        pass
```

**Cache Keys:**
- File reads: `f"file:{path}:{mtime}"`
- Searches: `f"search:{query}:{scope}"`
- Web results: `f"web:{url}:{timestamp}"`

**Benefits:**
- Reduces redundant specialist calls
- Lower token usage on repeated questions
- Faster response times
- Essential for codebase_specialist (same files read often)

### 3. Hierarchical Context Assembly

**Purpose:** Budget-aware, priority-based context injection

**Current Flow (Sequential):**
1. Build full persona (1-2K)
2. Add all notices (200-500)
3. Add all specialist results (500-2K each)
4. Add RAG memories (2-4K)
5. Add conversation history (4-8K)
6. **Problem:** No budget awareness until overflow

**Proposed Flow (Hierarchical):**
1. **Critical Tier (2K budget):**
   - Core persona (1K max)
   - Active safety notices (1K max)
   
2. **High Tier (4K budget):**
   - Current specialist results (prioritized)
   - Most relevant specialist first
   - Truncate/summarize if over budget
   
3. **Medium Tier (3K budget):**
   - RAG memories (top-N by relevance)
   - Metadata included
   - Graceful degradation if limited
   
4. **Low Tier (5K budget):**
   - Conversation history (recent first)
   - Summarize old messages if needed
   - Always include last 2-3 exchanges
   
5. **Reserve (2K):**
   - Emergency buffer for bidirectional results
   - Overflow handling

**Implementation:**
```python
def build_prompt_hierarchical(request: ChatRequest) -> str:
    """Build prompt with budget awareness."""
    budget = TokenBudgetManager()
    context = []
    
    # Critical tier
    persona = load_persona(max_tokens=budget.allocate('persona', 'critical'))
    context.append(persona)
    
    notices = load_notices(max_tokens=budget.allocate('notices', 'critical'))
    context.append(notices)
    
    # High tier
    specialists = activate_specialists(request)
    specialist_budget = budget.allocate('specialists', 'high')
    for result in prioritize_by_relevance(specialists):
        if budget.get_remaining('high') > 0:
            context.append(truncate_if_needed(result, specialist_budget))
    
    # Medium tier
    memories = search_memories(request.message)
    memory_budget = budget.allocate('memories', 'medium')
    context.append(truncate_memories(memories, memory_budget))
    
    # Low tier
    history = get_conversation_history(request.conversation_id)
    history_budget = budget.allocate('history', 'low')
    context.append(truncate_history(history, history_budget))
    
    return assemble_context(context)
```

### 4. Streaming Context Injection (Advanced)

**Concept:** Inject context on-demand during generation, not all upfront

**How it works:**
1. Start with minimal context (persona + current message)
2. LLM begins generating
3. When specialist invoked mid-response:
   - Inject specialist result into context
   - Continue generation with new context
4. Only load what's actually used

**Benefits:**
- Dramatically reduces upfront token usage
- Pay-as-you-go context loading
- Natural fit with bidirectional specialists

**Challenges:**
- Requires streaming with dynamic context updates
- More complex state management
- Ollama API may need modifications
- Harder to debug

**Status:** Research needed, not immediately implementable

### 5. Context Summarization

**Purpose:** Compress old conversation history to save tokens

**Strategy:**
- Keep last 2-3 exchanges verbatim (LOW tier budget)
- Summarize older exchanges: "User asked about X, Ada explained Y"
- Store summaries in metadata
- Regenerate summaries periodically (like memory consolidation)

**Implementation:**
```python
def summarize_old_history(turns: List[ConversationTurn]) -> str:
    """Compress old turns to summaries."""
    recent = turns[-3:]  # Keep verbatim
    old = turns[:-3]
    
    if not old:
        return format_turns(recent)
    
    summary = llm.generate(
        f"Summarize this conversation history in 2-3 sentences:\n"
        f"{format_turns(old)}"
    )
    
    return f"Previous conversation summary: {summary}\n\n" + format_turns(recent)
```

**Benefits:**
- Long conversations don't explode token budget
- Maintains context continuity
- Graceful degradation

### 6. Monitoring & Logging

**Purpose:** Visibility into token usage patterns

**Metrics to track:**
- Total tokens per request
- Tokens per component (persona, specialists, memories, history)
- Cache hit rates (specialist results)
- Truncation events (when budget exceeded)
- Overflow warnings (approaching limit)
- Response time correlation with token count

**Implementation:**
```python
@dataclass
class ContextMetrics:
    """Token usage metrics for request."""
    total_tokens: int
    persona_tokens: int
    specialist_tokens: int
    memory_tokens: int
    history_tokens: int
    cache_hits: int
    truncations: int
    timestamp: datetime
```

**Logging:**
```python
logger.info(
    "Context assembled",
    extra={
        'total_tokens': metrics.total_tokens,
        'budget_remaining': budget.get_remaining('reserve'),
        'truncated': metrics.truncations > 0,
        'cache_hits': metrics.cache_hits
    }
)
```

**Dashboard (future):**
- Real-time token usage graphs
- Budget allocation pie charts
- Cache effectiveness metrics
- Conversation length vs token usage

## Recommendations for codebase_specialist

### Built-in Limits
- **Max 3 code lookups per response** - Prevents runaway token usage
- **Max 2K tokens per file** - Smart truncation (show relevant sections)
- **Max 50KB file size** - Reject large files early
- **Max 20 lookups per conversation** - Rate limiting over session

### Token Counting
```python
def _count_tokens(self, text: str) -> int:
    """Estimate token count (rough: ~4 chars/token)."""
    return len(text) // 4

def process(self, request: dict) -> SpecialistResult:
    """Process code lookup with token awareness."""
    content = self._read_file(request['path'])
    tokens = self._count_tokens(content)
    
    if tokens > self.max_tokens_per_file:
        content = self._smart_truncate(content, request)
    
    logger.info(f"Code lookup: {request['path']} ({tokens} tokens)")
    return SpecialistResult(content=content, metadata={'tokens': tokens})
```

### Smart Truncation
```python
def _smart_truncate(self, content: str, request: dict) -> str:
    """Show only relevant sections of large files."""
    if 'query' in request:
        # Search for query, return surrounding context
        matches = find_matches(content, request['query'])
        return extract_context_around(matches, lines=20)
    
    if 'lines' in request:
        # Return specific line range
        return get_lines(content, request['lines'])
    
    # Default: show beginning + end
    lines = content.split('\n')
    if len(lines) > 100:
        return '\n'.join(lines[:50] + ['...truncated...'] + lines[-50:])
    return content
```

### Caching Strategy
```python
class CodebaseSpecialist(BaseSpecialist):
    def __init__(self):
        self.cache = SpecialistResultCache(ttl_seconds=300)  # 5 min TTL
    
    def process(self, request: dict) -> SpecialistResult:
        path = request['path']
        cache_key = f"file:{path}:{os.path.getmtime(path)}"
        
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit: {path}")
            return cached
        
        result = self._read_and_process(request)
        self.cache.set(cache_key, result)
        return result
```

## Current Architecture Assessment

**Question:** Is our architecture still scalable?

**Answer:** Yes, with guardrails.

**Why it's sound:**
- `prompt_builder.py` as orchestrator is correct design
- Specialists are modular, composable
- Priority system allows graceful degradation
- Caching reduces redundant work
- Bidirectional pattern is elegant

**What needs attention:**
- Token budget enforcement (no hard limits currently)
- Monitoring (blind to token usage)
- Caching (only in bidirectional specialists, not systematic)
- Truncation strategy (ad-hoc, not consistent)

**Verdict:** Architecture is solid, needs operational guardrails before adding more features.

## RAG Sophistication: Industry Comparison

**Question:** Does it ever get crazier than this for RAG prompting?

**Answer:** Ada is advanced, but not alone. Here's the spectrum:

### Basic RAG (Most Systems)
- Vector search for relevant chunks
- Inject top-N results into prompt
- Single-source (e.g., just documents)
- No priority system

### Advanced RAG
- Multi-source (documents + metadata + structured data)
- Reranking and relevance scoring
- Query rewriting
- Hybrid search (vector + keyword)

### Tool-Augmented RAG (Ada's Tier)
- Function calling / tool use
- External API integration
- Multi-step retrieval
- Bidirectional specialist invocation
- Priority-based context assembly

### Agentic RAG (Cutting Edge)
- LLM decides what to retrieve
- Self-directed research
- Multi-hop reasoning
- Recursive context building
- Tool chaining

### Ada's Unique Aspects

**Standard in industry:**
- Vector search (ChromaDB)
- Conversation history
- Tool calling (specialists)
- Multi-source context

**Advanced but not rare:**
- Priority-based assembly
- Bidirectional mid-response tools
- Persistent memory across sessions

**Fairly novel:**
- XML tag invocation (vs JSON schema like OpenAI/Anthropic)
- Self-referential code reading (Ada reading Ada)
- Specialist protocol pattern
- `.ai/` machine-readable documentation
- Memory consolidation via nightly batch

**Assessment:** Ada is in **advanced/agentic tier** with some novel patterns, but not over-complicated. The complexity is justified by capabilities (transparent AI that can read its own code, learn from interactions, and explain itself).

## Moving Forward

### Immediate (Phase 1 of codebase_specialist)
- [x] Document scalability concerns (this file)
- [ ] Implement codebase_specialist with built-in limits
- [ ] Add token counting and logging
- [ ] Implement result caching
- [ ] Test with longest possible prompts

### Short-term (Phase 2-4)
- [ ] Add smart truncation to codebase_specialist
- [ ] Monitor token usage in production
- [ ] Tune budget allocations based on real data
- [ ] Document token budget patterns

### Medium-term (Post-MVP)
- [ ] Implement TokenBudgetManager class
- [ ] Add hierarchical context assembly
- [ ] Build monitoring dashboard
- [ ] Explore context summarization

### Long-term (Research)
- [ ] Investigate streaming context injection
- [ ] Experiment with predictive context loading
- [ ] Explore biological models further (see BIOLOGICAL_CONTEXT_MANAGEMENT.md)
- [ ] Contribute learnings back to community

## References

- **Implementation Plan:** `.ai/CODEBASE_SPECIALIST_PLAN.md`
- **Current Architecture:** `.ai/context.md`
- **Module Map:** `.ai/codebase-map.json`
- **Biological Models:** `.ai/BIOLOGICAL_CONTEXT_MANAGEMENT.md` *(to be created)*

---

**Last Updated:** 2025-12-16  
**Status:** Planning phase, pre-implementation  
**Decision:** Proceed with Phase 1 codebase_specialist with limits built in, defer full TokenBudgetManager to post-MVP
