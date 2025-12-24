# Ollama Setup for Accessibility

Ada supports multiple Ollama configurations to maximize accessibility and minimize bandwidth usage.

## 🎯 Quick Start

**Auto-detect your best option:**
```bash
./scripts/detect-ollama.sh
```

## 📋 Setup Options

### Option 1: Use System Ollama (Recommended)
**Best for:** Bandwidth saving, sharing models across projects

```bash
# Install Ollama system-wide
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

# Use with Ada
export OLLAMA_BASE_URL=http://localhost:11434
docker compose --profile web up
```

### Option 2: Docker Ollama with Model Persistence
**Best for:** Isolation, consistent environments

```bash
# Models will be saved to ./data/ollama
docker compose --profile ollama --profile web up
```

### Option 3: Share System Models with Docker
**Best for:** Avoiding duplicate downloads

```bash
# Find your system Ollama directory
find /home /usr /var -name ".ollama" 2>/dev/null

# Share models with Docker
export OLLAMA_HOST_DIR="$HOME/.ollama"
docker compose --profile ollama --profile web up
```

## 🔧 Troubleshooting

### Docker Build Cache Issues
If you see `Cache export is not supported for the docker driver`:

```yaml
# This has been fixed in compose.yaml
# cache_to is now commented out by default
```

### Model Re-downloads
Models should only download once. If they re-download:

1. **Check volume persistence:** `docker volume ls`
2. **Check mount path:** `echo $OLLAMA_HOST_DIR`
3. **Use system Ollama:** Avoids Docker entirely

### Network Issues
For limited bandwidth:

1. **Use system Ollama** (no Docker model downloads)
2. **Share models** between Ada and other projects
3. **Download once** - models persist across restarts

## 🌍 Accessibility Features

- **Model persistence:** Download once, use forever
- **Bandwidth awareness:** Multiple options to avoid re-downloads  
- **Flexible setup:** System, Docker, or hybrid approaches
- **Auto-detection:** Script finds the best configuration
- **Clear guidance:** Error messages explain next steps

## 📱 Development Workflow

For development (frequent Docker rebuilds):

```bash
# Option A: Use system Ollama (no Docker models)
export OLLAMA_BASE_URL=http://localhost:11434

# Option B: Share system models with Docker  
export OLLAMA_HOST_DIR="$HOME/.ollama"

# Then develop normally
docker compose --profile web up
```