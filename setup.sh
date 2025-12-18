#!/usr/bin/env bash
# Setup script for Ada - creates required directories and validates environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛠️  Ada Setup Script"
echo ""

# Create required data directories
echo "📁 Creating data directories..."
mkdir -p data/ollama
mkdir -p data/brain
mkdir -p data/chroma
mkdir -p data/backups

# Set appropriate permissions
chmod 755 data/ollama data/brain data/chroma data/backups

echo "✓ Data directories created:"
echo "  - data/ollama (Ollama models)"
echo "  - data/brain (Ada Brain persistence)"
echo "  - data/chroma (Vector database)"
echo "  - data/backups (SQLite backups)"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    if [ -f .env.example ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ .env created - please review and update values"
    else
        echo "❌ No .env.example found"
        echo "   Please create .env manually"
    fi
    echo ""
fi

# Check for required tools
echo "🔍 Checking required tools..."
MISSING=()

command -v docker >/dev/null 2>&1 || MISSING+=("docker")
command -v docker compose >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1 || MISSING+=("docker-compose")
command -v uv >/dev/null 2>&1 || MISSING+=("uv")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Missing required tools: ${MISSING[*]}"
    echo ""
    echo "Installation instructions:"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    echo "  - uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ All required tools found"
echo ""

# If repository uses Nix flakes, try to update flake.lock to refresh any outdated GitHub links
if [ -f flake.lock ]; then
    echo "🔄 flake.lock detected — attempting to update to refresh inputs..."
    if command -v nix >/dev/null 2>&1; then
        # Try the more explicit recreate option first (newer nix)
        if nix flake update --recreate-lock-file 2>/dev/null; then
            echo "✓ flake.lock recreated successfully"
        else
            # Fallback to basic update for older nix versions
            if nix flake update 2>/dev/null; then
                echo "✓ flake.lock updated successfully"
            else
                echo "⚠️  nix flake update failed — continuing without updating flake.lock"
            fi
        fi
    else
        echo "⚠️  nix not found in PATH — skipping flake.lock update"
    fi
    echo ""
fi

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review and update .env if needed"
echo "  2. Start services: docker compose up -d"
echo "  3. Test MCP server: cd ada-mcp && uv run ada-mcp"
echo ""
