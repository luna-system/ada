# Ada

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Documentation](https://img.shields.io/badge/docs-read%20online-blue)](https://luna-system.github.io/ada/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-v1.1-green.svg)](ada-mcp/)

**Your personal AI assistant. Runs on your hardware. Learns from your conversations. Free forever.**

Named after Ada Lovelace, the first programmer.

---

## 📖 Documentation

**[→ Read the full docs online](https://luna-system.github.io/ada/)**  
*Or browse the [visual introduction](http://localhost:5000/garden) 🌱 (when running locally)*

*(Docs also available at http://localhost:5000/docs when running locally)*

**Quick links:**
- [Getting Started](https://luna-system.github.io/ada/getting_started.html) - Complete setup guide
- [Zero to Ada](https://luna-system.github.io/ada/zero_to_ada.html) - Fastest path (< 10 min)
- [Hardware Guide](https://luna-system.github.io/ada/hardware.html) - GPU setup (CUDA/ROCm/Metal)
- [Build a Specialist](https://luna-system.github.io/ada/build_specialist.html) - Add custom capabilities
- [API Reference](https://luna-system.github.io/ada/api_reference.html) - REST endpoints
- [Changelog](https://luna-system.github.io/ada/changelog.html) - Version history

---

## Why Ada Exists

AI assistants lock essential features behind subscriptions. Long-term memory, web search, custom personalities, tool use — these cost $20-200/month from commercial providers.

**Ada gives you these features**, running locally on models you choose, with zero API costs. Your conversations never leave your machine.

**The tradeoff:** You provide the compute. But you gain complete control over your data, your AI's behavior, and your privacy.

---

## Quick Start

### 1. Install

```bash
# Option A: Use Nix (recommended - handles Python 3.13 automatically)
nix develop
# or: direnv allow

# Option B: Have Python 3.13 already?
git clone https://github.com/luna-system/ada.git
cd ada
pip install -e .
```

### 2. Get Ollama + Pull a Model

```bash
# Install from ollama.ai
ollama pull deepseek-r1:14b
```

### 3. Run Ada

```bash
# Brain only (headless - use CLI, MCP, Matrix, or direct API)
ada run
# Or: docker compose up -d

# With web UI
docker compose --profile web up -d

# With Matrix bridge
docker compose --profile matrix up -d
```

**That's it.** Ada's brain runs at http://localhost:8000

### 4. Chat

```bash
# Terminal (works with any setup)
ada-cli "What's Python?"

# Web UI (if started with --profile web)
open http://localhost:5000

# VSCode/Neovim
# See ada-mcp/ for Model Context Protocol integration
```

---

## What It Does

- **🧠 Long-term memory** - Semantic search over all your conversations
- **🔌 Web search** - DuckDuckGo integration, wiki lookups
- **👁️ Vision** - OCR text extraction from images
- **🛠️ Tool use** - LLM can invoke specialists mid-response (bidirectional)
- **📝 Custom personality** - Edit `persona.md`, restart
- **🔒 Private by default** - No telemetry, runs offline after setup
- **⚡ Streaming responses** - Real-time token delivery via SSE
- **📡 Multiple interfaces** - CLI, Web UI, Matrix bot, MCP (editor integration)

---

## Core Features

### Memory (RAG)
Every conversation gets embedded and stored locally. Ada remembers context across chats. Automatic consolidation prevents memory bloat.

### Specialists (Plugins)
Drop a Python file in `brain/specialists/` for new capabilities. Built-in:
- `web_search` - DuckDuckGo queries
- `ocr` - Text extraction from images
- `wiki` - Wikipedia + Fandom lookups
- `docs` - Ada can read her own documentation

**[→ Build your own specialist](https://luna-system.github.io/ada/build_specialist.html)**

### Bidirectional Tool Use
The LLM can request specialists mid-response using XML tags:
```
<web_search>climate change 2025</web_search>
```
More natural than traditional function calling.

### Editor Integration (MCP)
Use Ada from VSCode, Cursor, Neovim, Helix via [Model Context Protocol](ada-mcp/):
```bash
cd ada-mcp
npm install
# Add to your editor's MCP config
```

---

## Architecture

```
Interfaces          Brain (FastAPI)              Services
---------          ---------------              --------
CLI                                             ChromaDB (vectors)
Web UI       →→→   Prompt Building     ←←←     Ollama (LLM)
Matrix Bot         + Specialists               External APIs
MCP Server         + Memory/RAG
```

**[→ Architecture details](https://luna-system.github.io/ada/architecture.html)**

---

## Philosophy

Ada is built on these principles:

1. **Always free and open source** - No paywalls, ever
2. **Privacy by default** - Your data stays on your machine
3. **Local-first** - No cloud dependencies after initial model pull
4. **Hackable** - Readable code, simple architecture, documented patterns
5. **No lock-in** - Standard formats, easy to migrate or self-host

We believe AI tools should be:
- Accessible to anyone with modest hardware
- Transparent in their operation
- Respectful of user privacy
- Extensible by users for their unique needs

**Not a product. A tool you control.**

---

## Project Status

**Current:** v2.1.0 (December 2025)

- ✅ Stable for personal use
- ✅ Streaming chat with memory
- ✅ Multiple interfaces (CLI, Web, Matrix, MCP)
- ✅ Extensible specialist system
- ✅ Multi-timescale context caching (~70% faster)
- 🚧 Authentication (bring your own reverse proxy)
- 🚧 Multi-user support (single-user focused currently)

**What's next:** [See roadmap](https://github.com/luna-system/ada/issues)

---

## Requirements

| Spec | Minimum | Recommended |
|------|---------|-------------|
| **RAM** | 8GB | 16GB |
| **Disk** | 10GB | 50GB SSD |
| **GPU** | None (CPU works) | 8GB+ VRAM |
| **OS** | Any (via Docker) | Ubuntu 22.04+, macOS 13+, Windows WSL2 |

**GPU support:** CUDA (NVIDIA), ROCm (AMD), Metal (Apple Silicon), Vulkan

**[→ Detailed hardware guide](https://luna-system.github.io/ada/hardware.html)**

---

## Contributing

We welcome:
- 🐛 Bug reports and fixes
- 📚 Documentation improvements  
- 🔌 New specialists (share your weird ideas!)
- 💡 Architecture suggestions

**Commit format:** [Conventional Commits](https://www.conventionalcommits.org/)
```bash
feat: add wikipedia specialist
fix: resolve memory leak in RAG
docs: update quickstart guide
```

**Your contributions join the commons** under CC0 1.0 Universal.

**[→ Development guide](https://luna-system.github.io/ada/development.html)**

---

## Provenance

This project is developed collaboratively by [Luna](https://github.com/luna-system) with **Claude Sonnet 4.5** (Anthropic) as an AI development partner.

**What this means:**
- Code, docs, and architecture were co-created with AI assistance
- All AI-generated content is reviewed, tested, and refined by humans
- Design decisions and principles remain human-driven
- This collaborative process is a feature, not hidden

**Why we're transparent:**
- AI assistance democratizes software development
- Others should know what's possible with human-AI collaboration
- Honesty builds trust

Quality standards remain high regardless of authorship.

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

---

**Let's build tools that let weird kids make weird things.** 💜
