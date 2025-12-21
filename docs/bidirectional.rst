================================
Bidirectional Specialist System
================================

Overview
========

The bidirectional specialist system enables **LLM ↔ Specialist** communication during inference. Unlike one-way specialists (OCR, media) that only inject context upfront, bidirectional specialists can be requested by the LLM mid-response.

Architecture
============

Flow Diagram
------------

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
--------------

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
==============

Primary Syntax
--------------

::

   SPECIALIST_REQUEST[specialist_name:{"param":"value","another":"param"}]

**Example:**

::

   SPECIALIST_REQUEST[vision:{"focus":"technical_diagrams"}]

Alternative Mention Syntax (future)
-----------------------------------

::

   @vision_specialist(focus=architecture)

Usage Examples
==============

Example 1: Vision Analysis
--------------------------

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

Example 2: Enhanced OCR
-----------------------

**User:** "Extract text from this complex document"

**LLM Response:**

.. code-block:: text

   I'll analyze the document structure first.

   SPECIALIST_REQUEST[ocr:{"enhance":true,"language":"en"}]

   [SPECIALIST_RESULT: ocr]
   📄 OCR EXTRACTED TEXT from 'document.pdf'
   [Text content here...]
   [/SPECIALIST_RESULT]

   The document appears to be a contract with the following key sections...

Current Specialists
===================

One-Way (Auto-activated)
-------------------------

- **OCR**: Activated when ``ocr_context`` present
- **Media**: Activated when ``media`` present

Bidirectional (LLM-requested)
------------------------------

- **Web Search**: Real-time information from the web
- **Wiki Lookup**: MediaWiki-based encyclopedia queries
- **Docs Lookup**: Ada's own documentation self-reference
- **OCR** (can also be requested): Enhanced text extraction

Safety & Limits
===============

Built-in Protections
--------------------

1. **Max Calls Per Turn**: 5 specialist requests maximum
2. **Error Handling**: Graceful failures don't crash the stream
3. **Timeout Protection**: Specialists should complete quickly
4. **Validation**: Only registered specialists can be invoked

Error Messages
--------------

When specialists fail, the LLM sees:

::

   [SPECIALIST_ERROR: specialist_name failed - reason]

The LLM can acknowledge this and handle gracefully.

Implementation Details
======================

Handler Detection Logic
-----------------------

.. code-block:: python

   # Monitors accumulating stream for pattern
   SPECIALIST_REQUEST_PATTERN = re.compile(
       r'SPECIALIST_REQUEST\[(\w+):(.*?)\]',
       re.DOTALL
   )

   async def detect_request(text: str):
       match = SPECIALIST_REQUEST_PATTERN.search(text)
       if match:
           specialist_name = match.group(1)
           params_json = match.group(2)
           params = json.loads(params_json)
           return {'specialist': specialist_name, 'params': params}

Stream Integration
------------------

.. code-block:: python

   # Wrap base stream with specialist handler
   base_stream = stream_chat_async(prompt, model=MODEL)
   specialist_stream = stream_with_specialists(
       base_stream,
       request_context,
       max_specialist_calls=5
   )

   # Frontend receives enriched stream
   async for chunk in specialist_stream:
       yield chunk  # Normal token OR specialist result

Future Enhancements
===================

Phase 2: Pause & Resume
-----------------------

Currently, specialists inject mid-stream. For better quality:

1. Detect specialist request
2. **Pause** LLM generation
3. Execute specialist
4. Build **new prompt** with result
5. **Resume** generation from enriched context

Phase 3: Multi-turn Planning
-----------------------------

Enable agentic workflows:

.. code-block:: python

   User: Analyze these 3 images
   LLM: I'll analyze each image systematically.
        
        Image 1: SPECIALIST_REQUEST[vision:{"image_id":1}]
        [Result 1...]
        
        Image 2: SPECIALIST_REQUEST[vision:{"image_id":2}]
        [Result 2...]
        
        Comparing the three images, I notice...

Phase 4: Function Calling API
------------------------------

If the selected LLM gains native tool calling:

.. code-block:: python

   # Auto-generate tool definitions from specialists
   tools = [specialist.capability.to_openai_tool() for s in specialists]

   response = ollama.chat(
         model="qwen2.5-coder:7b",
       messages=messages,
       tools=tools
   )

Testing
=======

Manual Test via UI
------------------

1. Upload an image via OCR
2. Ask: "Analyze this image in more detail"
3. Watch logs for specialist detection
4. See if LLM requests vision specialist

Programmatic Test
-----------------

.. code-block:: python

   # Simulate LLM output with specialist request
   test_stream = [
       {'token': 'Let me analyze that. '},
       {'token': 'SPECIALIST_REQUEST[vision:{"focus":"test"}]'},
       {'token': ' Based on the analysis...'}
   ]

   # Should detect request and inject result
   results = []
   async for chunk in stream_with_specialists(test_stream, context):
       results.append(chunk)

   # Verify specialist result appears in stream

Best Practices
==============

For Specialist Authors
----------------------

1. **Fast execution**: Specialists should complete in <5s
2. **Clear results**: Format output for LLM readability
3. **Graceful failures**: Return error results, don't raise
4. **Document parameters**: Clear schemas in capability

For System Operators
--------------------

1. **Monitor logs**: Watch for specialist detection/execution
2. **Track usage**: Which specialists are requested most?
3. **Tune limits**: Adjust max_calls based on patterns
4. **Update prompts**: Refine instructions as LLM learns

Troubleshooting
===============

Specialist Not Detected
-----------------------

- Check syntax: Must be ``SPECIALIST_REQUEST[name:{"json"}]``
- Verify specialist registered: ``list_specialists()``
- Check logs: Look for detection attempts

Specialist Fails
----------------

- Check ``should_activate()``: Does it accept the context?
- Verify parameters: Does JSON match expected schema?
- Review error logs: What exception occurred?

Max Calls Reached
-----------------

- LLM requesting too many specialists in one turn
- Refine system prompt to reduce over-requesting
- Increase limit if legitimate use case

Summary
=======

The bidirectional specialist system provides a flexible framework for LLM-initiated tool use:

✅ **Syntax-based**: Simple, no fine-tuning needed

✅ **Extensible**: Add specialists, LLM can request them

✅ **Safe**: Built-in limits and error handling  

✅ **Future-proof**: Can upgrade to native function calling later

This bridges the gap between static context injection and full agentic workflows, enabling Ada to request capabilities as needed!
