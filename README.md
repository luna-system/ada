# Ada

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](#quick-start)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-v1.1-green.svg)](ada-mcp/)
[![AI-Assisted](https://img.shields.io/badge/built%20with-AI%20assistance-blueviolet.svg)](#provenance)

**Personal AI with enterprise features, running on your hardware.**

Named after Ada Lovelace, the first programmer. Build AI assistants with memory, web search, vision, and tool use - features that usually cost $20-200/month - using any open model.

🔓 **Always free and open source** • 🏠 **Runs entirely local** • 🔧 **Extensible by design** • 📚 **Self-documenting architecture**

---

## Why Ada?

Most AI assistants lock essential features behind subscriptions:
- ChatGPT Plus ($20/mo) for web search and memory
- Claude Pro ($20/mo) for longer conversations  
- Custom GPTs ($20/mo) for personality and tools
- Enterprise APIs ($$$/mo) for embeddings and RAG

**Ada gives you these features for free**, running on models you choose, with no API costs or cloud dependencies.

### What You Get

| Feature | ChatGPT Plus | Claude Pro | Gemini Advanced | Ada |
|---------|--------------|------------|-----------------|-----|
| Streaming responses | ✅ | ✅ | ✅ | ✅ |
| Long-term memory | ✅ | ✅ | ✅ | ✅ |
| Web search | ✅ $20/mo | ❌ | ✅ | ✅ Free |
| Vision/OCR | ✅ | ✅ | ✅ | ✅ |
| Custom personality | ✅ | ✅ | Limited | ✅ |
| Custom tools | ✅ | ✅ | ❌ | ✅ |
| Runs offline | ❌ | ❌ | ❌ | ✅ |
| Your data stays local | ❌ | ❌ | ❌ | ✅ |
| Hackable/extensible | ❌ | ❌ | ❌ | ✅ |
| **Cost** | **$20-60/mo** | **$20/mo** | **$20/mo** | **$0** |

**The catch?** You need hardware to run the LLM (8GB+ VRAM recommended, or CPU-only works). But you can swap models freely, pay nothing for inference, and keep your data private.

---

## Quick Start

### 1. Install Prerequisites

- **Docker & Docker Compose** (required)
- **Docker BuildX** (recommended for fast builds)
  - Included with Docker Desktop
  - Linux: Run `./scripts/setup_buildx.sh` (auto-detects your distro)
  - Or manually install: `sudo pacman -S docker-buildx` (Arch), `sudo apt install docker-buildx-plugin` (Debian/Ubuntu)
- **Disk Space** ⚠️ **Important!**
  - Minimum: 20GB free space
  - Recommended: 50GB+ (allows multiple models)
  - Large models (DeepSeek R1): 15-20GB each
  - Tip: Run `./scripts/check_disk_space.sh` to monitor usage
- **GPU** (optional but recommended)
  - NVIDIA (CUDA) - Widest support
  - AMD (ROCm) - Great performance, Ada's default config
  - Apple Silicon (Metal) - M1/M2/M3/M4 Macs
  - CPU-only works but is slower
- **RAM**
  - Minimum: 8GB (small models)
  - Recommended: 16GB+ (larger models)

See [Hardware Guide](/docs/hardware.rst) for detailed setup and GPU configuration.

### 2. Clone and Setup

```bash
git clone https://github.com/luna-system/ada.git
cd ada

# Set up BuildX for fast builds (optional but recommended)
./scripts/setup_buildx.sh

# Create data directories and check prerequisites
./setup.sh

# Start Ada (CPU-only by default, headless)
docker compose up -d

# With web UI
docker compose --profile web up -d

# With Matrix bridge  
docker compose --profile matrix up -d

# With both web UI and Matrix
docker compose --profile web --profile matrix up -d

# OR with GPU acceleration (add to any of the above):
docker compose --profile cuda up -d             # NVIDIA GPUs
docker compose --profile rocm up -d             # AMD GPUs
docker compose --profile cuda --profile web up -d  # GPU + web UI
```

That's it! Ada will:
- Pull and start core services (Ollama, ChromaDB, brain API)
- Download the default model (DeepSeek-R1, ~4GB)
- Start interfaces based on profiles:
  - **Default (headless)**: API only at http://localhost:8000
  - **--profile web**: Web UI at http://localhost:5000
  - **--profile matrix**: Matrix bridge (see [setup](matrix-bridge/README.md))
  - **CLI**: `pip install -e adapters/cli && ada-cli` (works with any profile)

### 3. Customize (Optional)

**Change the AI model:**
```bash
# Edit .env
OLLAMA_MODEL=llama3.1
# or mistral, qwen, gemma, etc. - any model Ollama supports
```

**Give your AI a different personality:**
```bash
# Copy an example persona or create your own
cp examples/personas/coding-buddy.md persona.md
docker compose restart brain
```

**Change your AI's name:**
```bash
# In .env
AI_NAME=Jarvis
AI_USER_NAME=Tony
```
https://ada-docs.readthedocs.io/) for detailed customization.

---

## Core Features

**🧠 Memory & RAG** - Semantic search over conversations, automatic consolidation, persona injection. Your memories stay local on YOUR hardware.

**🔌 Extensible Specialists** - Drop a Python file in `brain/specialists/` for new capabilities. Built-in: web search, OCR, media analysis. [Build your own →](https://ada-docs.readthedocs.io/en/latest/build_specialist.html)

**📡 Bidirectional Tool Use** - LLM can request specialists mid-response for more natural, agentic behavior.

**🔒 Privacy by Default** - No telemetry, no tracking, no API keys. Works completely offline after setup.

**📚 Self-Documenting** - Query `/v1/info`, `/v1/specialists`, `/v1/schema` for complete introspection.

**⌨️ Editor Integration** - Use Ada from VSCode, Neovim, Helix via [Model Context Protocol](ada-mcp/).

See [full documentation](https://ada-docs.readthedocs.io/) for detail
See [ada-mcp/](/ada-mcp/) for setup instructions.

---

## Project Structure

```
ada/
├── brain/              # FastAPI backend + LLM orchestration
│   ├── specialists/    # Extensible plugin system
│   ├── app.py         # Main API endpoints
│   ├── llm.py         # LLM client (Ollama)
│   └── rag_store.py   # Vector memory (ChromaDB)
├── frontend/          # Web interface (Astro + vanilla JS)
├── docs/              # Sphinx documentation
├── examples/
│   └── personas/      # Example AI personalities
└── compose.yaml       # Docker orchestration
```

---

## Documentation

**Full documentation available at http://localhost:5000/docs** when running.

**Quick links:**
- [Getting Started from Scratch](/docs/getting_started_scratch.rst) - Customize your AI
- [Hardware Guide](/docs/hardware.rst) - GPU setup, hardware recommendations
- [SBC Guide](/docs/sbc.rst) - Running Ada on Raspberry Pi, Orange Pi, etc.
- [Build Your First Specialist](/docs/build_specialist.rst) - Extend capabilities
- [Architecture Guide](/docs/architecture.rst) - How it all works
- [API Reference](/docs/api_reference.rst) - Complete API docs
- [Specialists](/docs/specialists.rst) - Plugin system documentation
- [Xenofeminism & Design](/docs/xenofeminism.rst) - Our philosophical foundation
- [Principles](/PRINCIPLES.md) - Why Ada is always free and open

---

## Philosophy

Ada is built on core principles:

1. **Always free and open source** - No paywalls, ever
2. **Privacy by default** - Your data stays local
3. **Local-first** - No cloud dependencies
4. **Hackable** - Readable code, documented architecture
5. **No lock-in** - Standard formats, easy migration

Read the full [PRINCIPLES.md](PRINCIPLES.md) for our commitments.

---

## Use Cases

**For tinkerers:**
- Build an AI that speaks only in haiku
- Create a worldbuilding assistant for your novel
- Make a personal ADHD management system
- Design custom tools for YOUR workflow

**For developers:**
- Learn how RAG systems actually work
- Experiment with prompt engineering
- Build proof-of-concepts without API costs
- Understand bidirectional tool use

**For privacy advocates:**
- Keep conversations off corporate servers
- Control your own data
- No terms of service changes
- Run entirely air-gapped if needed

**For researchers:**
- Experiment without budget constraints
- Try unusual architectures
- Test edge cases freely
- Publish reproducible results

---

## Contributing

We welcome:
- 🐛 Bug reports and fixes
- 📚 Documentation improvements
- 🔌 New specialists (share your weird ideas!)
- 💡 Architecture suggestions
- 🧪 Testing improvements

Open an issue or pull request on [GitHub](https://github.com/luna-system/ada).

**Your contributions join the commons** under CC0 1.0 Universal, helping democratize AI infrastructure for everyone.

---

## Requirements

**Minimum:** Docker, 8GB RAM, 10GB disk, any CPU  
**Recommended:** 16GB RAM, 8GB+ VRAM GPU, 50GB SSD  
**Tested on:** Ubuntu 22.04+, macOS 13+ (Apple Silicon), Windows 11 WSL2

See [Hardware Guide](https://ada-docs.readthedocs.io/en/latest/hardware.html) for GPU setup and [SBC Guide](https://ada-docs.readthedocs.io/en/latest/sbc.html) for Raspberry Pi/ARM boards.

---

## Provenance

This project is developed collaboratively by [Luna](https://github.com/luna-system) in partnership with **Claude Sonnet 4.5** (Anthropic).

**What this means:**
- Significant portions of code, documentation, and architecture were generated or co-created with AI assistance
- All AI-generated content has been reviewed, tested, and refined by human maintainers
- Design decisions, principles, and project direction remain human-driven
- This collaborative process is a point of pride, not hidden - it's part of how we build in 2025

**Why we're transparent about this:**
- Honesty about our tools and methods builds trust
- AI assistance democratizes software development - this is a feature, not a bug
- We believe in showing our work, including our collaboration with AI systems
- Others should know what's possible when humans and AI work together well

**What hasn't changed:**
- All code is reviewed, tested, and maintained by humans
- Architecture and design decisions are made with human judgment
- The project's values and principles are deeply human
- Quality standards remain high regardless of authorship

This disclosure doesn't diminish the work - it celebrates a new way of building software that we believe makes projects like Ada possible for more people.

---

## License

**CC0 1.0 Universal (Public Domain)**

To the extent possible under law, the authors have waived all copyright and related rights to this work. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

See [LICENSE](LICENSE) for details.

---

## Credits

Named after **Ada Lovelace** (1815-1852), who wrote the first computer program and imagined machines that could create art and music - not just calculate.

Built with:
- [Ollama](https://ollama.ai) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Claude Sonnet 4.5](https://anthropic.com/claude) - AI development partner
A: It's stable for personal use. For production workloads, you'll want to add authentication, rate limiting, and monitoring.

**Q: How do I contribute a new specialist?**  
A: See [Build Your First Specialist](/docs/BUILD_YOUR_FIRST_SPECIALIST.md)! We love weird use cases.

---

**Let's build tools that let weird kihttps://ada-docs.readthedocs.io/en/latest/build_specialist.html)! We love weird use cases.

**Q: Was this really built with AI?**  
A: Mostly! See [Provenance](#provenance) for full transparency about our human-AI collaboration
