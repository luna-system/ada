# Changelog

All notable changes to Ada will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [2.2.0] - 2025-12-18

### 🔬 Research & Optimization
- **Memory importance signal weight optimization (Phases 1-7)**
  - Systematic research: property testing → synthetic data → ablation → grid search → production validation → deployment → visualization
  - **Key discovery:** Surprise-only (r=0.876) beats multi-signal baseline (r=0.869)
  - **Optimal weights found:** decay=0.10 (was 0.40), surprise=0.60 (was 0.30)
  - **Improvement:** 12-38% across synthetic datasets, +6.5% on real conversations
  - 80 tests, 3.56s total runtime, 100% passing
- **Research validated:** Temporal decay was overweighted 4x, surprise underweighted 2x
- Same-day deployment: Research → production in <24hrs via TDD methodology

### ✨ Features
- **Optimal importance weights deployed to production**
  - Updated `brain/config.py` with research-validated optimal configuration
  - Backward compatible: legacy weights available via environment variables
  - Rollback mechanism tested and ready
- **Comprehensive research documentation (Phase 8: Meta-Science)**
  - 9 narrative formats, 45,000 words total documenting same research:
    1. Machine-readable summary (`.ai/RESEARCH-FINDINGS-V2.2.md`)
    2. Academic article (peer-review ready, 8,000 words)
    3. CCRU-inspired experimental narrative (hyperstition engaged, 9,000 words)
    4. Blog post (accessible science communication, 4,500 words)
    5. Technical deep-dive (implementation guide, 6,000 words)
    6. Twitter thread (15 tweets, viral-ready)
    7. Recursion reveal README (meta-awareness, 3,500 words)
    8. Techno-horror essay (accelerationist, 5,000 words)
    9. Brief general audience explainer (3-minute read, 1,200 words)
  - New docs section: `docs/research_narratives.rst` showcasing all formats
  - Complete with navigation guide, verification hooks, and meta-narrative

### 📊 Visualizations
- **6 publication-quality research graphs generated (Phase 7)**
  - Ablation study comparison (signal configurations)
  - Grid search heatmap (decay vs surprise landscape)
  - Improvement distribution (before/after comparison)
  - Correlation vs weights (3D surface plot)
  - Detail level changes (gradient efficiency)
  - Production validation (real conversation results)
  - All graphs 300 DPI, publication-ready (2.2 MB total)

### 🧪 Testing
- **New research test suite**
  - `tests/test_property_based.py` - 27 tests, mathematical invariants
  - `tests/test_synthetic_data.py` - 10 tests, ground truth datasets
  - `tests/test_ablation_studies.py` - 12 tests, signal isolation
  - `tests/test_weight_optimization.py` - 7 tests, grid search (169 configurations)
  - `tests/test_production_validation.py` - 6 tests, real conversation data
  - `tests/test_deployment.py` - 11 tests, config validation & rollback
  - `tests/test_visualizations.py` - 7 tests, graph generation
  - Total: 80 new tests, all passing, <4s runtime

### 📚 Documentation
- Updated `.ai/context.md` with research findings and optimal weights
- Updated `docs/biomimetic_features.rst` with validation results
- Added `docs/research_narratives.rst` landing page for all narrative formats
- Machine docs in `.ai/RESEARCH-FINDINGS-V2.2.md` for AI assistant verification
- Research methodology documented for future phases (9-12 planned)

### 🔧 Configuration
- Optimal weights now default in `brain/config.py`
- Legacy weights available via: `IMPORTANCE_WEIGHT_DECAY=0.40 IMPORTANCE_WEIGHT_SURPRISE=0.30`
- All signal weights configurable via environment variables
- Maintains backward compatibility with existing deployments

### 🎯 Performance Impact
- Context selection improved by +6.5% per turn on real conversations
- 80% of turns show positive importance prediction changes
- 250% increase in medium-detail memory chunks (better gradient utilization)
- Token budget increase: +17.9% (acceptable trade-off for quality gain)

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
