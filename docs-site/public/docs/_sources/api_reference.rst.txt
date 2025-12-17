=============
API Reference
=============

:autogen:`Brain API Endpoints`
===============================

.. automodule:: brain.app
   :members: healthz, chat, chat_stream, list_memory, create_memory, delete_memory, rag_debug
   :undoc-members:
   :show-inheritance:


:autogen:`Endpoint Discovery`
=============================

**The API is fully self-documenting!** Query these endpoints to discover available functionality:

**GET /v1/info** — System capabilities and complete endpoint list

.. code-block:: bash

   curl http://localhost:5000/api/info | jq

Returns:

- Service version and Python version
- Feature flags (RAG, specialists, streaming, etc.)
- Active models (LLM and embedding)
- Complete list of all available endpoints
- Documentation URL

**GET /v1/specialists** — Available specialist capabilities

.. code-block:: bash

   curl http://localhost:5000/api/specialists | jq

Returns specialist names, descriptions, schemas, priorities, and enabled status.

**GET /v1/schema** — Data model schemas

.. code-block:: bash

   curl http://localhost:5000/api/schema | jq

Returns JSON Schema definitions for all document types (persona, faq, memory, turn, summary).

See :doc:`data_model` for complete schema documentation.

Key Endpoints
=============

The following endpoints are commonly used. For the complete list, query **GET /v1/info**.

For specialist system endpoints, see :doc:`specialists`. For data model schemas, see :doc:`data_model`.

Chat & Streaming
----------------

**POST /v1/chat/stream** — Streaming chat via Server-Sent Events

See :doc:`streaming` for detailed SSE event structure.

Memory Management
-----------------

**GET /v1/memory** — Search and list memories

**POST /v1/memory** — Create new memory

**DELETE /v1/memory/{id}** — Delete memory

See :doc:`memory` for memory management patterns.

Health & Diagnostics
--------------------

**GET /v1/healthz** — Service health and dependency status

**GET /v1/debug/rag** — RAG system diagnostics (when RAG_DEBUG=true)

**GET /v1/debug/prompt** — Inspect prompt construction

See :doc:`configuration` for debug configuration and :doc:`testing` for testing strategies.


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
