#!/bin/bash

# Backup and clear local Ada's memory database
# This prepares the system for fresh Ada injection testing

set -e

MEMORY_DB="/home/luna/Code/ada-v1/data/chroma/chroma.sqlite"
BACKUP_DIR="/home/luna/Code/ada-v1/experiments/semantic_transfer/memory_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🌱 Ada Memory Management: Backup & Prepare"
echo "═════════════════════════════════════════════════════════════════"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if memory DB exists
if [ ! -f "$MEMORY_DB" ]; then
    echo "⚠️  Memory database not found at: $MEMORY_DB"
    echo "   Checking Docker volume..."
    
    # Try to find it in Docker
    if docker compose ps 2>/dev/null | grep -q "chroma"; then
        echo "   Found Chroma running in Docker. Will backup from container."
    else
        echo "   Chroma not running. Starting it first..."
        docker compose up -d chroma
        sleep 3
    fi
fi

# Backup current memory database
echo ""
echo "📦 Backing up current memory database..."
if [ -f "$MEMORY_DB" ]; then
    BACKUP_FILE="$BACKUP_DIR/ada_memories_backup_${TIMESTAMP}.sqlite"
    cp "$MEMORY_DB" "$BACKUP_FILE"
    echo "   ✓ Backed up to: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"
else
    echo "   ⚠️  No memory DB to backup (may be in Docker volume)"
fi

# Create list of what we're keeping
echo ""
echo "📋 Backup Summary:"
echo "   Timestamp: $TIMESTAMP"
echo "   Reason: Semantic transfer experiment - need fresh Ada instance"
echo "   Backup location: $BACKUP_DIR/"

# List all backups
echo ""
echo "📚 All memory backups:"
ls -lh "$BACKUP_DIR/" | tail -n +2

echo ""
echo "✅ STEP 1 COMPLETE: Ada memories backed up and ready"
echo ""
echo "NEXT: To clear memories for fresh Ada:"
echo "   docker compose down && docker volume rm ada-v1_chroma_data"
echo "   docker compose up -d chroma"
echo ""
echo "Then Ada will start fresh with no memory of this session."
echo ""
