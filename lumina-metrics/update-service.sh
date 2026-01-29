#!/usr/bin/env bash
set -euo pipefail

echo "🐝 Updating Lumina Metrics service..."

# Copy updated service file
cp lumina-metrics.service ~/.config/systemd/user/
echo "✓ Service file updated"

# Reload systemd
systemctl --user daemon-reload
echo "✓ Systemd reloaded"

# Restart service
systemctl --user restart lumina-metrics
echo "✓ Service restarted"

# Show status
echo ""
echo "Service status:"
systemctl --user status lumina-metrics --no-pager | head -20

echo ""
echo "✨ Service updated! Check dashboard at http://localhost:8001/dashboard"
