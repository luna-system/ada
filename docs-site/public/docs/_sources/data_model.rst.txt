====================
Data Model Reference
====================

Ada stores all documents in a Chroma vector database with structured metadata schemas. This page documents the complete data model, including schemas, metadata fields, and usage patterns.

.. contents:: Contents
   :local:
   :depth: 2

--------
Overview
--------

Document Structure
==================

Every document in Ada's vector database has four components:

1. **ID**: Unique identifier (UUID format: ``doc-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx``)
2. **Text**: The actual content of the document (plain text)
3. **Embeddings**: 768-dimensional vector from ``nomic-embed-text`` model
4. **Metadata**: Structured fields describing the document (see schemas below)

Collection Organization
=======================

Ada uses a single Chroma collection named ``conversations`` that contains all document types. Documents are differentiated by their ``type`` metadata field.

Available document types:

- ``persona``: Identity and behavioral guidelines
- ``faq``: Knowledge base entries and specialist documentation
- ``memory``: Long-term facts and context
- ``turn``: Conversation history (user/assistant pairs)
- ``summary``: Conversation summaries

----------------------
Schema Introspection
----------------------

Live Schema API
===============

Ada provides a ``/v1/schema`` endpoint that returns JSON Schema definitions for all document types. This makes the data model fully introspectable at runtime.

**Get all schemas:**

.. code-block:: bash

   curl http://localhost:5000/api/schema

**Get specific schema:**

.. code-block:: bash

   curl http://localhost:5000/api/schema?doc_type=memory

**Response structure:**

.. code-block:: json

   {
     "document_type": "memory",
     "schema": { ... JSON Schema ... },
     "fields": ["type", "timestamp", "source", "scope", ...],
     "required_fields": ["type", "timestamp", "importance"]
   }

Python Schema Access
====================

Import Pydantic models directly for type-safe document creation:

.. code-block:: python

   from brain.schemas import (
       PersonaMetadata,
       FAQMetadata,
       MemoryMetadata,
       TurnMetadata,
       SummaryMetadata,
       validate_metadata,
       get_all_schemas,
   )
   
   # Validate metadata
   meta = {"type": "memory", "timestamp": "2025-12-16T06:00:00+00:00", "importance": 4}
   validated = validate_metadata("memory", meta)
   
   # Get JSON Schema
   schemas = get_all_schemas()
   memory_schema = schemas["memory"]

----------------
Document Schemas
----------------

Base Metadata (All Documents)
==============================

All documents share these common fields:

:type:
   :Type: ``string`` (enum)
   :Required: Yes
   :Values: ``persona``, ``faq``, ``memory``, ``turn``, ``summary``
   :Description: Document type identifier

:timestamp:
   :Type: ``string`` (ISO 8601 UTC)
   :Required: Yes
   :Example: ``2025-12-16T06:00:00+00:00``
   :Description: When document was created or last updated

:source:
   :Type: ``string``
   :Required: Yes
   :Default: ``system``
   :Values: ``chat``, ``kb``, ``system``, ``import``
   :Description: Origin of the document

:scope:
   :Type: ``string``
   :Required: Yes
   :Default: ``global``
   :Format: ``global`` or ``entity:<name>``
   :Description: Access scope for document retrieval
   :Example: ``entity:project-alpha`` for project-specific documents

Persona Documents
=================

**Purpose:** Define Ada's identity, tone, and behavioral guidelines.

**When used:** Loaded from ``persona.md`` on startup, retrieved when identity/tone questions arise.

**Metadata fields:**

:type:
   Fixed value: ``persona``

:version:
   :Type: ``string``
   :Required: Yes
   :Description: Version timestamp for persona updates
   :Example: ``2025-12-14T20:12:53.986582Z``

:topic:
   :Type: ``string`` (optional)
   :Description: Topic or section of persona if chunked
   :Examples: ``tone``, ``safety``, ``reasoning``

**Example document:**

.. code-block:: json

   {
     "id": "doc-abc123...",
     "document": "You are Ada, a helpful assistant...",
     "metadata": {
       "type": "persona",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "kb",
       "scope": "global",
       "version": "2025-12-14T20:12:53.986582Z",
       "topic": "tone"
     }
   }

**Query example:**

.. code-block:: python

   # Retrieve persona context for identity questions
   results = rag_store.col.query(
       query_texts=["What is my tone?"],
       where={"type": "persona"},
       n_results=2
   )

FAQ Documents
=============

**Purpose:** Knowledge base entries, specialist documentation, general reference.

**When used:** Retrieved via semantic similarity for relevant context.

**Metadata fields:**

:type:
   Fixed value: ``faq``

:topic:
   :Type: ``string`` (optional)
   :Description: Category for organization
   :Examples: ``specialists``, ``api``, ``configuration``, ``troubleshooting``

:specialist_name:
   :Type: ``string`` (optional)
   :Field name: ``_specialist_name`` (with underscore)
   :Description: Name of specialist this doc describes
   :Examples: ``web_search``, ``ocr``, ``vision``

:version:
   :Type: ``string`` (optional)
   :Field name: ``_version`` (with underscore)
   :Default: ``auto``
   :Description: Version of the FAQ entry

**Example documents:**

.. code-block:: json

   {
     "id": "doc-faq-001",
     "document": "Q: How do I use the web search specialist?\nA: Use SPECIALIST_REQUEST[web_search:{\"query\":\"...\"}]",
     "metadata": {
       "type": "faq",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "system",
       "scope": "global",
       "topic": "specialists",
       "_specialist_name": "web_search",
       "_version": "auto"
     }
   }

.. code-block:: json

   {
     "id": "doc-faq-002",
     "document": "Q: How do I configure RAG?\nA: Set RAG_ENABLED=true in .env...",
     "metadata": {
       "type": "faq",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "kb",
       "scope": "global",
       "topic": "configuration"
     }
   }

**Query example:**

.. code-block:: python

   # Retrieve FAQ entries about specialists
   results = rag_store.col.query(
       query_texts=["How do I invoke a specialist?"],
       where={"type": "faq", "topic": "specialists"},
       n_results=3
   )

Memory Documents
================

**Purpose:** Long-term facts and context that persist across conversations.

**When used:** Retrieved via semantic similarity, weighted by importance and recency.

**Metadata fields:**

:type:
   Fixed value: ``memory``

:importance:
   :Type: ``integer``
   :Required: Yes
   :Range: 1-5 (1=low, 5=critical)
   :Description: Importance level affecting retrieval ranking
   :Default: 3

:tags:
   :Type: ``array of strings`` (optional)
   :Description: Tags for categorization and filtering
   :Examples: ``["python", "preferences"]``, ``["project-alpha", "deadline"]``

:entity:
   :Type: ``string`` (optional)
   :Description: Entity this memory pertains to (extracted from scope)
   :Examples: ``project-alpha``, ``team-beta``

:conversation_id:
   :Type: ``string`` (optional)
   :Description: Original conversation where memory was created
   :Format: ``conv-<uuid>``

**Example documents:**

.. code-block:: json

   {
     "id": "doc-mem-001",
     "document": "luna prefers Python over JavaScript for backend development",
     "metadata": {
       "type": "memory",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "chat",
       "scope": "global",
       "importance": 4,
       "tags": ["preferences", "programming"]
     }
   }

.. code-block:: json

   {
     "id": "doc-mem-002",
     "document": "project-alpha deadline is December 20th, 2025",
     "metadata": {
       "type": "memory",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "chat",
       "scope": "entity:project-alpha",
       "entity": "project-alpha",
       "importance": 5,
       "tags": ["deadline", "critical"],
       "conversation_id": "conv-abc123"
     }
   }

**Query example:**

.. code-block:: python

   # Retrieve memories with entity scoping
   results = rag_store.retrieve_memories(
       query="project-alpha status",
       k=5,
       entity="project-alpha"  # Filter to entity-scoped memories
   )

Turn Documents
==============

**Purpose:** Conversation history (user messages and assistant responses).

**When used:** Retrieved for recent context in ongoing conversations.

**Metadata fields:**

:type:
   Fixed value: ``turn``

:conversation_id:
   :Type: ``string``
   :Required: Yes
   :Format: ``conv-<uuid>``
   :Description: Conversation this turn belongs to

:role:
   :Type: ``string``
   :Required: Yes
   :Values: ``user`` or ``assistant``
   :Description: Speaker role

:turn_index:
   :Type: ``integer`` (optional)
   :Description: Sequential turn number within conversation
   :Examples: ``1``, ``2``, ``3``

**Example documents:**

.. code-block:: json

   {
     "id": "doc-turn-001",
     "document": "How do I configure the web search specialist?",
     "metadata": {
       "type": "turn",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "chat",
       "scope": "global",
       "conversation_id": "conv-abc123",
       "role": "user",
       "turn_index": 1
     }
   }

.. code-block:: json

   {
     "id": "doc-turn-002",
     "document": "To configure web search, set SEARXNG_URL in your .env file...",
     "metadata": {
       "type": "turn",
       "timestamp": "2025-12-16T06:00:01+00:00",
       "source": "chat",
       "scope": "global",
       "conversation_id": "conv-abc123",
       "role": "assistant",
       "turn_index": 1
     }
   }

**Query example:**

.. code-block:: python

   # Retrieve recent turns from specific conversation
   results = rag_store.col.query(
       query_texts=["conversation context"],
       where={"type": "turn", "conversation_id": "conv-abc123"},
       n_results=10
   )

Summary Documents
=================

**Purpose:** Compressed summaries of conversation turns for efficient context.

**When used:** Generated periodically (every N turns) to maintain context efficiency.

**Metadata fields:**

:type:
   Fixed value: ``summary``

:conversation_id:
   :Type: ``string``
   :Required: Yes
   :Format: ``conv-<uuid>``
   :Description: Conversation this summary belongs to

:turn_range:
   :Type: ``string`` (optional)
   :Description: Range of turns covered by this summary
   :Format: ``<start>-<end>``
   :Examples: ``1-8``, ``9-16``

:summary_index:
   :Type: ``integer`` (optional)
   :Description: Sequential summary number within conversation
   :Examples: ``1``, ``2``, ``3``

**Example document:**

.. code-block:: json

   {
     "id": "doc-sum-001",
     "document": "Discussed web search configuration. User wants to set up SearxNG...",
     "metadata": {
       "type": "summary",
       "timestamp": "2025-12-16T06:08:00+00:00",
       "source": "system",
       "scope": "global",
       "conversation_id": "conv-abc123",
       "turn_range": "1-8",
       "summary_index": 1
     }
   }

**Query example:**

.. code-block:: python

   # Retrieve conversation summaries
   results = rag_store.col.query(
       query_texts=["web search configuration"],
       where={"type": "summary"},
       n_results=3
   )

--------------------
Retrieval Strategies
--------------------

Semantic Similarity
===================

All documents are retrieved via semantic similarity using the ``nomic-embed-text`` embedding model (768 dimensions).

.. code-block:: python

   # Basic semantic query
   results = rag_store.col.query(
       query_texts=["How do I use specialists?"],
       n_results=5
   )

Metadata Filtering
==================

Chroma supports filtering by metadata fields using ``where`` clauses:

.. code-block:: python

   # Filter by type
   where = {"type": "faq"}
   
   # Filter by multiple fields
   where = {"type": "memory", "importance": {"$gte": 4}}
   
   # Filter by scope
   where = {"scope": "entity:project-alpha"}
   
   # Complex filters
   where = {
       "$and": [
           {"type": "memory"},
           {"importance": {"$gte": 4}},
           {"tags": {"$contains": "critical"}}
       ]
   }

Importance-Weighted Retrieval
==============================

For memory documents, retrieval can be weighted by importance and recency:

.. code-block:: python

   # Memory retrieval with importance weighting
   memories = rag_store.retrieve_memories(
       query="project status",
       k=5,
       entity="project-alpha"  # Optional entity scoping
   )
   
   # Scoring formula:
   # score = (similarity * 0.5) + (importance * 0.5) + (recency_bonus)

Recency-Based Ranking
======================

Turn and summary documents use timestamp-based ranking for temporal awareness:

.. code-block:: python

   # Retrieve recent turns (automatically sorted by timestamp)
   recent_turns = rag_store.col.query(
       query_texts=["context"],
       where={
           "type": "turn",
           "conversation_id": conversation_id
       },
       n_results=RAG_TURN_TOP_K
   )

--------------
Usage Examples
--------------

Creating Documents
==================

**Persona:**

.. code-block:: python

   from brain.rag_store import RagStore
   
   rag_store = RagStore()
   rag_store.upsert_doc(
       text="You are Ada, a helpful assistant for luna.",
       type="persona",
       scope="global",
       timestamp="2025-12-16T06:00:00+00:00",
       source="kb",
       version="2025-12-16T06:00:00+00:00"
   )

**FAQ:**

.. code-block:: python

   rag_store.upsert_doc(
       text="Q: How do I use web search?\nA: Use SPECIALIST_REQUEST[web_search:...]",
       type="faq",
       scope="global",
       timestamp="2025-12-16T06:00:00+00:00",
       source="system",
       topic="specialists",
       _specialist_name="web_search"
   )

**Memory:**

.. code-block:: python

   rag_store.upsert_memory(
       text="luna prefers Python over JavaScript",
       scope="global",
       importance=4,
       tags=["preferences", "programming"],
       timestamp="2025-12-16T06:00:00+00:00",
       source="chat"
   )

**Turn:**

.. code-block:: python

   conversation_id = "conv-abc123"
   rag_store.upsert_turn(
       conversation_id=conversation_id,
       user_text="How do I configure web search?",
       assistant_text="Set SEARXNG_URL in .env...",
       user_ts="2025-12-16T06:00:00+00:00",
       assistant_ts="2025-12-16T06:00:01+00:00",
       source="chat"
   )

Querying Documents
==================

**Get persona context:**

.. code-block:: python

   persona_docs = rag_store.col.query(
       query_texts=["What is my tone?"],
       where={"type": "persona"},
       n_results=2
   )

**Search FAQs:**

.. code-block:: python

   faq_results = rag_store.col.query(
       query_texts=["specialist documentation"],
       where={"type": "faq", "topic": "specialists"},
       n_results=3
   )

**Retrieve memories:**

.. code-block:: python

   memories = rag_store.retrieve_memories(
       query="user preferences",
       k=5,
       entity=None  # Global scope
   )

**Get conversation history:**

.. code-block:: python

   turns = rag_store.col.query(
       query_texts=["recent discussion"],
       where={"type": "turn", "conversation_id": "conv-abc123"},
       n_results=10
   )

Validating Metadata
===================

Use Pydantic schemas for validation:

.. code-block:: python

   from brain.schemas import validate_metadata
   
   # Valid metadata
   meta = {
       "type": "memory",
       "timestamp": "2025-12-16T06:00:00+00:00",
       "source": "chat",
       "scope": "global",
       "importance": 4,
       "tags": ["test"]
   }
   validated = validate_metadata("memory", meta)
   
   # Invalid metadata (raises ValidationError)
   bad_meta = {
       "type": "memory",
       "importance": 10  # Out of range (1-5)
   }
   # Raises: ValidationError: importance must be between 1 and 5

--------------------
Configuration
--------------------

RAG-related configuration options (see :doc:`configuration` for full reference):

:RAG_ENABLED:
   Master toggle for RAG system (default: ``true``)

:RAG_ENABLE_PERSONA:
   Enable persona document retrieval (default: ``true``)

:RAG_ENABLE_FAQ:
   Enable FAQ document retrieval (default: ``true``)

:RAG_ENABLE_MEMORY:
   Enable memory document retrieval (default: ``true``)

:RAG_ENABLE_TURN:
   Enable turn document retrieval (default: ``true``)

:RAG_ENABLE_SUMMARY:
   Enable summary document retrieval (default: ``true``)

:RAG_TURN_TOP_K:
   Number of turns to retrieve (default: ``4``, range: 1-20)

:RAG_FAQ_TOP_K:
   Number of FAQs to retrieve (default: ``2``, range: 1-10)

:RAG_MEMORY_TOP_K:
   Number of memories to retrieve (default: ``3``, range: 1-20)

:RAG_SUMMARY_TOP_K:
   Number of summaries to retrieve (default: ``2``, range: 1-10)

See :doc:`configuration` for complete details on all RAG settings.

--------
See Also
--------

- :doc:`configuration` - Environment variable configuration
- :doc:`api_usage` - API usage and endpoints
- :doc:`memory` - Memory management and consolidation
- :doc:`architecture` - System architecture overview
- :doc:`testing` - Testing and validation
