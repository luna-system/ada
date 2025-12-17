Ada Adapters
=============

**Adapters** are how you interact with Ada's brain. Each adapter connects a different interface (web browser, terminal, chat app, IDE) to Ada's core API.

Ada's architecture treats all interfaces as **equal peers** - there's no "primary" interface. Choose the adapter(s) that fit your workflow.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

All adapters communicate with Ada's brain via the same REST API (``/v1/chat/stream``). The brain handles:

- RAG (semantic memory search)
- LLM inference (via Ollama)
- Specialist plugins (OCR, web search, etc.)
- Conversation context management

Adapters handle:

- Protocol translation (HTTP, Matrix, stdio, etc.)
- User interface
- Message formatting
- Authentication (when applicable)

Available Adapters
------------------

CLI (Command-Line Interface)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Best for:** Scripting, automation, terminal users

:Location: ``adapters/cli/``
:Complexity: ⭐ Simple (reference implementation)
:Status: ✅ Production
:Protocol: HTTP/SSE
:Dependencies: httpx, click, rich

The CLI adapter is the **reference implementation** for building new adapters. It shows both streaming and non-streaming patterns in the simplest possible way.

**Features:**

- Interactive REPL mode
- One-shot query mode (for scripts)
- JSON output (for automation)
- Conversation context
- Health checks

**Installation:**

.. code-block:: bash

   cd adapters/cli
   pip install -e .

**Usage:**

.. code-block:: bash

   # Interactive mode
   ada-cli
   
   # One-shot query
   ada-cli "What is 2+2?"
   
   # JSON output for scripting
   ada-cli --format json "Hello" | jq '.response'
   
   # Custom brain URL
   ada-cli --brain-url http://ada.example.com:8000 "Hello"

See ``adapters/cli/README.md`` for complete documentation.

Web UI
^^^^^^

**Best for:** Browser-based chat, visual interface

:Location: ``frontend/``
:Complexity: ⭐⭐ Medium
:Status: ✅ Production
:Protocol: HTTP/SSE (via nginx proxy)
:Dependencies: nginx, Astro, JavaScript

Browser-based single-page application with streaming responses.

**Features:**

- Real-time streaming (EventSource/SSE)
- Markdown rendering
- Memory management UI
- Conversation history
- File uploads (OCR, vision)

**Starting:**

.. code-block:: bash

   # Web UI is optional, requires profile
   docker compose --profile web up -d

**Access:**

- Web UI: http://localhost:5000
- Docs: http://localhost:5000/docs
- API: http://localhost:5000/api/* (proxied to brain)

Matrix Bridge
^^^^^^^^^^^^^

**Best for:** Federated chat, team collaboration, encrypted messaging

:Location: ``matrix-bridge/``
:Complexity: ⭐⭐⭐ Complex
:Status: ✅ Production
:Protocol: Matrix Client-Server API
:Dependencies: matrix-nio[e2e], httpx

Connects Ada to Matrix chat rooms with end-to-end encryption support.

**Features:**

- Auto-accept invites
- Per-room conversation context
- Reaction-based status (🧠→✅/❌)
- Privacy opt-out
- Encrypted rooms support

**Starting:**

.. code-block:: bash

   # Requires configuration first
   cp matrix-bridge/.env.example matrix-bridge/.env
   # Edit .env with Matrix credentials
   
   docker compose --profile matrix up -d

See ``matrix-bridge/README.md`` for complete setup guide.

MCP Server
^^^^^^^^^^

**Best for:** IDE integration, development tools

:Location: ``ada-mcp/``
:Complexity: ⭐⭐ Medium
:Status: ✅ Production
:Protocol: stdio JSON-RPC (Model Context Protocol)
:Dependencies: mcp, httpx

Integrates Ada with tools that support the Model Context Protocol (Claude Desktop, Zed, etc.).

**Features:**

- ``ada_chat`` tool - Chat with Ada
- ``ada_search_memory`` tool - Search Ada's memory
- ``ada_add_memory`` tool - Add memories
- ``ada_health`` tool - Check brain status
- Documentation resources from ``.ai/`` folder

**Installation:**

See ``ada-mcp/README.md`` for MCP client configuration.

Comparison Table
----------------

.. list-table::
   :header-rows: 1
   :widths: 15 15 25 15 15 15

   * - Adapter
     - Protocol
     - Use Case
     - Complexity
     - Streaming
     - Status
   * - **CLI**
     - HTTP/SSE
     - Terminal, scripting, automation
     - ⭐ Simple
     - ✅ Yes
     - ✅ Production
   * - **Web UI**
     - HTTP/SSE
     - Browser-based chat
     - ⭐⭐ Medium
     - ✅ Yes
     - ✅ Production
   * - **Matrix**
     - Matrix C2S
     - Federated chat rooms
     - ⭐⭐⭐ Complex
     - ❌ No*
     - ✅ Production
   * - **MCP**
     - stdio/JSON-RPC
     - IDE integration
     - ⭐⭐ Medium
     - ✅ Yes
     - ✅ Production
   * - Discord
     - Discord API
     - Gaming communities
     - ⭐⭐ Medium
     - TBD
     - 🚧 Planned
   * - Telegram
     - Telegram API
     - Mobile messaging
     - ⭐⭐ Medium
     - TBD
     - 🚧 Planned

\* Matrix bridge uses complete responses (not streaming) due to Matrix protocol limitations.

Building Your Own Adapter
--------------------------

**Start with the CLI adapter** - it's the reference implementation designed for learning and adaptation.

Required Steps
^^^^^^^^^^^^^^

1. **Create HTTP Client**

   Connect to Ada's brain API at ``/v1/chat/stream``:

   .. code-block:: python

      import httpx

      async def chat(message: str, conversation_id: str) -> str:
          url = "http://localhost:8000/v1/chat/stream"
          payload = {
              "prompt": message,
              "conversation_id": conversation_id,
              "stream": True
          }
          
          chunks = []
          async with httpx.AsyncClient() as client:
              async with client.stream("POST", url, json=payload) as response:
                  async for line in response.aiter_lines():
                      if line.startswith("data: "):
                          chunk = line[6:]  # Remove "data: " prefix
                          if chunk and chunk != "[DONE]":
                              chunks.append(chunk)
          
          return "".join(chunks)

2. **Add Protocol Handler**

   Translate your protocol to/from Ada's API:

   - **Discord**: Discord events → Ada client → Discord messages
   - **Telegram**: Telegram updates → Ada client → Telegram replies
   - **Slack**: Slack events → Ada client → Slack responses

3. **Manage Conversation Context**

   Use room/channel/user IDs as ``conversation_id``:

   .. code-block:: python

      # Use unique identifier for context
      conversation_id = f"discord-{channel_id}"
      response = await ada_client.chat(message, conversation_id)

4. **Handle Errors Gracefully**

   - Connection errors (brain down)
   - Timeout errors (long responses)
   - Rate limiting (if applicable)

Recommended Structure
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   adapters/your-adapter/
   ├── README.md              # Setup and usage guide
   ├── pyproject.toml         # Dependencies
   ├── your_adapter/
   │   ├── __init__.py
   │   ├── client.py          # Ada HTTP client
   │   ├── protocol.py        # Your protocol handler
   │   └── main.py            # Entry point
   ├── tests/
   │   └── test_client.py
   └── examples/
       └── example.py

See ``adapters/cli/`` for a working example of this structure.

Deployment Patterns
-------------------

Standalone Service
^^^^^^^^^^^^^^^^^^

Most adapters run as separate services (Matrix, MCP):

.. code-block:: yaml

   services:
     your-adapter:
       build: ./adapters/your-adapter
       depends_on:
         - brain
       environment:
         - ADA_BRAIN_URL=http://brain:7000

In-Process
^^^^^^^^^^

Some adapters run in the same process as the brain (future):

- Reduces latency
- Simpler deployment
- Tighter coupling

CLI Tool
^^^^^^^^

Installed as command-line tools (CLI, future SDK):

.. code-block:: bash

   pip install ada-your-adapter
   ada-your-adapter

Error Handling
--------------

All adapters should handle:

**Connection Errors**

.. code-block:: python

   try:
       response = await ada_client.chat(message)
   except AdaBrainConnectionError:
       # Brain is down or unreachable
       return "Sorry, I'm temporarily unavailable."

**Timeouts**

.. code-block:: python

   # Use appropriate timeouts for your use case
   client = AdaClient(timeout=120.0)  # 2 minutes

**Rate Limiting**

.. code-block:: python

   # If your protocol has rate limits
   async with rate_limiter:
       response = await ada_client.chat(message)

Best Practices
--------------

**Do:**

✅ Use the CLI adapter as a reference  
✅ Keep adapter logic separate from Ada's brain  
✅ Use ``conversation_id`` for context management  
✅ Handle errors gracefully  
✅ Document setup and usage  
✅ Include health checks  
✅ Test with real brain API  

**Don't:**

❌ Put adapter logic in the brain core  
❌ Assume brain is always available  
❌ Ignore conversation context  
❌ Skip error handling  
❌ Hardcode URLs (use config/env vars)  

Future Adapters
---------------

**In Planning:**

- Discord bot
- Telegram bot
- Slack app
- WhatsApp (via Twilio/MessageBird)
- SMS (via Twilio)
- Voice assistants (Alexa, Google Home)
- Mobile apps (React Native)

**Want to Build One?**

See the `Integration Plugins Plan <../INTEGRATION_PLUGINS_PLAN.md>`_ for the roadmap and ``.ai/adapter-contract.md`` for technical requirements.

See Also
--------

- :doc:`architecture` - Overall system architecture
- :doc:`api_reference` - Brain REST API documentation
- :doc:`development` - Development setup and workflows
- ``adapters/cli/README.md`` - CLI adapter (reference implementation)
- ``INTEGRATION_PLUGINS_PLAN.md`` - Adapter system roadmap
