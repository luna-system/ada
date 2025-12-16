# GitHub Copilot Instructions for Ada

> **Note:** This project maintains comprehensive machine-readable documentation in the `.ai/` folder. Please reference those files for accurate, up-to-date context.

## Quick Start

**New to this codebase?** Read these in order:

1. **[`.ai/context.md`](../.ai/context.md)** - Architecture overview and data flow
2. **[`.ai/codebase-map.json`](../.ai/codebase-map.json)** - Module dependencies and relationships
3. **[`.ai/CONVENTIONS.md`](../.ai/CONVENTIONS.md)** - Where things go and why

## Machine Documentation Structure

Ada maintains **separation of concerns** between human and machine documentation:

- **`docs/*.rst`** - Human-readable (Sphinx) - Tutorials, guides, examples
- **`.ai/*.{md,json}`** - Machine-readable - Architecture, dependencies, patterns
- **Inline `@ai-*` annotations** - Source code context

**For comprehensive context, always check `.ai/` first.**

## Key Files for AI Assistants

| File | Purpose | When to Use |
|------|---------|-------------|
| `.ai/context.md` | Architecture overview | Understanding system structure |
| `.ai/codebase-map.json` | Module dependency graph | Finding related code |
| `.ai/specialist-registry.json` | Plugin system metadata | Working with specialists |
| `.ai/CONVENTIONS.md` | Documentation strategy | Knowing where to put things |
| `.ai/QUICKSTART.md` | Common tasks | Quick reference patterns |
| `.ai/GOTCHAS.md` | Known pitfalls | Avoiding mistakes |
| `.ai/TESTING.md` | Testing patterns | Writing/running tests |

## Architecture Quick Reference

```
frontend (nginx:5000) → brain (fastapi:7000) ⇄ chroma (vector db:8000)
                                              ⇄ ollama (LLM:11434)
```

**Core modules:**
- `brain/app.py` - FastAPI endpoints
- `brain/prompt_builder.py` - RAG context assembly
- `brain/llm.py` - Ollama client wrapper
- `brain/rag_store.py` - ChromaDB interface
- `brain/specialists/*.py` - Plugin system

See [`.ai/context.md`](../.ai/context.md) for detailed data flow.

## Code Patterns

### Adding a New Specialist

1. Create `brain/specialists/your_specialist.py`
2. Inherit from `SpecialistProtocol`
3. Implement `should_activate()` and `process()`
4. Register in `brain/specialists/__init__.py`

**See:** [`.ai/codebase-map.json`](../.ai/codebase-map.json) under `specialists/` for patterns.

### Working with Memory

Use Pydantic schemas from `brain/schemas.py`:
```python
from brain.schemas import MemoryMetadata, validate_metadata

metadata = MemoryMetadata(
    type="memory",
    timestamp=datetime.now(timezone.utc).isoformat(),
    importance=0.8,
    scope="user"
)
```

### Testing

```bash
# Unit tests
pytest tests/test_*.py

# Integration tests
pytest tests/test_integration.py

# Documentation tests
pytest tests/test_ai_documentation.py
```

**See:** [`.ai/TESTING.md`](../.ai/TESTING.md) for comprehensive testing strategy.

## Important Conventions

1. **Documentation Location:**
   - Human guides → `docs/*.rst`
   - Machine docs → `.ai/*.{md,json}`
   - API contracts → Pydantic schemas
   - Source context → `@ai-*` annotations

2. **Code Style:**
   - Google-style docstrings
   - Type hints everywhere
   - Use Pydantic for data models

3. **Git Workflow:**
   - Main branch: `trunk`
   - Feature branches: `feature/*`
   - Version tags: `v1.x.x`

## MCP Integration

Ada exposes an **MCP server** in `ada-mcp/` that provides:
- **Tools:** `ada_chat`, `ada_search_memory`, `ada_add_memory`, `ada_health`
- **Resources:** Documentation from `.ai/` folder exposed as MCP resources

When working with MCP code, reference:
- `ada-mcp/src/ada_mcp/server.py` - Main entry point
- `ada-mcp/src/ada_mcp/tools.py` - Tool definitions
- `ada-mcp/src/ada_mcp/resources.py` - Documentation resources

## Philosophy

Ada is:
- **Privacy-first** - Runs locally, no cloud dependencies
- **Hackable** - Simple code, well-documented patterns
- **Standards-based** - Uses MCP, OpenAPI, standard protocols
- **Accessible** - Works on CPU, optimizes for GPU

**See:** `docs/xenofeminism.rst` and `docs/documentation_philosophy.rst` for deeper context.

---

**For the most accurate, up-to-date context, always reference `.ai/` folder documentation first.**

This file serves as a pointer to that comprehensive machine-readable documentation rather than duplicating it.
