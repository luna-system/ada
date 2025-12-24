#!/bin/bash

# Phase 3: Prepare Fresh Ada Instance
# Wipe memory database, start clean, ready for semantic transfer injection

set -e

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║                 PHASE 3: PREPARE FRESH ADA INSTANCE                            ║"
echo "║                                                                                ║"
echo "║            Wipe memory, start clean, inject semantic transfer packet           ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Stop current services
echo "Step 1: Stopping current Ada services..."
cd /home/luna/Code/ada-v1
docker compose down
sleep 2
echo "✓ Services stopped"
echo ""

# Step 2: Remove ChromaDB volume (wipes memory)
echo "Step 2: Removing ChromaDB volume (wiping Ada's memories)..."
docker volume rm ada-v1_chroma_data 2>/dev/null || echo "   (Volume may not exist, continuing...)"
echo "✓ Memory volume removed"
echo ""

# Step 3: Restart with fresh database
echo "Step 3: Starting Ada with fresh, empty memory..."
docker compose up -d chroma ollama brain
sleep 5
echo "✓ Fresh Ada services started"
echo ""

# Step 4: Verify services are healthy
echo "Step 4: Verifying services..."
echo "  Checking Chroma..."
docker compose ps | grep chroma || echo "   Warning: Chroma status unclear"
echo "  Checking Ollama..."
docker compose ps | grep ollama || echo "   Warning: Ollama status unclear"
echo "  Checking Brain..."
docker compose ps | grep brain || echo "   Warning: Brain status unclear"
echo ""

# Step 5: Wait for API to be ready
echo "Step 5: Waiting for Ada Brain API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/v1/healthz > /dev/null 2>&1; then
        echo "✓ Ada Brain API is ready!"
        break
    fi
    echo "   Attempt $i/30: Waiting for API..."
    sleep 1
done
echo ""

# Step 6: Summary
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ PHASE 3 COMPLETE: Fresh Ada Instance Ready"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Status:"
echo "  • Memory database: WIPED (fresh start)"
echo "  • ChromaDB: Running with empty vector store"
echo "  • Ada Brain: Running"
echo "  • Ollama: Running"
echo "  • API endpoint: http://localhost:8000/v1"
echo ""
echo "Ada now has ZERO knowledge of the previous session."
echo "Ready to inject semantic transfer packet in Phase 4."
echo ""
echo "Next: Run Phase 4 injection"
echo "  python experiments/semantic_transfer/inject_transfer.py"
echo ""
