# Specialist RAG Documentation System

## Overview

Instead of using static specialist instructions in the system prompt, Ada now uses **RAG-based dynamic documentation** that retrieves relevant specialist guidance based on the user's query context.

## How It Works

### 1. Automatic Sync on Startup

When the brain service starts:
```
[BRAIN] Discovered 2 specialists: 🎧 media, 📄 ocr
[BRAIN] Synced 8 specialist FAQ entries to RAG
```

The system:
- Discovers all registered specialists via the plugin registry
- Generates FAQ entries from specialist capabilities
- Stores them in Chroma with `type="faq"` and `topic="specialists"`
- Removes old entries to ensure idempotency

### 2. Context-Aware Retrieval

During prompt building (`build_prompt()` in prompt_builder.py):
- User's query is embedded
- RAG retrieves the top K most relevant specialist FAQs
- Retrieved docs are injected into the prompt before specialist execution
- This provides **just-in-time** specialist guidance instead of static instructions

### 3. FAQ Entry Types

The system generates multiple FAQ types:

**Overview FAQ:**
```
Q: What specialist capabilities are available?
A: Ada has 2 specialist capabilities integrated: 🎧 media, 📄 ocr. 
   These can be invoked mid-conversation using SPECIALIST_REQUEST[name:{params}] syntax...
```

**Per-Specialist Capability FAQ:**
```
Q: What does the ocr specialist do?
A: Extract text from images using Tesseract OCR (Priority: HIGH, Icon: 📄)
```

**Per-Specialist Syntax FAQ:**
```
Q: How do I invoke the ocr specialist?
A: Use the syntax SPECIALIST_REQUEST[ocr:{}] in your response. I will detect this pattern, 
   pause generation, execute the specialist, and resume with enriched context.
```

**Usage Pattern FAQs:**
- When to use specialists
- Chaining multiple specialists
- How pause/resume works

## Configuration

### Enable/Disable RAG Docs

```bash
SPECIALIST_RAG_DOCS=true  # Use dynamic RAG retrieval (default)
SPECIALIST_RAG_DOCS=false # Use static SPECIALIST_INSTRUCTIONS only
```

Set in `brain/config.py`:
```python
SPECIALIST_RAG_DOCS = os.getenv("SPECIALIST_RAG_DOCS", "true").lower() == "true"
```

### Retrieval Count

In `prompt_builder.py`, specialist docs retrieve 2 FAQs by default:
```python
specialist_docs = get_relevant_specialist_docs(user_prompt, rag_store, k=2)
```

## Benefits

### 1. **Context-Aware Guidance**
- User asks "can you analyze this image?" → OCR/vision docs retrieved
- User asks "what's playing?" → Media specialist docs retrieved
- Irrelevant specialists don't clutter the prompt

### 2. **Automatic Updates**
- Add a new specialist → FAQ entries auto-generated on next startup
- Modify specialist capability → Updated in RAG automatically
- No manual prompt engineering required

### 3. **Token Efficiency**
- Static `SPECIALIST_INSTRUCTIONS` = ~300 tokens always present
- Dynamic RAG retrieval = ~100-200 tokens only when relevant
- Reduces prompt bloat for non-specialist queries

### 4. **Semantic Matching**
- User query: "What can you see in this photo?"
- RAG retrieves: OCR + vision specialist documentation
- LLM learns specialist syntax contextually

## Implementation Files

### `brain/specialists/specialist_docs.py`
- `sync_specialist_docs_to_faq()` - Generate FAQ entries from all specialists
- `get_relevant_specialist_docs()` - Retrieve relevant docs for a query

### `brain/app.py` (lifespan)
```python
# Sync specialist documentation to FAQ system
if rag_store is not None:
    doc_count = sync_specialist_docs_to_faq(rag_store)
    print(f"[BRAIN] Synced {doc_count} specialist FAQ entries to RAG")
```

### `brain/prompt_builder.py`
```python
# --- Dynamic Specialist Documentation (RAG-based) ---
if SPECIALIST_RAG_DOCS and rag_store is not None:
    specialist_docs = get_relevant_specialist_docs(user_prompt, rag_store, k=2)
    if specialist_docs:
        sections.append(specialist_docs)
        used_context['specialist_docs'] = True
```

## Example Workflow

### User Query: "Can you read the text in this image?"

1. **Prompt Building Phase:**
   - Embed query: "Can you read the text in this image?"
   - RAG retrieves from `type="faq", topic="specialists"`:
     - "How do I invoke the ocr specialist?"
     - "What does the ocr specialist do?"
   - Format and inject into prompt:
     ```
     📚 Specialist Capabilities Reference:
       • Use the syntax SPECIALIST_REQUEST[ocr:{}]...
       • Extract text from images using Tesseract OCR...
     ```

2. **LLM Generation:**
   - Ada sees relevant OCR documentation in context
   - Generates: "I can extract the text using OCR. SPECIALIST_REQUEST[ocr:{}]"

3. **Specialist Execution (Pause/Resume):**
   - Generation pauses
   - OCR specialist extracts: "Annual Report 2024..."
   - Generation resumes with OCR result injected

4. **Final Response:**
   - "The image contains: Annual Report 2024..."

## Future Enhancements

### Phase 1: Embedding-Based Specialist Discovery
Instead of the LLM explicitly requesting specialists, the system could:
- Embed user query
- Check similarity to specialist capabilities
- Auto-suggest specialists in prompt

### Phase 2: Example-Based Learning
Store successful specialist invocations as FAQs:
```
Q: User uploaded a diagram and asked "what's the architecture?"
A: I used SPECIALIST_REQUEST[vision:{"focus":"architecture"}] to analyze...
```

### Phase 3: Failure Case Documentation
Track failed specialist calls and add FAQ warnings:
```
Q: Can OCR read handwritten text?
A: OCR works best with printed text. Handwritten text may have lower accuracy.
```

## Debugging

### Check Synced FAQs
```bash
# View all specialist FAQs
docker exec ada-v1-brain-1 python -c "
from rag_store import RagStore
store = RagStore()
result = store.col.query(
    query_texts=['specialists'],
    n_results=10,
    where={'type': 'faq', 'topic': 'specialists'}
)
for doc in result['documents'][0]:
    print(doc)
    print('---')
"
```

### Test Retrieval
Query the debug endpoint (if RAG_DEBUG=true):
```bash
curl "http://localhost:7000/v1/debug/prompt?prompt=analyze%20image&faq_k=5"
```

Check `used_context.specialist_docs` field to see if docs were injected.

### Monitor Logs
```bash
docker logs ada-v1-brain-1 | grep "Synced.*FAQ"
# [BRAIN] Synced 8 specialist FAQ entries to RAG
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SPECIALIST_RAG_DOCS` | `true` | Enable dynamic RAG-based specialist documentation |
| `SPECIALIST_PAUSE_RESUME` | `true` | Enable pause/resume for specialist execution |
| `SPECIALIST_MAX_TURNS` | `5` | Maximum specialist calls per conversation |
| `RAG_FAQ_TOP_K` | `2` | Number of FAQ entries to retrieve (includes specialist docs) |

## Migration Notes

### Before (Static Instructions)
- All specialist syntax in `SPECIALIST_INSTRUCTIONS` (300+ tokens)
- Present in every prompt regardless of relevance
- Manual updates required for new specialists

### After (Dynamic RAG)
- Specialist syntax retrieved on-demand from FAQ system
- Only relevant specialists injected based on query
- Automatic updates when specialists added/changed
- Backward compatible: static instructions still present as fallback

## Related Documentation

- [SPECIALISTS.md](SPECIALISTS.md) - Plugin protocol and creation guide
- [BIDIRECTIONAL_SPECIALISTS.md](BIDIRECTIONAL_SPECIALISTS.md) - Communication patterns
- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md) - RAG system overview
