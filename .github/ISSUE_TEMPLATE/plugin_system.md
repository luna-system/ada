---
name: Dual-Layer Plugin System
about: Implement formalized plugin architecture for interfaces and capabilities
title: 'Architecture: Dual-Layer Plugin System (Interfaces + Capabilities)'
labels: enhancement, architecture, phase-2
assignees: ''

---

## Overview
Formalize the emerging pattern of two distinct plugin types: **Interface Adapters** (how to talk to Ada) and **Capability Plugins** (what Ada can do).

## Current State
We have the pattern working but not formalized:

**Capability Plugins (Specialists):**
- ✅ `brain/specialists/` - OCR, web search, docs lookup, media
- ✅ `BaseSpecialist` protocol in `brain/specialists/protocol.py`
- ✅ Auto-discovery via `__init__.py`
- ✅ Registered in `.ai/specialist-registry.json`

**Interface Adapters (Not Formalized):**
- ✅ Web UI (`frontend/`) - HTTP/SSE interface
- ✅ Matrix Bridge (`matrix-bridge/`) - Matrix protocol interface  
- ✅ MCP Server (`ada-mcp/`) - Model Context Protocol interface
- ❌ No shared protocol or discovery mechanism
- ❌ Ad-hoc structure, not generalized

## Desired Architecture

```
ada/
  brain/              # Core system
  specialists/        # Capability plugins (what Ada can do)
    protocol.py       # BaseSpecialist
    ocr_specialist.py
    web_search_specialist.py
  interfaces/         # Interface plugins (how to talk to Ada)
    protocol.py       # BaseInterface
    web/              # HTTP/SSE interface
    matrix/           # Matrix bridge
    mcp/              # MCP server
    discord/          # Future
    telegram/         # Future
```

## Benefits

1. **Architectural Clarity**
   - Clear separation: interfaces vs capabilities
   - Easier to explain system structure
   - Better mental model for contributors

2. **Discoverability**
   - Auto-detect available interfaces
   - Runtime introspection (like `/v1/specialists`)
   - Health checks for each interface

3. **Extensibility**
   - Pattern for adding Discord, Telegram, Slack, IRC, etc.
   - Shared contracts via `BaseInterface` protocol
   - Consistent configuration approach

4. **Documentation**
   - Clear guide for "how to add a new interface"
   - Examples from existing implementations
   - Registry in `.ai/interface-registry.json`

## Implementation Plan

### Phase 1: Define Protocol
- [ ] Create `interfaces/protocol.py` with `BaseInterface`
- [ ] Define required methods: `start()`, `stop()`, `healthcheck()`, `get_metadata()`
- [ ] Document interface contract

### Phase 2: Migrate Existing Interfaces
- [ ] Refactor web UI to implement `BaseInterface`
- [ ] Refactor Matrix bridge to implement `BaseInterface`
- [ ] Refactor MCP server to implement `BaseInterface`
- [ ] Ensure backward compatibility

### Phase 3: Discovery & Registry
- [ ] Implement auto-discovery mechanism
- [ ] Create `.ai/interface-registry.json`
- [ ] Add `/v1/interfaces` endpoint to brain
- [ ] Health status aggregation

### Phase 4: Documentation
- [ ] Update architecture diagrams
- [ ] Write "Adding a New Interface" guide
- [ ] Document interface lifecycle
- [ ] Add examples to Sphinx docs

## Success Criteria

- [ ] All three interfaces (web, matrix, mcp) use `BaseInterface`
- [ ] New interfaces can be added with <100 lines of boilerplate
- [ ] `/v1/interfaces` endpoint shows all available interfaces
- [ ] Health checks work for all interfaces
- [ ] Documentation clearly explains the dual-layer architecture

## Dependencies

- Must complete Matrix bridge MVP first
- Must stabilize MCP server
- Should have 3+ working examples before generalizing

## References

- Current specialists system: `brain/specialists/protocol.py`
- Architectural discussion in commit/PR comments
- `.ai/GOTCHAS.md` - Documents the pattern conceptually

## Notes

This is a **Phase 2 refactor**, not blocking any MVP features. Wait until we have:
1. Working Matrix bridge (in production)
2. Stable MCP server (tested)
3. Clear pattern emerging from real usage

The pattern already works via Docker Compose isolation - this just makes it more discoverable and maintainable.
