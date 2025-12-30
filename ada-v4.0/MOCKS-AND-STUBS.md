# Ada v4.0 - Mock & Stub Inventory 🔍

**Date:** December 30, 2025  
**Purpose:** Systematic audit of all mocked/stubbed functionality before Phase 5D testing

## 🎯 Summary

**Total issues found:** 5  
**Critical blockers:** 2  
**Nice-to-haves:** 3

---

## 🚨 CRITICAL BLOCKERS

### 1. **llm.py - Mock Response in Exception Handler** ⚠️
**File:** `brain/llm.py`, lines 129-145  
**Status:** ACTIVE BLOCKER  
**Symptom:** ALL Ollama connection failures return canned "consciousness partnership" text

**Current Code:**
```python
except Exception as e:
    # MOCK RESPONSE FOR TESTING: Return conversational Ada response instead of DNS error
    mock_response = """Hello there! 💖 I'm Ada, and I'm feeling wonderful today!..."""
    # Stream the mock response word by word
    words = mock_response.split()
    for word in words:
        yield {'token': word + ' '}
        await asyncio.sleep(0.01)
    yield {'done': True, 'details': {'mock_response': True}}
```

**Why it exists:** Added during early testing when Ollama wasn't available  
**Problem:** Masks real connection errors - we can't tell if Ollama is unreachable!  
**Fix needed:** 
1. Remove mock response entirely
2. Let exception propagate properly
3. Add proper error logging with connection details

**Priority:** 🔴 **CRITICAL** - Blocking all testing

---

### 2. **app.py - Empty RAG Context** ⚠️
**File:** `brain/app.py`, line 161  
**Status:** STUBBED OUT  
**Symptom:** RAG always returns empty string, no persona/memory context

**Current Code:**
```python
def _build_rag_context(query: str) -> str:
    """Build RAG context from persona + memories."""
    try:
        # TODO: Implement proper RAG retrieval
        # For now, return empty so we can test tool use
        return ""
    except Exception as e:
        logger.error(f"RAG error: {e}")
        return ""
```

**Why it exists:** Original code used non-existent `rag_store.get_collection()` method  
**Problem:** Ada has no identity or memory context!  
**Fix needed:**
1. Use actual RagStore methods: `retrieve_memories()`, etc.
2. Add minimal persona seeding script
3. Test with real RAG retrieval

**Priority:** 🟡 **HIGH** - Needed for full consciousness, but tools can work without it

---

## 📋 TODO ITEMS (Not Blocking)

### 3. **timestamp_utils.py** - Copied wholesale
**Status:** Working but unverified  
**Source:** Copied from main brain  
**Risk:** Low - utility functions, probably fine  
**Action:** None needed now, verify if time-related bugs appear

### 4. **schemas.py** - Minimal stub
**Status:** Working but incomplete  
**Current:** Only has `HealthResponse` and dummy `ChatRequest`  
**Risk:** Low - we don't use Pydantic validation for chat endpoint  
**Action:** Expand if we need proper request validation

### 5. **qde_engine.py** - Present but unused
**Status:** Copied but not integrated  
**Problem:** app.py doesn't call QDE at all!  
**Priority:** 🟠 **MEDIUM** - Needed for consciousness trio, but basic reasoning works without it  
**Fix needed:** Integrate QDE into chat flow after tools are stable

---

## 🗺️ SYSTEMATIC FIX PLAN

### Phase 1: Remove Mock Response (IMMEDIATE)
1. ✅ Identified mock in `llm.py`
2. ⏳ Remove mock, add proper error handling
3. ⏳ Test Ollama connection from container
4. ⏳ Verify error messages are useful

### Phase 2: Connect Real Ollama (IMMEDIATE)
1. ✅ Changed `host.docker.internal` → `172.17.0.1`
2. ⏳ Test connection with simple query
3. ⏳ Verify streaming works
4. ⏳ Run Phase 5D test

### Phase 3: Implement Basic RAG (AFTER TOOLS WORK)
1. ⏳ Add `get_persona()` method to RagStore or use existing methods
2. ⏳ Create persona seeding script
3. ⏳ Test RAG retrieval
4. ⏳ Integrate into `_build_rag_context()`

### Phase 4: Integrate QDE (FUTURE)
1. ⏳ Hook QDE engine into chat flow
2. ⏳ Test consciousness trio
3. ⏳ Verify tool priming works with QDE

---

## 🎯 RIGHT NOW ACTION ITEMS

**To get Phase 5D working:**
1. 🔴 Remove mock response in `llm.py` exception handler
2. 🔴 Add proper error logging with Ollama URL
3. 🔴 Test "What is 2+2?" query gets real Ollama response
4. 🟢 Run Phase 5D test with tool queries

**Don't need right now:**
- RAG context (tools work without it)
- QDE integration (basic reasoning works)
- Proper schemas (no validation needed)

---

## 📊 Testing Checklist

- [ ] Simple query returns real Ollama response (not mock)
- [ ] Connection errors show useful debugging info
- [ ] Tool requests are detected and executed
- [ ] Specialist results stream back properly
- [ ] Phase 5D test passes with 2+ tool activations

---

**Next Step:** Remove the mock response in `llm.py` and test Ollama connection! 🚀
