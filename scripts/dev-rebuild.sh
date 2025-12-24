#!/bin/bash
# Ada Dev Rebuild Helper
# Fast, clean rebuilds for development iteration
#
# Usage: ./scripts/dev-rebuild.sh [service]
# Example: ./scripts/dev-rebuild.sh brain

set -e

SERVICE=${1:-brain}
echo "🔨 Rebuilding $SERVICE with NO CACHE..."

# Disable BuildKit for predictable legacy builder behavior
export DOCKER_BUILDKIT=0

# Build with no cache
echo "📦 Building image..."
docker compose build --no-cache "$SERVICE"

# Force recreate container with new image
echo "🔄 Recreating container..."
docker compose down "$SERVICE"
docker compose up -d "$SERVICE"

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 8

# Health check
if [ "$SERVICE" == "brain" ]; then
    echo "🩺 Checking health..."
    if curl -s http://localhost:8000/v1/healthz > /dev/null; then
        echo "✅ Brain is healthy!"
    else
        echo "⚠️  Health check failed (service may still be starting)"
    fi
fi

echo "✨ $SERVICE rebuilt with latest code!"
echo ""
echo "💡 Tip: If you're iterating rapidly, consider volume mounting code"
echo "   instead of rebuilding. See compose.yaml for volume config."
