# Ada Scripts & Tooling Container

This directory contains utility scripts for Ada's maintenance, debugging, testing, and operations.

## Tooling Container

All scripts should be run via the dedicated `scripts` Docker service, which provides:
- Consistent Python environment (same as brain service)
- All dependencies pre-installed
- Network access to chroma, ollama, etc.
- Proper module imports (brain, rag modules available)

### Usage Pattern

#### Quick Way (Recommended)

```bash
# Use the convenience wrapper
./scripts/run.sh health          # Run health check
./scripts/run.sh test            # Run test suite
./scripts/run.sh migrate         # Run migration (with confirmation)
./scripts/run.sh consolidate     # Run consolidation
./scripts/run.sh shell           # Interactive Python shell
./scripts/run.sh bash            # Bash shell in container
./scripts/run.sh my_script.py    # Run custom script
```

#### Direct Way (Full Control)

```bash
# Run any script directly
docker compose run --rm scripts python /app/scripts/<script_name>.py

# Examples
docker compose run --rm scripts python /app/scripts/health_check_chroma.py
docker compose run --rm scripts python /app/scripts/test_prompt_interface.py
docker compose run --rm scripts python /app/scripts/migrate_chroma_http.py
```

### Why Use the Scripts Container?

**Problem**: Running scripts directly on host causes issues:
- ❌ Different Python versions
- ❌ Missing dependencies
- ❌ Can't reach Docker services (chroma, ollama)
- ❌ Import errors (can't find brain/rag modules)
- ❌ Environment variable mismatches

**Solution**: Scripts container provides:
- ✅ Same Python 3.13 as brain
- ✅ All dependencies from requirements.txt
- ✅ Network access via Docker Compose
- ✅ Clean imports with PYTHONPATH set
- ✅ Consistent environment variables

## Available Scripts

### Health & Testing

#### Pytest Test Suite
Modern test suite using pytest with fixtures and better reporting.

```bash
# Run all tests
./scripts/run.sh test
# Or directly:
docker compose run --rm scripts pytest

# Run specific test file
docker compose run --rm scripts pytest tests/test_rag.py

# Run with more verbosity
docker compose run --rm scripts pytest -vv

# Run only tests matching a pattern
docker compose run --rm scripts pytest -k "memory"

# Skip slow tests
docker compose run --rm scripts pytest -m "not slow"
```

**Test files:**
- `tests/test_rag.py` - RAG store retrieval tests
- `tests/test_prompt_builder.py` - Prompt building tests
- `tests/test_specialists.py` - Specialist system tests

#### `health_check_chroma.py`
Comprehensive health check for Chroma database and RAG system (operational tool, not a test).

```bash
docker compose run --rm scripts python /app/scripts/health_check_chroma.py
```

**Checks**:
- Chroma server connectivity
- Collection existence and document count
- Embedding generation
- Memory/FAQ/turn query functionality
- Specialist docs retrieval
- Query consistency
- Persona loading

**Exit codes**: 0 (healthy), 1 (unhealthy)

#### `test_prompt_interface.py`
Unit/integration tests for prompt building and RAG retrieval.

```bash
docker compose run --rm scripts python /app/scripts/test_prompt_interface.py
```

**Tests**:
- RAG store initialization
- Memory retrieval
- FAQ retrieval
- Turn retrieval
- Prompt building
- Specialist docs retrieval
- Embedding generation
- Query consistency

**Exit codes**: 0 (all pass), 1 (any fail)

### Data Management

#### `migrate_chroma_http.py`
Migrate Chroma collection to HTTP-compatible format with fresh embeddings.

```bash
docker compose run --rm scripts python /app/scripts/migrate_chroma_http.py
```

**What it does**:
- Backs up existing collection
- Deletes old collection
- Creates fresh collection
- Re-generates embeddings for all documents
- Verifies query functionality

**When to use**:
- After upgrading Chroma
- When queries return unexpected results
- When switching from embedded to HTTP mode

#### `import_faq.py`
Import FAQs from JSONL file into Chroma.

```bash
docker compose run --rm scripts python /app/scripts/import_faq.py
```

#### `import_turns_csv.py`
Import conversation turns from CSV into Chroma.

```bash
docker compose run --rm scripts python /app/scripts/import_turns_csv.py
```

#### `load_persona.py`
Load persona from markdown file into Chroma.

```bash
docker compose run --rm scripts python /app/scripts/load_persona.py
```

#### `consolidate_memories.py`
Run nightly memory consolidation (creates daily/weekly summaries).

```bash
docker compose run --rm scripts python /app/scripts/consolidate_memories.py
```

**Note**: This runs automatically via `memory-consolidation` service at 02:00 UTC.

### Backup Management

#### `upload_backups_b2.py`
Upload Chroma backups to Backblaze B2.

```bash
docker compose run --rm scripts python /app/scripts/upload_backups_b2.py
```

**Note**: This runs automatically via `sqlite-backup` service hourly.

## Development Patterns

### Running Tests in CI/CD

```yaml
# .gitlab-ci.yml / .github/workflows/test.yml
test:
  script:
    - docker compose run --rm scripts python /app/scripts/test_prompt_interface.py
    - docker compose run --rm scripts python /app/scripts/health_check_chroma.py
```

### Pre-Deployment Health Check

```bash
#!/bin/bash
# pre-deploy.sh
docker compose run --rm scripts python /app/scripts/health_check_chroma.py
if [ $? -eq 0 ]; then
  echo "Health check passed, proceeding with deployment"
  docker compose up -d
else
  echo "Health check failed, aborting deployment"
  exit 1
fi
```

### Interactive Debugging

```bash
# Start an interactive Python session with all dependencies
docker compose run --rm scripts python

# Then in Python:
>>> from rag.store import RagStore
>>> store = RagStore()
>>> results = store.retrieve_memories("test query", k=5)
>>> print(results)
```

### Adding New Scripts

1. Create script in `scripts/` directory
2. Import brain/rag modules as needed:
   ```python
   from rag.store import RagStore
   from brain.config import Config
   ```
3. Run via scripts container:
   ```bash
   docker compose run --rm scripts python /app/scripts/new_script.py
   ```

No rebuild needed! Scripts are mounted as volumes.

## Troubleshooting

### Script not found
```
docker compose run --rm scripts python /app/scripts/my_script.py
# Error: No such file
```

**Solution**: Check that script exists in `scripts/` directory. Path should be `/app/scripts/`, not `./scripts/`.

### Import errors
```
ModuleNotFoundError: No module named 'brain'
```

**Solution**: Use the scripts container, not host Python. The PYTHONPATH is set correctly in the container.

### Can't reach Chroma/Ollama
```
httpx.ConnectError: [Errno 111] Connection refused
```

**Solution**: 
1. Ensure services are running: `docker compose ps`
2. Use service names (chroma, ollama), not localhost
3. Check environment variables: `CHROMA_URL=http://chroma:8000`

### Permission errors
```
PermissionError: [Errno 13] Permission denied
```

**Solution**: Scripts are mounted read-write. Check file permissions on host or run with appropriate user.

## Architecture

The scripts service is defined in `compose.yaml` with:

- **Base**: `scripts/Dockerfile` (Python 3.13-slim)
- **Profile**: `tools` (not started by default)
- **Dependencies**: brain, rag, scripts directories mounted
- **Environment**: Same as brain service
- **Network**: Can reach chroma, ollama by service name
- **No ports**: Not a server, just a runner

This pattern is similar to:
- Rails: `docker compose run --rm web bin/rails console`
- Django: `docker compose run --rm web python manage.py shell`
- Node.js: `docker compose run --rm node npm run test`

## Best Practices

1. **Always use scripts container**: Consistent environment
2. **Exit codes matter**: Scripts should return 0 (success) or 1 (failure)
3. **Log to stdout**: Docker captures logs automatically
4. **Handle errors gracefully**: Use try/except, print clear error messages
5. **Document usage**: Add script to this README with description
6. **Test in container**: Don't rely on host Python working

## See Also

- [TESTING.md](../TESTING.md): Comprehensive testing documentation
- [API_DOCUMENTATION.md](../API_DOCUMENTATION.md): API reference
- [README.md](../README.md): Main project documentation
