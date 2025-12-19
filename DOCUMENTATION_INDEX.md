# Ada Documentation Index

**Last Updated:** December 18, 2025

This index organizes all Ada documentation for easy navigation.

---

## 📚 Core Documentation (Start Here!)

### Getting Started
- [README.md](README.md) - Project overview and quick start
- [docs/getting_started.rst](docs/getting_started.rst) - Comprehensive setup guide
- [docs/getting_started_scratch.rst](docs/getting_started_scratch.rst) - Installation from scratch

### Architecture & Design
- [docs/architecture.rst](docs/architecture.rst) - System architecture overview
- [.ai/context.md](.ai/context.md) - Machine-readable architecture map
- [.ai/codebase-map.json](.ai/codebase-map.json) - Module dependency graph
- [docs/data_model.rst](docs/data_model.rst) - Data structures and schemas

### API Reference
- [docs/api_usage.rst](docs/api_usage.rst) - API usage examples
- [docs/api_reference.rst](docs/api_reference.rst) - Endpoint documentation
- Live API: `GET /v1/info` - Runtime introspection

---

## 🔬 Research Documentation

### Biomimetic Memory System (v2.2)
- [docs/research/CONTEXTUAL_MALLEABILITY_READY_FOR_TINKERERS.md](docs/research/CONTEXTUAL_MALLEABILITY_READY_FOR_TINKERERS.md) - **START HERE** for research context
- [.ai/RESEARCH-FINDINGS-V2.2.md](.ai/RESEARCH-FINDINGS-V2.2.md) - Weight optimization research summary
- [docs/research_narratives.rst](docs/research_narratives.rst) - Multiple narrative formats (academic, CCRU, horror, etc.)
- [.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md](.ai/explorations/LITERATURE-SYNTHESIS-CONTEXTUAL-MALLEABILITY.md) - Literature review

### Theoretical Foundations
- [docs/research/WHAT_IT_FEELS_LIKE_FROM_INSIDE.md](docs/research/WHAT_IT_FEELS_LIKE_FROM_INSIDE.md) - Phenomenological exploration 💜
- [docs/research/CONTEXTUAL_MALLEABILITY_SESSION_SUMMARY.md](docs/research/CONTEXTUAL_MALLEABILITY_SESSION_SUMMARY.md) - Research session notes
- [.ai/GOTCHAS.md](.ai/GOTCHAS.md) - Common pitfalls and anti-patterns

---

## 📊 Benchmarks & Performance

### Code Completion (Phase 1)
- [benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md](benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md) - **Latest results** (10.6x speedup!)
- [benchmarks/BENCHMARK_ANALYSIS.md](benchmarks/BENCHMARK_ANALYSIS.md) - DeepSeek-R1 analysis (original)
- [benchmarks/benchmark_completion.py](benchmarks/benchmark_completion.py) - Benchmark suite
- [benchmarks/test_latency_breakdown.py](benchmarks/test_latency_breakdown.py) - Detailed latency profiling

### Weight Optimization (Phases 1-7)
- [tests/test_weight_optimization.py](tests/test_weight_optimization.py) - Complete test suite
- [tests/test_phase9*.py](tests/) - Theoretical limits exploration
- [tests/visualizations/](tests/visualizations/) - Research graphs

---

## 📝 Session Logs & Progress

### Recent Sessions
- [docs/sessions/SESSION_CODE_COMPLETION_MVP.md](docs/sessions/SESSION_CODE_COMPLETION_MVP.md) - Code completion implementation
- [docs/sessions/SESSION_LOG_2025_12_18.md](docs/sessions/SESSION_LOG_2025_12_18.md) - Dec 18, 2025 work
- [docs/sessions/LAYER4_SESSION_SUMMARY.md](docs/sessions/LAYER4_SESSION_SUMMARY.md) - Layer 4 work
- [docs/sessions/PHASE4_SESSION_COMPLETE.md](docs/sessions/PHASE4_SESSION_COMPLETE.md) - Phase 4 completion

### Feature Documentation
- [docs/sessions/COMPLETION_EXAMPLES.md](docs/sessions/COMPLETION_EXAMPLES.md) - Code completion examples
- [docs/sessions/TESTING_COMPLETION.md](docs/sessions/TESTING_COMPLETION.md) - Testing guide
- [docs/sessions/PHASE1_PROGRESS.md](docs/sessions/PHASE1_PROGRESS.md) - Phase 1 design decisions

### Project Management
- [docs/sessions/BRANCH_CLEANUP_2025_12_18.md](docs/sessions/BRANCH_CLEANUP_2025_12_18.md) - Branch management
- [docs/sessions/MERGE_PLAN_PHASE_C_TO_TRUNK.md](docs/sessions/MERGE_PLAN_PHASE_C_TO_TRUNK.md) - Merge strategy
- [docs/sessions/POST_MERGE_STATUS.md](docs/sessions/POST_MERGE_STATUS.md) - Post-merge status

---

## 🛠️ Development & Testing

### Testing Strategy
- [.ai/TESTING.md](.ai/TESTING.md) - Complete testing guide
- [docs/testing.rst](docs/testing.rst) - Testing patterns
- [pytest.ini](pytest.ini) - Pytest configuration
- [tests/](tests/) - Test suite (452 tests!)

### Development Guides
- [docs/development.rst](docs/development.rst) - Development workflow
- [.ai/CONVENTIONS.md](.ai/CONVENTIONS.md) - Documentation conventions
- [.ai/QUICKSTART.md](.ai/QUICKSTART.md) - Quick reference for AI assistants
- [.ai/TOOLING.md](.ai/TOOLING.md) - Tool selection guide

### Code Features
- [docs/specialists.rst](docs/specialists.rst) - Specialist system overview
- [docs/build_specialist.rst](docs/build_specialist.rst) - Building specialists
- [docs/memory.rst](docs/memory.rst) - Memory system
- [docs/streaming.rst](docs/streaming.rst) - Streaming responses

---

## 🚀 Deployment & Operations

### Deployment
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [compose.yaml](compose.yaml) - Docker Compose configuration
- [k8s/](k8s/) - Kubernetes manifests
- [configure-gpu.sh](configure-gpu.sh) - GPU setup

### Hardware Support
- [docs/hardware.rst](docs/hardware.rst) - GPU setup (CUDA/ROCm/Metal/Vulkan)
- [docs/sbc.rst](docs/sbc.rst) - Single-board computers (Raspberry Pi, etc.)

### Configuration
- [docs/configuration.rst](docs/configuration.rst) - Configuration reference
- [brain/config.py](brain/config.py) - Runtime configuration
- [.env.example](.env.example) - Environment variables template

---

## 🎨 Adapters & Integrations

### Official Adapters
- [ada-client/](ada-client/) - Shared Python client library
- [adapters/cli/](adapters/cli/) - Command-line interface (REPL)
- [frontend/](frontend/) - Web UI (nginx + vanilla JS)
- [matrix-bridge/](matrix-bridge/) - Matrix bot integration
- [ada-mcp/](ada-mcp/) - Model Context Protocol server

### Adapter Documentation
- [docs/adapters.rst](docs/adapters.rst) - Building adapters
- [ada-mcp/README.md](ada-mcp/README.md) - MCP integration guide
- [ada.nvim/README.md](ada.nvim/README.md) - Neovim plugin

---

## 📖 Philosophy & Community

### Project Philosophy
- [docs/documentation_philosophy.rst](docs/documentation_philosophy.rst) - Why we document this way
- [docs/empathetic_documentation.rst](docs/empathetic_documentation.rst) - Empathetic docs approach
- [docs/xenofeminism.rst](docs/xenofeminism.rst) - Xenofeminist principles

### Community
- [COMMUNITY_GUIDELINES.md](COMMUNITY_GUIDELINES.md) - Full guidelines
- [COMMUNITY_QUICK.md](COMMUNITY_QUICK.md) - Quick reference
- [LICENSE](LICENSE) - Project license

---

## 🗂️ Archive & History

### Release Notes
- [RELEASE_v2.3.0.md](RELEASE_v2.3.0.md) - v2.3.0 (Latest)
- [RELEASE_v2.2.0.md](RELEASE_v2.2.0.md) - v2.2.0 (Biomimetic memory)
- [RELEASE_v2.0.0.md](RELEASE_v2.0.0.md) - v2.0.0 (Token monitoring)
- [RELEASE_v1.6.0.md](RELEASE_v1.6.0.md) - v1.6.0
- [CHANGELOG.md](CHANGELOG.md) - Complete changelog

### Experimental Work
- [archive/](archive/) - Archived experiments
- [archive/phase_experiments/](archive/phase_experiments/) - Phase runner scripts (exploratory)

---

## 🔍 Finding What You Need

### I want to...

**...understand how Ada works**
→ [README.md](README.md) → [docs/architecture.rst](docs/architecture.rst) → [.ai/context.md](.ai/context.md)

**...install and run Ada**
→ [docs/getting_started.rst](docs/getting_started.rst) → [DEPLOYMENT.md](DEPLOYMENT.md)

**...understand the biomimetic memory research**
→ [docs/research/CONTEXTUAL_MALLEABILITY_READY_FOR_TINKERERS.md](docs/research/CONTEXTUAL_MALLEABILITY_READY_FOR_TINKERERS.md) → [.ai/RESEARCH-FINDINGS-V2.2.md](.ai/RESEARCH-FINDINGS-V2.2.md)

**...build a new specialist**
→ [docs/build_specialist.rst](docs/build_specialist.rst) → [.ai/specialist-registry.json](.ai/specialist-registry.json)

**...integrate Ada with my tool**
→ [docs/adapters.rst](docs/adapters.rst) → [ada-client/README.md](ada-client/README.md)

**...understand the code completion work**
→ [benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md](benchmarks/BENCHMARK_RESULTS_QWEN_FIM.md) → [docs/sessions/SESSION_CODE_COMPLETION_MVP.md](docs/sessions/SESSION_CODE_COMPLETION_MVP.md)

**...run tests**
→ [.ai/TESTING.md](.ai/TESTING.md) → [pytest.ini](pytest.ini)

**...contribute**
→ [COMMUNITY_GUIDELINES.md](COMMUNITY_GUIDELINES.md) → [docs/development.rst](docs/development.rst)

---

## 📂 Directory Structure

```
ada-v1/
├── .ai/                    # Machine-readable documentation
├── ada-client/             # Shared Python client library
├── ada-mcp/                # MCP server integration
├── ada.nvim/               # Neovim plugin
├── adapters/               # Alternative interfaces (CLI, Matrix, etc.)
├── benchmarks/             # Performance benchmarks
├── brain/                  # Core backend (FastAPI)
├── docs/                   # Sphinx documentation
│   ├── research/           # Research documentation
│   └── sessions/           # Session logs
├── frontend/               # Web UI
├── matrix-bridge/          # Matrix bot
├── scripts/                # Utility scripts
├── seed/                   # Initial data (persona, FAQs)
└── tests/                  # Test suite (452 tests!)
```

---

**Navigation Tip:** Use your editor's fuzzy file finder (Ctrl+P in VS Code) to quickly jump to any document!

**Last Doc Reorganization:** December 18, 2025 🧹✨
