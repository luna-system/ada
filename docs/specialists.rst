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

Bidirectional Specialists
--------------------------

Overview
~~~~~~~~

Bidirectional specialists enable **LLM ↔ Specialist** communication during inference. Unlike one-way specialists (OCR, media) that only inject context upfront, bidirectional specialists can be requested by the LLM mid-response.

Flow Diagram
~~~~~~~~~~~~

::

   User Message → Prompt Assembly (with upfront specialists)
                         ↓
                 LLM starts generating
                         ↓
            Streaming tokens to frontend
                         ↓
       [LLM emits SPECIALIST_REQUEST[...]]
                         ↓
          Handler detects request syntax
                         ↓
             Execute requested specialist
                         ↓
          Inject result back into stream
                         ↓
         LLM continues with new context

Key Components
~~~~~~~~~~~~~~

**1. Bidirectional Handler** (``brain/specialists/bidirectional.py``)

- Monitors streaming output for specialist requests
- Parses request syntax and parameters
- Executes specialists on-demand
- Injects results back into token stream
- Safety limits (max 5 calls per turn)

**2. System Prompt** (``brain/config.py``)

- Teaches LLM the specialist request syntax
- Documents available specialists
- Provides usage examples
- Sets expectations (results format, limits)

**3. Stream Wrapper** (``brain/app.py``)

- Wraps base LLM stream with specialist handler
- Passes request context for specialist execution
- Seamlessly integrates with existing SSE streaming

Request Syntax
~~~~~~~~~~~~~~

**Primary Syntax:**

::

   SPECIALIST_REQUEST[specialist_name:{"param":"value","another":"param"}]

**Example:**

::

   SPECIALIST_REQUEST[vision:{"focus":"technical_diagrams"}]

**Alternative Mention Syntax (future):**

::

   @vision_specialist(focus=architecture)

Usage Examples
~~~~~~~~~~~~~~

**Example 1: Vision Analysis**

**User:** "What's in this image?"

**LLM Response:**

.. code-block:: text

   Let me analyze the image in detail.

   SPECIALIST_REQUEST[vision:{"focus":"content_description"}]

   [SPECIALIST_RESULT: vision]
   👁️ VISUAL ANALYSIS from 'diagram.png'
   The image contains a system architecture diagram showing microservices...
   [/SPECIALIST_RESULT]

   Based on the visual analysis, this is a microservices architecture with...

**Example 2: Web Search**

**User:** "What happened in AI today?"

**LLM Response:**

.. code-block:: text

   SPECIALIST_REQUEST[web_search:{"query":"AI news today"}]

   [Results injected]

   Based on the search results, here's what's happening in AI today:
   - OpenAI released...
   - Google announced...

Safety & Limits
~~~~~~~~~~~~~~~

**Built-in Protections:**

1. **Max Calls Per Turn:** 5 specialist requests maximum
2. **Error Handling:** Graceful failures don't crash the stream
3. **Timeout Protection:** Specialists should complete quickly
4. **Validation:** Only registered specialists can be invoked

**Error Messages:**

When specialists fail, the LLM sees:

::

   [SPECIALIST_ERROR: specialist_name failed - reason]

The LLM can acknowledge this and handle gracefully.

Web Search Specialist
---------------------

Overview
~~~~~~~~

The web search specialist provides Ada with real-time access to current information via your self-hosted SearxNG instance at https://hunt.airsi.de.

Features
~~~~~~~~

- **Bidirectional only:** LLM must explicitly request search (not auto-activated)
- **SearxNG integration:** Privacy-respecting metasearch aggregating multiple sources
- **Context injection:** Search results formatted and injected into prompt
- **Rate limit aware:** Handles 429 errors gracefully

Configuration
~~~~~~~~~~~~~

Set in ``.env``:

.. code-block:: bash

   SEARXNG_URL=https://hunt.airsi.de

The specialist auto-discovers when ``SEARXNG_URL`` is set.

Usage Pattern
~~~~~~~~~~~~~

**LLM Detection:**

When Ada realizes she needs current information:

.. code-block:: text

   User: What's the weather in Portland today?
   Ada: I don't have access to real-time weather data in my training. 
        Let me search for current information.
        SPECIALIST_REQUEST[web_search:{"query":"Portland weather today"}]

**Specialist Execution (Pause/Resume):**

1. Generation **pauses** when request detected
2. Web search executes via SearxNG
3. Results formatted and injected into context
4. Generation **resumes** with enriched prompt

**Result Format:**

.. code-block:: text

   🔍 Web Search Results for 'Portland weather today':

   1. Portland Weather - National Weather Service
      URL: https://weather.gov/portland
      Partly cloudy with high of 55°F. Rain expected this evening...

   2. Weather.com - Portland, OR
      URL: https://weather.com/weather/today/l/Portland+OR
      Current conditions: 52°F, mostly cloudy. Chance of rain 60%...

Request Schema
~~~~~~~~~~~~~~

.. code-block:: python

   {
       "query": str,           # Search terms (required)
       "num_results": int      # Number of results (default: 5)
   }

Example Interactions
~~~~~~~~~~~~~~~~~~~~

**News Query:**

.. code-block:: text

   User: What happened in AI today?
   Ada: SPECIALIST_REQUEST[web_search:{"query":"AI news today"}]

   [Results injected]

   Based on the search results, here's what's happening in AI today:
   - OpenAI released...
   - Google announced...

**Fact Checking:**

.. code-block:: text

   User: Is Python 3.13 released yet?
   Ada: Let me check the latest information.
        SPECIALIST_REQUEST[web_search:{"query":"Python 3.13 release"}]

   [Results show release date]

   Yes! Python 3.13 was released on October 7, 2024...

RAG-Based Documentation
-----------------------

Overview
~~~~~~~~

Instead of using static specialist instructions in the system prompt, Ada uses **RAG-based dynamic documentation** that retrieves relevant specialist guidance based on the user's query context.

How It Works
~~~~~~~~~~~~

**1. Automatic Sync on Startup**

When the brain service starts:

.. code-block:: text

   [BRAIN] Discovered 2 specialists: 🎧 media, 📄 ocr
   [BRAIN] Synced 8 specialist FAQ entries to RAG

The system:

- Discovers all registered specialists via the plugin registry
- Generates FAQ entries from specialist capabilities
- Stores them in Chroma with ``type="faq"`` and ``topic="specialists"``
- Removes old entries to ensure idempotency

**2. Context-Aware Retrieval**

During prompt building (``build_prompt()`` in ``prompt_builder.py``):

- User's query is embedded
- RAG retrieves the top K most relevant specialist FAQs
- Retrieved docs are injected into the prompt before specialist execution
- This provides **just-in-time** specialist guidance instead of static instructions

**3. FAQ Entry Types**

The system generates multiple FAQ types:

**Overview FAQ:**

.. code-block:: text

   Q: What specialist capabilities are available?
   A: Ada has 2 specialist capabilities integrated: 🎧 media, 📄 ocr. 
      These can be invoked mid-conversation using SPECIALIST_REQUEST[name:{params}] syntax...

**Per-Specialist Capability FAQ:**

.. code-block:: text

   Q: What does the ocr specialist do?
   A: Extract text from images using Tesseract OCR (Priority: HIGH, Icon: 📄)

**Per-Specialist Syntax FAQ:**

.. code-block:: text

   Q: How do I invoke the ocr specialist?
   A: Use the syntax SPECIALIST_REQUEST[ocr:{}] in your response. I will detect this pattern, 
      pause generation, execute the specialist, and resume with enriched context.

Configuration
~~~~~~~~~~~~~

Enable/Disable RAG Docs:

.. code-block:: bash

   SPECIALIST_RAG_DOCS=true  # Use dynamic RAG retrieval (default)
   SPECIALIST_RAG_DOCS=false # Use static SPECIALIST_INSTRUCTIONS only

Set in ``brain/config.py``:

.. code-block:: python

   SPECIALIST_RAG_DOCS = os.getenv("SPECIALIST_RAG_DOCS", "true").lower() == "true"

Benefits
~~~~~~~~

1. **Context-Aware Guidance**

   - User asks "can you analyze this image?" → OCR/vision docs retrieved
   - User asks "what's playing?" → Media specialist docs retrieved
   - Irrelevant specialists don't clutter the prompt

2. **Automatic Updates**

   - Add a new specialist → FAQ entries auto-generated on next startup
   - Modify specialist capability → Updated in RAG automatically
   - No manual prompt engineering required

3. **Token Efficiency**

   - Static ``SPECIALIST_INSTRUCTIONS`` = ~300 tokens always present
   - Dynamic RAG retrieval = ~100-200 tokens only when relevant
   - Reduces prompt bloat for non-specialist queries

4. **Semantic Matching**

   - User query: "What can you see in this photo?"
   - RAG retrieves: OCR + vision specialist documentation
   - LLM learns specialist syntax contextually

Implementation Files
~~~~~~~~~~~~~~~~~~~~

- ``brain/specialists/specialist_docs.py`` - Generate and retrieve FAQ entries
- ``brain/app.py`` - Sync on startup
- ``brain/prompt_builder.py`` - Retrieve and inject relevant docs

Example Workflow
~~~~~~~~~~~~~~~~

**User Query:** "Can you read the text in this image?"

1. **Prompt Building Phase:**

   - Embed query: "Can you read the text in this image?"
   - RAG retrieves from ``type="faq", topic="specialists"``:
     - "How do I invoke the ocr specialist?"
     - "What does the ocr specialist do?"
   - Format and inject into prompt

2. **LLM Generation:**

   - Ada sees relevant OCR documentation in context
   - Generates: "I can extract the text using OCR. SPECIALIST_REQUEST[ocr:{}]"

3. **Specialist Execution (Pause/Resume):**

   - Generation pauses
   - OCR specialist extracts: "Annual Report 2024..."
   - Generation resumes with OCR result injected

4. **Final Response:**

   - "The image contains: Annual Report 2024..."

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
