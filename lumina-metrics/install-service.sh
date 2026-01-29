#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE="lumina-metrics.service"
SERVICE_NAME="lumina-metrics"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "🐝 Installing Lumina Metrics systemd service..."

# Create systemd user directory if it doesn't exist
mkdir -p "$SYSTEMD_USER_DIR"

# Copy service file
cp "$SERVICE_FILE" "$SYSTEMD_USER_DIR/"
echo "✓ Service file copied to $SYSTEMD_USER_DIR"

# Reload systemd
systemctl --user daemon-reload
echo "✓ Systemd daemon reloaded"

# Enable service
systemctl --user enable "$SERVICE_NAME"
echo "✓ Service enabled"

# Start service
systemctl --user start "$SERVICE_NAME"
echo "✓ Service started"

# Show status
echo ""
echo "Service status:"
systemctl --user status "$SERVICE_NAME" --no-pager

echo ""
echo "✨ Lumina Metrics service installed successfully!"
echo ""
echo "Useful commands:"
echo "  systemctl --user status $SERVICE_NAME    # Check status"
echo "  systemctl --user restart $SERVICE_NAME   # Restart service"
echo "  systemctl --user stop $SERVICE_NAME      # Stop service"
echo "  journalctl --user -u $SERVICE_NAME -f    # View logs"
echo ""
echo "Dashboard: http://localhost:8001/dashboard"
echo "Metrics: http://localhost:8001/metrics"
