# Testing Ada

## Quick Start End-to-End Test

**Test that the README actually works:**

```bash
./scripts/test_quickstart_e2e.sh
```

This script:
- Follows the README quick start instructions exactly
- Tests identity configuration (AI_NAME, AI_USER_NAME)
- Verifies all services start correctly
- Tests chat, specialists, and persona swapping
- Runs the full unit/integration test suite
- Cleans up when done (restores your `.env`)

**Perfect for:**
- Validating changes before committing
- Ensuring documentation stays accurate
- Testing on your laptop before pushing
- Reproducing CI failures locally

---

## Manual Testing for Markdown Rendering

The frontend is served via Docker Compose through an Nginx reverse proxy. Testing can be done locally or against the running services.

## Option 1: Using Docker Compose (Recommended)

```bash
cd /home/luna/Code/ada-v1
docker compose up
```

Then open the UI in your browser at `http://localhost:5000/`.

## Option 2: Local Development (FastAPI Brain Service)

If testing the FastAPI backend directly without Docker:

```bash
cd /home/luna/Code/ada-v1
source .venv/bin/activate
python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000
```

The API will be available at `http://localhost:7000/v1/*` with interactive docs at `http://localhost:7000/docs`.

## Testing Markdown Rendering

With the frontend running (via Docker Compose or local dev server):

1. Try these messages in the chat composer and submit (note: inline markdown is rendered; block-level markdown/code fences are rendered with syntax highlighting):
   - Hello **bold** text
   - _italic_ and **bold** together
   - A link: [OpenAI](https://openai.com)
   - Inline code: `const a = 1;`
   - Code block:

```js
function test() {
  return 42;
}
```

2. Verify:
   - Messages render with bold/italic/links/inline code formatting
   - Links open in a new tab and have `rel="noopener noreferrer"` set
   - Code fences (```...```) render with a monospace, sanitized `<pre><code>` block and basic syntax highlighting
   - The 'Thinking' bubble (if enabled) renders inline markdown similarly
   - If markdown does not render, check the small header status next to the brand for `marked:✓ DOMPurify:✓ hljs:✓` — these indicate the client-side libraries loaded successfully
   - If any are missing (✕), open DevTools console to see errors and clear browser cache (or refresh with Ctrl/Cmd+Shift+R)

3. Optional: Check that the chat input and memory list still work as before.

## Testing API Endpoints Directly

To test API endpoints without the frontend:

```bash
# Health check
curl http://localhost:7000/v1/healthz

# Get recent conversations
curl http://localhost:7000/v1/conversations/recent

# Query memory
curl "http://localhost:7000/v1/memory?query=example"

# Create a memory
curl -X POST http://localhost:7000/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Test memory", "memory_type": "important"}'

# Interactive API docs
# Open http://localhost:7000/docs in your browser
```

## Testing with Frontend Proxy

All API calls from the frontend go through the Nginx reverse proxy:

```bash
# Same endpoints available via proxy
curl http://localhost:5000/api/health
curl http://localhost:5000/api/conversations/recent

# Stream endpoint (SSE)
curl http://localhost:5000/api/chat/stream -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_id": "test"}'
```

The proxy remaps `/api/*` → `/v1/*` on the brain service with proper SSE handling.
