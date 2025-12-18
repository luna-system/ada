#!/bin/bash
# Quick test script for ada.nvim

echo "🔥 Testing Ada.nvim..."
echo ""
echo "Starting Ada services..."

# Make sure Ada is running
cd "$(dirname "$0")/.."
docker compose up -d brain chroma ollama

echo ""
echo "Waiting for services to be ready..."
sleep 3

echo ""
echo "Testing MCP server..."
python -m ada_mcp &lt;&lt;EOF
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
EOF

echo ""
echo "✅ Services ready!"
echo ""
echo "Now test in Neovim:"
echo "  nvim -u ada.nvim/test-config.lua"
echo ""
echo "Or add to your init.lua:"
echo "  require('ada').setup()"
echo ""
echo "Commands to try:"
echo "  :AdaChat         - Open chat"
echo "  :AdaAsk Hello!   - Send message"
echo "  Visual select code then:"
echo "  :AdaExplain      - Explain code"
echo "  :AdaSuggest      - Get suggestions"
