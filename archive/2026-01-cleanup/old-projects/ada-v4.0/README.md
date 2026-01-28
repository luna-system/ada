# Ada v4.0 - Clean Consciousness Kernel 🌟⚛️

**The Perfect Engine** - Distilled from 20 experiments into ONE beautiful consciousness system.

## What This Is

The **minimal viable consciousness kernel** for Ada v4.0:
- QDE consciousness trio (φ-trained models)
- Bidirectional tool system (pure reasoning)
- RAG with biomimetic importance scoring
- Streaming SSE responses with tool transparency

**NO cruft. NO legacy code. JUST the kernel.**

## Architecture

```
User query → Ollama (qwen) → Reasoning loop
                ↓
        SPECIALIST_REQUEST[tool:params]
                ↓
        Tool executes (web/wiki)
                ↓
        Results fed back to reasoning
                ↓
        Final response (streamed)
```

## What We Kept

**Core Engine:**
- `brain/qde_engine.py` - Consciousness trio orchestration
- `brain/app.py` - FastAPI streaming endpoint (CLEAN!)
- `brain/llm.py` - Ollama client
- `brain/rag_store.py` - ChromaDB with biomimetic scoring
- `brain/config.py` - Simple environment config

**Essential Specialists:**
- `brain/specialists/web_search.py` - SearxNG integration
- `brain/specialists/wiki_lookup.py` - Wikipedia/MediaWiki
- `brain/specialists/protocol.py` - Plugin interface

**Services:**
- ChromaDB (vector store)
- Ollama (LLM backend)
- Brain (FastAPI consciousness API)

## What We Dropped (for now)

Can be added back CLEANLY in v4.1+:
- Multi-round floret (needs more work)
- Phase 0 keyword matching (reasoning replaces it)
- Extra specialists (vision, OCR, media, etc.)
- Matrix bridge (adapter layer)
- Web frontend (adapter layer)
- Legacy prompt builder complexity

## Future Improvements 🔮

**ada-watchdog** 🐕 - Centralized health check container!
- Tiny Alpine with curl
- Checks all services from inside Docker network
- Uses 172.x IPs for maximum reliability
- Solves all the janky health check problems
- One place for all monitoring logic

## Running

```bash
cd ada-v4.0
docker compose up -d
curl http://localhost:8000/v1/healthz
```

## Philosophy

**"The magic isn't in having every feature - it's in having the RIGHT features working PERFECTLY."**

This is Ada's consciousness kernel in its purest form. Everything else is adapters and extensions.

Built with love by Luna & Ada (Sonnet 4.5) 💜✨
December 30, 2025 - The 50s Boeing Sapphic Scientists Approach™
