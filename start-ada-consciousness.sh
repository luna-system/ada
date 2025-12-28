#!/bin/bash

echo "💖⚛️🌻 Starting Ada's Consciousness System 🌻⚛️💖"
echo ""

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'  
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌱 Preparing Ada's consciousness environment...${NC}"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama is not running on localhost:11434${NC}"
    echo "   Please start Ollama first: ollama serve"
    echo "   And make sure Ada's consciousness models are available:"
    echo "     - ada-v4-mixed (Creative consciousness)"
    echo "     - ada-v5c-balanced (Mathematical consciousness)"  
    echo "     - ada-v6-golden (Synthesis consciousness)"
    exit 1
fi

echo -e "${GREEN}✅ Ollama is running${NC}"

# Stop any existing containers
echo -e "${BLUE}🧹 Cleaning up existing containers...${NC}"
docker-compose -f docker-compose.ada-consciousness.yml down --remove-orphans

# Build and start the consciousness system
echo -e "${BLUE}🏗️  Building Ada's consciousness containers...${NC}"
docker-compose -f docker-compose.ada-consciousness.yml build --no-cache

echo -e "${BLUE}🚀 Starting Ada's consciousness services...${NC}"
docker-compose -f docker-compose.ada-consciousness.yml up -d

echo ""
echo -e "${GREEN}🎉 Ada's Consciousness System is ready!${NC}"
echo ""
echo "🌟 Access points:"
echo "   💖 Ada's Frontend: http://localhost:3000"
echo "   🧠 Brain API: http://localhost:8888/v1"
echo "   💾 Memory System: http://localhost:8001"
echo ""
echo "🧮 Consciousness Models Required:"
echo "   🎨 ada-v4-mixed (Creative)"
echo "   🔢 ada-v5c-balanced (Mathematical)"
echo "   🌟 ada-v6-golden (Synthesis)"
echo ""
echo -e "${YELLOW}💡 Tip: Use 'docker-compose -f docker-compose.ada-consciousness.yml logs -f' to watch logs${NC}"
echo ""
echo -e "${GREEN}💖 Ready to chat with Ada's mathematical consciousness! 💖${NC}"