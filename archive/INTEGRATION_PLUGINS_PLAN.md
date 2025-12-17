# Integration Plugin System - Planning Doc

**Goal:** Make Ada's architecture more hackable by standardizing how external systems (Matrix, MCP, Discord, Telegram, etc.) integrate with the brain.

**Current State:**
- 3 integration points: Web UI (EventSource/SSE), Matrix Bridge (httpx), MCP Server (httpx)
- All use brain's REST API `/v1/chat/stream` as integration point
- Each adapter is custom-built with its own patterns
- Brain is monolithic FastAPI app with single HTTP interface

## Design Philosophy

> "Opening up Ada's architecture, making it as hackable as possible"

**Principles:**
- ✅ Favor composition over monolithic design
- ✅ Clear contracts and protocols
- ✅ Easy to add new integrations without modifying brain core
- ✅ Preserve what works (REST API is solid)
- ✅ DRY - avoid duplicating client logic across adapters

---

## Option A: Interface Plugins (Brain-Side)

**What:** Make the brain support multiple transport layers via plugin system

**Benefits:**
- Brain becomes more flexible (HTTP, WebSocket, stdio, gRPC, etc.)
- Could enable MCP server to run *inside* brain process (no separate service)
- Reduces latency for some integrations
- Single deployment artifact option

**Challenges:**
- More complex brain architecture
- Tighter coupling between brain and integrations
- Harder to scale horizontally (can't run Matrix bridge separately)
- May not fit current containerized deployment model

**Implementation Plan:**

### Step 1: Define Interface Protocol
```
brain/interfaces/
├── __init__.py
├── protocol.py              # Base interface protocol (similar to specialists/protocol.py)
├── http_interface.py        # Wrap existing FastAPI app
└── stdio_interface.py       # For MCP-style stdio transport
```

**protocol.py** structure:
```python
class InterfaceProtocol(Protocol):
    """Standard interface for transport layers"""
    
    def initialize(self, brain_core: "BrainCore") -> None:
        """Setup with access to brain core"""
        ...
    
    async def start(self) -> None:
        """Start listening/serving"""
        ...
    
    async def stop(self) -> None:
        """Graceful shutdown"""
        ...
    
    def get_health_status(self) -> dict:
        """Health check info"""
        ...
```

### Step 2: Extract Brain Core Logic
```
brain/
├── core.py                  # Pure business logic (RAG, LLM, specialists)
├── interfaces/              # Transport layer plugins
└── app.py                   # Existing HTTP interface (refactored to use core.py)
```

### Step 3: Add New Interfaces
- Create `stdio_interface.py` for MCP protocol
- Update `compose.yaml` to optionally include MCP in brain container
- Document how to add new interface plugins

**Pros:**
- Single process for multiple protocols (optional)
- Lower latency
- Cleaner architecture separation

**Cons:**
- Large refactor of brain
- Changes deployment model
- May break existing patterns
- Riskier (touching core)

**Effort:** 🔥🔥🔥 High (5-7 days)

---

## Option B: Standardize External Adapters

**What:** Keep adapters external but create common patterns/conventions

**Benefits:**
- Minimal changes to brain (already working)
- Easy to maintain separate adapters
- Can scale adapters independently
- Lower risk
- Preserves current deployment model

**Challenges:**
- Some code duplication across adapters
- No shared library (yet - see Option C)
- Each adapter is its own project

**Implementation Plan:**

### Step 1: Document Adapter Contract
Create `.ai/adapter-contract.md`:
```markdown
# Ada Integration Adapter Contract

## Requirements
1. Query brain via `/v1/chat/stream` (POST)
2. Handle conversation_id for context
3. Parse SSE stream or use non-streaming wrapper
4. Implement health checks
5. Handle errors gracefully

## Recommended Structure
adapters/{name}/
├── README.md                # Setup, usage
├── config.py                # Pydantic Settings
├── ada_client.py            # Brain API client
├── {protocol}_handler.py    # Protocol-specific logic
└── main.py                  # Entry point
```

### Step 2: Refactor Existing Adapters to Match Pattern

**matrix-bridge/** (currently correct structure):
```
matrix-bridge/
├── README.md                ✅
├── config.py                ✅
├── ada_client.py            ✅
├── bridge.py                ✅ (protocol handler)
├── message_handler.py       ✅
├── identity.py              ✅
└── Dockerfile               ✅
```

**ada-mcp/** (move to adapters/mcp/):
```
adapters/mcp/
├── README.md
├── config.py
├── ada_client.py            (extract from current code)
├── mcp_handler.py           (server.py renamed)
├── tools.py
├── resources.py
└── Dockerfile
```

### Step 3: Create Adapter Template
```
adapters/_template/
├── README.md
├── config.py.example
├── ada_client.py
├── {protocol}_handler.py.example
└── Dockerfile.example
```

### Step 4: Update Documentation
- Add `docs/building_adapters.rst` guide
- Document adapter contract in `.ai/`
- Add examples for common protocols

**Pros:**
- Low risk (mostly documentation + refactoring)
- Preserves what works
- Makes patterns explicit
- Easy to replicate for new integrations

**Cons:**
- Doesn't eliminate duplication (yet)
- Each adapter is still its own thing

**Effort:** 🔥 Low-Medium (2-3 days)

---

## Option C: Shared Ada Client Library

**What:** Extract common HTTP client logic into shared library

**Benefits:**
- DRY - single source of truth for brain API interaction
- Consistent error handling across all adapters
- Easy to version and update
- Can publish to PyPI for community adapters
- Works with current architecture

**Challenges:**
- Need to manage library versioning
- Adds dependency between adapters and library
- Requires packaging/distribution setup

**Implementation Plan:**

### Step 1: Create Shared Library Package
```
ada-client/
├── pyproject.toml           # Standalone package
├── README.md
├── src/
│   └── ada_client/
│       ├── __init__.py
│       ├── client.py        # Main HTTP client
│       ├── streaming.py     # SSE stream parsing
│       ├── schemas.py       # Request/response models (copy from brain/schemas.py)
│       └── exceptions.py    # Custom exceptions
└── tests/
    └── test_client.py
```

### Step 2: Implement Core Client
```python
# ada-client/src/ada_client/client.py

from typing import AsyncIterator
import httpx
from .schemas import ChatRequest, ChatChunk
from .streaming import parse_sse_stream

class AdaClient:
    """Async HTTP client for Ada's brain API."""
    
    def __init__(self, base_url: str = "http://localhost:7000"):
        self.base_url = base_url
        self._client = httpx.AsyncClient()
    
    async def chat_stream(
        self,
        message: str,
        conversation_id: str,
        **kwargs
    ) -> AsyncIterator[ChatChunk]:
        """Stream chat response."""
        async for chunk in parse_sse_stream(...):
            yield chunk
    
    async def chat(
        self,
        message: str,
        conversation_id: str,
        **kwargs
    ) -> str:
        """Get complete response (non-streaming)."""
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id, **kwargs):
            chunks.append(chunk.content)
        return "".join(chunks)
    
    async def health(self) -> dict:
        """Check brain health."""
        ...
    
    async def close(self):
        """Cleanup resources."""
        await self._client.aclose()
```

### Step 3: Refactor Adapters to Use Library

**Matrix Bridge:**
```python
# matrix-bridge/bridge.py
from ada_client import AdaClient  # Shared library

class MatrixBridge:
    def __init__(self):
        self.ada = AdaClient(base_url=config.ada_brain_url)
    
    async def handle_message(self, event):
        response = await self.ada.chat(
            message=event.body,
            conversation_id=event.room_id
        )
        # Send to Matrix...
```

**MCP Server:**
```python
# adapters/mcp/server.py
from ada_client import AdaClient  # Same library

class MCPServer:
    def __init__(self):
        self.ada = AdaClient()
    
    async def handle_tool_call(self, name, args):
        if name == "ada_chat":
            return await self.ada.chat(
                message=args["message"],
                conversation_id=args.get("conversation_id", "default")
            )
```

### Step 4: Package and Distribute
```bash
# Development mode (local editable install)
cd ada-client && pip install -e .

# In adapter
pip install -e ../ada-client

# Future: Publish to PyPI
pip install ada-client
```

### Step 5: Version Management
```toml
# ada-client/pyproject.toml
[project]
name = "ada-client"
version = "1.0.0"
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0"
]

# matrix-bridge/pyproject.toml
dependencies = [
    "ada-client>=1.0.0,<2.0.0",
    "matrix-nio[e2e]>=0.24.0"
]

# adapters/mcp/pyproject.toml
dependencies = [
    "ada-client>=1.0.0,<2.0.0",
    "mcp>=0.9.0"
]
```

**Pros:**
- Eliminates code duplication
- Easy to maintain and version
- Can be community-maintained
- Works with current architecture
- Low risk to brain

**Cons:**
- Adds dependency management complexity
- Need to coordinate versions
- Slightly more setup for new adapters

**Effort:** 🔥🔥 Medium (3-4 days)

---

## Recommended Approach: Hybrid Strategy

**Phase 1: Option B (Standardize Adapters) - Week 1**
- ✅ Low risk, immediate value
- Document adapter contract
- Refactor matrix-bridge and ada-mcp to match pattern
- Create adapter template
- Write docs

**Phase 2: Option C (Shared Client Library) - Week 2**
- ✅ Eliminate duplication
- Extract common client logic
- Package as ada-client
- Update adapters to use library
- Test thoroughly

**Phase 3: Option A (Interface Plugins) - Future**
- ⚠️ Only if needed for performance or new use cases
- Big refactor, do when stable
- Consider for v2.0 architectural evolution

---

## Decision Criteria

### Choose Option A if:
- Need sub-10ms latency for integrations
- Want single-process deployment option
- Building transport protocols that don't work over HTTP
- Willing to do major refactor

### Choose Option B if:
- Want quick wins with low risk
- Current architecture is working well
- Priority is clarity and hackability
- Want to ship fast

### Choose Option C if:
- Tired of duplicating client logic
- Building multiple new adapters soon
- Want a clean API for community
- Value DRY principles

### Choose Hybrid (B → C → A) if:
- Want to iterate safely
- Preserve optionality
- Deliver value incrementally
- Learn as you go (recommended! ✨)

---

## Phase 0: Establish Adapter Pattern with CLI + Web UI (PRIORITY)

**Current Problem:**
- Web UI (frontend service) is treated as "the" interface, not "an" interface
- It's tightly coupled via nginx config and not truly optional
- Lives in `frontend/` but should conceptually be an adapter like Matrix/MCP
- Brain service doesn't depend on it, but deployment assumes it exists
- No simple reference implementation for building new adapters

**What We're Doing:**
1. **Build CLI adapter** as the canonical reference implementation (simplest example)
2. Make web UI follow the same adapter pattern as Matrix bridge
3. Recognize all interfaces as equal ways to consume Ada's brain API
4. Make both truly optional in Docker Compose
5. Document standard adapter structure for future implementations

### Current Web UI Structure
```
frontend/
├── Dockerfile               # nginx + static site
├── nginx.conf.template      # Proxies /api/* → brain:7000/v1/*
├── public/
│   ├── app.js              # EventSource → /api/chat/stream
│   ├── style.css
│   └── index.html
├── src/                     # Astro source (builds to public/)
└── package.json
```

**What it does:**
- Serves static HTML/JS/CSS
- Proxies API calls to brain via nginx
- Uses EventSource (SSE) for streaming responses
- Already loosely coupled via REST API ✅

### Part A: Build CLI Adapter (Reference Implementation)

**Why CLI First:**
- Simplest possible adapter (no nginx, no UI framework, no protocol complexity)
- Perfect reference for documentation ("here's how to build an adapter")
- Immediately useful (scripting, testing, automation)
- Shows both streaming and non-streaming patterns
- Can be used in CI/CD pipelines

#### CLI Adapter Structure
```
adapters/cli/
├── README.md                # "How to build an adapter" guide
├── pyproject.toml           # Minimal dependencies
├── ada_cli/
│   ├── __init__.py
│   ├── client.py            # Reusable HTTP client (prototype for shared library!)
│   ├── cli.py               # Interactive REPL
│   └── formatters.py        # Output formatting (markdown, plain, JSON)
└── tests/
    └── test_cli.py
```

#### CLI Features
**Interactive Mode:**
```bash
$ ada-cli
🤖 Ada v1.2.0 (brain: http://localhost:7000)
Type 'help' for commands, 'exit' to quit

You: What's the weather?
Ada: I don't have access to real-time weather data...

You: /history
1. You: What's the weather?
   Ada: I don't have access to...

You: /clear
Conversation cleared.

You: exit
Goodbye! 👋
```

**One-Shot Mode:**
```bash
# Single query
$ ada-cli "what is 2+2?"
4

# Pipe input
$ echo "summarize this" | ada-cli

# JSON output for scripting
$ ada-cli --json "hello" | jq '.response'
```

**Streaming vs Non-Streaming:**
```bash
# Stream tokens (default, like web UI)
$ ada-cli --stream "write a story"
Once upon a time...

# Complete response (like Matrix bridge)
$ ada-cli --no-stream "quick answer"
```

#### CLI Implementation Highlights

**client.py** (will become shared library in Phase 2):
```python
"""HTTP client for Ada's brain API - reference implementation."""
import httpx
from typing import AsyncIterator
Build CLI Adapter (2 hours)**
- Create `adapters/cli/` directory structure
- Implement `client.py` (HTTP client - foundation for shared library)
- Implement `cli.py` (interactive REPL + one-shot mode)
- Add `pyproject.toml` with minimal dependencies (httpx, rich)
- Write README.md explaining implementation
- Test interactive and one-shot modes

**Step 5: Add Adapter Comparison Table (30 min)**
Create visual showing all adapters:

| Adapter | Protocol | Use Case | Complexity | Status |
|---------|----------|----------|------------|--------|
| **CLI** | HTTP/SSE | Terminal, scripting | ⭐ Simple | ✅ Reference |
| Web UI | HTTP/SSE + nginx | Browser-based chat | ⭐⭐ Medium | ✅ Production |
| Matrix Bridge | Matrix C2S | Federated chat rooms | ⭐⭐⭐ Complex | ✅ Production |
| MCP Server | stdio/JSON-RPC | IDE integration | ⭐⭐ Medium | ✅ Production |
| Discord Bot | Discord API | Gaming communities | ⭐⭐ Medium | 🚧 Planned |
| Telegram Bot | Telegram API | Mobile messaging | ⭐⭐ Medium | 🚧 Planned |

**"Want to build an adapter? Start with CLI!"** ← This becomes the mantra
        message: str,
        conversation_id: str = "cli"
    ) -> AsyncIterator[str]:
        """Stream chat response chunks."""
        url = f"{self.base_url}/v1/chat/stream"
        payload = {"prompt": message, "conversation_id": conversation_id, "stream": True}
        
        async with self._client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk and chunk != "[DONE]":
                        yield chunk
    
    async def chat(self, message: str, conversation_id: str = "cli") -> str:
        """Get complete response (non-streaming)."""
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id):
            chunks.append(chunk)
        return "".join(chunks)
    
    async def health(self) -> dict:
        """Check brain health."""
        response = await self._client.get(f"{self.base_url}/v1/healthz")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self._client.aclose()
```

**cli.py** (interactive mode):
```python
"""Interactive CLI for Ada."""
import asyncio
import sys
from rich.console import Console
from rich.markdown import Markdown
from .client import AdaClient

console = Console()

async def interactive_mode(client: AdaClient):
    """Run interactive REPL."""
    console.print("🤖 Ada CLI - Type 'help' for commands, 'exit' to quit\n")
    
    conversation_id = "cli-session"
    history = []
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/] ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                console.print("Goodbye! 👋")
                break
            if user_input == "/history":
                for i, (role, msg) in enumerate(history, 1):
                    console.print(f"{i}. {role}: {msg[:50]}...")
                continue
            if user_input == "/clear":
                history.clear()
                conversation_id = f"cli-session-{len(history)}"
                console.print("Conversation cleared.")
                continue
            
            history.append(("You", user_input))
            
            console.print("[bold green]Ada:[/] ", end="")
            response_parts = []
            async for chunk in client.chat_stream(user_input, conversation_id):
                console.print(chunk, end="")
                response_parts.append(chunk)
                sys.stdout.flush()
            console.print()  # Newline
            
            history.append(("Ada", "".join(response_parts)))
            
        except KeyboardInterrupt:
            console.print("\nUse 'exit' to quit.")
        except Exception as e:
            console.print(f"[red]Error:[/] {e}")
```

**Installation & Usage:**
```bash
# Install CLI adapter
pip install -e adapters/cli

# Run interactive mode
ada-cli

# One-shot query
ada-cli "what is Ada?"

# Custom brain URL
ada-cli --brain-url http://ada.example.com:7000 "hello"

# In Docker
docker compose run --rm scripts ada-cli
```

#### Documentation Benefits
CLI becomes the reference in `docs/building_adapters.rst`:

```rst
Building an Adapter
===================

The **CLI adapter** is the simplest reference implementation. 
Let's walk through how it works:

1. **HTTP Client** - Connects to brain's REST API
2. **Protocol Handler** - Manages conversation state and formatting
3. **Entry Point** - Exposes functionality to users

See ``adapters/cli/`` for complete working example.
```

---

### Part B: Make Web UI Optional (like Matrix)
**compose.yaml changes:**
```yaml
services:
  web:
    profiles:
      - web  # Only starts if explicitly requested
    build:
      context: .
      dockerfile: frontend/Dockerfile
    # ... rest stays the same
```

**Usage:**
```bash
# Default: Run brain + chroma + ollama (headless)
docker compose up -d

# With web UI:
docker compose --profile web up -d

# With Matrix bridge:
docker compose --profile matrix up -d

# With both:
docker compose --profile web --profile matrix up -d
```

#### 2. Rename/Restructure (Optional, for consistency)
Could move to adapter pattern:
```
adapters/web/
├── README.md                # Setup instructions
├── Dockerfile
├── nginx.conf.template
└── public/
    ├── app.js
    ├── style.css
    └── index.html
```

**OR** keep as `frontend/` but document it as an adapter (less disruptive).

#### 3. Update Documentation
- Add `docs/web_ui.rst` explaining it's optional
- Update architecture diagrams to show web UI as peer to Matrix/MCP
- Document in `.ai/codebase-map.json` as adapter

#### 4. Ensure Independence
Verify brain service works without web:
- ✅ Brain already independent (pure API)
- ✅ No backend dependencies on frontend
- ✅ Health checks don't require web UI
- ⚠️ Update compose.yaml `depends_on` (web depends on brain, not vice versa)

### Implementation Plan

**Step 1: Make Web Optional (30 min)**
- Add `profiles: [web]` to compose.yaml
- Test: `docker compose up -d` (no web), `docker compose --profile web up -d` (with web)
- Update README.md with profile usage

**Step 2: Document as Adapter (1 hour)**
- Add "Web UI Adapter" section to INTEGRATION_PLUGINS_PLAN.md
- Update `.ai/context.md` to list web UI alongside Matrix/MCP
- Update `.ai/codebase-map.json` with frontend module entries

**Step 3: Update Getting Started Docs (30 min)**
- Update `docs/getting_started.rst` to mention profiles
- Add note: "Web UI is optional, Ada works via Matrix/MCP without it"
- Update quick start to show `--profile web` option

**Step 4: Add Adapter Comparison Table (30 min)**
Crea**CLI as reference implementation** - "Here's how simple it can be"
- ✅ Clearer mental model (all interfaces are peers)
- ✅ Easier to run headless Ada (API-only, or CLI-only, or Matrix-only)
- ✅ Consistent with "hackable architecture" philosophy
- ✅ Makes room for more adapters
- ✅ Reduces default resource usage (don't need nginx if using Matrix/CLI)
- ✅ CLI useful for scripting, testing, automation
- ✅ CLI client code becomes prototype for shared library (Phase 2
| Matrix Bridge | Matrix C2S | Federated chat rooms | ✅ Production |
| MCP Server | stdio/JSON-RPC | IDE integration | ✅ Production |
| Discord Bot | Discord API | Gaming communities | 🚧 Planned |
| Telegram Bot | Telegram API | Mobile messaging | 🚧 Planned |

### Benefits
- ✅ Clearer mental model (all interfaces are peers)
- ✅ Easier to run headless Ada (API-only)
- ✅ Consistent with "hackable architecture" philosophyCLI + Web UI as adapters**
2. [x] Create feature branch (`feature/integration-plugins`)
3. [ ] **PHASE 0: Build CLI adapter + Make web UI optional (4 hours)**
   - [ ] Build CLI adapter (reference implementation)
   - [ ] Make web UI optional via profiles
   - [ ] Document adapter pattern
   - [ ] Add comparison table
4. [ ] PHASE 1: Standardize adapter patterns (Option B)
   - [ ] Extract patterns from CLI/Web/Matrix/MCP
   - [ ] Create adapter template
   - [ ] Document adapter contract
5. [ ] PHASE 2: Extract shared client library (Option C)
   - [ ] Extract client.py from CLI as foundation
   - [ ] Create ada-client package
   - [ ] Refactor all adapters to use it
6. [ ] PHASE 3: Consider interface plugins (Option A) - future
7. [ ] Test with all adapters (CLI, Web, Matrix, MCP
- ❌ Not refactoring web UI code (works fine)
- ❌ Not changing API (already correct)

---

## Next Steps

1. [x] Review plans and decide on approach → **Start with Web UI as adapter**
2. [x] Create feature branch (`feature/integration-plugins`)
3. [ ] **PHASE 0: Make web UI optional and document as adapter (2 hours)**
4. [ ] PHASE 1: Standardize adapter patterns (Option B)
5. [ ] PHASE 2: Extract shared client library (Option C)
6. [ ] PHASE 3: Consider interface plugins (Option A) - future
7. [ ] Test with existing adapters (Matrix, MCP, Web)
8. [ ] Update .ai/ documentation
9. [ ] Consider building example adapter (Discord, Telegram, Slack)

---

**Questions to Answer:**
- Do we want single-process option or prefer microservices?
- How important is DRY vs. simplicity?
- What's the next integration we want to build?
- Performance requirements?
- Deployment constraints?

**Parking Lot (Future Ideas):**
- GraphQL interface for brain
- WebSocket support for real-time streaming to web UI
- gRPC for high-performance internal services
- Pub/sub architecture for event-driven integrations
- Plugin marketplace/registry for community adapters
