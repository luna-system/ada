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

## Next Steps

1. [ ] Review plans and decide on approach
2. [ ] Create feature branch (`feature/integration-plugins`)
3. [ ] Implement chosen option(s)
4. [ ] Test with existing adapters (Matrix, MCP)
5. [ ] Document patterns and contracts
6. [ ] Update .ai/ documentation
7. [ ] Consider building example adapter (Discord, Telegram, Slack)

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
