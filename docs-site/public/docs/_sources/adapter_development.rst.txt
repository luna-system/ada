Adapter Development Guide
=========================

This guide walks you through building a new adapter for Ada using the **CLI adapter as the reference implementation**.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

An **adapter** translates between an interface (web browser, chat app, IDE, terminal) and Ada's REST API. All adapters are equal peers - there's no "primary" interface.

**Core principle:** Keep adapters simple. Complex logic belongs in the brain, not in adapters.

Architecture Pattern
--------------------

All adapters follow this pattern::

    User Interface → Adapter → HTTP Client → Ada Brain API (/v1/chat/stream)
                                                     ↓
                                          RAG + Specialists + LLM
                                                     ↓
                                          SSE Stream Response
                                                     ↓
                     Display to User ← Adapter ← HTTP Client

The adapter has two responsibilities:

1. **Protocol Translation** - Convert interface messages to HTTP requests
2. **User Experience** - Present responses in the interface's native format

Reference Implementation
------------------------

The **CLI adapter** in ``adapters/cli/`` is the reference implementation. It demonstrates:

- Simplest possible adapter architecture
- Both streaming and non-streaming patterns
- Standard exception handling
- Type hints throughout
- Minimal dependencies

**Start here** when building a new adapter!

Standard HTTP Client
--------------------

All Python adapters use a standardized HTTP client pattern. See ``.ai/ADAPTER_STANDARDIZATION.md`` for details.

Required Components
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import AsyncIterator
   import httpx

   # Standard exception hierarchy
   class AdaBrainError(Exception):
       """Base exception for Ada Brain API errors."""

   class AdaBrainConnectionError(AdaBrainError):
       """Cannot connect to Ada Brain API."""

   class AdaBrainResponseError(AdaBrainError):
       """Ada Brain API returned an error."""

   class AdaClient:
       """HTTP client for Ada Brain API."""
       
       def __init__(self, base_url: str = "http://localhost:8000"):
           self.base_url = base_url
           self.client = httpx.AsyncClient(timeout=300.0)
       
       async def chat_stream(
           self, 
           message: str,
           conversation_id: str | None = None
       ) -> AsyncIterator[str]:
           """Stream chat response chunks (SSE)."""
           # Implementation: yield chunks from /v1/chat/stream
           
       async def chat(
           self,
           message: str,
           conversation_id: str | None = None
       ) -> str:
           """Non-streaming chat (collects full response)."""
           # Implementation: collect chunks from chat_stream()
           
       async def health(self) -> dict:
           """Check API health status."""
           # Implementation: GET /v1/healthz

Required Methods
~~~~~~~~~~~~~~~~

1. **chat_stream()** - Yields SSE chunks as they arrive
2. **chat()** - Collects full response (uses chat_stream internally)
3. **health()** - Returns health status dict

Exception Handling
~~~~~~~~~~~~~~~~~~

- Raise ``AdaBrainConnectionError`` for network failures
- Raise ``AdaBrainResponseError`` for API errors
- Let unexpected exceptions propagate (they're bugs!)

Example: CLI Adapter
--------------------

File Structure
~~~~~~~~~~~~~~

::

   adapters/cli/
   ├── ada_cli/
   │   ├── __init__.py
   │   ├── client.py      # HTTP client (standardized)
   │   └── cli.py         # User interface (Click + Rich)
   ├── pyproject.toml     # Package metadata
   └── README.md          # Usage instructions

Key Files
~~~~~~~~~

**client.py** - HTTP Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # See adapters/cli/ada_cli/client.py for full implementation
   
   class AdaClient:
       async def chat_stream(self, message: str) -> AsyncIterator[str]:
           """Stream chat response from Ada Brain API."""
           try:
               async with self.client.stream(
                   "POST",
                   f"{self.base_url}/v1/chat/stream",
                   json={"message": message},
                   headers={"Accept": "text/event-stream"}
               ) as response:
                   response.raise_for_status()
                   async for line in response.aiter_lines():
                       if line.startswith("data: "):
                           chunk = line[6:]  # Remove "data: " prefix
                           if chunk.strip() and chunk != "[DONE]":
                               yield chunk
           except httpx.ConnectError as e:
               raise AdaBrainConnectionError(f"Cannot connect: {e}")
           except httpx.HTTPStatusError as e:
               raise AdaBrainResponseError(f"API error: {e}")

**cli.py** - User Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import click
   from rich.console import Console
   from .client import AdaClient
   
   @click.command()
   @click.argument("message", required=False)
   @click.option("--api-url", default="http://localhost:8000")
   def main(message: str | None, api_url: str):
       """Ada CLI - Chat with Ada from your terminal."""
       client = AdaClient(base_url=api_url)
       
       if message:
           # One-shot mode
           asyncio.run(oneshot_mode(client, message))
       else:
           # Interactive REPL
           asyncio.run(interactive_mode(client))

Example: Matrix Bridge Adapter
-------------------------------

The Matrix bridge demonstrates a more complex adapter that:

- Maintains per-room conversation context
- Handles asynchronous events (messages, invites, reactions)
- Uses non-streaming API (collects full response before sending)
- Implements privacy controls

**Key differences from CLI:**

- **Event-driven** - Matrix sends events, adapter reacts
- **Stateful** - Tracks conversation context per room
- **Non-streaming** - Collects full response before replying (uses ``chat()`` not ``chat_stream()``)
- **Bot identity** - Clear transparency about being AI

See ``matrix-bridge/`` and ``docs/matrix_integration.rst`` for details.

Example: MCP Server Adapter
----------------------------

The MCP server demonstrates IDE integration:

- **stdio protocol** - Communicates via JSON-RPC over stdin/stdout
- **Tool pattern** - Exposes Ada as tools (``ada_chat``, ``ada_search_memory``, etc.)
- **Resource pattern** - Exposes documentation as MCP resources
- **Synchronous to async** - Bridges sync MCP calls to async HTTP client

See ``ada-mcp/`` for implementation details.

Building Your Adapter
----------------------

Step 1: Choose Your Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Streaming vs Non-Streaming:**

- **Streaming** (``chat_stream()``): Best for interactive UIs (CLI, web browser)
- **Non-streaming** (``chat()``): Best for chat apps (Matrix, Discord) and tools (MCP)

**Stateful vs Stateless:**

- **Stateful**: Adapter manages conversation context (Matrix bridge, web UI)
- **Stateless**: Brain manages context via ``conversation_id`` (CLI, MCP)

Step 2: Copy the Reference Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start with CLI adapter structure
   cp -r adapters/cli/ adapters/your-adapter/
   cd adapters/your-adapter/
   
   # Rename the module
   mv ada_cli your_adapter_name
   
   # Update pyproject.toml with your adapter name/description

Step 3: Implement Protocol Translation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keep the standard HTTP client (``client.py``), replace the UI layer:

.. code-block:: python

   # your_adapter_name/interface.py
   from .client import AdaClient, AdaBrainConnectionError
   
   async def your_interface_main():
       """Your adapter's main loop/entry point."""
       client = AdaClient(base_url="http://localhost:8000")
       
       # Check health
       try:
           status = await client.health()
           if not status.get("ok"):
               print("Warning: Ada Brain not fully ready")
       except AdaBrainConnectionError:
           print("Error: Cannot connect to Ada Brain")
           return
       
       # Your protocol-specific logic here
       # - Listen for messages from your interface
       # - Call client.chat_stream() or client.chat()
       # - Format and send responses back to interface

Step 4: Handle Errors Gracefully
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from .client import AdaBrainConnectionError, AdaBrainResponseError
   
   try:
       async for chunk in client.chat_stream(message):
           # Display chunk in your interface
           pass
   except AdaBrainConnectionError as e:
       # Network/connection failure - show user-friendly error
       print(f"Cannot reach Ada: {e}")
   except AdaBrainResponseError as e:
       # API returned error - show details
       print(f"Ada error: {e}")
   except Exception as e:
       # Unexpected error - this is a bug!
       print(f"Internal error (please report): {e}")
       raise

Step 5: Test Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Ensure Ada Brain is running
   docker compose up -d brain
   
   # Test health check
   curl http://localhost:8000/v1/healthz
   
   # Test your adapter
   # (depends on your interface)

Step 6: Document Usage
~~~~~~~~~~~~~~~~~~~~~~

Add a ``README.md`` to your adapter directory with:

- Installation instructions
- Configuration options
- Usage examples
- Troubleshooting tips

Best Practices
--------------

DO ✅
~~~~~

- **Keep it simple** - Adapters are thin translation layers
- **Use the standard client** - Don't reimplement HTTP logic
- **Handle exceptions** - Network failures are normal
- **Add type hints** - Makes code self-documenting
- **Test health checks** - Ensure Ada is ready before use
- **Document clearly** - Help others use your adapter

DON'T ❌
~~~~~~~~

- **Add business logic** - That belongs in the brain
- **Implement RAG/LLM** - The brain does this
- **Manage specialists** - The brain handles plugins
- **Parse responses** - Trust the SSE format
- **Swallow exceptions** - Let bugs surface during development
- **Skip health checks** - Always verify connectivity

Deployment Patterns
-------------------

Standalone Process
~~~~~~~~~~~~~~~~~~

**Good for:** Chat bots (Matrix, Discord), background services

.. code-block:: bash

   # Run as separate service
   docker compose up -d brain your-adapter

Embedded in Application
~~~~~~~~~~~~~~~~~~~~~~~

**Good for:** Web applications, desktop apps

.. code-block:: python

   from your_adapter.client import AdaClient
   
   # Use within your application
   client = AdaClient()
   response = await client.chat("Hello!")

On-Demand Tool
~~~~~~~~~~~~~~

**Good for:** CLI tools, scripts, IDE extensions

.. code-block:: bash

   # CLI tool
   ada-cli "What's the weather?"
   
   # IDE extension (MCP)
   # Invoked by IDE when user asks question

Troubleshooting
---------------

"Cannot connect to Ada Brain"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``AdaBrainConnectionError``

**Solutions:**

1. Check if brain is running: ``docker compose ps brain``
2. Verify URL: ``curl http://localhost:8000/v1/healthz``
3. Check network: ``docker compose logs brain``

"API returned error"
~~~~~~~~~~~~~~~~~~~~

**Symptom:** ``AdaBrainResponseError`` with HTTP status

**Solutions:**

1. Check brain logs: ``docker compose logs brain``
2. Verify request format (JSON schema)
3. Ensure dependencies ready (Ollama, ChromaDB)

"Response format unexpected"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Parsing errors, unexpected data

**Solutions:**

1. Check SSE format: Lines start with ``data: ``
2. Handle ``[DONE]`` marker (end of stream)
3. Verify you're using ``Accept: text/event-stream`` header

Next Steps
----------

- See ``docs/adapters.rst`` for adapter overview
- Check ``.ai/ADAPTER_STANDARDIZATION.md`` for implementation details
- Review existing adapters in ``adapters/``, ``matrix-bridge/``, ``ada-mcp/``
- Read ``docs/api_reference.rst`` for complete API documentation

Happy building! 🚀
