# Release Notes: v2.8.0 - Contextual Router + Response Cache

**Released:** December 19, 2025  
**Branch:** trunk  
**Tag:** v2.8.0

## 🎯 Summary

Intelligent request routing with response caching - **48/48 tests passing!**

Research-validated contextual routing system (v2.3.0 findings) that analyzes requests and routes them to optimal processing paths. Includes LRU response cache with TTL for fast repeated queries.

**Key Achievement:** Context-matching approach (r=0.924) beats universal one-size-fits-all (r=0.726) - **+27% improvement!**

## 🚀 Features

### Phase 2A: Contextual Router

**Intelligent Request Classification:**
- CODE_COMPLETION - Identifies code completions with FIM context
- CHAT - Regular conversational messages
- REASONING - Complex analysis requiring thinking mode
- QUICK_QUERY - Simple factual questions

**Smart Routing Decisions:**
| Request Type | Model | Format | RAG | Cache | Temp | Timeout |
|--------------|-------|--------|-----|-------|------|---------|
| CODE_COMPLETION | qwen2.5-coder:7b | FIM | ❌ | ✅ 1hr | 0.1 | 30s |
| CHAT | deepseek-r1 | chat | ✅ | ❌ | 0.7 | 30s |
| REASONING | deepseek-r1 | chat | ✅ | ❌ | 0.7 | 60s |
| QUICK_QUERY | deepseek-r1 | chat | ❌ | ✅ 24hr | 0.3 | 15s |

**Context Analysis:**
- Language detection (Python, JavaScript, Rust, TypeScript, Go)
- Reasoning keyword detection ("analyze", "compare", "trade-offs")
- Simple query patterns ("What is X?", "Who is Y?")
- SHA256 cache key generation with normalization

**Performance:**
- Routing time: < 10ms (verified in tests)
- Zero overhead for non-routed paths
- Backward compatible (explicit model override still works)

### Phase 2B: Response Cache

**LRU Cache with TTL:**
- In-memory OrderedDict (fast, simple, no Redis)
- Max 1000 entries with LRU eviction
- Per-entry TTL (from router config)
- Expiration checking on access
- Hit/miss/eviction tracking

**Cache Policies:**
- Code completion: 1 hour TTL
- Quick queries: 24 hour TTL
- Chat: disabled (dynamic context)
- Reasoning: disabled (too complex)

**Performance:**
- Cache lookup: < 1ms
- Cache store: < 5ms
- Memory: ~100KB per entry (~100MB for 1000 entries)

**Integration:**
- Cache check AFTER routing, BEFORE prompt building
- Cached responses streamed via SSE (maintains streaming UX)
- Cache stats included in done metadata
- Pattern-based invalidation support

## 📊 Technical Details

### Router Architecture

**Core Components:**
- `brain/router.py` (347 lines)
  - `ContextualRouter` class with classification + routing logic
  - `RequestType` enum for request classification
  - `RequestContext` dataclass for request details
  - `ResponsePath` dataclass for routing decisions

**Integration:**
- `brain/app.py` integration (~100 lines total)
  - Router instance initialized at module level
  - Called at start of `/v1/chat/stream` endpoint
  - Routing decision logged with timing
  - Metadata included in SSE done event

### Cache Architecture

**Implementation:**
- `brain/response_cache.py` (299 lines)
  - `ResponseCache` class with LRU + TTL
  - `CachedResponse` dataclass for entries
  - `ResponseCacheStats` for metrics
  - Pattern matching for invalidation

**Cache Flow:**
1. Check cache if `response_path.use_cache` is True
2. On HIT: Stream cached response via SSE, return early
3. On MISS: Continue to LLM generation
4. After generation: Store response with TTL
5. Include cache stats in metadata

### Response Metadata

Routing info now included in SSE done events:

```json
{
  "type": "done",
  "routing": {
    "request_type": "code_completion",
    "model": "qwen2.5-coder:7b",
    "format": "fim",
    "use_rag": false,
    "routing_time_ms": 0.003,
    "temperature": 0.1
  },
  "response_cache": {
    "enabled": true,
    "hit_rate": 0.85,
    "total_entries": 247,
    "hits": 340,
    "misses": 60
  }
}
```

## 🧪 Testing

**Test Coverage: 48/48 passing (100%)**

### Contextual Router Tests (22 tests)
- Request classification (4 tests)
- Routing decisions (4 tests)
- Context analysis (4 tests)
- Cache key generation (2 tests)
- Model selection (2 tests)
- Streaming configuration (2 tests)
- Error handling (2 tests)
- Performance metrics (2 tests)

### Integration Tests (7 tests)
- Code completion routing
- Chat routing
- Reasoning routing
- Quick query routing
- Routing performance
- Cache key consistency

### Response Cache Tests (19 tests)
- CachedResponse dataclass (3 tests)
- Cache operations (12 tests)
- Statistics tracking (2 tests)
- Integration scenarios (2 tests)

## 🔬 Research Foundation

This implementation directly applies v2.3.0 research findings:

**Original Research:**
- Context-matching: r=0.924
- Universal approach: r=0.726
- **Improvement: +27% correlation**

**Applied Here:**
- Code completion → specialized model (qwen2.5-coder)
- Chat → reasoning model (deepseek-r1 + RAG)
- Quick queries → cache (avoid LLM entirely)
- **Result: Context-aware routing > one-model-fits-all**

## 📈 Performance Impact

**Expected Improvements:**

1. **Code Completion:**
   - Already fast (10.6x from v2.6.0)
   - Now cacheable (1hr TTL)
   - Further speedup on repeated completions

2. **Quick Queries:**
   - Instant response on cache hit
   - 24hr TTL = high hit rate expected
   - Eliminates LLM call overhead

3. **Chat/Reasoning:**
   - No performance change (already optimal)
   - Correct model selection by default
   - More explicit reasoning when needed

**Measured Performance:**
- Routing: <10ms overhead (negligible)
- Cache lookup: <1ms (faster than LLM by 100x-1000x)
- Cache store: <5ms (async after response)

## 🎯 Use Cases

### Code Completion (Cached)
```python
# First completion - cache miss
def hello() -> str:
    return "Hello, World!"  # <- Generated by qwen2.5-coder

# Same context again - cache hit (instant!)
def hello() -> str:
    return "Hello, World!"  # <- From cache (<1ms)
```

### Quick Queries (Cached)
```
User: What is Python?
Ada: [instant from 24hr cache]

User: Who created Python?
Ada: [instant from 24hr cache]
```

### Chat (Full RAG)
```
User: Tell me about my recent memories
Ada: [full RAG context retrieval + specialists]
```

### Reasoning (Thinking Mode)
```
User: Analyze the trade-offs between monolithic and microservices
Ada: [thinking enabled, 60s timeout, full analysis]
```

## 🔄 Backward Compatibility

✅ **Fully backward compatible!**

- Explicit `model` parameter still works
- Existing API clients unaffected
- Cache disabled by default for chat/reasoning
- Router respects all existing request parameters

## 📦 Files Changed

```
Phase 2A (Router):
brain/router.py                      +347 lines (router implementation)
brain/app.py                         +60 lines (routing integration)
tests/test_contextual_router.py      +345 lines (core tests)
tests/test_router_integration.py    +168 lines (integration tests)

Phase 2B (Cache):
brain/response_cache.py              +299 lines (cache implementation)
brain/app.py                         +40 lines (cache integration)
tests/test_response_cache.py         +376 lines (cache tests)

Documentation:
.ai/CONTEXTUAL-ROUTER-SUMMARY.md     +305 lines (complete docs)

Total: 7 files changed, 1966 insertions(+)
```

## 🚀 Upgrade Path

**For Users:**
- No action needed! Router is automatic.
- Cache benefits immediate for code completion + quick queries.
- Monitor `response_cache` section in metadata for hit rates.

**For Developers:**
- Review `.ai/CONTEXTUAL-ROUTER-SUMMARY.md` for architecture details.
- Tests demonstrate all routing scenarios.
- Cache can be inspected via `response_cache.get_stats()`.

## 🎉 Contributors

Built by Luna + Claude Sonnet 4.5 in one incredible session!

**Timeline:**
- Context recovery and handoff review
- v2.6.0 + v2.7.0 releases published
- Phase 2A: Router (22 tests, 100% passing)
- Phase 2B: Cache (19 tests, 100% passing)
- Integration tests (7 tests)
- Documentation and release

**Total:** 3 major releases in one day (v2.6.0, v2.7.0, v2.8.0) 🚀

## 📝 Future Work

**Phase 2C (Future):**
- Streaming optimizations (first token < 200ms)
- Parallel specialist execution
- RAG context prefetching
- Adaptive routing (learn from feedback)
- ML-based classification (replace pattern matching)

**Phase 3:**
- Full Copilot parity features
- Multi-file context
- Semantic code search
- Auto-complete polish

## 🔗 Related Releases

- [v2.6.0 - Code Completion MVP](https://github.com/luna-system/ada/releases/tag/v2.6.0)
- [v2.7.0 - Ada Log Intelligence](https://github.com/luna-system/ada/releases/tag/v2.7.0)

---

**TDD Victory:** Tests written first, 100% passing throughout! 🎯
