# Changelog

All notable changes to Ada will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Progress
- Changelog automation with Conventional Commits

---

## [2.1.0] - 2025-12-17

### ⚡ Performance
- **Multi-timescale context caching system** - Dramatically reduces redundant RAG queries
  - Personas cached for 24 hours (identity rarely changes)
  - FAQs cached for 24 hours (knowledge base updates infrequently)
  - Memories cached for 5 minutes (balance freshness vs performance)
  - Conversation turns cached for 1 hour (recent context preserved)
- LRU eviction prevents unbounded memory growth
- Cache stats logged per request for observability
- Expected ~70% reduction in ChromaDB queries for repeated context

### ✨ Features
- **New modular prompt building architecture**
  - `PromptAssembler` - Clean orchestration with automatic caching
  - `ContextRetriever` - Cache-aware RAG data retrieval
  - `SectionBuilder` - Structured section formatting
  - `MultiTimescaleCache` - Production-ready caching implementation
- Cache integration transparent to specialists and adapters
- Per-request cache statistics in logs

### 🗑️ Removed (Breaking Changes)
- **Deleted legacy `brain/_legacy_prompt_builder.py`** (266 lines)
- **Removed backward-compatible `build_prompt()` shim**
- New code must use `PromptAssembler` API directly
- Technical debt eliminated: -299 net lines across the codebase

### 🔧 Fixes
- **Corrected default port from 7000 to 8000** in ada-client and ada-cli
  - Brain runs internally on 7000, exposed via Docker on 8000
  - Clients now default to correct external port
- Updated CLI Python requirement to >=3.13 for consistency

### 📚 Documentation
- Updated architecture.rst with caching system overview
- Refreshed API usage examples for new PromptAssembler
- Updated specialist RAG documentation
- Token monitoring examples modernized
- AI documentation (codebase-map.json) fully updated
- Marked TODO-CACHE-INTEGRATION.md as complete

### 🧪 Testing
- 23 new comprehensive cache tests (15 basic + 8 integration)
- Tests cover TTL expiration, LRU eviction, cache stats, and retriever integration
- All tests passing, cache validated in production

### 📦 Dependencies
- No new external dependencies (pure Python implementation)

### Impact
**Massive performance win:** Caching reduces latency on repeated queries from seconds to milliseconds. Cleaner codebase with 300 fewer lines of legacy code. Modern modular architecture ready for future optimization phases (FAQ caching, memory caching expansion).

**Migration Guide:**
```python
# Old (removed):
from brain.prompt_builder import build_prompt
prompt, context = await build_prompt(...)

# New (required):
from brain.prompt_builder import PromptAssembler
assembler = PromptAssembler()
prompt = assembler.build_prompt(
    user_message="...",
    conversation_id="...",
    notices=get_active_notices()
)
```

---

## [1.8.0] - 2025-12-16

### ✨ Features
- Complete Nix flake with development shell, package build, and NixOS module
- Python version fallback (python313 → python312 → python3) for compatibility
- Automatic locale fixes (LC_ALL=C.UTF-8) in Nix environment
- direnv integration for automatic environment activation
- Validation script (scripts/test_nix_setup.sh) with 10-point health check
- ada doctor command now detects Python version mismatches and suggests Nix

### 📚 Documentation
- New primary entry point: docs/zero_to_ada.rst with decision tree
- Comprehensive Nix guide: docs/nix.rst (537 lines)
- Real-world troubleshooting: docs/nix_troubleshooting.md
- Updated README.md to prioritize Nix for users without Python 3.13

### 🔧 Maintenance
- Version management automation (scripts/version.sh)
- Updated .gitignore for Nix artifacts

### Impact
Solves Python 3.13 availability on Ubuntu/Debian. Makes Ada accessible to users
on older distros without requiring Docker or building Python from source.

---

## [1.7.0] - 2025-12-16

### ✨ Features
- Kubernetes deployment manifests (k8s/deployment.yaml, service.yaml, configmap.yaml)
- Helm chart for one-command deployment (helm/)
- Nomad job specification for HashiCorp Nomad (nomad/ada.nomad)
- Multi-cloud deployment support (AWS EKS, GCP GKE, Azure AKS, local k3s/k0s)

### 📚 Documentation
- Comprehensive orchestration guides (docs/k8s.rst, docs/helm.rst, docs/nomad.rst)
- Hardware requirements and scaling guidance
- Multi-cloud deployment strategies
- Production deployment checklist

### 🔧 Maintenance
- Updated README.md with orchestration quick links
- Fixed markdown formatting in documentation

### Impact
Enterprise-ready deployment options. Ada can now run in production Kubernetes
clusters, scale horizontally, and integrate with cloud infrastructure.

---

## [1.6.0] - 2025-12-15

### ✨ Features
- Matrix bridge for chat integration (matrix-bridge/)
- Multiple interface adapters (CLI, Web, Matrix, MCP)
- Bidirectional specialists (LLM can invoke tools mid-response)
- Wikipedia and Fandom wiki lookup specialist
- Documentation specialist (Ada can read her own docs)
- Web search specialist with DuckDuckGo integration

### 🐛 Bug Fixes
- Fixed OCR specialist activation
- Improved memory consolidation reliability
- Fixed streaming response handling

### 📚 Documentation
- Architecture documentation overhaul
- Adapter pattern documentation
- Specialist system documentation
- Matrix integration guide

### 🔧 Maintenance
- Improved error handling in specialists
- Better logging throughout system
- Code cleanup and refactoring

---

## [1.5.0] - 2025-12-10

### ✨ Features
- MCP (Model Context Protocol) server implementation
- Ada CLI tool (ada-cli) for terminal interaction
- Streaming chat responses via Server-Sent Events
- RAG-based memory system with ChromaDB

### 📚 Documentation
- Getting started guide
- API documentation
- Specialist development guide

---

## Earlier Versions

See git history for changes before v1.5.0.

---

## Version Format

**Major.Minor.Patch** (Semantic Versioning)

- **Major**: Breaking changes, architectural shifts
- **Minor**: New features, backwards-compatible changes
- **Patch**: Bug fixes, documentation updates

**Commit Types** (Conventional Commits):
- `feat`: New feature → Minor version bump
- `fix`: Bug fix → Patch version bump
- `docs`: Documentation → Patch version bump
- `perf`: Performance improvement → Minor version bump
- `refactor`: Code refactoring → Patch version bump
- `test`: Test changes → Patch version bump
- `chore`: Maintenance → Patch version bump
- `BREAKING CHANGE`: in commit body → Major version bump

**Example**:
```bash
feat(specialists): add Wikipedia search
fix(matrix): handle rate limiting errors
docs: update changelog automation guide
```
