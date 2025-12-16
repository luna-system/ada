.. Ada Brain API documentation master file

==================
Ada Brain API Docs
==================

Welcome to the Ada Brain API documentation. This is the REST API backend for the conversational LLM system with Retrieval-Augmented Generation (RAG).

.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   getting_started
   getting_started_scratch
   configuration
   hardware
   sbc
   architecture
   data_model
   api_usage
   api_reference
   specialists
   build_specialist
   bidirectional
   specialist_rag
   web_search
   testing
   development
   streaming
   memory
   documentation_philosophy
   empathetic_documentation
   examples
   xenofeminism


Overview
--------

The Brain API provides endpoints for:

- **Chat with RAG** - Generate responses with context from persona, FAQ, memories, and conversation history
- **Streaming** - Real-time token delivery via Server-Sent Events (SSE)
- **Memory Management** - Store and retrieve long-term user/context memories
- **Health Monitoring** - Check service and dependency status
- **Debug Tools** - Inspect RAG system state

Key Features:

✓ Non-blocking streaming responses (see :doc:`streaming`)  
✓ Semantic search on memories (see :doc:`memory`)  
✓ Automatic conversation threading  
✓ Thinking/reasoning visibility  
✓ Entity-scoped context retrieval (see :doc:`data_model`)  
✓ Conversation summarization  
✓ Specialist plugin system (see :doc:`specialists`)  


Quick Start
-----------

**Health Check:**

.. code-block:: bash

   curl http://localhost:7000/v1/healthz

**Simple Chat:**

.. code-block:: bash

   curl -X POST http://localhost:7000/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!"}'

**Streaming Chat:**

.. code-block:: bash

   curl -N -X POST http://localhost:7000/v1/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello!"}'

See :doc:`getting_started` for detailed setup and configuration.


Full API Reference
-------------------

For complete endpoint documentation with parameters, responses, and examples, see :doc:`api_reference`.


Indices and search
------------------

* :ref:`genindex`
* :ref:`search`
