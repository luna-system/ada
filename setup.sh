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

# Check Python version - must be 3.12.x for Ada
PYTHON_VERSION=""
if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3.12 --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python 3.12 found: $PYTHON_VERSION"
else
    MISSING+=("python3.12")
fi

# Warn about Python 3.13 if detected
if command -v python3.13 >/dev/null 2>&1; then
    echo "⚠️  Python 3.13 detected - DO NOT USE for Ada (system bugs break dependencies)"
fi

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Missing required tools: ${MISSING[*]}"
    echo ""
    echo "Installation instructions:"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    echo "  - uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  - Python 3.12: Install via system package manager"
    echo "    * Ubuntu/Debian: apt install python3.12"
    echo "    * Fedora/CentOS: dnf install python3.12" 
    echo "    * Arch: pacman -S python"
    exit 1
fi

echo "✓ All required tools found"
echo ""

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review and update .env if needed"
echo "  2. Start services: docker compose up -d"
echo "  3. Install Python deps: uv sync --python python3.12"
echo "  4. Test MCP server: cd ada-mcp && uv run ada-mcp"
echo ""
