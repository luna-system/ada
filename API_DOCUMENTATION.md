# Ada v1 API Documentation

The Brain service is a pure **FastAPI** REST API service fully documented with docstrings and OpenAPI/Swagger specifications. The API handles LLM orchestration with retrieval-augmented generation (RAG).

## Quick Start

### Viewing API Documentation

**Option 1: Interactive API Docs (Recommended)**

Start the service and open the interactive docs in your browser:

```bash
cd /home/luna/Code/ada-v1

# Option A: Docker Compose (all services)
docker compose up
# Then visit: http://localhost:7000/docs

# Option B: Local development
source .venv/bin/activate
python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000
# Then visit: http://localhost:7000/docs
```

The `/docs` endpoint provides:
- **Swagger UI** - Interactive endpoint testing
- **OpenAPI 3.0 schema** - Auto-generated from FastAPI decorators and type hints
- **Request/response examples** - With actual JSON schemas
- **Try it out** - Send real requests directly from the UI

**Option 2: Using pydoc (Built-in)**

```bash
cd /home/luna/Code/ada-v1
python -m pydoc brain.app | less
```

**Option 3: VS Code Pylance Hover Tooltips**

Hover over any function/endpoint name in `brain/app.py` to see full documentation inline.

## API Architecture

### Framework

- **Framework:** FastAPI 0.109.0+
- **Server:** Gunicorn + Uvicorn workers (async ASGI)
- **Port:** 7000 (direct) / 5000 (via Nginx proxy)
- **Workers:** 25 Uvicorn workers (CPU × 2 + 1)
- **Timeout:** 300 seconds (for long LLM operations)

### Base URL

```
Direct:  http://localhost:7000/v1
Proxied: http://localhost:5000/api  (via Nginx, remapped to /v1)
```

### Request/Response Format

- **Content-Type:** `application/json`
- **Streaming:** Server-Sent Events (SSE) for `/v1/chat/stream`
- **Error Handling:** JSON with HTTP status codes and error messages

## API Endpoints

All endpoints are fully documented in `brain/app.py` with docstrings. Below is a summary:

### Health & Status

```
GET /v1/healthz
```
- **Purpose:** Service health check with dependency status
- **Returns:** JSON with service status, config, persona, Chroma connectivity
- **Example:**
  ```bash
  curl http://localhost:7000/v1/healthz
  ```

### Media Integration

```
GET /v1/media/listenbrainz
```
- **Purpose:** Get user's recent listening context from ListenBrainz
- **Returns:** User listening data or empty dict if not configured
- **Example:**
  ```bash
  curl http://localhost:7000/v1/media/listenbrainz
  ```

### Chat - Streaming (Recommended)

```
POST /v1/chat/stream
```
- **Purpose:** Stream LLM responses token-by-token via Server-Sent Events (SSE)
- **Request Body:**
  ```json
  {
    "message": "Your question here",
    "conversation_id": "optional-id"
  }
  ```
- **Response:** Server-Sent Events stream (each line is a JSON event)
- **Events:**
  - `data: {"token": "string"}` - Streamed token
  - `data: {"done": true}` - Stream complete
  - `data: {"error": "message"}` - Error occurred
- **Example:**
  ```bash
  curl http://localhost:7000/v1/chat/stream -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello", "conversation_id": "chat-1"}'
  ```
- **Note:** Nginx reverse proxy configured with `proxy_buffering off` for real-time SSE

### Memory Management

**List Memories**
```
GET /v1/memory?query=string&limit=10&conversation_id=id
```
- **Purpose:** Search long-term memories with semantic query
- **Query Parameters:**
  - `query` (string, required): Search text
  - `limit` (int, optional): Max results (default: 10)
  - `conversation_id` (string, optional): Filter by conversation
- **Returns:** List of memory objects with embeddings and metadata
- **Example:**
  ```bash
  curl "http://localhost:7000/v1/memory?query=previous%20topic&limit=5"
  ```

**Create Memory**
```
POST /v1/memory
```
- **Purpose:** Create new long-term memory entry
- **Request Body:**
  ```json
  {
    "content": "Memory text",
    "memory_type": "important|context|fact",
    "conversation_id": "optional-conversation-id"
  }
  ```
- **Returns:** Memory object with ID, embeddings, metadata
- **Status:** 201 Created
- **Example:**
  ```bash
  curl -X POST http://localhost:7000/v1/memory \
    -H "Content-Type: application/json" \
    -d '{"content": "User likes Python", "memory_type": "fact"}'
  ```

**Delete Memory**
```
DELETE /v1/memory/{mem_id}
```
- **Purpose:** Delete a specific memory entry
- **Path Parameter:** `mem_id` (string): Memory UUID
- **Returns:** Confirmation message
- **Example:**
  ```bash
  curl -X DELETE http://localhost:7000/v1/memory/abc-123-def
  ```

### Debug Endpoints

**RAG System Stats**
```
GET /v1/debug/rag
```
- **Purpose:** Get information about RAG system (Chroma vector DB)
- **Returns:** Database stats, indexed document count, embedding model info
- **Requires:** `RAG_DEBUG=true` environment variable
- **Example:**
  ```bash
  curl http://localhost:7000/v1/debug/rag
  ```

**Assembled Prompt Debug**
```
GET /v1/debug/prompt
```
- **Purpose:** See the final prompt that will be sent to the LLM
- **Returns:** Full prompt text with context, persona, memory, etc.
- **Requires:** `RAG_DEBUG=true` environment variable
- **Example:**
  ```bash
  curl http://localhost:7000/v1/debug/prompt
  ```

### Conversation History

**Recent Conversations**
```
GET /v1/conversations/recent?limit=10
```
- **Purpose:** Get list of recent conversations
- **Query Parameters:**
  - `limit` (int, optional): Max results (default: 10)
- **Returns:** List of conversation summaries
- **Example:**
  ```bash
  curl "http://localhost:7000/v1/conversations/recent?limit=5"
  ```

**Get Conversation Turns**
```
GET /v1/conversations/{conversation_id}
```
- **Purpose:** Get all turns (messages) in a specific conversation
- **Path Parameter:** `conversation_id` (string): Conversation UUID
- **Returns:** List of turns with timestamps, roles (user/assistant), content
- **Example:**
  ```bash
  curl http://localhost:7000/v1/conversations/chat-session-001
  ```

## Code Structure

### Main Files

- **brain/app.py** - Main FastAPI application (850 lines)
  - All 10 endpoints with async handlers
  - Type hints throughout
  - Full docstrings for each endpoint
  - Lifespan context manager for startup/shutdown

### Modular Components

- **brain/config.py** - Configuration management (60 lines)
  - Environment variables
  - Service URLs and settings

- **brain/rag_store.py** - RAG system integration (600 lines)
  - Chroma vector database interface
  - Semantic search over memories
  - Embedding generation

- **brain/llm.py** - LLM provider interface (60 lines)
  - Ollama API client
  - Token streaming

- **brain/media.py** - External media integration (100 lines)
  - ListenBrainz API client
  - User listening context

- **brain/prompt_builder.py** - Prompt assembly (150 lines)
  - System prompt construction
  - Context window management
  - RAG result formatting

## Type Hints & Documentation

All endpoints use FastAPI type hints:

```python
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse

@app.get('/v1/memory')
async def list_memory(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(10, description="Max results"),
) -> dict:
    """
    Search long-term memories with semantic query.
    
    Full docstring with details...
    """
```

This enables:
- ✅ Automatic request validation
- ✅ Type checking with Pylance
- ✅ Interactive API docs at `/docs`
- ✅ OpenAPI 3.0 schema export

## Error Handling

All errors return JSON with HTTP status codes:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common status codes:
- **200** - Success
- **201** - Created
- **400** - Bad request (invalid parameters)
- **404** - Not found
- **500** - Server error

## Deployment

### Docker Compose (Recommended)

```bash
cd /home/luna/Code/ada-v1
docker compose up
```

Services:
- **web** (port 5000): Nginx reverse proxy + static frontend
- **brain** (port 7000): FastAPI backend with Gunicorn + Uvicorn workers
- **chroma** (port 8000): Vector database
- **ollama** (port 11434): LLM inference server

### Local Development

```bash
cd /home/luna/Code/ada-v1
source .venv/bin/activate

# Install dependencies
uv sync

# Run development server
python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000 --reload
```

The `--reload` flag auto-restarts on code changes.

### Production Deployment

The `brain/gunicorn_config.py` file is configured for production:

```bash
gunicorn -c brain/gunicorn_config.py brain.wsgi:app
```

Configuration:
- Uvicorn workers (ASGI)
- 25 worker processes
- 300-second timeout (for LLM calls)
- Access logging
- Graceful shutdown

## Environment Variables

Required (in `.env`):
- `OLLAMA_BASE_URL` - Ollama API endpoint (e.g., `http://localhost:11434`)
- `CHROMA_HOST` - Chroma database host (e.g., `http://chroma:8000`)
- `PERSONA_FILE` - Path to persona configuration

Optional:
- `RAG_DEBUG=true` - Enable debug endpoints
- `LISTENBRAINZ_USER` - ListenBrainz username for media integration
- `LISTENBRAINZ_TOKEN` - ListenBrainz API token

## Integration with Frontend

The Nginx reverse proxy (`frontend/nginx.conf.template`) maps:

```
/api/*  →  http://brain:7000/v1/*
```

So frontend calls to `http://localhost:5000/api/chat/stream` are proxied to the backend at `http://brain:7000/v1/chat/stream`.

Special handling:
- **SSE streaming:** `proxy_buffering off` for real-time events
- **Headers:** X-Forwarded-* headers preserved for logging

## Adding New Endpoints

When adding new routes, follow this template:

```python
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

@app.get('/v1/new-endpoint', tags=['category'])
async def new_endpoint(
    param1: str = Query(..., description="Parameter description"),
    param2: int = Query(default=10, description="Optional param"),
) -> dict:
    """
    Brief one-line description.
    
    Longer explanation of what this endpoint does and when to use it.
    
    **Parameters:**
    - param1 (str): Required parameter
    - param2 (int): Optional parameter (default: 10)
    
    **Returns:**
    - dict with keys: result_key1, result_key2
    
    **Raises:**
    - ValueError: If param1 is empty
    
    **Example:**
    ```
    curl http://localhost:7000/v1/new-endpoint?param1=value&param2=20
    {"result": "value"}
    ```
    """
    try:
        # Your implementation
        return {"result": "value"}
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )
```

The docstring will automatically appear in:
- FastAPI `/docs` (Swagger UI)
- `python -m pydoc brain.app`
- VS Code Pylance tooltips

## Testing API Endpoints

### Using curl

```bash
# Simple GET
curl http://localhost:7000/v1/healthz

# GET with query parameters
curl "http://localhost:7000/v1/memory?query=test&limit=5"

# POST with JSON body
curl -X POST http://localhost:7000/v1/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Test", "memory_type": "fact"}'

# Stream response (SSE)
curl -N http://localhost:7000/v1/chat/stream -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Using Python

```python
import httpx

async with httpx.AsyncClient() as client:
    # Streaming
    async with client.stream('POST', 'http://localhost:7000/v1/chat/stream',
                            json={"message": "Hello"}) as response:
        async for line in response.aiter_lines():
            print(line)
```

### Using FastAPI's Interactive Docs

Open http://localhost:7000/docs in your browser to:
- See all endpoints
- Read full documentation
- Test endpoints with the "Try it out" button
- View request/response examples
- Export OpenAPI schema

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [Server-Sent Events (SSE)](https://html.spec.whatwg.org/multipage/server-sent-events.html)
