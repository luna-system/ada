#!/usr/bin/env bash
# Detect and configure Ollama for optimal accessibility
# This script helps users avoid unnecessary model downloads

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Ada Ollama Detection${NC}"
echo ""

# Check if system Ollama is running
if curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${GREEN}✅ System Ollama detected at localhost:11434${NC}"
    
    # Check if required models are available
    REQUIRED_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:7b}"
    EMBED_MODEL="${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
    
    echo "Checking for required models..."
    
    if curl -fsS "http://localhost:11434/api/tags" | grep -q "\"name\":\"$REQUIRED_MODEL\""; then
        echo -e "${GREEN}✅ Model $REQUIRED_MODEL found${NC}"
        MODEL_READY=true
    else
        echo -e "${YELLOW}⚠️  Model $REQUIRED_MODEL not found${NC}"
        MODEL_READY=false
    fi
    
    if curl -fsS "http://localhost:11434/api/tags" | grep -q "\"name\":\"$EMBED_MODEL\""; then
        echo -e "${GREEN}✅ Embedding model $EMBED_MODEL found${NC}"
        EMBED_READY=true
    else
        echo -e "${YELLOW}⚠️  Embedding model $EMBED_MODEL not found${NC}"
        EMBED_READY=false
    fi
    
    if [[ "$MODEL_READY" == "true" && "$EMBED_READY" == "true" ]]; then
        echo ""
        echo -e "${GREEN}🎉 Perfect! Use system Ollama with:${NC}"
        echo -e "   ${BLUE}export OLLAMA_BASE_URL=http://localhost:11434${NC}"
        echo -e "   ${BLUE}docker compose --profile web up${NC}"
        echo ""
        echo -e "${GREEN}💡 This avoids Docker model downloads entirely!${NC}"
        exit 0
    else
        echo ""
        echo -e "${YELLOW}📥 Missing models. Pull them with:${NC}"
        if [[ "$MODEL_READY" == "false" ]]; then
            echo -e "   ${BLUE}ollama pull $REQUIRED_MODEL${NC}"
        fi
        if [[ "$EMBED_READY" == "false" ]]; then
            echo -e "   ${BLUE}ollama pull $EMBED_MODEL${NC}"
        fi
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  System Ollama not detected${NC}"
    echo ""
fi

# Check Docker model persistence
OLLAMA_DATA_DIR="${OLLAMA_HOST_DIR:-./data/ollama}"

if [[ -d "$OLLAMA_DATA_DIR" ]] && [[ "$(ls -A "$OLLAMA_DATA_DIR" 2>/dev/null)" ]]; then
    echo -e "${GREEN}✅ Docker Ollama models found in $OLLAMA_DATA_DIR${NC}"
    echo -e "${GREEN}💡 Models will persist across Docker rebuilds${NC}"
else
    echo -e "${YELLOW}ℹ️  No existing Docker Ollama models found${NC}"
    echo -e "   Models will be downloaded on first run"
fi

# Check for system Ollama model directory to suggest sharing
SYSTEM_OLLAMA_DIRS=(
    "$HOME/.ollama"
    "/usr/share/ollama/.ollama"
    "/var/lib/ollama/.ollama"
)

for dir in "${SYSTEM_OLLAMA_DIRS[@]}"; do
    if [[ -d "$dir" ]] && [[ "$(ls -A "$dir" 2>/dev/null)" ]]; then
        echo ""
        echo -e "${BLUE}💡 Found system Ollama models in $dir${NC}"
        echo -e "   To share these models with Docker, run:"
        echo -e "   ${BLUE}export OLLAMA_HOST_DIR='$dir'${NC}"
        echo -e "   ${BLUE}docker compose --profile ollama --profile web up${NC}"
        echo ""
        break
    fi
done

echo -e "${GREEN}🚀 Ready to start Ada!${NC}"
echo ""
echo "Choose your setup:"
echo -e "  ${BLUE}System Ollama:${NC} export OLLAMA_BASE_URL=http://localhost:11434"
echo -e "  ${BLUE}Docker Ollama:${NC} docker compose --profile ollama --profile web up"
echo -e "  ${BLUE}Share models:${NC} export OLLAMA_HOST_DIR='/path/to/system/ollama'"