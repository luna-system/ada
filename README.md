# Ada

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](#quick-start)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-v1.1-green.svg)](ada-mcp/)

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
- **GPU** (optional but recommended)
  - NVIDIA (CUDA) - Widest support
  - AMD (ROCm) - Great performance, Ada's default config
  - Apple Silicon (Metal) - M1/M2/M3/M4 Macs
  - CPU-only works but is slower
- **8GB+ RAM** for smaller models, 16GB+ for larger ones

See [Hardware Guide](/docs/hardware.rst) for detailed setup and recommendations.

### 2. Clone and Setup

```bash
git clone https://github.com/luna-system/ada.git
cd ada
./setup.sh          # Creates data directories and checks prerequisites
docker compose up -d
```

That's it! Ada will:
- Pull and start all services (Ollama, ChromaDB, frontend, brain API)
- Download the default model (DeepSeek-R1, ~4GB)
- Start the web interface at **http://localhost:5000**

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

See [Getting Started from Scratch](/docs/GETTING_STARTED_FROM_SCRATCH.md) for detailed customization.

---

## Core Features

### 🧠 Memory & RAG

Ada remembers conversations using **Retrieval-Augmented Generation (RAG)**:
- Semantic search over past conversations
- Automatic memory consolidation
- Persona and FAQ injection
- Context-aware responses

Unlike subscription services, your memories stay on YOUR hardware in a local ChromaDB instance.

### 🔌 Extensible Specialists

Drop a Python file in \`brain/specialists/\` and Ada gains new capabilities:

**Built-in specialists:**
- **Web search** - Real-time information from the internet
- **OCR** - Extract text from images
- **Media analysis** - Understand images and documents
- **Docs search** - Ada can read her own documentation

**Build your own in minutes:**
```python
# brain/specialists/weather_specialist.py
class WeatherSpecialist(BaseSpecialist):
    async def process(self, location: str):
        # Your weather API logic here
        return SpecialistResult(data={...})
```

See [Building Your First Specialist](/docs/BUILD_YOUR_FIRST_SPECIALIST.md) for a complete tutorial.

### 📡 Bidirectional Tool Use

Unlike most AI frameworks, Ada's specialists work **bidirectionally**:
- 👉 **User → AI:** "Search the web for Python 3.13 release date"
- 👈 **AI → Specialist → AI:** LLM emits \`<web_search>query</web_search>\` mid-response, gets results, continues naturally

This creates more natural, agentic behavior.

### 🔒 Privacy by Default

- ✅ No telemetry or tracking
- ✅ Conversations stay on your hardware
- ✅ No API keys required for core features
- ✅ Works completely offline after setup

Your data is yours. No companies, no cloud, no compromise.

### 📚 Self-Documenting

Ada can introspect herself:
- \`GET /v1/info\` - All capabilities and endpoints
- \`GET /v1/specialists\` - Available tools with schemas
- \`GET /v1/schema\` - Complete API documentation
- Built-in docs specialist - Ada reads her own Sphinx documentation

### ⌨️ Editor Integration (v1.1+)

Use Ada directly from your editor via Model Context Protocol:
- **VSCode/GitHub Copilot** - Chat with Ada without leaving your code
- **Any MCP-compatible editor** - Neovim, Helix, Zed, etc.
- 4 tools exposed: chat, search memory, add memory, health check

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

### Minimum
- Docker & Docker Compose
- 8GB RAM
- 10GB disk space
- Any CPU (slower but works)

### Recommended
- 16GB RAM
- NVIDIA GPU with 8GB+ VRAM
- 50GB disk space (for multiple models)
- SSD for better performance

### Tested On
- Ubuntu 22.04 / Debian 12
- macOS 13+ (Apple Silicon)
- Windows 11 with WSL2

---

## License

**CC0 1.0 Universal (Public Domain)**

To the extent possible under law, the authors have waived all copyright and related rights to this work. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.

See [LICENSE](LICENSE) for details.

---

## Credits

Built by [Luna](https://github.com/luna-system) with significant contributions from Claude Sonnet 4.5.

Named after **Ada Lovelace** (1815-1852), who wrote the first computer program and imagined machines that could create art and music - not just calculate.

Special thanks to the open source community and projects that make this possible:
- [Ollama](https://ollama.ai) - Local LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

## FAQ

**Q: Do I need a GPU?**  
A: No, but it's MUCH faster. CPU-only works fine for smaller models or if you're patient.

**Q: What models can I use?**  
A: Anything supported by Ollama: Llama, Mistral, Gemma, Qwen, DeepSeek, etc. Just change \`OLLAMA_MODEL\` in \`.env\`.

**Q: How is this different from Open WebUI / text-generation-webui?**  
A: Those are model runners with UIs. Ada is a framework for building personalized AI assistants with memory, tools, and extensibility.

**Q: Can I use commercial APIs like OpenAI instead of local models?**  
A: Yes, but that defeats the purpose. Ada is designed for local/open models to maintain privacy and zero costs.

**Q: Is this production-ready?**  
A: It's stable for personal use. For production workloads, you'll want to add authentication, rate limiting, and monitoring.

**Q: How do I contribute a new specialist?**  
A: See [Build Your First Specialist](/docs/BUILD_YOUR_FIRST_SPECIALIST.md)! We love weird use cases.

---

**Let's build tools that let weird kids build weird things that change the world.** 🚀
