# Scripts Tooling Container

## What Problem Does This Solve?

**Before**: Running utility scripts was error-prone
- ❌ Different Python versions on different machines
- ❌ Missing dependencies
- ❌ Can't reach Docker services (chroma, ollama)
- ❌ Import errors (brain/rag modules not found)
- ❌ Environment variable mismatches
- ❌ "Works on my machine" syndrome

**After**: Consistent, containerized execution
- ✅ Same Python 3.13 environment everywhere
- ✅ All dependencies from requirements.txt installed
- ✅ Network access to all Docker services
- ✅ Proper PYTHONPATH for imports
- ✅ Shared environment variables
- ✅ Works the same for everyone

## Quick Start

```bash
# Run health check
./scripts/run.sh health

# Run tests
./scripts/run.sh test

# Start interactive Python shell
./scripts/run.sh shell

# See all commands
./scripts/run.sh
```

## How It Works

1. **Dockerfile** (`scripts/Dockerfile`): Builds container with all dependencies
2. **Compose Service** (`compose.yaml`): Defines `scripts` service with profile `tools`
3. **Run Script** (`scripts/run.sh`): Convenience wrapper for common commands

## Architecture

```
scripts/
├── Dockerfile           # Container definition
├── run.sh              # Convenience wrapper
├── README.md           # Full documentation
├── QUICKSTART.md       # This file
├── health_check_chroma.py
├── test_prompt_interface.py
├── migrate_chroma_http.py
└── ... other scripts ...
```

The container:
- Based on Python 3.13-slim
- Installs all dependencies from requirements.txt
- Copies brain module for imports
- Mounts scripts/ directory for live updates
- Has network access to chroma, ollama, etc.
- Shares environment variables with other services

## Common Development Patterns

### Similar Tools in Other Ecosystems

- **Rails**: `docker compose run --rm web bin/rails console`
- **Django**: `docker compose run --rm web python manage.py shell`
- **Node.js**: `docker compose run --rm node npm test`
- **Kubernetes**: Init containers for migrations/setup

This is a well-established pattern for containerized development!

### When to Use This

✅ **Use the scripts container for**:
- Running health checks
- Running tests
- Database migrations
- Data imports/exports
- One-off maintenance tasks
- Interactive debugging

❌ **Don't use for**:
- Running the main application (use `brain` service)
- Anything that needs to stay running (use a regular service)

## Examples

### Pre-Deployment Check
```bash
#!/bin/bash
./scripts/run.sh health || exit 1
./scripts/run.sh test || exit 1
docker compose up -d
```

### CI/CD Integration
```yaml
# .gitlab-ci.yml
test:
  script:
    - docker compose run --rm scripts python /app/scripts/test_prompt_interface.py
```

### Interactive Debugging
```bash
./scripts/run.sh shell

# Then in Python:
>>> from rag_store import RagStore
>>> store = RagStore()
>>> results = store.retrieve_memories("test", k=5)
>>> print(results)
```

### Adding New Scripts

1. Create `scripts/my_script.py`
2. Import what you need:
   ```python
   from rag_store import RagStore
   from brain.config import Config
   ```
3. Run it:
   ```bash
   ./scripts/run.sh my_script.py
   # or
   docker compose run --rm scripts python /app/scripts/my_script.py
   ```

No rebuild needed! Scripts are mounted as volumes.

## Benefits

### For Developers
- No need to manage virtualenvs
- No "works on my machine" issues
- Easy to run any script consistently
- Same environment locally and in CI/CD

### For Operations
- Pre-deployment health checks
- Database maintenance tasks
- Data migrations
- Automated monitoring scripts

### For Everyone
- Single source of truth for dependencies
- Easy onboarding (just `./scripts/run.sh`)
- Consistent across team
- Works on any machine with Docker

## Testing

We use **pytest** for testing. Tests are in the `tests/` directory:

```bash
# Run all tests
./scripts/run.sh test

# Run specific test file
docker compose run --rm scripts pytest tests/test_rag.py

# Run with pattern matching
docker compose run --rm scripts pytest -k "memory"

# Verbose output
docker compose run --rm scripts pytest -vv
```

**Test structure:**
- `tests/conftest.py` - Shared fixtures (rag_store, conversation_id)
- `tests/test_rag.py` - RAG retrieval tests
- `tests/test_prompt_builder.py` - Prompt building tests
- `tests/test_specialists.py` - Specialist system tests

**Adding new tests:**
```python
# tests/test_my_feature.py
def test_my_feature(rag_store):
    """Test description."""
    result = my_feature(rag_store)
    assert result == expected
```

## See Also

- [scripts/README.md](README.md) - Full documentation
- [TESTING.md](../TESTING.md) - Testing infrastructure
- [compose.yaml](../compose.yaml) - Service definition
