=======
Memory
=======

The Brain API provides long-term memory storage and semantic retrieval to personalize responses.

Endpoints
---------

- **GET /v1/memory** — Search memories (semantic)
- **POST /v1/memory** — Create memory
- **DELETE /v1/memory/<id>** — Delete memory

Search Memories
---------------

.. code-block:: bash

   curl "http://localhost:7000/v1/memory?search=preferences&limit=5"

Query Parameters:

- ``search``: Semantic search query (required for retrieval)
- ``entity``: Optional entity/topic scope
- ``limit``: Max results (default 20, capped at 20)

Create Memory
-------------

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/memory \
     -H "Content-Type: application/json" \
     -d '{
       "text": "User prefers concise answers",
       "importance": 4,
       "scope": "global"
     }'

Fields:

- ``text`` (required): Memory text
- ``importance`` (1-5, default 3)
- ``scope`` (default ``global``)
- ``entity`` (optional): Topic/entity scope

Delete Memory
-------------

.. code-block:: bash

   curl -X DELETE http://localhost:7000/v1/memory/memory-id-here

Notes
-----

- RAG must be enabled (``RAG_ENABLED=true``) and Chroma reachable.
- Memories are retrieved semantically; include clear, concise facts.
- Entity scopes (``entity:project-x``) let you isolate context by topic.
- Memory saves from chat occur after completion of a turn/stream.
