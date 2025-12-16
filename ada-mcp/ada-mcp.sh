#!/usr/bin/env bash
# Quick Ada MCP launcher using uv

set -e

cd "$(dirname "$0")"

echo "🚀 Ada MCP Server"
echo "📍 Base URL: ${ADA_BASE_URL:-http://localhost:8000}"
echo ""

exec uv run ada-mcp
