API Usage Guide
===============

The Brain service is a pure **FastAPI** REST API service fully documented with docstrings and OpenAPI/Swagger specifications. The API handles LLM orchestration with retrieval-augmented generation (RAG).

Quick Start
-----------

This guide covers API usage patterns and integration. For setup instructions, see :doc:`getting_started`. For configuration options, see :doc:`configuration`.

Viewing API Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option 1: Interactive API Docs (Recommended)**

Start the service and open the interactive docs in your browser:

.. code-block:: bash

   cd /home/luna/Code/ada-v1

   # Option A: Docker Compose (all services)
   docker compose up
   # Then visit: http://localhost:7000/docs

   # Option B: Local development
   source .venv/bin/activate
   python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000
   # Then visit: http://localhost:7000/docs

The ``/docs`` endpoint provides:

- **Swagger UI** - Interactive endpoint testing
- **OpenAPI 3.0 schema** - Auto-generated from FastAPI decorators and type hints
- **Request/response examples** - With actual JSON schemas
- **Try it out** - Send real requests directly from the UI

**Option 2: Using pydoc (Built-in)**

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   python -m pydoc brain.app | less

**Option 3: VS Code Pylance Hover Tooltips**

Hover over any function/endpoint name in ``brain/app.py`` to see full documentation inline.

API Architecture
----------------

Framework
~~~~~~~~~

- **Framework:** FastAPI 0.109.0+
- **Server:** Gunicorn + Uvicorn workers (async ASGI)
- **Port:** 7000 (direct) / 5000 (via Nginx proxy)
- **Workers:** 25 Uvicorn workers (CPU × 2 + 1)
- **Timeout:** 300 seconds (for long LLM operations)

Base URL
~~~~~~~~

::

   Direct:  http://localhost:7000/v1
   Proxied: http://localhost:5000/api  (via Nginx, remapped to /v1)

Request/Response Format
~~~~~~~~~~~~~~~~~~~~~~~

- **Content-Type:** ``application/json``
- **Streaming:** Server-Sent Events (SSE) for ``/v1/chat/stream`` (see :doc:`streaming`)
- **Error Handling:** JSON with HTTP status codes and error messages

API Endpoints
-------------

All endpoints are fully documented in ``brain/app.py`` with docstrings. Below is a summary:

Health & Status
~~~~~~~~~~~~~~~

``GET /v1/healthz``

- **Purpose:** Service health check with dependency status
- **Returns:** JSON with service status, config, persona, Chroma connectivity
- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/healthz

Media Integration
~~~~~~~~~~~~~~~~~

``GET /v1/media/listenbrainz``

- **Purpose:** Get user's recent listening context from ListenBrainz
- **Returns:** User listening data or empty dict if not configured
- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/media/listenbrainz

Chat - Streaming (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``POST /v1/chat/stream``

- **Purpose:** Stream LLM responses token-by-token via Server-Sent Events (SSE)
- **Request Body:**

.. code-block:: json

   {
     "message": "Your question here",
     "conversation_id": "optional-id"
   }

- **Response:** Server-Sent Events stream (each line is a JSON event)
- **Events:**

  - ``data: {"token": "string"}`` - Streamed token
  - ``data: {"done": true}`` - Stream complete
  - ``data: {"error": "message"}`` - Error occurred

- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/chat/stream -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "conversation_id": "chat-1"}'

.. note::
   Nginx reverse proxy configured with ``proxy_buffering off`` for real-time SSE

Memory Management
~~~~~~~~~~~~~~~~~

**List Memories**

``GET /v1/memory?query=string&limit=10&conversation_id=id``

- **Purpose:** Search long-term memories with semantic query
- **Query Parameters:**

  - ``query`` (string, required): Search text
  - ``limit`` (int, optional): Max results (default: 10)
  - ``conversation_id`` (string, optional): Filter by conversation

- **Returns:** List of memory objects with embeddings and metadata
- **Example:**

.. code-block:: bash

   curl "http://localhost:7000/v1/memory?query=previous%20topic&limit=5"

**Create Memory**

``POST /v1/memory``

- **Purpose:** Create new long-term memory entry
- **Request Body:**

.. code-block:: json

   {
     "content": "Memory text",
     "memory_type": "important|context|fact",
     "conversation_id": "optional-conversation-id"
   }

- **Returns:** Memory object with ID, embeddings, metadata
- **Status:** 201 Created
- **Example:**

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/memory \
     -H "Content-Type: application/json" \
     -d '{"content": "User likes Python", "memory_type": "fact"}'

**Delete Memory**

``DELETE /v1/memory/{mem_id}``

- **Purpose:** Delete a specific memory entry
- **Path Parameter:** ``mem_id`` (string): Memory UUID
- **Returns:** Confirmation message
- **Example:**

.. code-block:: bash

   curl -X DELETE http://localhost:7000/v1/memory/abc-123-def

For detailed memory patterns and best practices, see :doc:`memory`. For memory schema definitions, see :doc:`data_model`.
Debug Endpoints
~~~~~~~~~~~~~~~

**RAG System Stats**

``GET /v1/debug/rag``

- **Purpose:** Get information about RAG system (Chroma vector DB)
- **Returns:** Database stats, indexed document count, embedding model info
- **Requires:** ``RAG_DEBUG=true`` environment variable
- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/debug/rag

**Assembled Prompt Debug**

``GET /v1/debug/prompt``

- **Purpose:** See the final prompt that will be sent to the LLM
- **Returns:** Full prompt text with context, persona, memory, etc.
- **Requires:** ``RAG_DEBUG=true`` environment variable
- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/debug/prompt

Conversation History
~~~~~~~~~~~~~~~~~~~~

**Recent Conversations**

``GET /v1/conversations/recent?limit=10``

- **Purpose:** Get list of recent conversations
- **Query Parameters:**

  - ``limit`` (int, optional): Max results (default: 10)

- **Returns:** List of conversation summaries
- **Example:**

.. code-block:: bash

   curl "http://localhost:7000/v1/conversations/recent?limit=5"

**Get Conversation Turns**

``GET /v1/conversations/{conversation_id}``

- **Purpose:** Get all turns (messages) in a specific conversation
- **Path Parameter:** ``conversation_id`` (string): Conversation UUID
- **Returns:** List of turns with timestamps, roles (user/assistant), content
- **Example:**

.. code-block:: bash

   curl http://localhost:7000/v1/conversations/chat-session-001

Quick Reference
---------------

Common Operations
~~~~~~~~~~~~~~~~~

Health Check
^^^^^^^^^^^^

.. code-block:: bash

   curl http://localhost:7000/v1/healthz

Streaming Chat
^^^^^^^^^^^^^^

.. code-block:: bash

   curl -N -X POST http://localhost:7000/v1/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!", "conversation_id": "chat-123"}'

Search Memories
^^^^^^^^^^^^^^^

.. code-block:: bash

   curl "http://localhost:7000/v1/memory?search=preferences&limit=5"

Add Memory
^^^^^^^^^^

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/memory \
     -H "Content-Type: application/json" \
     -d '{"text": "User prefers concise answers", "importance": 4}'

Response Status Codes
~~~~~~~~~~~~~~~~~~~~~

=========  ============  =============================================
Code       Endpoint      Meaning
=========  ============  =============================================
200        All           Success
201        /memory       Created
400        /chat*        Invalid parameters
404        /debug/*      Debug disabled
500        All           Server error (Ollama/DB issue)
503        /memory*      RAG not available
503        /healthz      Critical dependency unavailable
=========  ============  =============================================

Python Examples
~~~~~~~~~~~~~~~

Non-Streaming Request
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import requests

   response = requests.post(
       'http://localhost:7000/v1/chat',
       json={'prompt': 'Hello!', 'include_thinking': True}
   )
   data = response.json()
   print(data['response'])

Streaming Request
^^^^^^^^^^^^^^^^^

.. code-block:: python

   import requests
   import json

   response = requests.post(
       'http://localhost:7000/v1/chat/stream',
       json={'prompt': 'Hello!'},
       stream=True
   )
   
   for line in response.iter_lines():
       if line.startswith(b'data: '):
           event = json.loads(line[6:])
           if event['type'] == 'token':
               print(event['content'], end='', flush=True)

JavaScript Examples
~~~~~~~~~~~~~~~~~~~

Using Fetch + EventSource
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

   // Using EventSource (simpler)
   const es = new EventSource('/api/chat/stream');
   es.addEventListener('message', (e) => {
     const data = JSON.parse(e.data);
     if (data.type === 'token') {
       document.body.innerHTML += data.content;
     }
     if (data.type === 'done') es.close();
   });

Using Fetch + ReadableStream
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

   const res = await fetch('/api/chat/stream', {
     method: 'POST',
     body: JSON.stringify({prompt: 'Hello!'})
   });
   
   const reader = res.body.getReader();
   const decoder = new TextDecoder();
   let buffer = '';
   
   while (true) {
     const {done, value} = await reader.read();
     if (done) break;
     
     buffer += decoder.decode(value);
     const lines = buffer.split('\n');
     buffer = lines.pop();
     
     for (const line of lines) {
       if (line.startsWith('data: ')) {
         const data = JSON.parse(line.slice(6));
         if (data.type === 'token') {
           document.body.innerHTML += data.content;
         }
       }
     }
   }

Environment Variables
---------------------

Key environment variables affecting the API:

=========================  ==================================  ==================================================
Variable                   Default                             Description
=========================  ==================================  ==================================================
``OLLAMA_BASE_URL``        http://localhost:11434              LLM backend
``CHROMA_HOST``            http://chroma:8000                  Vector database
``PERSONA_FILE``           /app/persona.md                     Persona configuration
``RAG_DEBUG``              false                               Enable debug endpoints
``LISTENBRAINZ_USER``      -                                   ListenBrainz username
``LISTENBRAINZ_TOKEN``     -                                   ListenBrainz API token
``SEARXNG_URL``            -                                   Web search service URL
=========================  ==================================  ==================================================

Code Structure
--------------

Main Files
~~~~~~~~~~

- ``brain/app.py`` - Main FastAPI application (850+ lines)

  - All 10 endpoints with async handlers
  - Type hints throughout
  - Full docstrings for each endpoint
  - Lifespan context manager for startup/shutdown

Modular Components
~~~~~~~~~~~~~~~~~~

- ``brain/config.py`` - Configuration management (60 lines)
- ``brain/rag_store.py`` - RAG system integration (600+ lines)
- ``brain/llm.py`` - LLM provider interface (60 lines)
- ``brain/media.py`` - External media integration (100 lines)
- ``brain/prompt_builder/`` - Modular prompt assembly package:
  - ``context_retriever.py`` - RAG data retrieval (100 lines)
  - ``section_builder.py`` - Section formatting (150 lines)
  - ``prompt_assembler.py`` - Final assembly (150 lines)
  - Legacy ``build_prompt()`` available via package import

Type Hints & Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All endpoints use FastAPI type hints:

.. code-block:: python

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

This enables:

✅ Automatic request validation
✅ Type checking with Pylance
✅ Interactive API docs at ``/docs``
✅ OpenAPI 3.0 schema export

Error Handling
--------------

All errors return JSON with HTTP status codes:

.. code-block:: json

   {
     "detail": "Error message describing what went wrong"
   }

Common status codes:

- **200** - Success
- **201** - Created
- **400** - Bad request (invalid parameters)
- **404** - Not found
- **500** - Server error

Deployment
----------

Docker Compose (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   docker compose up

Services:

- **web** (port 5000): Nginx reverse proxy + static frontend
- **brain** (port 7000): FastAPI backend with Gunicorn + Uvicorn workers
- **chroma** (port 8000): Vector database
- **ollama** (port 11434): LLM inference server

Local Development
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   source .venv/bin/activate

   # Install dependencies
   uv sync

   # Run development server
   python -m uvicorn brain.app:app --host 0.0.0.0 --port 7000 --reload

The ``--reload`` flag auto-restarts on code changes.

Production Deployment
~~~~~~~~~~~~~~~~~~~~~

The ``brain/gunicorn_config.py`` file is configured for production:

.. code-block:: bash

   gunicorn -c brain/gunicorn_config.py brain.wsgi:app

Configuration:

- Uvicorn workers (ASGI)
- 25 worker processes
- 300-second timeout (for LLM calls)
- Access logging
- Graceful shutdown

Integration with Frontend
-------------------------

The Nginx reverse proxy (``frontend/nginx.conf.template``) maps:

::

   /api/*  →  http://brain:7000/v1/*

So frontend calls to ``http://localhost:5000/api/chat/stream`` are proxied to the backend at ``http://brain:7000/v1/chat/stream``.

Special handling:

- **SSE streaming:** ``proxy_buffering off`` for real-time events
- **Headers:** X-Forwarded-* headers preserved for logging

Adding New Endpoints
--------------------

When adding new routes, follow this template:

.. code-block:: python

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
       
       .. code-block:: bash
       
          curl http://localhost:7000/v1/new-endpoint?param1=value&param2=20
       
       Response:
       
       .. code-block:: json
       
          {"result": "value"}
       """
       try:
           # Your implementation
           return {"result": "value"}
       except ValueError as e:
           return JSONResponse(
               status_code=400,
               content={"detail": str(e)}
           )

The docstring will automatically appear in:

- FastAPI ``/docs`` (Swagger UI)
- ``python -m pydoc brain.app``
- VS Code Pylance tooltips

Resources
---------

- `FastAPI Documentation <https://fastapi.tiangolo.com/>`_
- `Uvicorn Documentation <https://www.uvicorn.org/>`_
- `OpenAPI 3.0 Specification <https://spec.openapis.org/oas/v3.0.0>`_
- `Server-Sent Events (SSE) <https://html.spec.whatwg.org/multipage/server-sent-events.html>`_
