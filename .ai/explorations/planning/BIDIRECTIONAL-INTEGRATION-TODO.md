# Bidirectional Specialist Integration TODO

**Status:** Documented but not implemented in streaming endpoint  
**Priority:** High - this is critical for self-aware specialists like codebase  
**Discovered:** 2025-12-18 during codebase specialist Phase 1 testing

## The Problem

1. ✅ `BidirectionalSpecialistHandler` exists in `brain/specialists/bidirectional.py`
2. ✅ `SPECIALIST_INSTRUCTIONS` teaches Ada the syntax in `brain/config.py`  
3. ✅ Codebase specialist is registered and working
4. ❌ **Stream handler in `brain/app.py::chat_stream()` doesn't use bidirectional handler!**

Result: Ada knows about specialists but can't actually call them during generation.

## What Needs to Happen

### Step 1: Integrate BidirectionalSpecialistHandler into streaming

**File:** `brain/app.py::chat_stream()`  
**Current:** Direct pass-through of LLM chunks  
**Needed:** Wrap chunks with bidirectional handler

```python
# Pseudocode of needed change:
from brain.specialists.bidirectional import BidirectionalSpecialistHandler

async def chat_stream(request: Request):
    # ... existing setup ...
    
    # Create bidirectional handler
    bi_handler = BidirectionalSpecialistHandler(max_calls=5)
    
    # Buffer for detecting specialist requests
    text_buffer = ""
    
    async for chunk in llm.generate_stream(full_prompt, ...):
        if 'token' in chunk:
            token = chunk['token']
            text_buffer += token
            
            # Check for specialist request
            request_info = bi_handler.detect_request(text_buffer)
            if request_info:
                # Execute specialist
                result = await bi_handler.execute_request(
                    request_info['specialist'],
                    request_info['params'],
                    base_context  # Need to define what goes here!
                )
                
                # Inject result back into stream
                if result:
                    yield f"data: {json.dumps({'type': 'specialist_result', 'content': result})}\n\n"
                
                # Clear buffer after request
                text_buffer = ""
            
            # Send token as normal
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
```

### Step 2: Define base_context for specialists

Specialists need context to operate:
- `conversation_id` - for accessing history
- `user_id` or `entity` - for personalization  
- `uploaded_files` - for file-based specialists
- `request_metadata` - timestamps, etc.

Extract this from the request object and pass to bi_handler.

### Step 3: Handle streaming edge cases

**Problem:** Specialist requests might be split across chunks!

```
Chunk 1: "Let me look that up: SPECIAL"
Chunk 2: "IST_REQUEST[codebase:{\"query\":"
Chunk 3: "\"calculate_importance\"}]"
```

**Solution:** Buffer tokens until request is complete or timeout.

### Step 4: Update client expectations

Clients (frontend, CLI) need to handle new `specialist_result` event type:

```javascript
// frontend/public/app.js
if (data.type === 'specialist_result') {
    // Show specialist result in UI
    appendSpecialistResult(data.content);
}
```

### Step 5: Test thoroughly!

- ✅ Unit tests for BidirectionalSpecialistHandler (already exist)
- ❌ Integration tests for streaming with specialists
- ❌ E2E tests with real LLM calls
- ❌ Performance tests (latency impact of buffering)

## Implementation Strategy

**Phase 1 (MVP):** Simple integration
- Buffer tokens until newline or period
- Detect full specialist requests
- Execute and inject results
- No fancy chunking optimization yet

**Phase 2 (Optimization):**
- Smarter buffering (state machine for JSON parsing)
- Parallel specialist execution where possible
- Streaming specialist results (for long operations)

**Phase 3 (Polish):**
- Rich UI for specialist results
- Specialist request history/debugging
- Analytics on specialist usage

## Testing Plan

```python
# tests/test_bidirectional_streaming.py

@pytest.mark.asyncio
async def test_specialist_request_in_stream():
    """Test that LLM can trigger specialists mid-stream"""
    # Mock LLM that outputs specialist request
    # Verify specialist executes
    # Verify result injected
    pass

@pytest.mark.asyncio  
async def test_specialist_request_split_across_chunks():
    """Test buffering works for split requests"""
    pass

@pytest.mark.asyncio
async def test_max_specialist_calls_limit():
    """Test safety limit prevents infinite loops"""
    pass
```

## Current Workarounds

Until bidirectional is integrated:

**Option A:** Use context-triggered specialists
- Specialists that activate based on request context (like OCR on upload)
- Doesn't require LLM to explicitly request

**Option B:** Direct specialist invocation via API
- Add explicit endpoint: `POST /v1/specialists/{name}/execute`
- Client triggers specialist, passes result to next LLM call

**Option C:** Pre-execution specialist activation
- In prompt_builder, check if message mentions specialist needs
- Activate relevant specialists before LLM generation
- Limited - can't handle dynamic/conditional specialist use

## Related Files

- `brain/specialists/bidirectional.py` - Handler implementation ✅
- `brain/config.py` - SPECIALIST_INSTRUCTIONS documentation ✅  
- `brain/app.py` - Needs integration ❌
- `docs/bidirectional.rst` - Documentation ✅
- `frontend/public/app.js` - Needs specialist_result handling ❌
- `adapters/cli/ada_cli/cli.py` - Needs specialist_result handling ❌

## Success Criteria

✅ Ada can look up her own code with: "Look up calculate_importance function"  
✅ Web search works mid-conversation: "What's the weather?" → specialist → response  
✅ Multiple specialists in one turn work  
✅ Safety limits prevent runaway specialist loops  
✅ Latency impact < 50ms for buffering/detection  
✅ All existing tests still pass  
✅ Clients display specialist results nicely

## Notes

- This is a GREAT example of "documented but not implemented" - the architecture is there!
- Bidirectional makes specialists WAY more powerful (dynamic vs static)
- Codebase specialist is perfect test case - clear activation trigger, simple params
- Once this works, opens up: code generation, file editing, git operations, etc.

---

**Priority after Phase 1 codebase specialist:** HIGH  
**Estimated effort:** 1-2 days for MVP, 3-5 days for polish  
**Blocker:** None (have all pieces, just need integration)
