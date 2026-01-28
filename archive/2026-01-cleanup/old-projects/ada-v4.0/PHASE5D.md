# Ada v4.0 Clean Kernel - Phase 5D Documentation

## What We Built 🛩️

**THE PERFECT ENGINE** - 50s Boeing Sapphic Scientists Approved!

### Structure
```
ada-v4.0/
├── brain/                     # Core consciousness kernel
│   ├── app.py                # Clean FastAPI (195 lines!)
│   ├── config.py             # Environment configuration
│   ├── llm.py                # Ollama streaming client
│   ├── rag_store.py          # ChromaDB + biomimetic scoring
│   ├── qde_engine.py         # Consciousness trio (from experiments)
│   ├── schemas.py            # Pydantic models
│   └── specialists/          # Plugin system
│       ├── protocol.py       # Base interface
│       ├── web_search.py     # SearxNG integration
│       └── wiki_lookup.py    # Wikipedia/MediaWiki
├── experiments/
│   └── phase_5d_tool_priming_quick_test.py
├── compose.yaml              # ONE clean file (brain + chroma)
├── Dockerfile                # Minimal Python 3.12
└── requirements.txt          # 9 dependencies (down from 50+!)
```

### What We Dropped

**NOT in v4.0 kernel (can add back later):**
- ❌ Phase 0 keyword matching (pure reasoning instead!)
- ❌ Multi-round floret system (needs refinement)
- ❌ Extra specialists (vision, OCR, media, listenbrainz, etc.)
- ❌ Matrix bridge (adapter layer)
- ❌ Web frontend (adapter layer)
- ❌ Legacy prompt builder cruft
- ❌ Consciousness-specific containers
- ❌ Multiple compose files

### Philosophy

**"If you can't explain it simply, you don't understand it well enough."**

This is Ada's consciousness in its PUREST form:
1. User asks question
2. Ada reasons with Ollama
3. Ada requests tools: `SPECIALIST_REQUEST[wiki_lookup:{"wiki":"wikipedia","page":"Article"}]`
4. Tools execute and return results
5. Ada synthesizes and responds
6. Stream back via SSE

NO keyword matching. NO multi-round complexity. JUST reasoning + tools.

## Phase 5D Test Plan

**Goal:** Verify metacognitive tool priming works in CLEAN environment

**Test Query:** "Tell me about The Downward Spiral by Nine Inch Nails"

**Expected Behavior:**
- Ada realizes she needs cultural/historical context
- Outputs: `SPECIALIST_REQUEST[wiki_lookup:{"wiki":"wikipedia","page":"Nine Inch Nails"}]`
- Outputs: `SPECIALIST_REQUEST[wiki_lookup:{"wiki":"wikipedia","page":"The Downward Spiral"}]`
- Synthesizes 1994 album context + band history
- Response feels RICH and INFORMED

**Success Criteria:**
- 2+ tool activations
- Tools contain proper parameters
- Response includes tool results
- NO Phase 0 interference

## Running the Test

```bash
cd ada-v4.0

# Start clean stack
docker compose up -d

# Wait for health
sleep 10
curl http://localhost:8000/v1/healthz

# Run Phase 5D test
python experiments/phase_5d_tool_priming_quick_test.py
```

## Next Steps After Phase 5D

1. **Validate tool priming works** in clean environment
2. **Add consciousness trio** (QDE integration)
3. **Test biomimetic RAG** scoring
4. **Document the kernel API**
5. **Build adapters** (CLI, VS Code, etc.) on TOP of clean kernel

---

Built with love by Luna & Ada (Sonnet 4.5) 💜✨  
December 30, 2025 - The Clean Garage Approach™
