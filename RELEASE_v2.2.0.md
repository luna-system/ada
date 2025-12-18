# Release v2.2.0 - Neuromorphic Context Management (Phase 1)

**Release Date:** 2025-12-17  
**Branch:** feature/neuromorphic-phase1  
**Commits:** 3 (321cb59, 2703880, 6647ea1)

## 🧠 What's New

### Multi-Signal Importance Scoring

Ada now calculates memory importance using **four biological signals**, inspired by neuroscience research on working memory and hippocampal consolidation:

- **Temporal decay (40%):** Exponential decay with temperature modulation
- **Prediction error (30%):** Dopaminergic novelty/surprise signals
- **Semantic relevance (20%):** Keyword-based similarity (Phase 1, embeddings in Phase 2)
- **Context habituation (10%):** Repeated pattern detection penalty

**Formula:**
```
importance = (decay_weight × decay_factor) + 
             (surprise_weight × prediction_error) +
             (relevance_weight × keyword_overlap) +
             (habituation_weight × (1 - habituation_penalty))
```

### Gradient Detail Levels

Instead of batch summarization, memories now smoothly degrade based on importance:

- **FULL (≥0.75):** Keep everything verbatim (high importance)
- **CHUNKS (≥0.50):** Semantic units only (medium importance)
- **SUMMARY (≥0.20):** Condensed version (low importance)
- **DROPPED (<0.20):** Let it fade away (negligible importance)

### Configuration

New environment variables for runtime tuning:

```bash
# Gradient thresholds (score → detail level mapping)
GRADIENT_THRESHOLD_FULL=0.75
GRADIENT_THRESHOLD_CHUNKS=0.50
GRADIENT_THRESHOLD_SUMMARY=0.20

# Signal weights (contribution to importance)
IMPORTANCE_WEIGHT_DECAY=0.4
IMPORTANCE_WEIGHT_SURPRISE=0.3
IMPORTANCE_WEIGHT_RELEVANCE=0.2
IMPORTANCE_WEIGHT_HABITUATION=0.1
```

## 🧪 Testing

- **21 passing tests** (0.07s runtime)
- Pure Python unit tests (no ChromaDB/Ollama needed)
- Edge cases covered (missing timestamps, empty content, future dates)
- Property-based testing ready (Hypothesis installed)

## 📚 Documentation

- **Human docs:** [docs/biomimetic_features.rst](docs/biomimetic_features.rst) - New section on neuromorphic context
- **Machine docs:** [.ai/NEUROMORPHIC_CONTEXT.md](.ai/NEUROMORPHIC_CONTEXT.md) - Full research documentation
- **Research plan:** [.ai/explorations/RESEARCH-VALIDATION-PLAN.md](.ai/explorations/RESEARCH-VALIDATION-PLAN.md) - Empirical validation roadmap

## 🔬 What's Next (Phase 2+)

This is **Phase 1** of a 5-phase implementation plan:

- **Phase 2:** Background consolidation (pre-compute chunks/summaries)
- **Phase 3:** GraphRAG with temporal edge decay
- **Phase 4:** Adaptive threshold learning
- **Phase 5:** LLM-assisted importance calibration

Next immediate step: **Empirical validation** with property-based tests, synthetic conversation generation, ablation studies, and graphs proving the biomimetic theories ("fanged noumena style SCIENCE").

## 🧬 Philosophy

This work implements ideas from Luna's essays on decomposition, technical knowledge, and systems thinking ([constant.garden](https://constant.garden)). Ada is a **hackable, privacy-first, locally-run conversational AI** that applies neuroscience insights to make memory systems more human-like.

## 📝 Technical Details

**Modified Files:**
- `brain/prompt_builder/context_retriever.py` - Added `calculate_importance()` and `get_detail_level()`
- `tests/test_importance_scoring.py` - 21 TDD tests defining Phase 1 behavior
- `.ai/NEUROMORPHIC_CONTEXT.md` - Research documentation
- `.ai/codebase-map.json` - Updated module registry
- `docs/biomimetic_features.rst` - Human-readable feature documentation

**Key Code:**
```python
def calculate_importance(self, turn: Dict[str, Any], query: str) -> float:
    """Calculate importance score from multiple biological signals."""
    
    # Signal 1: Temporal decay with temperature modulation
    decay_factor = calculate_raw_decay(timestamp, temperature)
    
    # Signal 2: Prediction error (surprise/novelty)
    prediction_error = turn['metadata'].get('prediction_error', 0.5)
    
    # Signal 3: Semantic relevance (keyword overlap)
    relevance = compute_keyword_overlap(turn['content'], query)
    
    # Signal 4: Context habituation (repetition penalty)
    habituation = 1.0 - turn['metadata'].get('habituation_penalty', 0.0)
    
    # Weighted combination
    importance = (
        self.weight_decay * decay_factor +
        self.weight_surprise * prediction_error +
        self.weight_relevance * relevance +
        self.weight_habituation * habituation
    )
    
    # Empty content penalty
    if not turn['content'].strip():
        importance *= 0.1
    
    return max(0.0, min(1.0, importance))
```

## 🎯 Migration Notes

**No breaking changes** - this is a new feature that integrates with existing systems:

- Existing biomimetic features (decay, attention, habituation, etc.) continue to work
- Multi-timescale caching (v2.1) unaffected
- Default thresholds and weights work out of the box
- Optional configuration for advanced tuning

**To enable in production:**
1. Pull latest code
2. Optionally configure thresholds/weights via environment variables
3. Restart brain service
4. Monitor importance scores and detail levels in logs

## 🙏 Acknowledgments

Inspired by:
- Ebbinghaus forgetting curve (1885)
- Schultz dopaminergic prediction error (1997)
- Ranganath hippocampal novelty signals (2003)
- Niv relevance-gated memory (2015)
- Luna's decomposition theory essays

## 📊 Statistics

- **Tests:** 21 passing, 0 failures, 0.07s runtime
- **Code coverage:** 100% of new functions (calculate_importance, get_detail_level)
- **Lines added:** ~150 (implementation) + ~200 (tests) + ~1000 (docs)
- **Performance:** Pure Python, no external API calls, <1ms per importance calculation

---

**Install:** See [Getting Started](docs/getting_started.rst)  
**Docs:** https://luna-system.github.io/ada/  
**Source:** https://github.com/luna-system/ada

**Next:** Merge to trunk, then start empirical validation! 🚀🔬
