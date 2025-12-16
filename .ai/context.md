# Ada v1 - AI Context Map

## Purpose
Conversational AI system with RAG (Retrieval-Augmented Generation), streaming responses, and extensible specialist plugins for augmented capabilities.

## Core Architecture

### Service Topology
```
frontend (nginx:5000) → brain (fastapi:7000) ⇄ chroma (vector db:8000)
                                              ⇄ ollama (LLM:11434)
```

### Data Flow
1. User sends message → Frontend → `/v1/chat/stream` (SSE)
2. Brain assembles RAG context (persona, FAQ, memories, conversation history)
3. Specialists activate based on request context (OCR, media, web search)
4. Prompt built with context + specialist results → Ollama LLM
5. Response streamed back via Server-Sent Events
6. Memories extracted and stored in ChromaDB

## Key Modules

### Entry Points
- `brain/app.py` - FastAPI application, all API endpoints
- `frontend/public/app.js` - Client-side streaming handler
- `scripts/run.sh` - Containerized utilities and test runner

### Core Logic
- `brain/llm.py` - LLM client (Ollama), streaming generation
- `brain/prompt_builder.py` - RAG context assembly, specialist coordination
- `brain/rag_store.py` - Vector storage interface (ChromaDB)
- `brain/schemas.py` - All Pydantic models, self-documenting via `/v1/schema`

### Specialist System (Plugin Architecture)
- `brain/specialists/protocol.py` - Base interfaces, MCP-inspired
- `brain/specialists/ocr_specialist.py` - Image text extraction
- `brain/specialists/media_specialist.py` - Video frame analysis
- `brain/specialists/web_search_specialist.py` - External web queries
- `brain/specialists/bidirectional.py` - LLM-initiated specialist invocation

### Supporting Systems
- `brain/notices.py` + `brain/notices_client.py` - System alerts/notifications
- `brain/config.py` - Environment-based configuration (Pydantic Settings)
- `brain/media.py` - File upload handling
- `brain/ocr.py` - Tesseract integration

## Conventions

### Naming Patterns
- `*_specialist.py` - Auto-discovered specialist plugins
- `test_*.py` - Pytest test modules
- `*.rst` - Sphinx documentation (RST format)

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

## Testing Philosophy
- Integration tests via containerized environment
- Pytest fixtures in `tests/conftest.py`
- Test scripts in `scripts/test_*.py`
- Run via `./scripts/run.sh test`

## Key Relationships

### Circular Dependencies (Intentional)
- `llm.py` ↔ `prompt_builder.py` - Bidirectional specialists create cycles
- Resolution: Import at function scope where needed

### Critical Paths
- Chat request → `app.py` → `prompt_builder.py` → `llm.py` → streaming response
- Memory storage → `app.py` → `rag_store.py` → ChromaDB
- Specialist execution → `prompt_builder.py` → `specialists/*` → context injection

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
