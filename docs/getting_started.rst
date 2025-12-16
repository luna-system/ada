===============
Getting Started
===============

Installation
============

Requirements
------------

- Python 3.13+
- Ollama (LLM backend)
- ChromaDB (Vector database)
- Docker Compose (optional, for containerized setup)

Setup
-----

1. **Clone and activate virtual environment:**

   .. code-block:: bash

      cd /home/luna/Code/ada-v1
      source .venv/bin/activate

2. **Start dependencies:**

   .. code-block:: bash

      docker compose up -d

   This starts:
   - Ollama LLM backend (port 11434)
   - ChromaDB vector store (port 8000)
   - Web server (port 5000)
   - Brain API (port 7000)

3. **Verify health:**

   .. code-block:: bash

      curl http://localhost:7000/v1/healthz

Configuration
=============

Environment Variables
---------------------

Copy `.env.example` to `.env` and configure:

.. code-block:: bash

   cp .env.example .env

Key variables:

- ``OLLAMA_BASE_URL`` - LLM backend URL (default: http://localhost:11434)
- ``OLLAMA_MODEL`` - Model name (default: deepseek-r1)
- ``CHROMA_URL`` - Vector DB URL (default: http://localhost:8000)
- ``RAG_ENABLED`` - Enable RAG features (default: true)
- ``RAG_ENABLE_PERSONA`` - Load persona/style guidelines (default: true)
- ``RAG_ENABLE_FAQ`` - Include FAQ retrieval (default: true)
- ``RAG_ENABLE_MEMORY`` - Include memory retrieval (default: true)
- ``RAG_ENABLE_SUMMARY`` - Auto-generate conversation summaries (default: true)
- ``RAG_DEBUG`` - Enable debug endpoints (default: false)

For complete configuration reference, see :doc:`configuration`.

.. tip::
   
   **Runtime Configuration Discovery:** Query **GET /v1/info** to see the current active configuration, enabled features, and models in use.

Running the Service
===================

Start Brain API
---------------

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   source .venv/bin/activate
   python brain/app.py

Or with Gunicorn (production):

.. code-block:: bash

   gunicorn -b 0.0.0.0:7000 brain.app:app

Start Web Server
----------------

.. code-block:: bash

   cd /home/luna/Code/ada-v1
   source .venv/bin/activate
   python webserver/app.py

Or with Gunicorn:

.. code-block:: bash

   gunicorn -b 0.0.0.0:5000 webserver.app:app

Using Docker Compose
--------------------

Start all services:

.. code-block:: bash

   docker compose up

Stop services:

.. code-block:: bash

   docker compose down

View logs:

.. code-block:: bash

   docker compose logs -f brain
   docker compose logs -f web

Your First Request
==================

Health Check
------------

.. code-block:: bash

   curl http://localhost:7000/v1/healthz

Response:

.. code-block:: json

   {
     "ok": true,
     "service": "brain",
     "python": "3.13.0",
     "config": {
       "OLLAMA_BASE_URL": "http://localhost:11434",
       "OLLAMA_MODEL": "deepseek-r1",
       ...
     },
     "persona": {"loaded": true},
     "chroma": {"ok": true}
   }

Simple Chat
-----------

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What is the capital of France?",
       "include_thinking": false
     }'

Response:

.. code-block:: json

   {
     "response": "The capital of France is Paris, located in northern France on the Seine River. It is the largest city in France and serves as the country's political, economic, and cultural center.",
     "thinking": null,
     "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
     "user_timestamp": "2025-12-13T10:30:45.123456+00:00",
     "assistant_timestamp": "2025-12-13T10:30:48.456789+00:00",
     "request_id": "abc12345",
     "used_context": {
       "persona": {"included": true, "version": null, "timestamp": null},
       "faqs": [],
       "turns": [],
       "memories": [],
       "summaries": [],
       "entity": null
     }
   }

Streaming Response
------------------

For real-time token delivery, see :doc:`streaming`.

Troubleshooting
===============

Service Won't Start
-------------------

**Issue:** ``Connection refused to Ollama``

**Solution:** 

1. Ensure Ollama is running:

   .. code-block:: bash

      docker ps | grep ollama

2. Check Ollama API:

   .. code-block:: bash

      curl http://localhost:11434/api/tags

3. If not running, start with Docker Compose:

   .. code-block:: bash

      docker compose up -d ollama

**Issue:** ``ChromaDB connection failed``

**Solution:**

1. Verify Chroma is running:

   .. code-block:: bash

      curl http://localhost:8000/api/v1/heartbeat

2. Restart if needed:

   .. code-block:: bash

      docker compose restart chroma

See :doc:`architecture` for details on the RAG infrastructure.

Health Check Failing
--------------------

**Issue:** ``GET /v1/healthz returns 503``

**Solution:**

The health check probes dependencies. Check which one is failing:

1. Ollama:

   .. code-block:: bash

      curl http://localhost:11434/api/tags

2. ChromaDB:

   .. code-block:: bash

      curl http://localhost:8000/api/v1/heartbeat

3. RAG system:

   .. code-block:: bash

      curl "http://localhost:7000/v1/debug/rag"

Memory Not Saving
-----------------

**Issue:** ``POST /v1/memory returns 503``

**Solution:**

Ensure RAG is enabled in `.env`:

.. code-block:: bash

   RAG_ENABLED=true
   CHROMA_URL=http://localhost:8000

Then restart Brain API. See :doc:`configuration` for complete RAG configuration options and :doc:`memory` for memory management patterns.

Debugging
=========

Enable Debug Mode
------------------

.. code-block:: bash

   # In .env
   RAG_DEBUG=true

Then restart services.

View Debug Info
---------------

.. code-block:: bash

   # Get RAG statistics
   curl "http://localhost:7000/v1/debug/rag?conversation_id=your-uuid"

View Logs
---------

With Docker:

.. code-block:: bash

   docker compose logs -f brain

Direct:

.. code-block:: bash

   # Set log level
   export LOG_LEVEL=DEBUG
   python brain/app.py

Check Imports
-------------

Verify all dependencies are installed:

.. code-block:: bash

   source .venv/bin/activate
   python -c "from brain.app import *; print('✓ All imports OK')"

Next Steps
==========

- :doc:`api_reference` - Complete endpoint documentation
- :doc:`streaming` - Real-time SSE streaming implementation
- :doc:`memory` - Long-term memory management
- :doc:`specialists` - Plugin system for extended capabilities
- :doc:`configuration` - Full configuration reference
- :doc:`testing` - Testing guide and best practices
- :doc:`examples` - Code examples in multiple languages
- See :doc:`streaming` for real-time response handling
- See :doc:`memory` for memory management
- See :doc:`examples` for code examples
