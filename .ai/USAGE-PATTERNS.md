# Using Ada - Multiple Paths to Success

Ada follows a "convenience layers + open access" philosophy. Choose your path based on your needs!

## Quick Reference

| Task | New User | Contributor | Power User |
|------|----------|-------------|------------|
| **Start Ada** | `ada run` | `docker compose up -d` | `uvicorn brain.app:app --reload` |
| **Run tests** | `ada test` | `uv run pytest tests/` | `pytest tests/test_specific.py -v --pdb` |
| **Development** | `ada dev` | `docker compose up` | `docker compose up brain --build` |
| **Health check** | `ada doctor` | `curl localhost:8000/v1/healthz` | `docker compose ps && ollama list` |
| **MCP server** | `ada mcp` | `ada-mcp/ada-mcp.sh` | `uv run --directory ada-mcp ada-mcp` |

## The Convenience Layer (`ada` command)

**When to use:** Quick tasks, learning, "just make it work"

```bash
# Health & setup
ada doctor          # Check if everything works
ada setup           # Initial setup wizard
ada status          # Service status

# Running
ada run             # Auto-detects best mode
ada dev             # Development mode with reload

# Development
ada test            # Run tests
ada mcp             # Start MCP server
ada introspect      # Self-analysis

# Interaction
ada chat "help me"  # One-shot questions
```

**Benefits:**
- ✅ Single obvious way (democratic!)
- ✅ Self-documenting (`ada --help`)
- ✅ Shows underlying commands (educational)
- ✅ Handles environment detection
- ✅ Nice error messages

## Direct Tool Access

**When to use:** Precise control, scripting, advanced features

### Docker Compose
```bash
# Full Docker orchestration
docker compose up -d                    # Start all services
docker compose up brain --build         # Rebuild brain
docker compose logs -f brain            # Follow logs
docker compose --profile web up         # Web UI profile
docker compose down -v                  # Clean shutdown
```

### UV Package Manager
```bash
# Dependency management
uv sync                                 # Install all dependencies
uv pip install <package>                # Add package
uv pip install -e .                     # Editable install
uv run pytest                           # Run with auto-venv
```

### Direct Services
```bash
# Brain API
uvicorn brain.app:app --reload          # Development
gunicorn -c brain/gunicorn_config.py    # Production

# MCP Server
cd ada-mcp && uv run ada-mcp            # Standard way
./ada-mcp/ada-mcp.sh                    # Wrapper script

# CLI Adapter
cd adapters/cli && uv run ada-cli "hi"  # Direct CLI
```

### Testing
```bash
# Pytest with full control
uv run pytest tests/                               # All tests
uv run pytest tests/test_memory.py -v              # Verbose
uv run pytest --ignore=tests/conftest.py           # Skip fixtures
uv run pytest tests/ --cov=brain --cov-report=html # Coverage
```

### Scripts
```bash
# Specialized maintenance
./scripts/run.sh health              # Health check
./scripts/run.sh migrate             # Database migration
./scripts/run.sh consolidate         # Memory consolidation
```

## Why Both Paths?

### The Ada Philosophy

> **"Add layers for convenience. Direct access remains open."**

This pattern appears throughout Ada's architecture:

**Specialists:**
- Convenience: Auto-activation based on context
- Direct: Explicit specialist invocation

**API:**
- Convenience: High-level `/v1/chat/stream` endpoint
- Direct: Individual LLM/RAG/specialist calls

**CLI:**
- Convenience: `ada run`, `ada test`
- Direct: `docker compose`, `uv run`

**Tools:**
- Convenience: Bidirectional (LLM requests tools)
- Direct: Programmatic tool invocation

### Different Users, Different Needs

**New users:** Want it to "just work"
- `ada run` and forget about Docker/Ollama details
- Clear error messages with solutions
- Progressive learning path

**Contributors:** Want to understand internals
- See what `ada test` actually runs
- Can drop down to direct commands
- Learn by exploration

**Power users:** Want maximum control
- Full Docker Compose options
- pytest flags and fixtures
- Custom orchestration

## Documentation Strategy

All Ada documentation shows **both paths**:

````markdown
# Quick Start (Recommended)
```bash
ada run
```

# Advanced: Manual Control
```bash
docker compose up -d ollama chroma
uvicorn brain.app:app --reload
```
````

This honors different user needs and skill levels.

## Self-Recursive Pattern

**Ada uses Ada to develop Ada:**

```bash
# During Ada development, we run:
ada test                    # Run Ada's tests
ada dev                     # Start Ada in dev mode
ada introspect              # Ada reads herself
ada doctor                  # Check Ada's health
```

This is the ultimate validation: if Ada's developers reach for `ada` commands, the convenience layer works!

## Integration Examples

### VS Code
Uses `ada-mcp/ada-mcp.sh` directly (wrapper script level, not `ada mcp`)

### CI/CD
```yaml
# Clarity in CI logs
- name: Run tests
  run: uv run pytest tests/
```

### User Scripts
```bash
# Use whatever makes sense
ada test || exit 1              # Convenience
uv run pytest -v || exit 1      # Direct
```

Both work! Choose based on context.

## The Meta-Level

This document follows the pattern it describes:

- **Convenience**: Read this high-level guide
- **Direct**: Explore `.ai/context.md`, source code

Both paths lead to understanding, at different speeds. ✨

---

**See also:**
- `.ai/DESIGN-PHILOSOPHY.md` - Why this pattern
- `.ai/CONVENIENCE-LAYER.md` - Implementation details
- `.ai/UV-STANDARDIZATION.md` - Package manager strategy
