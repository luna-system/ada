# Ada Tooling Guide

**Quick reference for which tool to use when**

## The Four Tools

```
bash ──> Shell scripting, orchestration, glue
nix  ──> Declarative environments (optional, for reproducibility)
uv   ──> Fast Python package management (optional, replaces pip)
docker -> Service isolation + deployment
```

## Decision Matrix

| Task | Tool | Command | Speed | Why |
|------|------|---------|-------|-----|
| **Run unit tests** | Local Python | `pytest tests/test_*.py` | < 1s | Pure logic, no services |
| **Run integration tests** | Docker | `docker compose up -d && pytest` | ~10s | Needs chroma + ollama |
| **Install Python package** | UV (fast) | `uv pip install <pkg>` | < 1s | Faster than pip |
| **Install Python package** | pip | `pip install <pkg>` | ~5s | Traditional method |
| **Enter dev environment** | Nix | `nix develop` | ~2s | Reproducible setup |
| **Start Ada stack** | Docker | `docker compose up` | ~30s | Full system |
| **Run utility script** | Bash | `./scripts/run.sh <cmd>` | Varies | Orchestration |

## Common Scenarios

### I want to test my code changes
```bash
# ✅ Fast unit tests (changed logic):
pytest tests/test_memory_decay.py -v

# ✅ Integration tests (changed API/services):
docker compose up -d
pytest tests/test_integration.py
```

### I want to add a dependency
```bash
# Add to pyproject.toml [project.dependencies]
# Then:
uv pip install -e .   # OR: pip install -e .
```

### I want a clean Python environment
```bash
# Option A - UV (fast, simple):
uv venv && uv pip install -e .

# Option B - Nix (reproducible, complex):
nix develop

# Option C - Traditional venv:
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
```

### I want to run Ada
```bash
# Full stack:
docker compose up

# With web UI:
docker compose --profile web up

# With GPU:
docker compose --profile cuda up
```

## Anti-Patterns

### ❌ Docker for unit tests
```bash
# DON'T:
docker compose run scripts pytest tests/test_memory_decay.py

# DO:
pytest tests/test_memory_decay.py
```
**Reason:** Unit tests don't need chroma/ollama. Docker adds 10+ seconds startup time.

### ❌ Mixing Nix + UV for same task
```bash
# DON'T:
nix develop
uv pip install <pkg>  # Confusing - which env?

# DO (pick one):
nix develop           # Nix manages everything
# OR
uv venv && uv pip install <pkg>  # UV manages Python
```

### ❌ Running services individually
```bash
# DON'T:
docker run -d chromadb/chroma
docker run -d ollama/ollama
# ...then try to connect them

# DO:
docker compose up  # Configured networking
```

## Tool Purposes (Non-Overlapping)

### Bash
- **Purpose:** Glue and orchestration
- **Use for:** Running commands, scripts, CI/CD workflows
- **Not for:** Environment management, package installation

### Nix
- **Purpose:** Declarative, reproducible dev environments
- **Use for:** Setting up development shell with exact versions
- **Not for:** Production deployment, quick tests
- **Status in Ada:** Optional (requires Nix installation)

### UV
- **Purpose:** Fast Python package management
- **Use for:** Installing packages, creating venvs quickly
- **Not for:** Non-Python dependencies, service orchestration
- **Status in Ada:** Optional (faster alternative to pip)

### Docker
- **Purpose:** Service isolation, deployment, integration testing
- **Use for:** Running Ada stack, integration tests, production
- **Not for:** Unit tests, quick iteration on Python code

## Quick Troubleshooting

### "ModuleNotFoundError: No module named 'chromadb'"
```bash
# You're running outside Ada's environment
# Fix: Use Docker OR install in local venv
docker compose run scripts pytest  # OR
pip install chromadb  # If testing locally
```

### "permission denied: /nix/var/nix/db/big-lock"
```bash
# Nix multi-user setup issue
# Workaround: Use UV or local venv instead
uv venv && uv pip install -e .
```

### "no such service: ollama"
```bash
# Ollama is in a profile, not started by default
# Fix: Add profile OR use external ollama
docker compose --profile ollama up  # OR
export OLLAMA_BASE_URL=http://external-ollama:11434
```

### Tests are slow
```bash
# Probably using Docker unnecessarily
# Fix: Run unit tests directly
pytest tests/test_*.py --ignore=tests/conftest.py
```

## Recommended Setup (Pick Your Style)

### Minimalist (pip + Docker)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
# Unit tests: pytest
# Integration: docker compose up
```

### Fast (UV + Docker)
```bash
uv venv
uv pip install -e .
# Unit tests: uv run pytest
# Integration: docker compose up
```

### Reproducible (Nix + Docker)
```bash
nix develop
# Unit tests: pytest
# Integration: docker compose up
```

## Summary

**One sentence per tool:**

- **Bash:** Run commands and orchestrate workflows
- **Nix:** Create reproducible dev environments (optional)
- **UV:** Install Python packages fast (optional, replaces pip)
- **Docker:** Run services and deploy Ada (required for integration tests)

**Golden rule:** Use the simplest tool that works for your task.

---

**See also:**
- `.ai/GOTCHAS.md` - Anti-patterns and mistakes
- `.ai/QUICKSTART.md` - Getting started with Ada
- `docs/development.rst` - Full development guide
