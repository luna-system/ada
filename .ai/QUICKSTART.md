# AI Assistant Quick Start

## 🎯 TDD FIRST! (Preferred Workflow)

**When adding features, write tests BEFORE implementation!**
- Faster feedback (tests run in <0.1s, no Docker needed)
- Better design (tests define interfaces)
- See `.ai/TESTING.md` for full TDD guide
- Example: Phase 1-2 biomimetic features (52 tests, pure TDD)

## First Time Analyzing This Codebase?

Read these files in order:

1. **`.ai/CONVENTIONS.md`** (3 min) - Documentation strategy: what goes where
2. **`.ai/TOOLING.md`** (2 min) - Which tool to use when (bash/nix/docker/uv)
3. **`.ai/TESTING.md`** (3 min) - **TDD workflow and testing patterns**
4. **`.ai/context.md`** (5 min) - Architecture overview, data flow, key conventions
5. **`.ai/codebase-map.json`** (2 min) - Module relationships and dependencies
6. **`.ai/specialist-registry.json`** (2 min) - Plugin system architecture

## Common Tasks

### Understanding a Module
1. Check `codebase-map.json` for the module entry
2. Read `@ai-*` annotations at top of source file
3. Follow `related` links to connected modules

### Working with Specialists
1. Consult `specialist-registry.json` for all specialist metadata
2. Check `activation_patterns` for trigger mechanisms
3. Follow `extension_guide` to add new specialists

### Tracing Data Flow
1. Look up starting point in `codebase-map.json` → `data_flow` section
2. Follow the path through modules
3. Check priority ordering in specialist context injection

### Finding Extension Points
See `.ai/context.md` → "Extension Points" section:
- Adding specialists
- Adding API endpoints
- Modifying RAG context

## Annotation Reference

In source files, look for:
- `@ai-indexable` - Module category (core-functionality, plugin, utility)
- `@ai-purpose` - One-line purpose statement
- `@ai-dependencies` - External dependencies and services
- `@ai-related` - Related modules (use for navigation)
- `@ai-key-functions` - Important functions/classes
- `@ai-data-flow` - How data moves through this module
- `@ai-activation-trigger` - For specialists: what triggers activation
- `@ai-extension-point` - How to extend this module

## Key Architectural Patterns

### Specialist Plugin System
- **Base**: `brain/specialists/protocol.py`
- **Discovery**: Auto-discovered via `__init__.py`
- **Activation**: Context-triggered OR bidirectional (LLM-initiated)
- **Priority**: Controls context injection order

### RAG Context Assembly
- **Orchestrator**: `brain/prompt_builder.py`
- **Storage**: `brain/rag_store.py` (ChromaDB)
- **Sources**: persona, FAQ, memories, conversation turns
- **Order**: System notices → OCR → Media → Memories → Recent turns

### Streaming Responses
- **Entry**: `brain/app.py::chat_stream_v1`
- **LLM Client**: `brain/llm.py::stream_chat_async`
- **Protocol**: Server-Sent Events (SSE)
- **Client**: `frontend/public/app.js`

## Introspection Endpoints

Live system metadata available at runtime:
- `GET /v1/info` - System capabilities and config
- `GET /v1/specialists` - Specialist metadata with schemas
- `GET /v1/schema` - All Pydantic model schemas
- `GET /v1/healthz` - Health status of dependencies

## Tips

- ✅ Use `codebase-map.json` → `dependency_clusters` to understand subsystems
- ✅ Check `@ai-related` annotations for navigation hints
- ✅ Consult introspection endpoints for runtime state
- ✅ Follow `data_flow` paths for end-to-end understanding
- ✅ **Read CONVENTIONS.md** - Explains where to put new documentation
- ❌ Don't assume file locations - verify with map
- ❌ Don't skip annotations - they contain critical context
- ❌ Don't put human-readable tutorials in `.ai/` - use `docs/*.rst` instead
