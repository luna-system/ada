#!/bin/bash
# Check disk space and warn if running low
# Provides actionable commands to free up space

set -e

THRESHOLD=80  # Warn if >80% full
CRITICAL=90   # Critical warning if >90% full

# Get disk usage for current directory
USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
AVAIL=$(df -h . | awk 'NR==2 {print $4}')

echo "💾 Disk Space Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Usage: ${USAGE}%"
echo "Available: $AVAIL"
echo ""

if [ "$USAGE" -gt "$CRITICAL" ]; then
    echo "🚨 CRITICAL: Disk usage above ${CRITICAL}%!"
    echo ""
    echo "Immediate actions:"
    echo "  1. Remove unused Docker images:"
    echo "     docker system prune -a"
    echo ""
    echo "  2. Remove unused Ollama models:"
    echo "     docker exec ada-v1-ollama-1 ollama list"
    echo "     docker exec ada-v1-ollama-1 ollama rm MODEL_NAME"
    echo ""
    echo "  3. Clean old backups:"
    echo "     ./scripts/cleanup_old_backups.sh"
    echo ""
elif [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "⚠️  WARNING: Disk usage above ${THRESHOLD}%"
    echo ""
    echo "Suggested actions:"
    echo "  • Clean Docker build cache:"
    echo "    docker builder prune --filter until=24h"
    echo ""
    echo "  • Remove dangling images:"
    echo "    docker image prune"
    echo ""
    echo "  • Check Ada's disk usage:"
    echo "    du -sh ./data/*"
    echo ""
else
    echo "✅ Disk usage healthy (below ${THRESHOLD}%)"
fi

# Show Ada-specific usage
echo ""
echo "Ada Disk Usage:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
du -sh ./data/* 2>/dev/null | sort -h || echo "(Unable to read data directory)"

echo ""
echo "Docker Disk Usage:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker system df 2>/dev/null || echo "(Docker not running)"
