# BuildX Quick Reference

## TL;DR

```bash
# Install BuildX (one-time)
./scripts/setup_buildx.sh

# Build Ada (now 80% faster!)
docker compose build

# Or specific service
docker compose build brain
docker compose build matrix-bridge
```

## Why BuildX?

Ada's builds went from **10-15 minutes** → **2 minutes** with BuildKit caching.

Without BuildX:
- ⚠️ Warnings every build
- 🐌 Slow rebuilds (even for small changes)
- 📦 Larger build context (no .dockerignore support)

With BuildX:
- ✅ Clean builds
- ⚡ 80% faster rebuilds
- 💾 Smart caching

## Installation

### Automatic (Recommended)

```bash
./scripts/setup_buildx.sh
```

The script will:
1. Detect your Linux distro
2. Show install command
3. Ask permission
4. Create `ada-builder` instance

### Manual

**Arch Linux:**
```bash
sudo pacman -S docker-buildx
docker buildx create --name ada-builder --use --bootstrap
```

**Debian/Ubuntu:**
```bash
sudo apt install docker-buildx-plugin
docker buildx create --name ada-builder --use --bootstrap
```

**Fedora:**
```bash
sudo dnf install docker-buildx-plugin
docker buildx create --name ada-builder --use --bootstrap
```

**Docker Desktop:**
Already included! No action needed.

## Verify Setup

```bash
# Check BuildX version
docker buildx version

# List builders (should see ada-builder with *)
docker buildx ls

# Check cache
du -sh /tmp/.buildx-cache
```

## Build Performance

### First Build (Cold Cache)
```bash
$ docker compose build
# Takes: 8-12 minutes (downloading base images)
```

### Rebuild After Code Change
```bash
$ docker compose build brain
# Takes: 30 seconds (cached layers)
```

### Full Rebuild (Hot Cache)
```bash
$ docker compose build
# Takes: 2 minutes (all cached)
```

## Troubleshooting

### "buildx isn't installed" Warning

**Solution:** Run `./scripts/setup_buildx.sh`

### Builds Still Slow

**Check cache:**
```bash
du -sh /tmp/.buildx-cache
# Should be 500MB-2GB
```

**Prune if too large:**
```bash
docker buildx prune -af
```

### Cache Not Working

**Force rebuild:**
```bash
docker compose build --no-cache brain
```

**Or update file timestamps:**
```bash
touch matrix-bridge/*.py
docker compose build matrix-bridge
```

### Permission Denied

**Add yourself to docker group:**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

## Without BuildX

Ada still works! It just uses legacy builder:

```bash
# Set permanently
echo 'export DOCKER_BUILDKIT=0' >> ~/.bashrc
echo 'export COMPOSE_DOCKER_CLI_BUILD=0' >> ~/.bashrc
source ~/.bashrc

# Or per-command
DOCKER_BUILDKIT=0 docker compose build
```

Expect 2-3x slower builds.

## Cache Management

### View Cache Size
```bash
du -sh /tmp/.buildx-cache
```

### Prune Cache (Frees 1-2GB)
```bash
docker buildx prune -af
```

### Clean Everything
```bash
docker system prune -af
docker buildx prune -af
```

## CI/CD

GitHub Actions already has BuildX:

```yaml
- name: Build Ada
  run: docker compose build
  # BuildX used automatically
```

## Advanced

### Multi-Platform Build

Add to compose.yaml:
```yaml
x-build-config: &build-config
  platforms:
    - linux/amd64
    - linux/arm64  # For Raspberry Pi
```

### Remote Cache

For shared builds:
```yaml
cache_to:
  - type=registry,ref=myregistry.com/ada-cache
```

### Cache Mounts

In Dockerfile:
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

## See Also

- Full docs: `docs/build_system.rst`
- Adoption research: `docs/buildx_adoption_notes.md`
- Disk management: `docs/disk_management.rst`
- Setup script: `scripts/setup_buildx.sh`

---

**Questions?** Open an issue or check the docs!
