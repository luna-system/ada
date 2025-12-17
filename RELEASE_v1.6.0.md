# Ada v1.6.0 - Local Mode Release Notes

## 🎉 Major New Feature: Run Ada Without Docker!

Ada now supports running entirely locally without Docker containers. This is the **recommended** deployment mode for most users.

## Quick Start (30 seconds!)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# 2. Clone and setup
git clone https://github.com/luna-system/ada.git
cd ada
python3 ada_main.py setup

# 3. Pull a model
ollama pull deepseek-r1:14b

# 4. Run Ada!
ada run
```

That's it! Ada runs at http://localhost:7000 with no Docker containers.

## Master CLI Commands

```bash
ada setup      # Setup wizard (venv, deps, .env)
ada doctor     # Health check (Python, Ollama, ChromaDB status)
ada run        # Start Ada (auto-detects local/Docker)
ada status     # Show service status
ada chat "hi"  # Quick one-shot query
ada stop       # Stop all services
ada logs       # View logs (Docker mode)
```

## Auto-Detection

The `ada run` command automatically detects your environment:

- **Local Ollama found** → Uses local mode (embedded ChromaDB)
- **Docker available, no Ollama** → Uses Docker mode
- **Neither found** → Shows installation instructions

You can force a specific mode:
```bash
ada run --local  # Force local mode
ada run --docker # Force Docker mode
ada run --dev    # Development mode (hot reload)
```

## Local vs Docker Comparison

| Feature | Local Mode | Docker Mode |
|---------|-----------|-------------|
| **Setup Time** | < 5 minutes | 10-15 minutes |
| **Memory Usage** | ~2GB | ~4GB |
| **Startup Time** | < 5 seconds | ~30 seconds |
| **GPU Support** | Native (CUDA/ROCm/Metal) | Requires passthrough |
| **Development** | Hot reload built-in | Requires rebuild |
| **Model Storage** | Single shared copy | Separate volume |
| **Data Backup** | Simple `./data/` folder | Container volumes |

## What Changed

### New Files
- **ada_main.py** - Master CLI tool with Click framework
- **docs/local_mode.md** - Comprehensive local mode guide

### Updated Files
- **brain/config.py** - Added CHROMA_MODE and DATA_DIR support
- **brain/rag_store.py** - Already supported embedded ChromaDB!
- **pyproject.toml** - Added Click dependency, ada command entry point
- **.env.example** - Local mode as Option 1 (recommended)
- **README.md** - Local quick start first, Docker as optional

### Configuration
```bash
# .env for local mode
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_MODE=embedded
DATA_DIR=./data
```

## Benefits of Local Mode

1. **Faster** - No container orchestration overhead
2. **Lighter** - One Ollama instance shared across tools
3. **Native GPU** - Direct hardware access, no passthrough config
4. **Better DX** - Hot reload, native debugging
5. **Simpler Backups** - Just copy `./data/` folder
6. **No Duplication** - Models stored once, used everywhere

## Docker Still Supported

Docker mode remains fully supported for:
- **Production deployments** with multiple services
- **Web UI** (nginx)
- **Matrix bridge**
- **Isolated testing** environments
- **Teams** needing consistent setup

## Migration Path

### From Docker to Local

```bash
# 1. Export data from Docker
docker run --rm -v ada-v1_chroma-data:/data -v $(pwd)/data:/backup \
  alpine tar -czf /backup/chroma.tar.gz -C /data .

# 2. Extract locally
mkdir -p data/chroma
tar -xzf data/chroma.tar.gz -C data/chroma/

# 3. Update .env for local mode
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_MODE=embedded

# 4. Start local
ada run --local
```

### From Local to Docker

```bash
# 1. Data already in ./data/
# 2. Update .env for Docker mode
OLLAMA_BASE_URL=http://ollama:11434
CHROMA_URL=http://chroma:8000
COMPOSE_PROFILES=ollama

# 3. Start Docker
docker compose up -d
```

## Hybrid Setups

You can mix and match:

```bash
# Local brain + Docker Ollama
OLLAMA_BASE_URL=http://localhost:11434 ada run --local
docker compose up -d ollama

# Local brain + Docker web UI
ada run --local &
docker compose up -d frontend
```

## Examples

### Development Workflow
```bash
# Start in dev mode (hot reload)
ada run --dev

# Edit brain/*.py files
# Changes apply immediately!

# Run tests
pytest tests/
```

### Quick Chat
```bash
# One-shot query
ada chat "What's Python?"

# Interactive mode
ada-cli  # From adapters/cli package
```

### Custom Model
```bash
ollama pull llama3.1:70b
# Edit .env: OLLAMA_MODEL=llama3.1:70b
ada run
```

## Troubleshooting

### "Ollama not running"
```bash
ollama serve
# Then: ada run
```

### "Port 7000 in use"
```bash
ada run --port 8000
```

### "Permission denied: data/"
```bash
chmod -R 755 data/
```

## Philosophy

> **Docker should be a bonus, not a requirement.**

We built Ada to be:
- **Accessible** - Run on any machine with Python and Ollama
- **Portable** - Copy the `data/` folder, you're migrated
- **Hackable** - Edit code, see changes immediately
- **Free** - No cloud, no subscriptions, no API costs
- **Private** - Your data never leaves your machine

Local mode embodies these values. Docker mode adds orchestration for those who need it.

## Next Steps

1. **Try it:** `ada run`
2. **Read the guide:** [docs/local_mode.md](docs/local_mode.md)
3. **Join the community:** https://github.com/luna-system/ada/discussions

---

## Version Details

**Version:** v1.6.0  
**Released:** December 16, 2025  
**Type:** Minor (new feature)  
**Breaking Changes:** None

**Download:**
```bash
git clone https://github.com/luna-system/ada.git
cd ada
git checkout v1.6.0
```

**Tag Message:**
> Major new feature: Run Ada without Docker! Master CLI tool with auto-detection,
> embedded ChromaDB, setup wizard, and comprehensive local mode documentation.
> Makes Ada more accessible and portable while keeping Docker fully supported
> for production deployments.

---

**Made with 💜 by the Ada team**  
*Docker optional, autonomy essential.*
