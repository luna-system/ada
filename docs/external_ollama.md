# Using External Ollama

Ada's dockerized Ollama service is now **optional**! You can use an existing Ollama installation to avoid duplicating large models.

## Quick Start

### Option 1: Use Dockerized Ollama (Default)

```bash
# Just start normally - ollama service included by default
docker compose up
```

Models stored in: `./data/ollama/`

### Option 2: Use Existing Ollama Installation

**Step 1:** Edit `.env` file:

```bash
# Change this line:
OLLAMA_BASE_URL=http://ollama:11434

# To point to your existing Ollama:
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Step 2:** Start Ada WITHOUT the ollama service:

```bash
# Method A: Explicitly exclude ollama profile
docker compose --profile web up

# Method B: Set empty profiles (cleaner)
COMPOSE_PROFILES="" docker compose up

# Method C: Override in .env
echo 'COMPOSE_PROFILES=""' >> .env
docker compose up
```

**Step 3:** Make sure your Ollama has the required models:

```bash
# Check existing models
ollama list

# Pull required models if needed
ollama pull deepseek-r1:14b
ollama pull nomic-embed-text
```

## Benefits of External Ollama

✅ **No Model Duplication** - Use models already pulled  
✅ **Shared Models** - Multiple projects can use same Ollama  
✅ **Faster Startup** - No need to pull models in Docker  
✅ **Easier Updates** - Update Ollama independently  

## Important: Shell Environment Variables

**Docker Compose priority:** Shell environment > .env file > compose.yaml defaults

If you have `OLLAMA_BASE_URL` set in your shell environment (e.g., in `~/.bashrc` or `~/.zshrc`), it will OVERRIDE the `.env` file!

**Check your shell environment:**
```bash
echo $OLLAMA_BASE_URL
# If this shows a value, it's overriding your .env
```

**Solution:** Unset the variable or export the new value:
```bash
# Option A: Unset it (use .env value)
unset OLLAMA_BASE_URL

# Option B: Export new value
export OLLAMA_BASE_URL=http://host.docker.internal:11434

# Then start
docker compose up
```

## Troubleshooting

### "Connection refused" errors

Make sure `host.docker.internal` resolves (it should on Docker Desktop automatically).

If using Linux without Docker Desktop:

```bash
# Add to compose.yaml's brain service:
extra_hosts:
  - "host.docker.internal:172.17.0.1"  # Docker bridge IP
```

Or use the host's actual IP:

```bash
OLLAMA_BASE_URL=http://192.168.1.100:11434  # Your machine's IP
```

### Check Ollama is accessible

From inside the brain container:

```bash
docker compose exec brain curl http://host.docker.internal:11434/api/tags
```

Should return JSON with your models.

## Configuration Reference

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `deepseek-r1:14b` | Main LLM model |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model for RAG |
| `COMPOSE_PROFILES` | (unset) | Set to `""` to disable ollama service |

## Example Setups

### Local Development (Shared Ollama)

```bash
# .env
OLLAMA_BASE_URL=http://host.docker.internal:11434
COMPOSE_PROFILES=""
```

### Production (Dockerized Ollama)

```bash
# .env
OLLAMA_BASE_URL=http://ollama:11434
# COMPOSE_PROFILES not set (default includes ollama)
```

### GPU Server (External Ollama)

```bash
# .env
OLLAMA_BASE_URL=http://gpu-server.local:11434
COMPOSE_PROFILES=""
```

## Migration

### From Dockerized to External

1. Note your current model in `.env` (e.g., `deepseek-r1:14b`)
2. Pull that model in your external Ollama: `ollama pull deepseek-r1:14b`
3. Update `OLLAMA_BASE_URL` in `.env`
4. Set `COMPOSE_PROFILES=""` in `.env`
5. Restart: `docker compose down && docker compose up`

### From External to Dockerized

1. Remove `COMPOSE_PROFILES=""` from `.env`
2. Set `OLLAMA_BASE_URL=http://ollama:11434` in `.env`
3. Restart: `docker compose down && docker compose up`
4. Wait for `ollama-init` to pull models (shown in logs)

---

**Note:** The `extra_hosts` configuration in `compose.yaml` already includes `host.docker.internal` mapping, so it should "just work" on most systems!
