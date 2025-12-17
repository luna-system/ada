# Docker Build Setup for Ada

## Current Issue

You're seeing this warning:
```
WARN[0000] Docker Compose is configured to build using Bake, but buildx isn't installed
```

This happens because:
1. Docker Compose defaults to BuildKit when available
2. Your system doesn't have `docker buildx` installed
3. This causes inconsistent caching and build failures

## Solution: Install Docker Buildx

### Option 1: Install Buildx Plugin (Recommended)

```bash
# Download buildx
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/buildx/releases/download/v0.12.1/buildx-v0.12.1.linux-amd64 \
  -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx

# Verify
docker buildx version
```

### Option 2: Use Standard Build (Current Workaround)

If you don't want to install buildx, you can force legacy build:

```bash
# Set environment variable
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Or add to ~/.bashrc
echo 'export DOCKER_BUILDKIT=0' >> ~/.bashrc
echo 'export COMPOSE_DOCKER_CLI_BUILD=0' >> ~/.bashrc
```

### Option 3: Update Docker Engine

On modern systems, buildx is included:

```bash
# Check your Docker version
docker version

# If < 20.10, consider updating
# Arch: sudo pacman -S docker docker-compose
# Ubuntu: sudo apt update && sudo apt install docker-ce docker-compose-plugin
```

## Why This Matters for Ada

Ada's build has:
- **5 services** with custom Dockerfiles
- **Multi-stage builds** (planned optimization)
- **Large dependencies** (100+ packages in matrix-bridge)
- **Frequent rebuilds** during development

BuildKit provides:
- ✅ **Better caching** - Reuses layers more intelligently
- ✅ **Parallel builds** - Faster multi-service builds
- ✅ **BuildKit features** - Advanced Dockerfile syntax
- ✅ **Consistent behavior** - Same as CI/CD

Without BuildKit:
- ❌ Cache misses (COPY commands invalidate unnecessarily)
- ❌ Slower builds (sequential layer building)
- ❌ Warnings spam (annoying but harmless)

## Current Workaround in Place

We've already added `.dockerignore` files to reduce image sizes, but proper BuildKit would be better.

## Testing Your Build Setup

```bash
# Test buildx
docker buildx version

# If installed, enable BuildKit
export DOCKER_BUILDKIT=1

# Rebuild matrix-bridge
docker compose build matrix-bridge

# You should see:
# [+] Building X.Xs (buildx)
# instead of:
# WARN[0000] Docker Compose is configured to build using Bake, but buildx isn't installed
```

## Recommendation

**For development**: Install buildx (Option 1)  
**For production**: Use Docker 20.10+ with built-in buildx  
**Quick fix**: Use legacy build (Option 2) - works but slower

## See Also

- [Docker BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [Docker Compose Build Configuration](https://docs.docker.com/compose/compose-file/build/)
- `.ai/DISK_OPTIMIZATION.md` - Multi-stage builds (requires BuildKit)
