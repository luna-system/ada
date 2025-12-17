# Disk Usage Optimization for Ada

**Current Audit Results:**
- 📊 Ollama models: ~4.9GB (DeepSeek R1)
- 📦 Docker images: ~106GB (!!!)  
- 💾 ChromaDB data: Minimal
- 🗃️ Docker build cache: ~9.7GB

**Total Ada footprint: ~120GB** (before user adds more models!)

---

## Quick Wins (Immediate)

### 1. Clean Up Old Docker Images & Cache 🧹

```bash
# Remove unused images (safe - keeps running containers)
docker image prune -a

# Remove build cache
docker builder prune -a

# Remove unused volumes
docker volume prune

# Nuclear option (removes EVERYTHING not running)
docker system prune -a --volumes

# Expected savings: 50-100GB
```

**Safe version (recommended):**
```bash
# Only remove dangling images
docker image prune

# Only remove old build cache
docker builder prune --filter "until=24h"

# Expected savings: 10-50GB
```

### 2. Add .dockerignore Files ✂️

Prevent copying unnecessary files into images:

```bash
# Already exists in root - verify it's comprehensive
cat .dockerignore

# Add to matrix-bridge/ if missing
cat matrix-bridge/.dockerignore
```

### 3. Enable Log Rotation 📝

```yaml
# Add to compose.yaml services:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 4. Document Model Sizes Upfront 📖

Update README with clear expectations:
- Minimum: 10GB (small model)
- Recommended: 30GB (medium model)  
- DeepSeek R1: ~15GB
- Total with Docker: 20-50GB

---

## Medium-Term Optimizations

### 5. Multi-Stage Docker Builds 🏗️

Reduce image sizes by 30-50%:

```dockerfile
# Example for brain/Dockerfile
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
```

### 6. Use Alpine Base Images (Where Possible) 🏔️

Some images could use alpine (60MB → 5MB base):

```dockerfile
# For services without complex dependencies
FROM python:3.13-alpine
# Note: Ollama needs glibc, so can't use alpine there
```

### 7. Ollama Model Management 🤖

```bash
# List models and sizes
ollama list

# Remove unused models
ollama rm model-name

# Use model linking for shared models
# (multiple containers can share same model file)
```

### 8. ChromaDB Cleanup 🗄️

```python
# scripts/cleanup_old_memories.py (create this)
# - Remove memories older than retention period
# - Compact ChromaDB database
# - Vacuum SQLite files
```

---

## Long-Term Strategies

### 9. Quantized Models 📉

Use smaller quantized versions:
- `deepseek-r1:8b` instead of `:14b` (saves 6-8GB)
- `q4_K_M` quantization (smaller with minimal quality loss)

### 10. Shared Ollama Instance 🔗

Multiple Ada instances can share one Ollama:

```yaml
# Don't run Ollama per-instance
# Point to shared Ollama server
environment:
  - OLLAMA_BASE_URL=http://shared-ollama:11434
```

### 11. External Storage for Models 💾

Mount Ollama models from larger disk:

```yaml
volumes:
  - /mnt/large-disk/ollama:/root/.ollama
```

---

## Recommended Maintenance Schedule

### Daily (Automatic)
```bash
# Add to cron or systemd timer
docker image prune -f  # Remove dangling images
```

### Weekly
```bash
docker system prune -f  # Remove unused containers/networks
docker builder prune --filter "until=168h" -f  # Week-old cache
```

### Monthly
```bash
# Review Ollama models
ollama list
# Remove unused models manually

# Check total usage
docker system df
du -sh ~/Code/ada-v1/data/*
```

### On Low Disk Space
```bash
# Emergency cleanup
docker system prune -a --volumes -f
# WARNING: Removes all unused images/volumes!
```

---

## Configuration Changes (Apply Now)

### Add Log Rotation to compose.yaml

```yaml
x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

services:
  brain:
    logging: *default-logging
    # ... rest of config
    
  matrix-bridge:
    logging: *default-logging
    # ... rest of config
```

### Add Backup Cleanup Script

```bash
# scripts/cleanup_old_backups.sh
#!/bin/bash
# Keep only last 7 days of backups
find ./data/backups -name "chroma-*.sqlite3" -mtime +7 -delete
```

### Add Health Check Script

```bash
# scripts/check_disk_space.sh
#!/bin/bash
THRESHOLD=80  # Warn if >80% full

USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "⚠️  WARNING: Disk usage at ${USAGE}%"
  echo "Run: docker system prune -a"
  echo "Or: ollama list and remove unused models"
fi
```

---

## Expected Savings

| Optimization | Savings | Effort | Risk |
|--------------|---------|--------|------|
| **docker system prune -a** | 50-100GB | 1 min | Low* |
| **Log rotation** | 100MB-1GB | 5 min | None |
| **.dockerignore** | 10-50MB/image | 5 min | None |
| **Multi-stage builds** | 200-400MB | 1 hour | Low |
| **Remove unused models** | 5-15GB/model | 2 min | None |
| **Alpine base images** | 50-100MB/image | 2 hours | Medium** |
| **Quantized models** | 5-10GB | 10 min | Low*** |

\* *Safe if you rebuild images after*  
\*\* *Some dependencies don't work on Alpine*  
\*\*\* *Slight quality degradation*

---

## User-Facing Documentation Updates

### README.md - System Requirements Section

```markdown
## System Requirements

**Minimum:**
- 8GB RAM
- 20GB free disk space
- x86_64 or ARM64 CPU

**Recommended:**
- 16GB RAM
- 50GB free disk space (allows multiple models)
- GPU (NVIDIA/AMD/Apple Silicon)

**Disk Space Breakdown:**
- Base system (Docker images): ~2GB
- Ollama model (DeepSeek R1): ~15GB
- ChromaDB data: ~1GB (grows over time)
- Logs & cache: ~1-2GB

**Managing Disk Usage:**
See [Disk Management Guide](docs/disk_management.rst)
```

### New Documentation Page

Create `docs/disk_management.rst` with:
- Disk usage expectations
- Cleanup commands
- Model size comparison table
- Troubleshooting full disk scenarios

---

## Immediate Action Items

1. **Add log rotation to compose.yaml** (5 minutes)
2. **Add .dockerignore to matrix-bridge/** (2 minutes)
3. **Create cleanup scripts** (15 minutes)
4. **Update README with disk requirements** (10 minutes)
5. **Run `docker system prune -a`** (user decision)

---

## Detection & Warning System

### Add to Health Check Endpoint

```python
# brain/app.py
@app.get("/v1/healthz")
async def healthz():
    # ... existing checks
    
    # Check disk space
    import shutil
    disk = shutil.disk_usage(".")
    disk_usage_pct = (disk.used / disk.total) * 100
    
    warnings = []
    if disk_usage_pct > 80:
        warnings.append(f"Disk usage high: {disk_usage_pct:.1f}%")
    
    return {
        "status": "healthy",
        "disk_usage_percent": round(disk_usage_pct, 1),
        "warnings": warnings
    }
```

### Add to Web UI

Show disk warning banner when >80% full.

---

## Pain Point Analysis

**What happened to the kiddo:**
- Starting from "mostly full" disk
- Added Ada (~20GB base)
- Pulled DeepSeek R1 model (~15GB)
- **Total: ~35GB added suddenly**
- Result: Full disk 😰

**Prevention:**
1. ✅ Check available space before install
2. ✅ Warn during model pull
3. ✅ Document requirements clearly
4. ✅ Provide cleanup tools

---

## Quick Reference Commands

```bash
# Check Ada's disk usage
du -sh ~/Code/ada-v1/data/*
docker system df

# Clean up safely
docker image prune
docker builder prune --filter "until=24h"

# Clean up aggressively
docker system prune -a

# Check Ollama models
docker exec ada-v1-ollama-1 ollama list

# Remove unused model
docker exec ada-v1-ollama-1 ollama rm model-name

# Check available disk space
df -h .
```

---

**Status:** Needs implementation (log rotation, docs, scripts)  
**Priority:** High (affects user experience significantly)  
**Estimated time:** 1-2 hours for full implementation
