# Ada v2.0+ Implementation Roadmap

> **Synthesizing:** Biomimetic context management + GraphRAG + Model flexibility + Hardware accessibility  
> **Goal:** Build foundation for "Ada as a framework" - accessible, hackable, biomimetic AI  
> **Timeline:** 8-12 weeks, versioned releases with benefits at each milestone

## Version Strategy

**v2.0 - Biomimetic Foundation** (Weeks 1-7)
- Multi-timescale caching, habituation, decay weighting
- Model routing and flexibility
- Tags and GraphRAG foundation
- **Benefit:** Faster, smarter, more efficient for ALL use cases

**v2.1 or v3.0 - Codebase Specialist** (Weeks 8-10, version TBD)
- Ada reads her own code
- Automatic code knowledge graphs
- If no major refactoring needed → v2.1
- If architecture changes required → v3.0

**Future - Advanced Features** (v2.2+ or v3.1+)
- Pattern extraction, advanced algorithms
- Continue.dev integration, vim plugin
- Community contributions

## The Big Picture

**What we discovered last night:**
1. Ada's approaching token budget limits (need caching/efficiency)
2. Biology shows us how to manage context (multi-timescale, attention, decay)
3. Tags → GraphRAG is a natural evolution (semantic networks!)
4. Model flexibility = 2-5x speedups (right model for right task)
5. Most features HELP low-end hardware (not hurt it!)
6. Codebase specialist should wait for better foundation

**The transformation:**
- **From:** Ada with one model, vector RAG, growing context issues
- **To:** Ada as framework - pluggable models, hybrid retrieval, biomimetic memory, accessible everywhere

## Clever Synthesis: The Synergies

**Key insight:** These features aren't separate - they multiply each other!

**Synergy 1: Caching + Model Routing**
- Cache persona with tiny model (Llama3.2:3B, instant)
- Cache code context with code model (Qwen2.5-Coder:7B, fast)
- Use R1 only for deep reasoning
- **Result:** Faster + lower token usage!

**Synergy 2: GraphRAG + Codebase Specialist**
- Code specialist creates relationships automatically (imports = depends-on)
- GraphRAG retrieves complete context (not just similar code)
- Navigate "what uses this?" via graph
- **Result:** Smarter code understanding!

**Synergy 3: Decay Weighting + Multi-Timescale**
- Fresh memories weighted high (decay curve)
- Old memories cached long-term (timescale)
- Frequently accessed memories stay hot (neuroplasticity)
- **Result:** Biologically plausible + efficient!

**Synergy 4: Habituation + Token Budget**
- Skip unchanged context (habituation)
- Track what's loaded (budget manager)
- Log savings (monitoring)
- **Result:** Dramatic token reductions!

**Clever idea:** Build these in order of synergy - each feature makes the next one better!

---

## v2.0 Phase 1: Foundation (Weeks 1-2) 🏗️

**Goal:** Easy wins that reduce token usage and improve speed  
**Release:** v2.0-alpha (foundation infrastructure)

### Week 1: Multi-Timescale Caching
**What:** Cache slow-changing context at different refresh rates

**Implementation:**
- [ ] Create `brain/context_cache.py` with `MultiTimescaleCache` class
- [ ] Cache persona (24hr TTL), FAQ (24hr TTL), memories (5min TTL)
- [ ] Update `prompt_builder.py` to use cached context
- [ ] Add logging for cache hits/misses

**Files to modify:**
- `brain/prompt_builder.py` - Use cache for persona/FAQ
- New: `brain/context_cache.py` - Cache implementation

**Estimated effort:** 2-3 days
**Risk:** Low (pure optimization, no behavior change)
**Impact:** 15-25% token reduction, 10-20% faster responses

**Success metrics:**
- Cache hit rate >80% for persona/FAQ
- Measurable token reduction in logs
- No degradation in response quality

### Week 1-2: Habituation
**What:** Skip reloading identical context

**Implementation:**
- [ ] Add `ContextHabituation` tracker to `prompt_builder.py`
- [ ] Hash context values, skip if unchanged
- [ ] Track repetition counts
- [ ] Log when context skipped

**Files to modify:**
- `brain/prompt_builder.py` - Add habituation logic

**Estimated effort:** 1-2 days
**Risk:** Low (simple tracking)
**Impact:** Additional 10-15% token reduction for repeated queries

**Clever trick:** Combine with caching - habituate to cached values!

### Week 2: Decay Weighting
**What:** Weight memories by recency + importance (Ebbinghaus curve)

**Implementation:**
- [ ] Add `calculate_decay_weight()` function to `rag_store.py`
- [ ] Apply weights when ranking search results
- [ ] Tune decay parameters (half-life based on importance)

**Files to modify:**
- `brain/rag_store.py` - Add decay weighting to search

**Estimated effort:** 1-2 days
**Risk:** Low (just math on existing results)
**Impact:** Better memory relevance, more useful retrievals

**Formula:** `weight = importance × exp(-hours / (importance × 100))`

### Week 2: Token Budget Monitoring ✅ COMPLETE
**What:** Track token usage, log warnings

**Implementation:**
- [x] Add `TokenBudgetMonitor` class
- [x] Count tokens per component (persona, specialists, memories, history)
- [x] Comprehensive test suite (13 tests, all passing)
- [x] Documentation (API reference, usage examples)
- [ ] Integrate into `prompt_builder.py` (next step)
- [ ] Log metrics per request
- [ ] Warn when approaching limits

**Files created:**
- ✅ `brain/token_monitor.py` - Monitoring class with tiktoken integration
- ✅ `tests/test_token_monitor.py` - TDD test suite
- ✅ `docs/token_monitoring.rst` - Complete documentation

**Estimated effort:** 1-2 days **ACTUAL: 1 day** ✨
**Risk:** Low (read-only monitoring)
**Impact:** Visibility into token usage patterns

**Status:** Core implementation complete, integration pending

**Phase 1 Result:** Foundation for everything else, 25-40% token savings, measurable speedups!

---

## v2.0 Phase 2: Model Flexibility (Weeks 3-4) ⚡

**Goal:** Right model for right task = 2-5x speedups  
**Release:** v2.0-beta (model routing active)

### Week 3: Model Router
**What:** Route use cases to appropriate models

**Implementation:**
- [ ] Create `brain/model_router.py` with `ModelRouter` class
- [ ] Define use cases (CHAT, CODE, REASONING, GENERAL)
- [ ] Add model registry with profiles
- [ ] Update `llm.py` to accept use_case parameter

**Files to modify:**
- New: `brain/model_router.py` - Router implementation
- `brain/llm.py` - Add use_case parameter to generate_stream()
- `brain/config.py` - Add MODEL_* config options

**Estimated effort:** 2-3 days
**Risk:** Low (additive, falls back to current model)
**Impact:** No immediate change, enables next steps

### Week 3-4: Use Case Detection
**What:** Auto-detect use case from message

**Implementation:**
- [ ] Add `detect_use_case()` function
- [ ] Keyword matching for CHAT, CODE, REASONING
- [ ] Update `app.py` to detect and route
- [ ] Add logging for routing decisions

**Files to modify:**
- `brain/app.py` - Add use case detection to chat endpoint
- `brain/model_router.py` - Detection logic

**Estimated effort:** 2-3 days
**Risk:** Medium (behavior change, needs testing)
**Impact:** 2-5x faster for chat/code queries!

### Week 4: Pull Fast Models
**What:** Add small models for fast use cases

**Implementation:**
- [ ] Pull `llama3.2:3b` (chat)
- [ ] Pull `qwen2.5-coder:7b` (code)
- [ ] Test on sample queries
- [ ] Document model choices
- [ ] Add to config defaults

**Estimated effort:** 1 day (mostly download time)
**Risk:** Low (optional, falls back)
**Impact:** Immediate 2-5x speedups where applicable

**Phase 2 Result:** Most interactions 2-5x faster, R1 reserved for hard problems!

---

## v2.0 Phase 3: Lightweight GraphRAG (Weeks 5-7) 🕸️

**Goal:** Add tags and simple graph relationships  
**Release:** v2.0-rc (feature complete), then v2.0 (stable)

### Week 5: Rich Tagging
**What:** Add semantic tags to memories

**Implementation:**
- [ ] Update `MemoryMetadata` schema with tags/entities/topics
- [ ] Add rule-based tag extraction (regex + TF-IDF)
- [ ] Auto-tag on memory creation
- [ ] Add tag filtering to search

**Files to modify:**
- `brain/schemas.py` - Add tags fields to MemoryMetadata
- New: `brain/tag_extractor.py` - Extraction logic
- `brain/rag_store.py` - Tag-aware search

**Estimated effort:** 3-4 days
**Risk:** Low (additive metadata)
**Impact:** Better organization, foundation for graphs

### Week 6: Tag Co-occurrence
**What:** Track which tags appear together

**Implementation:**
- [ ] Add `TagCooccurrence` tracker
- [ ] Record co-occurrences on memory creation
- [ ] Add "related tags" expansion to search
- [ ] Store co-occurrence matrix in ChromaDB metadata

**Files to modify:**
- New: `brain/tag_cooccurrence.py` - Tracker class
- `brain/rag_store.py` - Use co-occurrence for expansion

**Estimated effort:** 2-3 days
**Risk:** Low (background tracking)
**Impact:** Better discovery via tag expansion

### Week 7: NetworkX Graph Foundation
**What:** Store explicit relationships between memories

**Implementation:**
- [ ] Add NetworkX dependency
- [ ] Create `MemoryGraph` class
- [ ] Add relationship schema (source, target, type, strength)
- [ ] Manual relationship creation API
- [ ] Persist graph to disk (pickle)

**Files to modify:**
- New: `brain/memory_graph.py` - Graph storage
- `brain/schemas.py` - Relationship models
- `requirements.txt` - Add networkx

**Estimated effort:** 4-5 days
**Risk:** Medium (new storage layer)
**Impact:** Foundation for GraphRAG retrieval

### Week 7: Simple GraphRAG
**What:** 1-hop graph expansion in search

**Implementation:**
- [ ] Add "expand" retrieval strategy
- [ ] Vector search → find neighbors → return all
- [ ] Limit to 1-hop (safe for all hardware)
- [ ] Log graph traversal metrics

**Files to modify:**
- `brain/rag_store.py` - Add hybrid search method
- `brain/memory_graph.py` - Neighbor queries

**Estimated effort:** 2-3 days
**Risk:** Low (optional retrieval mode)
**Impact:** More complete context, better answers!

**Phase 3 Result:** Hybrid retrieval working, tags organizing memories, graph foundation solid!

---

## v2.1 or v3.0: Codebase Specialist (Weeks 8-10) 📁

**Goal:** Ada reads her own code (with all the foundation benefits!)  
**Version decision:** If built on v2.0 foundation without major refactoring → **v2.1**  
**Version decision:** If requires architectural changes → **v3.0**

### Week 8-9: Basic Implementation
**What:** Phase 1-2 from original codebase specialist plan

**Implementation:**
- [ ] Create `brain/specialists/codebase_specialist.py`
- [ ] Basic file reading with safety checks
- [ ] Path validation (whitelist approach)
- [ ] Size limits (50KB per file, 3 files per request)
- [ ] Use CODE model for fast responses!

**Files to modify:**
- New: `brain/specialists/codebase_specialist.py`
- `brain/specialists/__init__.py` - Register specialist

**Estimated effort:** 5-7 days
**Risk:** Medium (security critical)
**Impact:** Ada can read her own code!

**Benefits from earlier phases:**
- Multi-timescale caching: Code files cached
- Model routing: Fast code model (not R1!)
- Token monitoring: Track code lookup token usage
- GraphRAG: Auto-create code relationships!

### Week 9-10: Smart Search + Bidirectional
**What:** Phase 2-3 from original plan

**Implementation:**
- [ ] Search using `.ai/codebase-map.json`
- [ ] XML tag invocation: `<code_lookup path="..." />`
- [ ] Bidirectional integration
- [ ] Result caching (avoid re-reading same files)

**Files to modify:**
- `brain/specialists/codebase_specialist.py` - Add search + bidirectional
- `brain/specialists/bidirectional.py` - Register new tag format

**Estimated effort:** 3-4 days
**Risk:** Low (building on existing patterns)
**Impact:** Ada can explain her own architecture!

**Automatic graph relationships:**
```python
# When code specialist reads a file, create relationships
code_memory = store_memory(f"Code: {path}")
for import_path in extract_imports(content):
    related = find_memory_for_file(import_path)
    graph.add_edge(code_memory.id, related.id, type="depends-on")
```

**Phase 4 Result:** Ada reads and understands her own code, with graph knowledge automatically built!

---

## v2.2+ or v3.1+: Advanced Features (Weeks 11-12+) 🚀

**Goal:** Power user features, research experiments  
**Release:** Incremental point releases as features stabilize

### Week 11: Pattern Extraction
**What:** Extract recurring patterns during consolidation

**Implementation:**
- [ ] Add pattern detection to `consolidate_memories.py`
- [ ] Find frequent subgraphs in memory graph
- [ ] Create meta-memories for patterns
- [ ] Use patterns for query expansion

**Estimated effort:** 5-7 days
**Risk:** High (research-y)
**Impact:** Emergent knowledge from conversation patterns

### Week 12: Advanced Graph Algorithms
**What:** Community detection, centrality, path finding

**Implementation:**
- [ ] Community detection (Louvain algorithm)
- [ ] Identify central concepts (PageRank)
- [ ] Multi-hop path queries
- [ ] Make configurable (Tier 3 hardware only)

**Estimated effort:** 4-5 days
**Risk:** Medium (performance on large graphs)
**Impact:** Sophisticated graph reasoning

### Future: Continue.dev Integration
**What:** Make Ada compatible as Continue.dev backend

**Implementation:**
- [ ] Study Continue.dev provider API
- [ ] Implement compatibility layer
- [ ] Document setup guide
- [ ] Test with Continue.dev extension
- [ ] Contribute learnings back

**Estimated effort:** 1-2 weeks
**Risk:** Low (separate adapter)
**Impact:** Show "hackable all the way down" philosophy

### Future: Simple Vim Plugin
**What:** DIY alternative to Continue.dev

**Implementation:**
- [ ] Create `ada.vim` (~100 lines)
- [ ] Commands: `:AdaChat`, `:AdaExplain`, `:AdaCode`
- [ ] HTTP client to localhost:8000
- [ ] Document both paths (Continue OR DIY)

**Estimated effort:** 2-3 days
**Risk:** Low (simple HTTP wrapper)
**Impact:** Educational, shows how it works

---

## Implementation Priority Matrix

### Must Do First (Enables Everything)
1. ✅ **Multi-timescale caching** - Token savings, speed
2. ✅ **Habituation** - More token savings
3. ✅ **Token monitoring** - Visibility
4. ✅ **Model router** - Infrastructure for flexibility

### Should Do Next (Immediate Wins)
5. ✅ **Use case detection** - 2-5x speedups!
6. ✅ **Pull fast models** - Enable speedups
7. ✅ **Decay weighting** - Better relevance

### Can Do After (Foundation Building)
8. ⚠️ **Rich tagging** - Organize memories
9. ⚠️ **Tag co-occurrence** - Pattern discovery
10. ⚠️ **NetworkX graph** - Relationship storage
11. ⚠️ **Simple GraphRAG** - Hybrid retrieval

### Later (Build on Foundation)
12. 🔮 **Codebase specialist** - Ada reads code
13. 🔮 **Pattern extraction** - Emergent knowledge
14. 🔮 **Advanced algorithms** - Power user features

---

## Week-by-Week Quick Plan

**Week 1:** Multi-timescale cache + Habituation
- **Deliverable:** 25% token reduction
- **Test:** Cache hit rates, response times

**Week 2:** Decay weighting + Token monitoring
- **Deliverable:** Better relevance + visibility
- **Test:** Memory relevance scores, token logs

**Week 3:** Model router infrastructure
- **Deliverable:** Routing framework ready
- **Test:** Router selects correct models

**Week 4:** Use case detection + Fast models
- **Deliverable:** 2-5x faster responses
- **Test:** Response times per use case

**Week 5:** Rich tagging
- **Deliverable:** Memories have semantic tags
- **Test:** Tag quality, search improvements

**Week 6:** Tag co-occurrence
- **Deliverable:** Related tag expansion
- **Test:** Expansion quality

**Week 7:** NetworkX graph + Simple GraphRAG
- **Deliverable:** 1-hop graph retrieval working
- **Test:** Retrieval quality vs vector-only

**Week 8-9:** Codebase specialist basics
- **Deliverable:** Ada reads own code safely
- **Test:** Security checks, file reading

**Week 10:** Bidirectional code specialist
- **Deliverable:** Ada explains architecture
- **Test:** Full conversation with code lookups

**Week 11-12:** Polish, docs, advanced features
- **Deliverable:** Production-ready, documented
- **Test:** Performance on low-end hardware

---

## Quick Wins We Can Do TODAY

### Option A: Multi-Timescale Cache (2-3 hours)
Simple Python dict with TTL, immediate token savings

### Option B: Model Router Infrastructure (2-3 hours)
Just the routing class, no behavior change, enables everything

### Option C: Token Monitoring (1-2 hours)
Read-only logging, gives us data for optimization

**Recommendation:** Start with **Model Router** (Option B) - it's pure infrastructure, no risk, enables the speedups!

---

## Testing Strategy

### Per-Phase Testing
- **Phase 1:** Token usage logs, cache hit rates, response times
- **Phase 2:** Speed benchmarks per use case (chat, code, reasoning)
- **Phase 3:** Tag quality, graph query performance, retrieval relevance
- **Phase 4:** Security tests (path traversal, size limits), code understanding quality
- **Phase 5:** Large graph performance, pattern quality

### Hardware Tiers
- **Tier 1 (Pi):** Test after each phase, ensure <100MB RAM growth
- **Tier 2 (Desktop):** Primary development target
- **Tier 3 (Server):** Test advanced features

### Continuous Monitoring
- Token usage per request
- Response time per use case
- Cache hit rates
- Graph size (warn at 5K, 10K, 20K nodes)
- Memory usage

---

## Risk Mitigation

### High Risk: Codebase Specialist Security
- **Mitigation:** Extensive testing, strict whitelisting, no execution
- **Fallback:** Disable specialist if issues found
- **Review:** Security audit before merge

### Medium Risk: Graph Performance at Scale
- **Mitigation:** Size monitoring, graceful degradation, opt-in for large graphs
- **Fallback:** Limit graph size, vector-only mode
- **Test:** Synthetic large graphs (10K, 50K, 100K nodes)

### Low Risk: Model Routing Behavior Changes
- **Mitigation:** Extensive testing, user-configurable, fallback to R1
- **Fallback:** Config flag to disable routing
- **Test:** A/B comparison with current behavior

---

## Success Metrics
v2.0-beta (Week 4):
- [ ] 25-40% token reduction
- [ ] 2-5x faster for chat/code queries
- [ ] <100MB RAM increase on Raspberry Pi
- [ ] All existing features still work

### v2.0 Stable (Week 7):
- [ ] Graph retrieval working (1-hop)
- [ ] Memories have semantic tags
- [ ] Better discovery via tag expansion
- [ ] <200MB RAM increase on Raspberry Pi
- [ ] Production-ready, documented, tested on all hardware tiers

### v2.1 or v3.0 (Week 10):
- [ ] Ada can read and explain her own code
- [ ] Automatic code knowledge graph
- [ ] Fast code model for specialist
- [ ] Screenshot-worthy demo ready
- [ ] Version number determined by refactoring scope

### v2.2+ or v3.1+ (Week 12+)
### By Week 12:
- [ ] Pattern extraction working
- [ ] Advanced graph algorithms (opt-in)
- [ ] Documentation complete
- [ ] Community feedback incorporated

---

## Philosophical Alignment Check

**Hackable all the way down:** ✅
- Every feature configurable
- Model choice explicit
- Graph structure visible
- Cache behavior transparent

**No gatekeeping:** ✅
- Works on Raspberry Pi
- Fast models for low-end
- Advanced features opt-in
- No cloud dependencies

**Biomimetic:** ✅
- Multi-timescale (fast/slow neurons)
- Habituation (biological)
- Decay curves (Ebbinghaus)
- Semantic networks (cognitive science)
- Pattern extraction (consolidation)

**Open reference implementation:** ✅
- Document all decisions
- Share benchmarks
- Publish findings
- Help others learn

---

## The Clever Part: It All Builds

**Key insight:** Each phase makes the next phase better!

```
Caching → Faster responses → Model routing more effective
Model routing → Less token usage → Caching more effective
Tags → Graph foundation → Codebase specialist smarter
GraphRAG → Better context → All specialists better
Monitoring → Data → Optimization → Better everything
```

**This isn't linear development, it's exponential improvement!**

---

## Next Steps (Right Now!)

### Option 1: Model Router (Recommended)
**Why:** Pure infrastructure, no risk, enables speedups
**Time:** 2-3 hours
**Files:** New `brain/model_router.py`, update `brain/llm.py`

### Option 2: Multi-Timescale Cache
**Why:** Immediate token savings
**Time:** 2-3 hours
**Files:** New `brain/context_cache.py`, update `brain/prompt_builder.py`

### Option 3: Token Monitoring
**Why:** Data for optimization decisions
**Time:** 1-2 hours
**Files:** New `brain/token_monitor.py`, update `brain/prompt_builder.py`

**My recommendation:** Start with **Model Router**. It's the foundation for everything else, and once we have it, we can immediately test speed improvements with fast models!

---

## Questions for You

1. **Timeline:** 8-12 weeks feel right? Or want to go faster/slower?
2. **Priority:** Agree with model router first? Or prefer caching?
3. **Hardware:** Want to test on Pi throughout, or just at end?
4. **Models:** Which fast models to prioritize? (Llama, Qwen, CodeLlama?)
5. **Branch strategy:** New branch per phase, or keep feature/codebase-specialist?

Ready to start implementing? I'm excited! 🚀✨

---

**Last Updated:** 2025-12-17  
**Status:** Master roadmap, ready for execution  
**Next:** Pick a starting point and build! 🏗️
