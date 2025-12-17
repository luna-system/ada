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

**New here?** 👉 See [Zero to Ada](docs/zero_to_ada.rst) for the fastest path from nothing to working Ada!

Choose your setup method:

- **[Nix](#nix-flake)** - Works on any system, instant Python 3.13 (recommended for most users)
- **[Local Mode](#local-mode-no-docker)** - If you already have Python 3.13
- **[Docker Mode](#docker-mode-optional)** - Containerized deployment

### Local Mode (No Docker!)

#### 1. Install Prerequisites

- **Python 3.13+** (required)
  
  **Don't have Python 3.13?** Your distro might not have it yet (Ubuntu 24.04 maxes at 3.12).  
  👉 **Use [Nix](#nix-flake)** for instant Python 3.13 - no compilation needed!
  
- **Ollama** (required) - Get from [ollama.ai](https://ollama.ai)
- **8GB+ RAM** recommended
- **GPU** (optional) - CUDA, ROCm, or Metal for faster inference

### 2. Setup

```bash
# Clone repository
git clone https://github.com/luna-system/ada.git
cd ada

# Run setup wizard
python3 ada_cli.py setup

# Pull a model
ollama pull deepseek-r1:14b

# Start Ada
ada run
```

**That's it!** Ada runs at http://localhost:7000

### 3. Use Ada

```bash
# Check status
ada status

# Chat from terminal
ada chat "What's Python?"

# Interactive CLI
ada-cli

# Web UI (optional)
cd frontend && npm run dev
```

### 4. Customize (Optional)

```bash
# Change model
ollama pull llama3.1
# Edit .env: OLLAMA_MODEL=llama3.1
ada run

# Custom personality
cp examples/personas/coding-buddy.md persona.md
ada run

# Change AI name
# Edit .env: AI_NAME=Jarvis, AI_USER_NAME=Tony
```

See [docs/local_mode.rst](docs/local_mode.rst) for complete guide.

---

### Nix Flake

For reproducible, declarative environments:

```bash
# Development shell
nix develop

# Or with automatic activation
direnv allow

# Run Ada directly
nix run github:luna-system/ada

# Build package
nix build

# NixOS module available!
```

See [NIX.md](NIX.md) or [docs/nix.rst](docs/nix.rst) for complete guide.

---

## Docker Mode (Optional)

Want isolated services or multi-container orchestration? Ada also supports Docker!

```bash
# Start with Docker instead
docker compose up -d

# With web UI
docker compose --profile web up -d

# With Matrix bridge
docker compose --profile matrix up -d

# With GPU support
docker compose --profile cuda up -d  # NVIDIA
docker compose --profile rocm up -d  # AMD
```

See [docs/external_ollama.md](docs/external_ollama.md) for hybrid setups.

---

## Core Features

**🧠 Memory & RAG** - Semantic search over conversations, automatic consolidation, persona injection. Your memories stay local on YOUR hardware.

**🔌 Extensible Specialists** - Drop a Python file in `brain/specialists/` for new capabilities. Built-in: web search, OCR, media analysis. [Build your own →](https://ada-docs.readthedocs.io/en/latest/build_specialist.html)

**📡 Bidirectional Tool Use** - LLM can request specialists mid-response for more natural, agentic behavior.

**🔒 Privacy by Default** - No telemetry, no tracking, no API keys. Works completely offline after setup.

**📚 Self-Documenting** - Query `/v1/info`, `/v1/specialists`, `/v1/schema` for complete introspection.

**⌨️ Editor Integration** - Use Ada from VSCode, Neovim, Helix via [Model Context Protocol](ada-mcp/).

**📖 Full Documentation** - Complete guides at http://localhost:5000/docs (when running) or see [docs/](docs/) folder.

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

**📖 Complete documentation at http://localhost:5000/docs** (when Ada is running)

All guides are in [docs/](docs/) as Sphinx RST files:
- **[Getting Started](docs/getting_started.rst)** - Quick setup with `ada` CLI
- **[Local Mode Guide](docs/local_mode.md)** - Running without Docker
- **[Getting Started from Scratch](docs/getting_started_scratch.rst)** - Customize your AI
- **[Hardware Guide](docs/hardware.rst)** - GPU setup and optimization
- **[Build a Specialist](docs/build_specialist.rst)** - Extend capabilities
- **[Architecture](docs/architecture.rst)** - How it all works
- **[API Reference](docs/api_reference.rst)** - REST API documentation

Start with **Getting Started** for the fastest onboarding!

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

### Commit Messages

Ada uses [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation:

```bash
feat: add new specialist       # New feature → minor version bump
fix: resolve memory leak       # Bug fix → patch version bump
docs: update API reference     # Documentation → patch version bump
```

See [Version Management Guide](docs/versioning.rst) for complete workflow.

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
A: See [Build a Specialist](docs/build_specialist.rst)! We love weird use cases.

**Q: Was this really built with AI?**  
A: Mostly! See [Provenance](#provenance) for full transparency about our human-AI collaboration

---

**Let's build tools that let weird kids make weird things.** 💜
