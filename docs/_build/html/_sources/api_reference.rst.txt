=============
API Reference
=============

Brain API Endpoints
===================

.. automodule:: brain.app
   :members: healthz, chat, chat_stream, list_memory, create_memory, delete_memory, rag_debug
   :undoc-members:
   :show-inheritance:


Endpoint Summary
================

Health & Monitoring
-------------------

**GET /v1/healthz** — Service health status and dependency info.

Status codes: 200 (healthy), 503 (dependency unavailable).

Chat Endpoints
--------------

**POST /v1/chat** — Non-streaming chat with RAG.

Status codes: 200 (ok), 400 (bad request), 500 (server error).

**POST /v1/chat/stream** — Streaming chat via SSE.

Status codes: 200 (stream), 400 (bad request), 500 (server error).

Memory Endpoints
----------------

**GET /v1/memory** — Semantic search over memories.

Query params: search, entity, limit.
Status codes: 200 (ok), 500 (query error).

**POST /v1/memory** — Create memory entry.

Status codes: 201 (created), 400 (bad request), 503 (RAG unavailable).

**DELETE /v1/memory/<mem_id>** — Delete memory entry.

Status codes: 200 (ok), 503 (RAG unavailable), 500 (delete error).

Debug Endpoint
--------------

**GET /v1/debug/rag** — RAG statistics (RAG_DEBUG=true).

Query params: conversation_id (optional).
Status codes: 200 (ok), 404 (debug disabled), 500 (error).


Request/Response Models
=======================

Chat Request
------------

.. code-block:: json

   {
     "prompt": "Your question here",
     "conversation_id": "uuid-optional",
     "include_thinking": false,
     "entity": "optional-topic",
     "save_memory": false,
     "memory_text": "optional-custom-text",
     "turns_k": 3,
     "faq_k": 3,
     "memory_k": 5
   }

Chat Response
-------------

.. code-block:: json

   {
     "response": "Assistant response text",
     "thinking": "Reasoning (if enabled)",
     "conversation_id": "uuid-here",
     "used_context": {
       "persona": {"included": true},
       "faqs": ["faq text snippets"],
       "turns": ["previous exchanges"],
       "memories": ["relevant memories"],
       "summaries": ["conversation summaries"],
       "entity": null
     },
     "user_timestamp": "2025-12-13T10:30:45.123456+00:00",
     "assistant_timestamp": "2025-12-13T10:30:48.456789+00:00",
     "request_id": "abc12345"
   }

Stream Events (SSE)
-------------------

Token Event:

.. code-block:: json

   {
     "type": "token",
     "content": "Hello "
   }

Thinking Event:

.. code-block:: json

   {
     "type": "thinking",
     "content": "The user is asking..."
   }

Done Event:

.. code-block:: json

   {
     "type": "done",
     "conversation_id": "uuid",
       "used_context": [],
       "user_timestamp": "2024-01-01T00:00:00Z",
       "assistant_timestamp": "2024-01-01T00:00:01Z",
       "request_id": "req-123"
   }

Error Event:

.. code-block:: json

   {
     "type": "error",
     "error": "Error message"
   }

Memory Request
--------------

.. code-block:: json

   {
     "text": "Memory content to store",
     "importance": 3,
     "scope": "global",
     "entity": "optional-topic"
   }

Memory Response
---------------

.. code-block:: json

   {
     "id": "memory-uuid",
     "text": "Memory content",
     "meta": {
       "importance": 3,
       "timestamp": "2025-12-13T10:30:45.123456+00:00",
       "source": "chat",
       "scope": "global",
       "entity": null
     }
   }

Status Codes
============

200 OK
   Request succeeded. Response in body.

201 Created
   Resource created successfully.

400 Bad Request
   Invalid parameters or missing required fields.

404 Not Found
   Endpoint not found or feature disabled.

500 Internal Server Error
   Server error (Ollama down, database error, etc).

503 Service Unavailable
   Critical dependency unavailable (RAG, database).

HTTP Status Code Reference
---------------------------

.. csv-table::
   :header: "Code", "Meaning", "Common Causes"
   :widths: 10, 20, 40

   "200", "Success", "Valid request processed"
   "201", "Created", "Memory created successfully"
   "400", "Bad Request", "Missing prompt, invalid JSON"
   "404", "Not Found", "Debug disabled (RAG_DEBUG=false)"
   "500", "Server Error", "Ollama timeout, DB error"
   "503", "Unavailable", "RAG disabled, Chroma down"
