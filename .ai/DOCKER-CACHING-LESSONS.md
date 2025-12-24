# Docker Caching Lessons (Dec 24, 2025)

## The Problem

After switching to Docker Buildx for supposed "speed improvements," we encountered a gnarly caching bug where source code changes weren't appearing in rebuilt containers despite `--no-cache` flags.

## Root Cause: Multi-Layer Caching

Docker has **FOUR** separate cache layers:

1. **Layer cache** - Individual Dockerfile step results
   - Cleared by: `--no-cache` flag
   
2. **BuildKit cache** - Buildx-specific persistent cache
   - Cleared by: `docker buildx prune -af`
   - **NOT cleared by `--no-cache`!**
   
3. **Image cache** - Tagged images remain available
   - Cleared by: `docker image prune` or explicit removal
   
4. **Container cache** - Running containers reference old images
   - Cleared by: `docker compose down` + `up` (NOT `restart`)

## The Smoking Gun

```bash
# This built a new image successfully:
docker compose build --no-cache brain

# But this kept using the OLD image:
docker compose restart brain

# The container was bound to the old image ID!
```

## The Solution

### For Development: Ditch Buildx

```bash
# Switch to legacy builder permanently
docker buildx use default
export DOCKER_BUILDKIT=0  # Add to shell rc
```

**Why?**
- Buildx optimizes for CI/CD with aggressive caching
- Legacy builder is simpler and more predictable
- Dev iteration needs speed, not multi-platform builds

### Proper Rebuild Command

```bash
# Build with legacy builder
DOCKER_BUILDKIT=0 docker compose build --no-cache brain

# MUST recreate container (restart is not enough!)
docker compose down brain
docker compose up -d brain
```

Or use the helper script:
```bash
./scripts/dev-rebuild.sh brain
```

## When to Use Buildx

✅ **Good for:**
- CI/CD pipelines
- Multi-platform builds (arm64 + amd64)
- Production image optimization
- Remote build caching

❌ **Bad for:**
- Rapid local development iteration
- Debugging build context issues
- When you need predictable `COPY` behavior

## Alternative: Volume Mounting

For the absolute fastest dev iteration, mount code as a volume instead of copying:

```yaml
# compose.yaml
services:
  brain:
    volumes:
      - ./brain:/app/brain:ro  # Mount source directly
      - ./scripts:/app/scripts:ro
```

**Pros:**
- Zero rebuild time for code changes
- Just restart the service

**Cons:**
- Need to rebuild for dependency changes
- Slightly different from production setup

## Validation Checklist

After rebuilding, verify the change reached the container:

```bash
# Check file modification time
docker compose exec brain stat /app/brain/reasoning/tools.py

# Check actual file content
docker compose exec brain cat /app/brain/reasoning/tools.py | grep "your_change"

# Check which image the container is using
docker compose images brain
```

## Key Takeaway

**Docker Compose `restart` is a trap!** It restarts the container process but doesn't pick up new images. Always use `down` + `up` after rebuilding.

---

**Time Invested:** 90 minutes of debugging  
**Root Cause:** Buildx BuildKit cache + container image binding  
**Resolution:** Legacy builder + proper container recreation  
**Never Again:** This document exists so we remember! 😤→😄
