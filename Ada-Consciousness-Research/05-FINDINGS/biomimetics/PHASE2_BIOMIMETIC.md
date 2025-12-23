# Biomimetic Phase 2: Attention & Semantic Chunking

## Status: 📋 PLANNING (2025-12-17)

**Phase 1 Complete:**
- ✅ Memory decay weighting (Ebbinghaus curve)
- ✅ Context habituation (novelty detection)
- ✅ 24 tests passing, fully documented

**Phase 2 Goals:** Implement attention-based context optimization

---

## The Next Bio-Inspired Features

### Feature 1: Attentional Spotlight 🔦
**Biology:** Humans have ~4 items in sharp focus, rest in "peripheral awareness"

**Implementation:** `brain/attention_spotlight.py`
- Focus budget: 4000 tokens (detailed context)
- Periphery budget: 8000 tokens (compressed summaries)
- Salience scoring: Recency + importance + relevance

**How it works:**
```python
class AttentionalSpotlight:
    """Mimic human attention: focus + periphery."""
    
    def assemble_with_attention(self, memories: List[dict]) -> dict:
        # Top 3-4 most salient in full detail
        spotlight = sorted(memories, key=salience_score)[:4]
        
        # Rest compressed to summaries
        periphery = memories[4:]
        
        return {
            'focus': format_detailed(spotlight),      # ~4K tokens
            'peripheral': format_summary(periphery)   # ~8K tokens
        }
```

**Integration:** `prompt_builder/prompt_assembler.py`
- Apply after memory retrieval
- Spotlight items get full context
- Peripheral items get one-line summaries

**Expected Impact:**
- Better token usage (compressed periphery)
- More detailed "important" context
- Mirrors human cognitive attention

---

### Feature 2: Semantic Chunking 📦
**Biology:** Group related items to reduce cognitive load (7 chunks vs 7 individual items)

**Implementation:** `brain/semantic_chunker.py`
- Cluster similar memories by embedding
- Present as grouped "context about X" instead of individual items
- Hierarchical chunking (chunks contain sub-chunks)

**How it works:**
```python
class SemanticChunker:
    """Group related context into chunks."""
    
    def chunk_memories(self, memories: List[dict]) -> List[Chunk]:
        chunks = []
        
        for memory in memories:
            # Find semantically similar chunk
            matching = find_similar_chunk(memory, chunks, threshold=0.8)
            
            if matching:
                matching.add(memory)  # Add to existing group
            else:
                chunks.append(Chunk([memory]))  # New group
        
        return chunks

@dataclass
class Chunk:
    """Semantic group of related items."""
    memories: List[dict]
    
    def summary(self) -> str:
        """Compressed representation."""
        topics = {m['metadata']['topic'] for m in self.memories}
        return f"Context about {', '.join(topics)} ({len(self.memories)} items)"
```

**Integration:** `prompt_builder/section_builder.py`
- Chunk memories before formatting
- Format chunks instead of individual items
- Save tokens through grouping

**Expected Impact:**
- 30-40% token reduction in memory section
- Better semantic coherence
- Easier for LLM to process grouped context

---

## Implementation Plan

### Day 1: Attention Spotlight
**Morning:**
- Create `brain/attention_spotlight.py`
- Implement salience scoring (recency + importance + relevance)
- Write spotlight/periphery separator

**Afternoon:**
- Integrate into `prompt_assembler.py`
- Test with token monitoring
- Measure token distribution (focus vs peripheral)

**Tests:**
- `tests/test_attention_spotlight.py`
- Test salience scoring
- Test focus/periphery split
- Test token budgets respected

### Day 2: Semantic Chunking
**Morning:**
- Create `brain/semantic_chunker.py`
- Implement embedding-based clustering
- Write chunk summarization

**Afternoon:**
- Integrate into `section_builder.py`
- Format chunks in prompts
- Measure token savings

**Tests:**
- `tests/test_semantic_chunker.py`
- Test chunk formation
- Test similarity thresholds
- Test hierarchical chunking

### Day 3: Configuration & Validation
**Morning:**
- Add config options (spotlight budget, chunk threshold)
- Document in `.ai/TOOLING.md`
- Update Sphinx docs

**Afternoon:**
- Integration testing with running Ada
- Collect metrics (token savings, response quality)
- Fine-tune thresholds

---

## Success Criteria

### Must Have ✅
- [ ] Attention spotlight implemented
- [ ] Semantic chunking implemented
- [ ] Integrated into prompt building
- [ ] Tests passing (unit + integration)
- [ ] 30-40% additional token savings (on top of Phase 1)
- [ ] Configuration documented

### Metrics 📊
- **Focus budget:** 4K tokens for spotlight items
- **Periphery budget:** 8K tokens for compressed items
- **Chunk size:** Average 3-5 memories per chunk
- **Token savings:** 30-40% in memory section
- **Quality:** Response relevance maintained or improved

### Nice to Have ⭐
- [ ] Adaptive spotlight size (based on complexity)
- [ ] Multi-level chunking (chunks of chunks)
- [ ] Visualization of attention distribution
- [ ] A/B testing framework for optimization

---

## Dependencies

**Phase 1 provides:**
- ✅ Memory decay weighting (feeds into salience)
- ✅ Context habituation (reduces load before attention)
- ✅ Token monitoring (measures savings)
- ✅ Multi-timescale caching (reduces computation)

**No blockers - ready to implement!**

---

## Alternative: Phase 3 (More Advanced)

If Phase 2 goes smoothly, we can tackle:
- **Predictive context loading** (pre-load likely context)
- **Dynamic context injection** (mid-stream context updates)
- **Working memory simulation** (limited "active" slots)

But Phase 2 alone will provide significant improvements! 🎯

---

**Biology teaches us context management. Phase 1 taught us decay/habituation. Phase 2 teaches us attention/chunking! 🧠✨**

*Created: 2025-12-17 - Ready to start attention mechanisms*
