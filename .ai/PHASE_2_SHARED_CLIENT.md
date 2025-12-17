# Phase 2: Shared Client Library (`ada-client`)

## Goal

Extract common HTTP client code from adapters into a reusable package that all adapters can depend on.

## Current State

**Working Adapters (Standardized):**
- ✅ CLI (`adapters/cli/ada_cli/client.py`) - Reference implementation
- ✅ Matrix bridge (`matrix-bridge/ada_client.py`) - Standardized to match CLI
- ✅ MCP server (`ada-mcp/src/ada_mcp/ada_client.py`) - Standardized to match CLI
- ✅ Web UI (`frontend/public/app.js`) - JavaScript, uses Fetch API

**Common Pattern:**
- Exception hierarchy: `AdaBrainError`, `AdaBrainConnectionError`, `AdaBrainResponseError`
- Streaming method: `chat_stream()` returns AsyncIterator
- Non-streaming wrapper: `chat()` collects chunks
- Health check: `health()` returns dict or raises typed exception

See `.ai/adapter-contract.md` for full specification.

## Architecture Plan

### Package Structure

```
ada-client/
├── pyproject.toml          # Python package definition
├── README.md               # Usage guide
├── src/
│   └── ada_client/
│       ├── __init__.py     # Public API exports
│       ├── client.py       # Main AdaClient class
│       ├── exceptions.py   # Exception hierarchy
│       ├── schemas.py      # Pydantic models (optional)
│       └── types.py        # Type hints
├── tests/
│   ├── test_client.py
│   └── test_exceptions.py
└── examples/
    ├── streaming.py
    └── oneshot.py
```

### API Design

```python
from ada_client import AdaClient, AdaBrainError

# Initialize
client = AdaClient(base_url="http://localhost:8000")

# Streaming
async for chunk in client.chat_stream("Hello Ada"):
    print(chunk, end="", flush=True)

# Non-streaming
response = await client.chat("What's the weather?")
print(response)

# Memory operations
await client.add_memory("Luna prefers techno music", importance=0.8)
memories = await client.search_memories("music preferences")

# Health check
health = await client.health()
if health["brain"]["status"] == "healthy":
    print("Ada is ready!")
```

### Adapter Migration

**Before (current):**
```python
# matrix-bridge/bridge.py
from matrix_bridge.ada_client import AdaClient  # Local copy
```

**After (Phase 2):**
```python
# matrix-bridge/bridge.py
from ada_client import AdaClient  # Shared package

# pyproject.toml adds dependency:
[project]
dependencies = ["ada-client>=1.0.0"]
```

## Implementation Steps

### 1. Create Package Skeleton

```bash
# Create new package
mkdir -p ada-client/src/ada_client
cd ada-client

# Initialize pyproject.toml
cat > pyproject.toml << EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ada-client"
version = "1.0.0"
description = "Python client for Ada brain API"
dependencies = ["httpx>=0.27.0"]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "pytest-cov"]
EOF
```

### 2. Extract Core Client

Copy `adapters/cli/ada_cli/client.py` as base:

```python
# src/ada_client/client.py
"""Ada brain API client - streaming and non-streaming interface."""
import httpx
from typing import AsyncIterator, Dict, Any

from .exceptions import AdaBrainError, AdaBrainConnectionError, AdaBrainResponseError


class AdaClient:
    """HTTP client for Ada brain REST API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
    
    async def chat_stream(
        self, 
        message: str, 
        conversation_id: str | None = None
    ) -> AsyncIterator[str]:
        """Stream chat response chunks (Server-Sent Events)."""
        # Implementation from reference client
        ...
    
    async def chat(
        self,
        message: str,
        conversation_id: str | None = None
    ) -> str:
        """Non-streaming chat (collects all chunks)."""
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id):
            chunks.append(chunk)
        return "".join(chunks)
    
    async def search_memories(self, query: str, limit: int = 5) -> list[dict]:
        """Search Ada's memory store."""
        ...
    
    async def add_memory(
        self,
        content: str,
        importance: float = 0.5,
        scope: str = "user",
        memory_type: str = "note"
    ) -> dict:
        """Add memory to Ada's store."""
        ...
    
    async def health(self) -> dict:
        """Check health of all services."""
        ...
```

### 3. Create Exception Module

```python
# src/ada_client/exceptions.py
"""Exception hierarchy for Ada client errors."""


class AdaBrainError(Exception):
    """Base exception for Ada brain client errors."""
    pass


class AdaBrainConnectionError(AdaBrainError):
    """Network/connection errors communicating with brain."""
    pass


class AdaBrainResponseError(AdaBrainError):
    """Brain returned an error response (4xx/5xx)."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
```

### 4. Write Tests

```python
# tests/test_client.py
import pytest
from ada_client import AdaClient, AdaBrainConnectionError


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check."""
    client = AdaClient(base_url="http://localhost:8000")
    health = await client.health()
    
    assert "brain" in health
    assert health["brain"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_connection_error():
    """Test connection error handling."""
    client = AdaClient(base_url="http://localhost:9999")
    
    with pytest.raises(AdaBrainConnectionError):
        await client.health()
```

### 5. Update Adapters to Use Shared Client

**Matrix bridge:**
```bash
cd matrix-bridge
# Update pyproject.toml or requirements.txt
echo "ada-client @ file:///home/luna/Code/ada-v1/ada-client" >> requirements.txt

# Update import
sed -i 's/from matrix_bridge.ada_client/from ada_client/' bridge.py
```

**MCP server:**
```bash
cd ada-mcp
# Update pyproject.toml
uv add ../ada-client

# Update imports
sed -i 's/from ada_mcp.ada_client/from ada_client/' src/ada_mcp/tools.py
```

**CLI adapter:**
```bash
cd adapters/cli
# Update pyproject.toml
uv add ../../ada-client

# Update imports
sed -i 's/from ada_cli.client/from ada_client/' ada_cli/cli.py
```

### 6. Clean Up Duplicates

```bash
# Remove local copies
rm matrix-bridge/ada_client.py
rm ada-mcp/src/ada_mcp/ada_client.py
rm adapters/cli/ada_cli/client.py
```

## Testing Strategy

### Unit Tests
- Exception hierarchy
- URL construction
- Timeout handling
- Chunk parsing (SSE format)

### Integration Tests
- Against running brain service
- Streaming vs non-streaming parity
- Memory operations
- Health checks

### Adapter Tests
- Each adapter still works after migration
- No behavior changes
- Error handling preserved

## Benefits

### For Developers
- Single source of truth for client logic
- Easier to add new features (add once, all adapters benefit)
- Consistent behavior across all adapters
- Easier testing (mock client in adapter tests)

### For Maintenance
- Bug fixes in one place
- Easier to track breaking changes
- Version compatibility clear
- Documentation in one place

### For New Adapters
- Just `pip install ada-client` or `uv add ada-client`
- No need to copy-paste client code
- Reference implementation always available
- Examples in package

## Timeline

**Estimated effort:** 4-6 hours

1. **Hour 1:** Create package skeleton, extract client code
2. **Hour 2:** Write exception module, basic tests
3. **Hour 3:** Update Matrix bridge to use shared client
4. **Hour 4:** Update MCP server to use shared client
5. **Hour 5:** Update CLI adapter to use shared client
6. **Hour 6:** Integration testing, documentation, cleanup

## Risks & Mitigations

### Risk: Breaking changes during migration
**Mitigation:** Keep local copies until all tests pass, then remove

### Risk: Import issues with local package
**Mitigation:** Use editable install: `uv add -e ../ada-client`

### Risk: Async context issues
**Mitigation:** Test with pytest-asyncio, ensure no context leaks

### Risk: Version skew between adapters
**Mitigation:** Pin version in all adapter dependencies

## Success Criteria

- ✅ All adapters use `from ada_client import AdaClient`
- ✅ No local `ada_client.py` copies in adapter directories
- ✅ All existing tests pass
- ✅ New shared tests cover common patterns
- ✅ Documentation updated in all adapters
- ✅ Package can be installed: `pip install -e ada-client`

## Related Documentation

- `.ai/ADAPTER_STANDARDIZATION.md` - Work that led to this phase
- `.ai/adapter-contract.md` - API specification for client
- `adapters/cli/ada_cli/client.py` - Current reference implementation
- `docs/adapters.rst` - Adapter architecture guide

---

**Last Updated:** 2025-12-16  
**Status:** 📋 Planning phase - Ready to implement  
**Dependencies:** Phase 1 adapter standardization ✅ complete

