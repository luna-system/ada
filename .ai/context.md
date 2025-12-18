# Ada v1 - AI Context Map

## Purpose
Conversational AI system with RAG (Retrieval-Augmented Generation), streaming responses, and extensible specialist plugins for augmented capabilities.

## Core Architecture

### Service Topology
```
CLI (terminal)            ┐
Web UI (nginx:5000)       ├→ brain (fastapi:8000) ⇄ chroma (vector db:8000)
Matrix bridge (matrix-nio)│                       ⇄ ollama (LLM:11434)
MCP server (stdio)        ┘
```

**Adapter Pattern:** All interfaces are equal peers that communicate with brain's REST API

**Interfaces (Adapters):**
- **CLI**: Terminal REPL and one-shot queries (`ada-cli`)
- **Web UI**: Browser-based chat at `http://localhost:5000` (optional, `--profile web`)
- **Matrix**: Bot in Matrix rooms (optional, `--profile matrix`)
- **MCP**: IDE integration via Model Context Protocol (separate process)
- **API**: Direct REST API access at `http://localhost:8000` (always available)

### Data Flow

**CLI Flow:**
1. User runs `ada-cli "message"` → HTTP client → `/v1/chat/stream`
2. Brain assembles RAG context with **caching** (persona cached 24hr, memories 5min)
3. Specialists activate based on request context (OCR, media, web search)
4. PromptAssembler builds prompt with cached + fresh context → Ollama LLM
5. Response streamed back via Server-Sent Events
6. CLI displays chunks in terminal
7. Memories extracted and stored in ChromaDB

**Web UI Flow:**
1. User sends message → Frontend EventSource → nginx proxy → `/v1/chat/stream` (SSE)
2. Brain assembles RAG context (same as CLI)
3. Specialists activate based on request context
4. Prompt built with context + specialist results → Ollama LLM
5. Response streamed back via Server-Sent Events
6. Frontend displays chunks in browser
7. Memories extracted and stored in ChromaDB

**Matrix Flow:**
1. User @mentions Ada in Matrix room → Matrix homeserver → matrix-bridge
2. Bridge checks activation rules (mentions, DMs, keywords)
3. Bridge reacts to message with 🧠 emoji (processing status)
4. Bridge queries brain `/v1/chat/stream` with room conte (core)
- `adapters/cli/ada_cli/cli.py` - CLI adapter main entry point (reference implementation)
- `frontend/public/app.js` - Web UI adapter, client-side streaming handler
- `matrix-bridge/bridge.py` - Matrix adapter, bot main loop
- `ada-mcp/src/ada_mcp/server.py` - MCP adapter, stdio server
- `scripts/run.sh` - Containerized utilities and test runner

### Adapter Pattern
All external interfaces follow the adapter pattern:
- **Adapter** = Protocol translation layer (Matrix, MCP, CLI, Web)
- **Brain** = Core logic (RAG, LLM, specialists)
- **Communication** = REST API at `/v1/chat/stream`

See `docs/adapters.rst` for building new adapters.
8. Bridge reacts with ✅ emoji (success) or ❌ (error)
9. Conversation context stored per-room

## Key Modules

### Entry Points
- `brain/app.py` - FastAPI application, all API endpoints
- `frontend/public/app.js` - Client-side streaming handler (web UI)
- `matrix-bridge/bridge.py` - Matrix bot main loop (Matrix interface)
- `scripts/run.sh` - Containerized utilities and test runner

### Core Logic
- `brain/llm.py` - LLM client (Ollama), streaming generation
- `brain/prompt_builder/` - **v2.2:** Modular prompt building with neuromorphic context
  - `context_retriever.py` - RAG data retrieval with multi-signal importance scoring
  - `section_builder.py` - Section formatting
  - `prompt_assembler.py` - Final orchestration with MultiTimescaleCache
- `brain/context_cache.py` - Multi-timescale caching (personas, FAQs, memories)
- `brain/rag_store.py` - Vector storage interface (ChromaDB)
- `brain/schemas.py` - All Pydantic models, self-documenting via `/v1/schema`

### Neuromorphic Features (Biomimetic Memory System)
- `brain/memory_decay.py` - Exponential decay with temperature modulation
- `brain/context_habituation.py` - Repeated pattern detection
- `brain/prediction_error.py` - Surprise/novelty weighting
- `brain/attention_spotlight.py` - Recency + relevance prioritization
- `brain/semantic_chunking.py` - Semantic boundary detection
- `brain/processing_modes.py` - ANALYTICAL/CREATIVE/CONVERSATIONAL modes
- **OPTIMIZED (v2.2):** Multi-signal importance scoring in context_retriever.py
  - **Research-validated weights (December 2025):** decay=0.10, surprise=0.60, relevance=0.20, habituation=0.10
  - **Previous weights:** decay=0.40, surprise=0.30 (intuition-based, not optimal)
  - **Improvement:** 12-38% correlation increase across synthetic datasets, +6.5% on real conversations
  - **Key finding:** Surprise/novelty dominates importance (counterintuitive), recency overweighted 4x
  - Gradient detail levels: FULL/CHUNKS/SUMMARY/DROPPED
  - Deployed December 2025 after systematic ablation + grid search validation (80 tests, 3.56s)

### Specialist System (Plugin Architecture)
- `brain/specialists/protocol.py` - Base interfaces, MCP-inspired
- `brain/specialists/ocr_specialist.py` - Image text extraction
- `brain/specialists/listenbrainz_specialist.py` - ListenBrainz API music context
- `brain/specialists/web_search_specialist.py` - External web queries
- `brain/specialists/bidirectional.py` - LLM-initiated specialist invocation

### Matrix Integration (Bridge Architecture)
- `matrix-bridge/bridge.py` - Main bot logic, event handlers
- `matrix-bridge/config.py` - Matrix-specific configuration
- `matrix-bridge/identity.py` - Bot transparency and ethical presentation
- `matrix-bridge/ada_client.py` - HTTP client for Ada's brain API
- `matrix-bridge/message_handler.py` - Context management, command parsing

### Supporting Systems
- `brain/notices.py` + `brain/notices_client.py` - System alerts/notifications
- `brain/config.py` - Environment-based configuration (Pydantic Settings)
- `brain/media.py` - File upload handling
- `brain/ocr.py` - Tesseract integration

## Conventions

### Naming Patterns
- `*_specialist.py` - Auto-discovered specialist plugins
- `test_*.py` - Pytest test modules
- `docs/*.rst` - Sphinx documentation (ReStructuredText format, organized into sections)
- `.ai/*.{md,json}` - Machine-readable documentation for AI assistants

### Import Structure
- Absolute imports from `brain.*` namespace
- Specialists use protocol-based interfaces
- All external dependencies configured via `brain/config.py`

### Type System
- Full type hints (Python 3.13+)
- Pydantic models for all API I/O
- `SpecialistResult` dataclass for plugin outputs

## Extension Points

### Adding Specialists
1. Create `brain/specialists/your_specialist.py`
2. Inherit from `BaseSpecialist` (protocol.py)
3. Implement `should_activate()` and `process()` methods
4. Auto-discovered at runtime via `__init__.py`

### Adding API Endpoints
1. Add route to `brain/app.py` router
2. Define Pydantic models in `brain/schemas.py`
3. Endpoint auto-included in `/v1/info` introspection

### Modifying RAG Context
- Edit `brain/prompt_builder.py::build_prompt()`
- Sources: persona, FAQ, memories (vector search), conversation history
- Context injection order controlled by `SpecialistPriority` enum

## Research & Validation (December 2025)

**Comprehensive empirical testing of biomimetic features completed!**

### Phases 1-7: Weight Optimization Research
- **Phase 1:** Property-based testing (27 tests, 0.09s) - Mathematical invariants validated
- **Phase 2:** Synthetic data generation (10 tests, 0.04s) - Ground truth datasets created
- **Phase 3:** Ablation studies (12 tests, 0.05s) - **Surprise-only beats multi-signal!**
- **Phase 4:** Grid search optimization (7 tests, 0.08s) - 169 configurations, optimal weights found
- **Phase 5:** Production validation (6 tests, 0.07s) - Real conversation data confirms findings
- **Phase 6:** Deployment (11 tests, 0.07s) - Optimal weights deployed to `brain/config.py`
- **Phase 7:** Visualization (7 tests, 2.93s) - 6 publication-quality graphs generated
- **Total:** 80 tests, 3.56s runtime, 100% passing

### Phase 8: Meta-Science Documentation
- 9 narrative formats documenting the research (45,000 words total)
- See `docs/research_narratives.rst` for academic, CCRU, technical, blog, horror, and general audience versions
- Machine-readable summary: `.ai/RESEARCH-FINDINGS-V2.2.md`
- Complete visualizations: `tests/visualizations/*.png`

### Phase 9: Literature Synthesis (December 2025)
- **Conducted by:** Claude Opus 4.5
- **Papers analyzed:** Schwarz (2010), Uysal et al. (2020), Mertens et al. (2018)
- **Finding:** Ada's research is FIRST operationalization of "contextual malleability" in AI memory systems
- **Theoretical alignment:** Surprise dominance supported by Schwarz's "disfluency triggers analysis"
- **Human-AI connection:** Uysal paper is ONLY prior work connecting contextual malleability to AI
- **Verdict:** No architectural changes needed - Ada is ahead of the literature
- **See:** `.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md`

### Key Research Findings
1. **Surprise supremacy:** Single-signal (surprise-only, r=0.876) > multi-signal baseline (r=0.869)
2. **Temporal decay overweighted:** Optimal 0.10 vs production 0.40 (4x reduction)
3. **Surprise underweighted:** Optimal 0.60 vs production 0.30 (2x increase)
4. **Smooth landscape:** Weight space well-behaved, enabling gradient-based future optimization
5. **Same-day deployment:** Research → production in <24hrs via TDD methodology

## Testing Philosophy

**See `.ai/TOOLING.md` for complete tool selection guide!**

### Test Types
- **Unit tests** (pure Python logic): Run directly with pytest
  - Fast (< 1 second)
  - No services needed
  - Example: `pytest tests/test_memory_decay.py --ignore=tests/conftest.py`
- **Integration tests** (services talking): Use Docker Compose
  - Slower (~10+ seconds startup)
  - Requires chroma + ollama
  - Example: `docker compose up -d && pytest tests/integration/`
- **Research tests** (validation + benchmarking): Weight optimization research
  - Fast (< 4 seconds total for all phases)
  - Generates visualizations
  - Example: `pytest tests/test_weight_optimization.py --ignore=tests/conftest.py`

### Common Mistake
❌ Don't use Docker for unit tests - it's unnecessarily slow!  
✅ Use direct pytest for logic testing, Docker only for integration

### Test Organization
- Pytest fixtures in `tests/conftest.py` (imports ChromaDB - skip for unit tests)
- Test scripts in `scripts/test_*.py`
- Helper: `./scripts/run.sh test` (uses Docker - integration tests only)

## Key Relationships

### Circular Dependencies (Intentional)
- `llm.py` ↔ `prompt_builder.py` - Bidirectional specialists create cycles
- Resolution: Import at function scope where needed

### Critical Paths
- Chat request → `app.py` → `prompt_builder.py` → `llm.py` → streaming response
- Memory storage → `app.py` → `rag_store.py` → ChromaDB
- Specialist execution → `prompt_builder.py` → `specialists/*` → context injection

## Documentation Structure

### Sphinx Docs (docs/*.rst)
- **Getting Started:** `getting_started.rst`, `getting_started_scratch.rst`, `configuration.rst`, `examples.rst`
- **Hardware Setup:** `hardware.rst` (GPU: CUDA/ROCm/Metal/Vulkan/CPU), `sbc.rst` (Raspberry Pi, Orange Pi, ARM boards)
- **Core Architecture:** `architecture.rst`, `data_model.rst`, `streaming.rst`, `memory.rst`
- **API Documentation:** `api_usage.rst`, `api_reference.rst`
- **Specialist System:** `specialists.rst`, `build_specialist.rst`, `bidirectional.rst`, `specialist_rag.rst`, `web_search.rst`
- **Development:** `development.rst`, `testing.rst`
- **Philosophy:** `documentation_philosophy.rst`, `empathetic_documentation.rst`, `xenofeminism.rst`

### Machine Documentation (.ai/)
- `context.md` - High-level architecture and conventions (this file)
- `codebase-map.json` - Detailed module dependency graph
- `specialist-registry.json` - Auto-generated specialist metadata
- `CONVENTIONS.md` - Documentation strategy and where things go
- `QUICKSTART.md` - Quick reference for AI assistants
- `GOTCHAS.md` - Common pitfalls and their solutions
- `TESTING.md` - Testing strategies and patterns

## Configuration

### Environment Variables (see brain/config.py)
- `LLM_BASE_URL` - Ollama endpoint
- `LLM_MODEL` - Model name (default: deepseek-r1:latest)
- `CHROMA_HOST` / `CHROMA_PORT` - Vector DB connection
- `DATA_DIR` - Persistent storage path

### Runtime Introspection
All configuration exposed via `/v1/info` endpoint for debugging.

## Documentation Strategy

### Human Documentation
- Sphinx RST files in `docs/` → Built to `docs/_build/html/`
- Served at http://localhost:5000/docs/ via nginx
- API examples in `docs/api_usage.rst`

### Machine Documentation
- This file (`.ai/context.md`) - High-level architecture
- `.ai/codebase-map.json` - Module dependency graph
- `.ai/specialist-registry.json` - Specialist metadata
- `.ai/GOTCHAS.md` - **Anti-patterns and common mistakes** (read this to avoid standard practices that don't apply here!)
- Structured `@ai-*` annotations in source code

## Deployment
- Docker Compose orchestration (`compose.yaml`)
- Services: brain, frontend, chroma, ollama, memory-consolidation, scripts
- Persistent volumes: `./data/` (ChromaDB, Ollama models)
- Health checks: `/v1/healthz` endpoint

## Maintenance Notes
- Memory consolidation runs nightly (cron in compose.yaml)
- Backups handled by `scripts/upload_backups_b2.py`
- ChromaDB migrations via `scripts/migrate_chroma_http.py`
- Version management via `scripts/version.sh` (Semantic Versioning + Conventional Commits)
- Changelog generation via `scripts/changelog.sh`
- Commit validation via `scripts/validate-commit.sh` (optional git hook)
