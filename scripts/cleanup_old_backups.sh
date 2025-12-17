#!/bin/bash
# Cleanup old backup files to save disk space
# Keeps last 7 days of backups

set -e

BACKUP_DIR="./data/backups"
DAYS_TO_KEEP=7

echo "🧹 Cleaning up old backups..."
echo "Directory: $BACKUP_DIR"
echo "Retention: $DAYS_TO_KEEP days"
echo ""

if [ ! -d "$BACKUP_DIR" ]; then
    echo "⚠️  Backup directory not found: $BACKUP_DIR"
    exit 0
fi

# Count files before cleanup
BEFORE=$(find "$BACKUP_DIR" -name "chroma-*.sqlite3" -type f | wc -l)

# Remove old backups
find "$BACKUP_DIR" -name "chroma-*.sqlite3" -type f -mtime +$DAYS_TO_KEEP -delete

# Count files after cleanup
AFTER=$(find "$BACKUP_DIR" -name "chroma-*.sqlite3" -type f | wc -l)
REMOVED=$((BEFORE - AFTER))

echo "✅ Cleanup complete"
echo "   Before: $BEFORE backups"
echo "   After:  $AFTER backups"
echo "   Removed: $REMOVED backups"

if [ $REMOVED -eq 0 ]; then
    echo "   (No old backups to remove)"
fi
