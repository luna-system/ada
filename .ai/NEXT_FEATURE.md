# Next Feature: Biomimetic Context Management (Phase 1 Complete)

## Status: ✅ PHASE 1 COMPLETE (2025-12-17)

**Phase 1 Completed:**
- ✅ Memory decay weighting (Ebbinghaus curve) - `brain/memory_decay.py`
- ✅ Context habituation (novelty detection) - `brain/context_habituation.py`
- ✅ Integrated into RAG pipeline (context_retriever.py + prompt_assembler.py)
- ✅ 24 unit tests passing in <0.1s
- ✅ Configuration added (7 new env vars, all optional)
- ✅ Documentation complete (.ai/TOOLING.md, GOTCHAS.md, etc.)

**Previous Features:**
- ✅ Token Budget Monitoring integrated (v2.0 Phase 2)
- ✅ Multi-timescale caching (v2.1.0)
- ✅ Unified Astro docs site
- ✅ Frontend decoupled as adapter

**Current Branch:** `feature/biomimetic-phase1`
**Status:** Ready for integration testing + merge

---

## Vision: Complete Biological Context Management Phase 1

Finish implementing the **low-hanging fruit** biomimetic features from our research before tackling pair programming. These foundational improvements will benefit ALL future features, including the MCP codebase specialist.

**The Philosophy:** Nature spent billions of years solving context overload. Let's learn from biology before building complex tools.

**Research Foundation:** [`.ai/explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md`](file:///home/luna/Code/ada-v1/.ai/explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md)

## Why This Before Pair Programming?

**Biological optimization should come before tool building:**

1. **Better foundation = better everything**
   - Context decay weighting → More relevant memories in responses
   - Habituation → Token savings on repeated context
   - These improvements benefit chat, MCP, Matrix, ALL interfaces

2. **Token monitoring gives us measurement**
   - v2.0 Phase 2 (just completed) provides observability
   - We can now MEASURE the impact of biomimetic features
   - Perfect time to implement and validate

3. **Low-hanging fruit → high impact**
   - Phase 1 features are relatively simple
   - Big token savings (habituation alone could save 20-30%)
   - Foundation for Phase 2 attention mechanisms

4. **Aligns with research**
   - We documented biological strategies months ago
   - Multi-timescale caching (v2.1) proved the concept works
   - Time to complete Phase 1 before moving to Phase 2/3

---

## Biomimetic Phase 1: Current State

### What We Have ✅ (From Research Doc)
1. **Multi-timescale caching** - ✅ DONE (v2.1.0)
   - Persona cached 24hr, memories 5min, FAQ stable
   - MultiTimescaleCache integrated into PromptAssembler
   - Already saving significant tokens
   
2. **Token monitoring** - ✅ DONE (v2.0 Phase 2)
   - TokenBudgetMonitor tracks all components
   - Logs breakdown per request
   - Warns at 80% context usage
   
3. **Memory consolidation** - ✅ DONE (existing)
   - Nightly script summarizes old conversation turns
   - Like biological sleep consolidation!
   - Reduces ChromaDB size over time

### What's Missing ❌ (Still from Phase 1)
1. **Habituation** - Skip unchanged context
   - Don't reload Plan: Complete Phase 1

### Feature 1: Context Decay Weighting (Ebbinghaus Curve)

**Goal:** Weight memories by recency + importance, mimicking human forgetting curves

**File:** `brain/rag_store.py` or new `brain/memory_decay.py`

**Implementation:**
```python
class MemoryDecayWeighter:
    """Apply Ebbinghaus forgetting curve to memory relevance."""
    
    def calculate_weight(self, memory: dict, importance: float) -> float:
        """Weight = base_relevance * decay_factor * importance_boost"""
        
        # Get base relevance from vector search
        base_relevance = memory.get('distance', 0.5)
        
        # Apply decay curve: R = e^(-t/S)
        timestamp = datetime.fromisoformat(memory['metadata']['timestamp'])
        hours_ago = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
        
        # Strength = importance * 100 (scale to hours)
        strength = importance * 100
        decay_factor = math.exp(-hours_ago / strength)
        
        # Combine factors
        final_weight = base_relevance * decay_factor * (1 + importance)
        
        return final_weight
```

**Integration Point:** `brain/prompt_builder/context_retriever.py::get_memories()`
- Apply decay weighting after vector search
- Re-sort by decayed weights
- Return top N by final weight

**Expected Impact:**
- Recent conversations weighted higher
- Important memories don't decay as fast
- More contextually relevant memory selection

### Feature 2: 1-2 days (focused, incremental)

**Day 1 Morning:** Memory decay weighting
- Implement `MemoryDecayWeighter`
- Integrate into `context_retriever.py`
- Test with token monitoring logs

**Day 1 Afternoon:** Context habituation
- Implement `ContextHabituation`
- Integrate into `section_builder.py`
- Measure token savings

**Day 2 Morning:** Cache-aware assembly
### Must Have ✅
- [ ] **Memory decay weighting** - Ebbinghaus curve applied to memories
- [ ] **Context habituation** - Repeated context reduced in weight
- [ ] **Cache-aware assembly** - Skip re-assembly of cached items
- [ ] **Token savings measured** - Expect 20-30% reduction
- [ ] **Tests pass** - Unit tests for decay + habituation
- [ ] **Docs updated** - Biomimetic features documented

### Validation Metrics 📊
- **Before:** Token usage baseline from monitoring logs
- **After Decay:** Memory relevance scores improve
- **After Habituation:** Persona injection reduced
- **After Cache-Aware:** Cache hit rate increases
- **Overall:** 20-30% token reduction expected

### Nice to Have ⭐
- [ ] Configurable decay curves (Ebbinghaus vs linear)
- [ ] Per-user habituation tracking
- [ ] Adaptive thresholds (learn optimal values)
- [ ] Visualization of decay weights in logs implementations from research doc  
**Dependencies:** Token monitoring (done), caching (done) - ready to build!  
**Enables:** Phase 2 biomimetics (attention, chunking), better foundation for ALL features
class ContextHabituation:
    """Track repeated context and reduce its priority."""
    
    def __init__(self):
        self.last_seen = {}      # context_key -> (value_hash, timestamp, count)
        self.threshold = 3       # Habituate after 3 repetitions
    
    def check_habituation(self, key: str, value: str) -> float:
        """Return weight multiplier (1.0 = full, 0.0 = skip)."""
        
        value_hash = hashlib.md5(value.encode()).hexdigest()
        
        if key not in self.last_seen:
            # First time, full weight
            self.last_seen[key] = (value_hash, datetime.now(), 1)
            return 1.0
        
        last_hash, last_time, count = self.last_seen[key]
        
        if last_hash != value_hash:
            # Changed! Reset (dishabituation)
            self.last_seen[key] = (value_hash, datetime.now(), 1)
            return 1.0
        
        # Repeated unchanged
        new_count = count + 1
        self.last_seen[key] = (value_hash, datetime.now(), new_count)
        
        if new_count >= self.threshold:
            # Habituated - skip or reduce weight
            return 0.1  # 10% weight for "background awareness"
        
        return 1.0
```

**Integration Point:** `brain/prompt_builder/section_builder.py`
- Check habituation before formatting each section
- Apply weight multiplier to priority
- Low-weight sections moved to periphery or skipped

**Expected Impact:**
- Persona not re-injected at full weight every request
- FAQ only loaded when likely relevant
- Token savings: 20-30% estimated

### Feature 3: Cache-Aware Assembly

**Goal:** Don't re-assemble sections that are cached and unchanged

**File:** `brain/prompt_builder/prompt_assembler.py` (enhancement)

**Implementation:**
```python
class PromptAssembler:
    def build_prompt(self, ...):
        # Check cache first
        cached_persona = self.cache.get('persona')
        
        if cached_persona and not self.habituation.changed('persona'):
            # Use cached, don't re-fetch or re-format
            persona_section = cached_persona
            self.token_monitor.track('persona', persona_section, cached=True)
        else:
            # Fetch fresh
            persona_data = self.retriever.get_persona()
            persona_section = self.builder.format_persona(persona_data)
            self.cache.set('persona', persona_section)
            self.token_monitor.track('persona', persona_section, cached=False)
```

**Integration Point:** Already in PromptAssembler, just enhance logic
- Track cache hits/misses in token monitor
- Log when using cached vs fresh context
- Combine with habituation for maximum efficiency

**Expected Impact:**
- Reduced RAG queries (already happening)
- Reduced token counting overhead
- Clear metrics on cache effectivenessits, file type allowlist)

### Phase 2: MCP Tool
Add `ada_read_code` tool to `ada-mcp/src/ada_mcp/tools.py`:
- Expose codebase reading to MCP clients
- Editors can request code directly
- Enables "explain this function" workflows

### Phase 3: Documentation & Testing
- Add to specialist registry
- Write Sphinx docs
- Update persona
- Write tests
- Test in multiple editors

**See below for detailed specifications.**

---

## Timeline & Effort
Files to Create/Modify

### New Files
1. `brain/memory_decay.py` - Decay weighting implementation
2. `brain/context_habituation.py` - Habituation tracker
3. `tests/test_memory_decay.py` - Decay tests
4. `tests/test_context_habituation.py` - Habituation tests

### Modified Files
1. `brain/prompt_builder/context_retriever.py` - Apply decay to memories
2. `brain/prompt_builder/section_builder.py` - Check habituation before format
3. `brain/prompt_builder/prompt_assembler.py` - Cache-aware assembly
4. `brain/config.py` - Add decay/habituation config
5. `.ai/context.md` - Update with biomimetic features
6. `docs/architecture.rst` - Document biological inspirations

---

## Related Research & Planning

- **Primary:** [`.ai/explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md`](file:///home/luna/Code/ada-v1/.ai/explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md) - Complete research foundation
- **Caching:** v2.1 MultiTimescaleCache - Already implemented, proven pattern
- **Monitoring:** v2.0 TokenBudgetMonitor - Provides measurement framework
- **Consolidation:** `scripts/consolidate_memories.py` - Sleep-like pattern already working

---

## After Phase 1: What's Next?

Once biomimetic Phase 1 is complete, we can choose:

### Option A: Phase 2 Biomimetics (Attention & Chunking)
- Attentional spotlight (detail for top-3, summaries for rest)
- Semantic chunking (group related context)
- Salience detection (prioritize surprising info)

### Option B: MCP Codebase Specialist (Pair Programming)
- Read source code files
- MCP tool for editors
- Foundation for Continue.dev integration

### Option C: Phase 3 Biomimetics (Predictive Loading)
- Context priming
- Prediction error detection
- Dynamic context injection

---

## What's Next? Three Options:

### Option 1: 🧪 Integration Test Phase 1
- Start Ada stack and validate habituation works
- Measure actual token savings
- Collect metrics on decay weighting effectiveness
- **Time:** 1-2 hours testing
- **Benefit:** Validates implementation, catches edge cases

### Option 2: 🧬 Biomimetic Phase 2
Continue biological optimization with attention mechanisms:
- **Attention-based context filtering** (like human selective attention)
- **Working memory windowing** (limited context slots)
- **Semantic chunking** (group related memories)
- **File:** `.ai/explorations/research/BIOLOGICAL_CONTEXT_MANAGEMENT.md` (already researched!)
- **Time:** 2-3 days implementation
- **Benefit:** Further token optimization, better context quality

### Option 3: 💻 MCP Codebase Specialist (Pair Programming)
Start building the full-suite local pair programmer:
- Codebase search/read specialist
- Symbol lookup and navigation
- AST analysis integration
- **File:** `.ai/explorations/planning/CODEBASE_SPECIALIST_PLAN.md`
- **Time:** 3-5 days implementation
- **Benefit:** Moves toward user's stated goal

**Recommendation:** Option 2 (Phase 2 Biomimetics)
- Phase 1 foundation is solid, keep momentum
- Attention mechanisms are natural next step
- Further optimization before adding complexity
- Can do Option 1 (testing) in parallel with development

---

**Phase 1 Complete! 🎉 Nature spent billions of years solving context overload - we've implemented the foundations!**

*Updated: 2025-12-17 - Phase 1 implementation complete, ready for Phase 2 or MCP
- [`.ai/explorations/planning/CODEBASE_SPECIALIST_PLAN.md`](/home/luna/Code/ada-v1/.ai/explorations/planning/CODEBASE_SPECIALIST_PLAN.md) - Detailed technical plan
- [`TODO.md`](/home/luna/Code/ada-v1/TODO.md) - MCP enhancements section
- [`brain/specialists/docs_specialist.py`](/home/luna/Code/ada-v1/brain/specialists/docs_specialist.py) - Similar pattern for reading files

---

## Quick Start

```bash
# Review detailed plan first
cat .ai/explorations/planning/CODEBASE_SPECIALIST_PLAN.md

# Create feature branch
git checkout -b feature/mcp-codebase-specialist

# Start with brain-side specialist
code brain/specialists/codebase_specialist.py

# Then MCP tool
code ada-mcp/src/ada_mcp/tools.py
```

---

**This is the foundation for Ada as a true pair programmer. Let's build it! 🤖💜**

*Updated: 2025-12-18 after MCP capability survey*
