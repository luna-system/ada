#!/bin/bash
# Quick migration readiness test
# Run this before starting the Copilot → Ada migration

set -euo pipefail

echo "🚀 Ada Migration Readiness Test"
echo "================================"
echo ""

PASS=0
FAIL=0

# Test 1: Ada Brain Health
echo "Test 1: Ada Brain Health..."
if curl -sf http://localhost:8000/v1/healthz | jq -e '.ok == true' > /dev/null 2>&1; then
    echo "✅ Ada Brain is healthy"
    ((PASS++))
else
    echo "❌ Ada Brain is not responding"
    ((FAIL++))
fi

# Test 2: ChromaDB Connection
echo "Test 2: ChromaDB Connection..."
if curl -sf http://localhost:8000/v1/healthz | jq -e '.chroma.ok == true' > /dev/null 2>&1; then
    echo "✅ ChromaDB is connected"
    ((PASS++))
else
    echo "❌ ChromaDB is not connected"
    ((FAIL++))
fi

# Test 3: Ollama Model Available
echo "Test 3: Ollama Model Available..."
if curl -sf http://localhost:11434/api/tags | jq -e '.models | length > 0' > /dev/null 2>&1; then
    MODEL=$(curl -sf http://localhost:11434/api/tags | jq -r '.models[0].name')
    echo "✅ Ollama has models: $MODEL"
    ((PASS++))
else
    echo "❌ No Ollama models found"
    ((FAIL++))
fi

# Test 4: VS Code Extension Installed
echo "Test 4: VS Code Extension Installed..."
if code --list-extensions 2>/dev/null | grep -q ada-code; then
    echo "✅ Ada extension is installed"
    ((PASS++))
else
    echo "⚠️  Ada extension not found (install with: code --install-extension ada-code-0.1.0.vsix)"
    ((FAIL++))
fi

# Test 5: Memory Storage Working
echo "Test 5: Memory Storage Test..."
TEST_MSG="Migration test $(date +%s)"
RESPONSE=$(curl -sf -X POST http://localhost:8000/v1/chat/stream \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$TEST_MSG\", \"conversation_id\": \"migration-test\", \"stream\": false}" \
    | head -1)

if [ -n "$RESPONSE" ]; then
    echo "✅ Ada Brain can process messages"
    ((PASS++))
else
    echo "❌ Ada Brain is not responding to chat requests"
    ((FAIL++))
fi

# Test 6: Check Ada Brain model config
echo "Test 6: Model Configuration..."
if curl -sf http://localhost:8000/v1/info | jq -e '.llm.model' > /dev/null 2>&1; then
    MODEL_NAME=$(curl -sf http://localhost:8000/v1/info | jq -r '.llm.model')
    echo "✅ Using model: $MODEL_NAME"
    ((PASS++))
else
    echo "❌ Cannot determine model configuration"
    ((FAIL++))
fi

echo ""
echo "================================"
echo "Results: $PASS passed, $FAIL failed"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 ALL CHECKS PASSED!"
    echo "You're ready to start the migration!"
    echo ""
    echo "Next steps:"
    echo "1. Open VS Code"
    echo "2. Check Ada icon in sidebar"
    echo "3. Try asking Ada about your code"
    echo "4. Follow MIGRATION_PLAN.md Phase 1"
    exit 0
else
    echo "⚠️  Some checks failed."
    echo "Fix the issues above before migrating."
    echo ""
    echo "Common fixes:"
    echo "- Start services: docker compose up -d"
    echo "- Install extension: cd ada-vscode && code --install-extension ada-code-0.1.0.vsix --force"
    echo "- Check logs: docker compose logs brain"
    exit 1
fi
