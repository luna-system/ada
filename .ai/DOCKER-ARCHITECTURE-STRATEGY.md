# Docker Architecture Strategy - Ollama Deployment Patterns

**Problem:** Dual-Ollama confusion (Docker CPU vs Local GPU)  
**Solution:** Clear tiering + intentional defaults  
**Philosophy:** Democratic = hackable, not homogeneous

---

## Current Reality Check

**Ollama Service in compose.yaml:**
- Already in `--profile ollama` (not default!)
- Good! This means Docker Ollama is opt-in
- Bad! Our .env defaulted to `http://ollama:11434` (wrong service name for default path)

**The Fix We Just Made:**
- Changed `.env` default: `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- Now brain defaults to local Ollama (fast, GPU)
- Docker Ollama only starts with `--profile ollama` (slow, CPU, for testing)

---

## Recommended Architecture: Hybrid-First

### Default Setup (What Users Get)

```bash
# 1. Install Ollama locally (official way)
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull model
ollama pull qwen2.5-coder:7b

# 3. Start Ada services
git clone https://github.com/luna-system/ada
cd ada
docker compose up -d

# Brain automatically uses local GPU Ollama ✓
```

**What's in Docker:**
- brain (FastAPI orchestration)
- chroma (vector DB)
- web (optional, `--profile web`)
- matrix-bridge (optional, `--profile matrix`)

**What's Local:**
- ollama (LLM inference with GPU access)

**Why:**
- ✅ Local Ollama is official install method (curl script)
- ✅ GPU access is automatic (no Docker passthrough hell)
- ✅ Performance is optimal (137ms TTFT)
- ✅ Upgrades are simple (`ollama pull`)
- ✅ Brain stays containerized (reproducible)

---

## Docker Ollama Profile (Testing/CI)

### When to Use Docker Ollama

```bash
# Start with Docker Ollama (CPU-only, slow)
docker compose --profile ollama up -d
```

**Use cases:**
- CI/CD pipelines (GitHub Actions doesn't have GPU)
- Testing on potato hardware
- Fully airgapped deployments (no local install)
- Initial "does it work?" verification

**Expected performance:**
- TTFT: 6-15 seconds (CPU inference)
- Acceptable for: Testing, one-off queries
- **Not** acceptable for: Real-time coding, chat

**How it works:**
```yaml
services:
  brain:
    environment:
      # With --profile ollama, change this:
      - OLLAMA_BASE_URL=http://ollama:11434
  
  ollama:
    profiles: [ollama]  # Only starts with --profile
    image: ollama/ollama:latest
    # No GPU passthrough - CPU only
```

---

## GPU Docker Profile (Advanced Users)

### If You Really Want Ollama in Docker with GPU

See `compose.profiles.yaml`:

```bash
# NVIDIA GPU
docker compose --profile cuda up -d

# AMD GPU  
docker compose --profile rocm up -d
```

**Requirements:**
- NVIDIA: nvidia-container-toolkit installed
- AMD: ROCm drivers + container support
- Mac: Docker Desktop 4.25+ with GPU passthrough enabled

**Why this is NOT the default:**
- Complex setup (driver toolkit)
- Platform-specific (Linux works, Mac/Windows fragile)
- Debugging GPU issues ≠ beginner-friendly
- Upstream (Ollama docs) recommends local install

**When it makes sense:**
- K8s deployments (centralized GPU pool)
- Multi-user shared instances
- You already have nvidia-container-toolkit working

---

## Mental Model: Separation of Concerns

```
┌─────────────────────────────────────────────────┐
│ SERVICES BY DEPLOYMENT PATTERN                  │
├─────────────────────────────────────────────────┤
│                                                 │
│ Always Docker (Orchestration + Storage)         │
│ ├─ brain         → FastAPI, coordinates        │
│ ├─ chroma        → Vector DB, persistent       │
│ └─ web/matrix   → Optional adapters (profiles) │
│                                                 │
│ Default Local (Heavy Compute)                   │
│ └─ ollama        → LLM inference, needs GPU    │
│                                                 │
│ Optional Docker (Testing/CI)                    │
│ └─ ollama        → CPU-only, slow, --profile   │
└─────────────────────────────────────────────────┘
```

**Principle:** Run services in Docker when isolation/reproducibility matters. Run heavy compute locally when performance matters.

---

## .env Configuration Patterns

### Default (Local Ollama)
```bash
# .env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

Brain uses local GPU Ollama.

### Docker Ollama (Testing)
```bash
# docker-compose.override.yml
services:
  brain:
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
```

Then: `docker compose --profile ollama up -d`

### Remote Ollama (Shared Server)
```bash
# .env
OLLAMA_BASE_URL=http://my-server.local:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

Brain uses remote Ollama instance.

---

## Documentation Strategy

### README.md Quick Start
```markdown
## Installation

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5-coder:7b
```

### 2. Start Ada
```bash
docker compose up -d
```

That's it! Ada brain will automatically use your local Ollama.

### Alternative: Docker Ollama (slower, no GPU)
```bash
docker compose --profile ollama up -d
```
```

### Getting Started Guide
- **First section:** Local Ollama (recommended)
- **Second section:** Docker Ollama (testing/CI)
- **Third section:** GPU Docker profiles (advanced)

### Troubleshooting Section
**"Ada is slow!"**
- Check: `curl http://localhost:11434/api/ps`
- If empty → model not loaded
- If no response → Ollama not running
- Solution: `ollama pull qwen2.5-coder:7b`

**"Which Ollama is Ada using?"**
- Check: `docker compose exec brain printenv | grep OLLAMA`
- `host.docker.internal` → local (fast)
- `ollama:11434` → Docker (slow)

---

## For Kids & Hackers

### Teaching Moment: Why Not Just Docker Everything?

**Docker is great for:**
- Isolation (services don't conflict)
- Reproducibility (works on my machine → works everywhere)
- Easy deployment (one command)

**Docker is not great for:**
- Heavy GPU workloads (passthrough is complex)
- Real-time performance (network overhead)
- Debugging hardware issues

**Ada's approach:**
- Put orchestration in Docker (brain knows how to talk to services)
- Keep heavy compute local (Ollama has direct GPU access)
- **Result:** Best of both worlds!

### Learning Path

1. **Start simple:** Local Ollama + Docker brain
2. **Understand why:** See performance difference (6s vs 137ms)
3. **Experiment:** Try `--profile ollama` to see CPU inference
4. **Advanced:** Try GPU Docker if you want the challenge

---

## Decision Matrix

| Scenario | Deployment | Why |
|----------|-----------|-----|
| **Daily development** | Local Ollama + Docker brain | Fast, simple, best UX |
| **CI/CD testing** | `--profile ollama` | No GPU in CI, reproducible |
| **Learning Docker** | `--profile ollama` | See full stack in containers |
| **Multi-user prod** | K8s + GPU profiles | Centralized, scalable |
| **Potato hardware** | `--profile ollama` | Works on anything (slowly) |
| **Offline/airgap** | `--profile ollama` | No external dependencies |

---

## Success Metrics

### Current (Post-Fix)
- ✅ Default setup uses local GPU Ollama
- ✅ 137ms TTFT (Copilot-class)
- ✅ Docker Ollama is opt-in (`--profile`)
- ✅ Clear documentation path

### Improvements Needed
- 📝 Update README.md with local-first instructions
- 📝 Add troubleshooting section ("which Ollama am I using?")
- 📝 Document all three patterns (local/docker/remote)
- 📝 Add `.env.example` with comments

---

## Philosophical Note: Democratic ≠ Uniform

**Democratic software doesn't mean "one way to run it."**

It means:
- **Transparent:** You can see how it works
- **Modular:** You can swap components
- **Progressive:** Simple start → advanced options
- **Respectful:** Works on your hardware, not idealized setup

Ada runs:
- On a $35 Pi Zero (slowly, but works)
- On a $3000 gaming rig (fast, real-time)
- In Docker, locally, remotely, K8s, whatever

**The architecture supports this by being composable, not prescriptive.**

---

## Implementation Checklist

- [x] Move Docker Ollama to `--profile ollama`
- [x] Change `.env` default to `host.docker.internal`
- [x] Test local Ollama connection (works: 137ms TTFT)
- [ ] Update README.md with local-first instructions
- [ ] Add troubleshooting guide
- [ ] Document Docker Ollama profile usage
- [ ] Create `.env.example` with comments
- [ ] Update getting_started.rst
- [ ] Add architecture diagram to docs

---

## Related Files

- `compose.yaml` - Main Docker Compose config
- `compose.profiles.yaml` - GPU profiles (CUDA/ROCm)
- `.env` - Environment configuration
- `docs/external_ollama.md` - Local Ollama guide
- `docs/getting_started.rst` - Setup instructions
- `.ai/ADAPTIVE-MODEL-WARMING.md` - Model warming strategy

---

**TL;DR:** Default to local Ollama (fast), Docker Ollama is for testing/CI, GPU Docker is for advanced users. This is the democratic way - simple start, advanced options available.
