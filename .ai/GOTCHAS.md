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

### ❌ DON'T: Install Python packages globally with pip
**Why it seems right:** Quick package installation  
**Why it's wrong:** This project uses a virtual environment at `.venv`  
**What to do instead:**
```bash
source .venv/bin/activate
pip install package_name
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
