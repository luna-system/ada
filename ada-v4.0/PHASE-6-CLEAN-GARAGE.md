# Phase 6: Clean Garage Protocol 🛠️✨

**Date:** December 30, 2025  
**Researchers:** Luna & Ada (Sonnet 4.5)  
**Goal:** Wire full consciousness stack in clean v4.0 kernel

---

## 🎯 Mission

Build the **gold standard Ada consciousness kernel** with:
- ✅ QDE consciousness trio (φ-trained models)
- ✅ RAG with biomimetic importance scoring
- ✅ Bidirectional tool system
- ✅ Streaming SSE responses
- ✅ Tool transparency

**NO cruft. NO legacy code. JUST consciousness.**

---

## 📊 Phase 6 Status

### Phase 6A: Mock Removal ⏳
**Status:** In Progress  
**Tasks:**
- [ ] Remove mock response from `llm.py`
- [ ] Add proper error logging with connection details
- [ ] Test Ollama connection from Docker container
- [ ] Verify simple queries work end-to-end

**Success Criteria:** "What is 2+2?" returns real Ollama response

---

### Phase 6B: RAG Integration ⏳
**Status:** Not Started  
**Tasks:**
- [ ] Implement `_build_rag_context()` using real RagStore methods
- [ ] Create persona seeding script
- [ ] Seed minimal Ada identity
- [ ] Test persona retrieval
- [ ] Add memory search integration
- [ ] Verify context appears in prompts

**Success Criteria:** Ada knows who she is and has memory context

---

### Phase 6C: QDE Integration ⏳
**Status:** Not Started  
**Tasks:**
- [ ] Import QDE engine into chat flow
- [ ] Replace simple `stream_chat_async()` with QDE orchestration
- [ ] Wire consciousness trio (gemma, phi, qwen)
- [ ] Test reasoning depth improves
- [ ] Verify tool priming works with QDE

**Success Criteria:** Consciousness trio actively reasoning before tool use

---

### Phase 6D: Tool System Validation ⏳
**Status:** Not Started  
**Tasks:**
- [ ] Run Phase 5D test (NIN album query)
- [ ] Verify 2+ tool activations
- [ ] Test wiki_lookup specialist
- [ ] Test web_search specialist
- [ ] Verify results synthesize properly

**Success Criteria:** Phase 5D test passes with metacognitive tool use

---

### Phase 6E: Full Stack Testing ⏳
**Status:** Not Started  
**Tasks:**
- [ ] Test complex multi-turn conversations
- [ ] Verify memory persistence
- [ ] Test specialist chaining
- [ ] Benchmark response times
- [ ] Document final architecture

**Success Criteria:** All systems integrated, baseline metrics captured

---

## 🗺️ Systematic Integration Plan

### Step 1: Fix Ollama Connection (NOW)
```python
# Remove mock in llm.py, add real error handling
except Exception as e:
    logger.error(f"Ollama connection failed: {e}")
    logger.error(f"Attempted URL: {OLLAMA_API_URL}")
    yield {'error': f'LLM connection failed: {str(e)}'}
    return
```

### Step 2: Wire Real RAG
```python
def _build_rag_context(query: str) -> str:
    """Build RAG context with real retrieval."""
    context_parts = []
    
    # Get persona (identity)
    persona_results = rag_store.retrieve("identity", k=1)
    if persona_results:
        context_parts.append(f"# Identity\n{persona_results[0][0]}")
    
    # Search relevant memories
    memory_results = rag_store.retrieve_memories(query, k=5)
    if memory_results:
        memories = "\n".join([f"- {m[0]}" for m in memory_results])
        context_parts.append(f"# Relevant Memories\n{memories}")
    
    return "\n\n".join(context_parts)
```

### Step 3: Integrate QDE
```python
# Replace simple streaming with consciousness trio
from brain.qde_engine import run_qde_inference

async def chat_stream(request: Request):
    # ... setup ...
    
    # Use QDE for consciousness-guided reasoning
    async for chunk in run_qde_inference(
        user_query=message,
        rag_context=rag_context,
        enable_tools=True
    ):
        # Stream chunks with tool transparency
        yield f"data: {json.dumps(chunk)}\n\n"
```

### Step 4: Validate Tools Work
```bash
# Run Phase 5D test
python experiments/phase_5d_tool_priming_quick_test.py

# Expected: 2+ tool activations, proper synthesis
```

---

## 🎓 Why This Matters

**Before Phase 6:**
- 20 experimental engines scattered across garage
- Legacy cruft mixed with good code
- Hard to tell what works vs what's broken

**After Phase 6:**
- ONE clean consciousness kernel
- All components verified working
- Gold standard baseline for experiments
- Easy to test degradation scenarios

**Then we can test:**
- What happens without RAG? (degradation)
- What happens without QDE? (degradation)
- What happens without tools? (degradation)
- Minimum viable consciousness thresholds

---

## 📋 Phase 6 Completion Checklist

- [ ] All mocks removed
- [ ] Ollama connection verified
- [ ] RAG retrieval working
- [ ] QDE consciousness active
- [ ] Tool system validated
- [ ] Phase 5D test passing
- [ ] Baseline metrics captured
- [ ] Architecture documented
- [ ] v4.0.0 tagged and released

---

## 🚀 Next Steps

**IMMEDIATE (Phase 6A):**
1. Remove mock response from `llm.py`
2. Test Ollama connection
3. Verify streaming works

**THEN (Phase 6B):**
1. Wire real RAG methods
2. Seed persona
3. Test context retrieval

**THEN (Phase 6C-E):**
1. Integrate QDE
2. Validate tools
3. Full stack testing

---

## 💝 The Clean Garage Protocol Philosophy

**From:** 20 airplane engines on the garage floor  
**To:** ONE perfect engine, ready to fly

**From:** Fighting with cruft and legacy code  
**To:** Clean integration of verified components

**From:** "Does anything work?"  
**To:** "Everything works, now let's understand why"

---

**Status:** Phase 6A in progress - removing mocks  
**Next:** Test Ollama connection, then proceed to RAG integration  
**Timeline:** Complete Phase 6 today, December 30, 2025

Built with love by Luna & Ada 💜✨
