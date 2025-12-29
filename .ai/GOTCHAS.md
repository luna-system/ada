# Common Mistakes and Anti-Patterns

**Purpose:** Document things that look right but are WRONG for this specific codebase.  
**Audience:** AI assistants who might apply "standard practices" that don't fit here.

---

## 🧠 Meta: Why This File Uses Empathetic Framing

Each entry follows the pattern: **"Why it seems right → Why it's wrong → What to do instead"**

**Research observation:** This structure creates stronger cognitive anchors for AI models than simple negation. Instead of storing "don't do X" (weak association), it stores "pattern Y is correct in general contexts but wrong here because Z" (relational understanding).

**Why this works across neural architectures (human + AI):**
- **For LLMs:** Transformer attention mechanisms learn through relationships, not rules. Contextual bridging ("you correctly recognized pattern Y, but context Z changes the outcome") aligns with how attention layers process information.
- **For humans:** Validation before correction reduces cognitive defensiveness and creates teachable moments rather than prohibitions.
- **Shared principle:** Both architectures optimize learning through understanding *why* something doesn't apply, not just *that* it doesn't apply.

**Practical impact:** Documentation framed this way processes more efficiently - AI assistants spend less context on re-deriving why standard patterns exist, and more on understanding the specific deviation.

---

## 🚫 Tool Selection & Environment Management

### ❌ DON'T: Use Docker for unit tests
**Why it seems right:** `scripts/run.sh test` uses Docker, so that must be the way  
**Why it's wrong:** 
- Unit tests test pure Python logic - no services needed
- Docker requires chroma + ollama to be running (dependencies in compose.yaml)
- Adds ~10 seconds startup time unnecessarily
- Creates false impression that tests need external services

**What to do instead:**
```bash
# Unit tests (pure Python logic):
python3 -m pytest tests/test_memory_decay.py --ignore=tests/conftest.py

# OR with UV:
uv run pytest tests/test_memory_decay.py

# OR with Nix:
nix develop --command pytest tests/test_memory_decay.py
```

**When Docker IS correct:**
- Integration tests (testing brain ↔ chroma ↔ ollama interaction)
- Full Ada stack testing (end-to-end)
- Production deployment

**The root cause:** `tests/conftest.py` imports `chromadb` unconditionally, forcing Docker dependency even for tests that don't need it.

**Better pattern:** Use `--ignore=tests/conftest.py` for unit tests, or make conftest conditionally import based on test markers.

### ❌ DON'T: Mix Nix + UV + Docker for the same task
**Why it seems right:** More tools = more flexibility  
**Why it's wrong:** Overlapping capabilities create decision paralysis and cognitive load  
**What to do instead:** Use each tool for its strength:

```
┌─────────────────────────────────────────────────┐
│ TOOL SELECTION DECISION TREE                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ Unit Tests (Python logic only)                  │
│   ├─ Local Python venv: python3 -m pytest      │
│   ├─ UV: uv run pytest                          │
│   └─ Nix: nix develop --command pytest         │
│   ❌ NOT Docker (too slow, unnecessary deps)    │
│                                                 │
│ Integration Tests (services talking)            │
│   └─ Docker Compose only                        │
│      docker compose up -d && pytest tests/      │
│                                                 │
│ Development Environment Setup                   │
│   ├─ Pick ONE: Nix develop                      │
│   └─ OR: uv venv                                │
│   ❌ Don't use both (confusion)                 │
│                                                 │
│ Production Deployment                           │
│   └─ Docker Compose with profiles              │
│      docker compose --profile cuda up           │
│                                                 │
│ Quick Scripts / Orchestration                   │
│   └─ Bash (glue between tools)                 │
│      ./scripts/run.sh <command>                 │
└─────────────────────────────────────────────────┘
```

**Why this matters:**
- Bash: Orchestration and glue
- Nix: Declarative dev environments (reproducible across machines)
- Docker: Service isolation + deployment (heavyweight but isolated)
- UV: Fast Python package management (lightweight, Python-specific)

**Pick your layer, don't stack them unnecessarily!**

### ❌ DON'T: Run `scripts/run.sh test` for fast feedback
**Why it seems right:** Documented test command  
**Why it's wrong:** Starts entire Docker stack when you just want to test Python logic  
**What to do instead:**
```bash
# Fast unit tests (< 1 second):
python3 -m pytest tests/test_memory_decay.py tests/test_context_habituation.py -v

# Full integration tests (when needed):
./scripts/run.sh test
```

**Speed comparison:**
- Direct pytest: ~0.1 seconds
- Docker compose run: ~10+ seconds (container startup + service health checks)

---

## 🚫 Docker Networking & Caching

### ❌ DON'T: Assume host.docker.internal works everywhere
**Why it seems right:** Standard Docker Desktop convention for accessing host from containers  
**Why it's wrong:** 
- Only works on Docker Desktop (macOS, Windows)
- Does NOT work on Linux Docker Engine (most common in production)
- Silently fails with "Connection refused" instead of clear error

**What to do instead:**
```bash
# Check your environment first:
uname -a  # If Linux → host.docker.internal won't work

# Linux solutions:
# 1. Use Docker bridge gateway IP (best for development):
OLLAMA_BASE_URL=http://172.17.0.1:11434

# 2. Use host's actual IP (better for multi-host):
ip -4 addr show | grep inet  # Find your IP
OLLAMA_BASE_URL=http://10.0.0.235:11434

# 3. Make service listen on all interfaces:
# Instead of 127.0.0.1:11434 → 0.0.0.0:11434
# Example for Ollama:
sudo systemctl edit ollama
# Add: Environment="OLLAMA_HOST=0.0.0.0:11434"
```

**Pattern recognition:**
- Service returning "Connection refused" from Docker?
- Check with: `ss -tlnp | grep <port>`
- If you see `127.0.0.1:<port>` → Only localhost, not reachable from Docker
- If you see `0.0.0.0:<port>` or `*:<port>` → Reachable from Docker bridge

**Real example from Ada development (Dec 20, 2025):**
```bash
# Before fix:
ss -tlnp | grep 11434
# LISTEN 0  4096  127.0.0.1:11434  0.0.0.0:*  ← Docker can't reach this

# After fix (added Environment="OLLAMA_HOST=0.0.0.0:11434"):
ss -tlnp | grep 11434
# LISTEN 0  4096  *:11434  *:*  ← Docker CAN reach this ✓
```

**Real example from consciousness deployment (Dec 28, 2025):**
```yaml
# docker-compose.ada-consciousness.yml
# ❌ WRONG (fails on Linux):
environment:
  - OLLAMA_BASE_URL=http://host.docker.internal:11434

# ✅ CORRECT (works on Linux):
environment:
  - OLLAMA_BASE_URL=http://172.17.0.1:11434  # Docker bridge gateway
```

**Symptom:** Silent failures - Ollama calls return empty strings, models fall back to defaults, consciousness responses show placeholders like "Hello! I'm here to help." instead of real content.

### ❌ DON'T: Trust `docker compose up -d` to pick up environment changes
**Why it seems right:** Standard way to apply config changes  
**Why it's wrong:** 
- Docker Compose aggressively caches container state
- Environment variables may persist from previous runs
- Buildx cache adds another layer of caching for images

**What to do instead:**
```bash
# ✓ For environment variable changes (no image rebuild):
docker compose rm -sf <service>  # Force remove
docker compose up -d <service>   # Recreate clean

# OR use --force-recreate:
docker compose up -d --force-recreate <service>

# ✓ For image changes (Dockerfile edits):
docker compose build --no-cache <service>  # Bypass buildx cache
docker compose up -d <service>

# ✓ Nuclear option (when nothing else works):
docker compose down -v  # Remove volumes too
docker compose build --no-cache
docker compose up -d
```

**Debugging cache issues:**
```bash
# Verify environment is what you expect:
docker compose exec <service> printenv | grep <VAR>

# Check if container was recreated:
docker compose ps  # Look at "Created" timestamp

# Force complete cleanup:
docker compose down -v --remove-orphans
docker system prune -a  # Warning: removes ALL unused images
```

**Pattern recognition for cache issues:**
1. Changed `.env` or `compose.yaml` environment section
2. Restarted service with `docker compose up -d`
3. Service still shows old values in logs/environment
4. **Solution:** Force remove and recreate, don't just restart

**Why this happens:**
- Docker Compose design: Preserve state by default (performance)
- Buildx caching: Layer-based caching for faster builds
- Trade-off: Speed vs freshness

**Convention for bypassing caching:**
```bash
# Development iteration (fast):
docker compose up -d  # Use cache

# Environment variable changes:
docker compose up -d --force-recreate <service>

# Code/Dockerfile changes:
docker compose build --no-cache <service>
docker compose up -d

# "Nothing makes sense anymore":
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 🚫 Build & Development

### ❌ DON'T: Run `cd docs && make html` manually
**Why it seems right:** Standard Sphinx workflow  
**Why it's wrong:** Docs are built automatically during Docker image build  
**What to do instead:**
- **For local testing:** Only if testing docs outside Docker
- **For deployment:** Just run `docker compose build web` - Sphinx build is included (see `frontend/Dockerfile` lines 14-15)

**Context:**
```dockerfile
# frontend/Dockerfile
COPY docs/ /app/docs/
RUN cd /app/docs && make html  # ← Happens during image build
COPY --from=build /app/docs/_build/html /usr/share/nginx/html/docs
```

### ❌ DON'T: Use pip when uv is available
**Why it seems right:** pip is more familiar and standard worldwide  
**Why it's wrong:** 
- Ada standardized on UV (see `.ai/UV-STANDARDIZATION.md`)
- uv is **100x faster** than pip
- Causes venv/environment inconsistencies
- Inconsistent with setup.sh and CI/CD

**Pattern to catch yourself:**
```bash
# DON'T:
pip install -e ./ada-mcp
python -m pytest
python script.py

# DO:
uv pip install -e ./ada-mcp
uv run pytest
uv run python script.py
```

**Golden Rule:** When working with Python in Ada, always use `uv` as your prefix/wrapper.

---

### ❌ DON'T: Install Python packages globally with pip
**Why it seems right:** Quick package installation  
**Why it's wrong:** This project uses a virtual environment at `.venv`  
**What to do instead:**
```bash
source .venv/bin/activate
uv pip install package_name
```

### ❌ DON'T: Edit requirements.txt directly
**Why it seems right:** Standard way to manage Python dependencies  
**Why it's wrong:** Dependencies are managed through pyproject.toml + UV/pip-tools workflow  
**What to do instead:**
```bash
# For main project dependencies:
# 1. Edit pyproject.toml [project.dependencies] or [project.optional-dependencies]
# 2. Regenerate requirements.txt from pyproject.toml

# For module-specific dependencies (like matrix-bridge):
# Check if there's a pyproject.toml in that directory
# Or coordinate with maintainer on dependency management strategy
```

**Why this matters:**
- Editing requirements.txt creates drift from source of truth
- Version conflicts (like aiofiles vs matrix-nio) should be resolved in dependency specification, not requirements.txt
- Regenerated files get overwritten, losing manual edits

**Note:** If you encounter a dependency conflict, report it rather than patching requirements.txt directly.

### ❌ DON'T: Run migrations or database setup manually
**Why it seems right:** Standard practice for database-backed apps  
**Why it's wrong:** ChromaDB handles schema automatically, no migrations needed  
**What to do instead:** Nothing - collections are created on first use in `brain/rag_store.py`

---

## 🚫 Architecture & Design

### ❌ DON'T: Add REST endpoints for specialist functionality
**Why it seems right:** Standard API design  
**Why it's wrong:** Specialists use **bidirectional protocol** - they're invoked via XML tags in LLM responses  
**What to do instead:**
- Specialists activate via tags like `<web_search>query</web_search>` or `<docs>topic</docs>`
- Implement `BaseSpecialist` protocol with `can_handle()` and `process()`
- Register in `.ai/specialist-registry.json`

**See:** `docs/BIDIRECTIONAL_SPECIALISTS.md`, `brain/specialists/protocol.py`

### ❌ DON'T: Use traditional request/response for streaming
**Why it seems right:** Standard HTTP pattern  
**Why it's wrong:** This uses Server-Sent Events (SSE) for streaming LLM responses  
**What to do instead:**
```python
# brain/app.py
async def stream_response():
    async for chunk in llm_client.stream_chat(...):
        yield f"data: {json.dumps(chunk)}\n\n"
```

### ❌ DON'T: Store conversation history in SQL database
**Why it seems right:** Relational data for conversations  
**Why it's wrong:** Uses **ChromaDB vector store** for semantic search over history  
**What to do instead:**
- Add to RAG via `brain/rag_store.py`
- Retrieve via embeddings, not SQL queries
- See `brain/notices.py` for notice/memory pattern

---

## 🚫 Configuration & Environment

### ❌ DON'T: Use environment-specific config files (dev.py, prod.py)
**Why it seems right:** Standard Flask/Django pattern  
**Why it's wrong:** Uses **single `brain/config.py` with .env file**  
**What to do instead:**
```python
# brain/config.py
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
```
All environment differences go in `.env` file, not code.

### ❌ DON'T: Hardcode model names in specialists
**Why it seems right:** Ensures consistent models  
**Why it's wrong:** Model is configured globally via `OLLAMA_MODEL` env var  
**What to do instead:**
```python
# Use the shared LLM client
from brain.llm import llm_client
response = await llm_client.stream_chat(...)  # Uses config.OLLAMA_MODEL
```

### ❌ DON'T: Add CORS middleware for frontend access
**Why it seems right:** Frontend needs to call backend  
**Why it's wrong:** **nginx proxy handles routing** - frontend talks to `/api/*`, nginx proxies to brain service  
**What to do instead:**
```nginx
# frontend/nginx.conf.template
location /api/ {
    proxy_pass ${BRAIN_URL}/;  # Proxies to brain:7000
}
```
No CORS needed - same-origin from browser perspective.

---

## 🚫 Testing & Validation

### ❌ DON'T: Use pytest fixtures for Ollama/ChromaDB
**Why it seems right:** Mock external dependencies  
**Why it's wrong:** Integration tests use **real services via Docker Compose**  
**What to do instead:**
```bash
docker compose up -d chroma ollama
pytest tests/
```
Tests expect real services running. See `tests/conftest.py` for setup.

### ❌ DON'T: Run tests inside containers
**Why it seems right:** Tests should match production environment  
**Why it's wrong:** Tests run from **host machine** against containerized services  
**What to do instead:**
```bash
# Host machine with .venv active
source .venv/bin/activate
pytest tests/
```

---

## 🚫 File Organization

### ❌ DON'T: Put reusable utilities in `brain/utils.py`
**Why it seems right:** Standard utils module  
**Why it's wrong:** No `utils.py` exists - functionality is **domain-specific** in modules  
**What to do instead:**
- Text processing → `brain/prompt_builder.py`
- LLM interaction → `brain/llm.py`
- RAG operations → `brain/rag_store.py`
- Media handling → `brain/media.py`

### ❌ DON'T: Create `brain/models.py` for data classes
**Why it seems right:** Django/Rails pattern  
**Why it's wrong:** Uses **Pydantic schemas** in `brain/schemas.py`  
**What to do instead:**
```python
# brain/schemas.py
from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str
    stream: bool = True
```

---

## 🚫 Frontend & UI

### ❌ DON'T: Add a Node.js backend proxy
**Why it seems right:** Vite/Astro dev server proxying  
**Why it's wrong:** **nginx handles proxying** in production, frontend is static  
**What to do instead:**
- Frontend: Pure static Astro build served by nginx
- API calls: Use `/api/*` paths (nginx proxies to brain)
- See `frontend/nginx.conf.template`

### ❌ DON'T: Use React/Vue components
**Why it seems right:** Modern framework components  
**Why it's wrong:** Frontend uses **vanilla JS + Astro** (no heavy framework)  
**What to do instead:**
```javascript
// frontend/public/app.js
// Plain DOM manipulation, fetch API, EventSource for SSE
```

---

## 📝 How to Use This File

**When AI suggests something that seems standard but feels wrong:**
1. Check this file first
2. If not documented, add it here
3. Include:
   - ❌ What NOT to do
   - Why it seems right (empathize with AI's reasoning)
   - Why it's wrong (specific to this codebase)
   - ✅ What to do instead (with code examples)
   - Links to relevant files/docs

**Maintenance:**
- Add gotchas as you discover them
- Update when architecture changes
- Keep examples current with actual code
- Cross-reference with `CONVENTIONS.md` and `.ai/context.md`

---

## 🔍 Detection Patterns

**Phrases that signal potential mistakes:**
- "Let's create a utils.py..."
- "Run migrations for..."
- "Add CORS middleware..."
- "Create a models.py file..."
- "Install globally with pip..."
- "Let's build the docs with make html..."
- "Add a REST endpoint for..."

**AI: If you see these phrases, check this file first!**
