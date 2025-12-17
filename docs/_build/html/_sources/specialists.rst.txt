Specialist System
=================

The specialist plugin system provides extensible AI capabilities through a standardized interface. Drop a new ``*_specialist.py`` file into ``brain/specialists/`` and it's automatically discovered and integrated.

Overview
--------

Architecture
~~~~~~~~~~~~

**Core Components:**

1. **Protocol** (``protocol.py``): Defines the ``Specialist`` interface and base types
2. **Registry** (``__init__.py``): Auto-discovers and manages specialist plugins
3. **Specialists** (``*_specialist.py``): Individual capability modules

Data Flow
~~~~~~~~~

::

   User Request → Registry.execute_for_context() → Specialists (filtered by should_activate)
                                                 ↓
                                       Parallel execution
                                                 ↓
                                  Results sorted by priority
                                                 ↓
                                 prompt_builder injects contexts
                                                 ↓
                                       LLM receives enriched prompt

Creating a New Specialist
--------------------------

Step 1: Create the File
~~~~~~~~~~~~~~~~~~~~~~~~

Create ``brain/specialists/your_name_specialist.py``:

.. code-block:: python

   from .protocol import (
       BaseSpecialist,
       SpecialistCapability,
       SpecialistResult,
       SpecialistPriority
   )

   class YourSpecialist(BaseSpecialist):
       """Your specialist description."""
       
       def __init__(self):
           capability = SpecialistCapability(
               name="your_name",
               description="What your specialist does",
               version="1.0.0",
               context_priority=SpecialistPriority.MEDIUM,
               context_icon="🔧",
               tags=["tag1", "tag2"],
           )
           super().__init__(capability)
       
       def should_activate(self, request_context: dict) -> bool:
           """Return True if your specialist should process this request"""
           # Check request_context for relevant data
           return request_context.get('your_key') is not None
       
       async def process(self, **kwargs) -> SpecialistResult:
           """Execute your specialist logic"""
           your_data = kwargs.get('your_key')
           
           if not your_data:
               return self.error_result("Missing data", "missing_data")
           
           try:
               # Your processing logic here
               result_text = f"Processed: {your_data}"
               
               # Format for LLM
               context_text = self.format_context(
                   title="Your Specialist Output",
                   content=result_text,
                   metadata={'key': 'value'}
               )
               
               return self.success_result(
                   context_text=context_text,
                   data={'raw': your_data},
                   metadata={'processed': True}
               )
           
           except Exception as e:
               return self.error_result(f"Error: {e}", "processing_error")

Step 2: That's It!
~~~~~~~~~~~~~~~~~~

The registry automatically discovers your specialist on next startup. No registration code needed.

Discovering Available Specialists
----------------------------------

**The specialist system is self-documenting!** Query the introspection endpoint:

.. code-block:: bash

   curl http://localhost:5000/api/specialists | jq

**Returns for each specialist:**

- Name and description
- Icon (for UI display)
- Version
- Priority level (critical/high/medium/low)
- Enabled status
- Tags for categorization
- Input/output JSON schemas

**Example Response:**

.. code-block:: json

   {
     "specialists": [
       {
         "name": "web_search",
         "description": "Search the web for current information",
         "icon": "🔍",
         "version": "1.0.0",
         "priority": "high",
         "enabled": true,
         "tags": ["web", "search", "current-events"],
         "input_schema": {
           "type": "object",
           "properties": {
             "query": {"type": "string"}
           },
           "required": ["query"]
         }
       }
     ],
     "count": 3
   }

Currently Available Specialists
--------------------------------

As of this writing, Ada includes:

- **OCR** (📄) - Text extraction from images via Tesseract
- **Media** (🎧) - ListenBrainz music context integration  
- **Web Search** (🔍) - Real-time web search via SearxNG

Use **GET /v1/specialists** for the current list and their schemas.

Request Context Structure
-------------------------

When specialists execute, they receive a ``request_context`` dict:

.. code-block:: python

   {
       'prompt': str,              # User's message
       'conversation_id': str,     # Current conversation
       'entity': str | None,       # Optional entity filter
       'media': dict | None,       # ListenBrainz data
       'ocr_context': dict | None, # OCR extraction result
       'user_timestamp': str,      # Request timestamp
       # ... extensible
   }

Specialists check this context in ``should_activate()`` to determine if they're relevant.

Priority System
---------------

Controls injection order in the prompt:

=============  =====  ========================================
Priority       Value  Usage
=============  =====  ========================================
CRITICAL       0      System notices, identity
HIGH           10     User-provided context (OCR, vision)
MEDIUM         50     External data (media, APIs)
LOW            100    Supplementary info
=============  =====  ========================================

Lower numbers appear earlier in the prompt.

Advanced Topics
---------------

For detailed information on these advanced specialist features, see:

- :doc:`bidirectional` - Bidirectional specialist system (LLM ↔ Specialist communication)
- :doc:`web_search` - Web search specialist configuration and usage
- :doc:`specialist_rag` - RAG-based dynamic specialist documentation

Testing Specialists
-------------------

Test Discovery
~~~~~~~~~~~~~~

.. code-block:: python

   from brain.specialists import get_registry, list_specialists

   registry = get_registry()
   specialists = list_specialists()

   for s in specialists:
       print(f"{s.capability.name}: {s.capability.description}")

Test Execution
~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from brain.specialists import execute_specialists

   context = {'ocr_context': {'text': 'Hello'}}
   results = await execute_specialists(context)

   for r in results:
       print(f"{r.specialist_name}: {r.success}")

Future Enhancements
-------------------

Phase 2: Pause & Resume
~~~~~~~~~~~~~~~~~~~~~~~~

Currently, specialists inject mid-stream. For better quality:

1. Detect specialist request
2. **Pause** LLM generation
3. Execute specialist
4. Build **new prompt** with result
5. **Resume** generation from enriched context

Phase 3: Multi-turn Planning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable agentic workflows:

.. code-block:: text

   User: Analyze these 3 images
   LLM: I'll analyze each image systematically.
        
        Image 1: SPECIALIST_REQUEST[vision:{"image_id":1}]
        [Result 1...]
        
        Image 2: SPECIALIST_REQUEST[vision:{"image_id":2}]
        [Result 2...]
        
        Comparing the three images, I notice...

Phase 4: Function Calling API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If DeepSeek gains native tool calling:

.. code-block:: python

   # Auto-generate tool definitions from specialists
   tools = [specialist.capability.to_openai_tool() for s in specialists]

   response = ollama.chat(
       model="deepseek-r1",
       messages=messages,
       tools=tools
   )

Service-Based Specialists
~~~~~~~~~~~~~~~~~~~~~~~~~

For GPU-intensive models (Phi-3.5-Vision), the same protocol supports remote specialists:

.. code-block:: python

   class RemoteVisionSpecialist(BaseSpecialist):
       async def process(self, **kwargs):
           # Call separate service via HTTP/gRPC
           response = await http_client.post('http://vision-service:8080/analyze', ...)
           return self.success_result(...)

No changes to registry or prompt_builder needed!

Best Practices
--------------

1. **Single Responsibility:** Each specialist does one thing well
2. **Fail Gracefully:** Return error results, don't raise exceptions
3. **Metadata Rich:** Include useful metadata for debugging/logging
4. **Format Consistently:** Use ``format_context()`` for prompt injection
5. **Document Activation:** Clearly state when specialist activates
6. **Version Carefully:** Bump version on breaking changes

Debugging
---------

Check Synced FAQs
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # View all specialist FAQs
   docker exec ada-v1-brain-1 python -c "
   from brain.rag_store import RagStore
   store = RagStore()
   result = store.col.query(
       query_texts=['specialists'],
       n_results=10,
       where={'type': 'faq', 'topic': 'specialists'}
   )
   for doc in result['documents'][0]:
       print(doc)
       print('---')
   "

Test Retrieval
~~~~~~~~~~~~~~

Query the debug endpoint (if ``RAG_DEBUG=true``):

.. code-block:: bash

   curl "http://localhost:7000/v1/debug/prompt?prompt=analyze%20image&faq_k=5"

Resources
---------

- See :doc:`api_usage` for API integration details
- See :doc:`testing` for specialist testing patterns
- See :doc:`development` for adding new specialists
