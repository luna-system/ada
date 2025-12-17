.. Ada Brain API documentation master file

==================
Ada Brain API Docs
==================

Welcome to Ada! Your personal AI assistant that runs entirely on your hardware.

**New to Ada?** Start here:

1. **Quick Start:** :doc:`getting_started` - Get Ada running in 5 minutes with the ``ada`` CLI
2. **Customize:** :doc:`getting_started_scratch` - Make Ada truly yours
3. **Explore:** :doc:`specialists` - Extend Ada's capabilities

**Local Mode (Recommended):** Ada now runs without Docker! Just Python and Ollama. See :doc:`getting_started` for the fastest setup.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started
   local_mode
   nix
   getting_started_scratch
   configuration
   examples

.. toctree::
   :maxdepth: 2
   :caption: Hardware Setup

   hardware
   sbc

.. toctree::
   :maxdepth: 2
   :caption: Core Architecture

   architecture
   data_model
   streaming
   memory

.. toctree::
   :maxdepth: 2
   :caption: Interfaces & Adapters

   adapters
   adapter_development
   matrix_integration
   api_usage
   api_reference

.. toctree::
   :maxdepth: 2
   :caption: Specialist System

   specialists
   build_specialist
   bidirectional
   specialist_rag
   web_search

.. toctree::
   :maxdepth: 2
   :caption: Operations

   build_system
   buildx_adoption_notes
   disk_management

.. toctree::
   :maxdepth: 2
   :caption: Development

   development
   testing

.. toctree::
   :maxdepth: 1
   :caption: Philosophy & Design

   project_philosophy
   documentation_philosophy
   ai_documentation
   empathetic_documentation
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
