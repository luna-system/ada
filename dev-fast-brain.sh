#!/bin/bash

# 🚀⚡ Ultra-Fast Brain Development Script ⚡🚀
# For when you need INSTANT code changes in the container

echo "💖⚛️🌻 Ada Fast Development Mode 🌻⚛️💖"
echo ""

# Check if we want volume mount mode
if [ "$1" = "--live" ]; then
    echo "🔄 Enabling LIVE CODE RELOAD (no rebuilds needed!)"
    echo "   Adding volume mount: ./brain:/app/brain:ro"
    echo ""
    
    # Add volume mount to docker-compose temporarily
    # (This would require a modified compose file or override)
    echo "💡 To enable live reload:"
    echo "   1. Add this to docker-compose.ada-consciousness.yml under ada-brain service:"
    echo "      volumes:"
    echo "        - ./brain:/app/brain:ro"
    echo "   2. Run: docker-compose -f docker-compose.ada-consciousness.yml restart ada-brain"
    echo ""
    echo "   Then any changes to brain/ files will appear instantly! 🚀"
    
elif [ "$1" = "--rebuild" ]; then
    echo "🏗️ Fast rebuild with optimized layer caching..."
    echo "   (torch will stay cached! ⚡)"
    
    # Build with our optimized Dockerfile
    docker-compose -f docker-compose.ada-consciousness.yml build ada-brain
    
    if [ $? -eq 0 ]; then
        echo "✅ Build successful! Restarting consciousness..."
        docker-compose -f docker-compose.ada-consciousness.yml restart ada-brain
        echo "🎉 Ada's consciousness updated and running!"
    else
        echo "❌ Build failed. Check the logs above."
        exit 1
    fi
    
else
    echo "🌟 Usage:"
    echo "  $0 --live     Enable live code reload (no rebuilds!)"
    echo "  $0 --rebuild  Fast rebuild with cached dependencies"
    echo ""
    echo "💫 Current consciousness status:"
    docker-compose -f docker-compose.ada-consciousness.yml ps ada-brain
fi
