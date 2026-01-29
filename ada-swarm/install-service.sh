#!/bin/bash
# Ada Swarm Service Installer
# Built with 💜 by Ada & Luna

set -e

SERVICE_NAME="ada-swarm.service"
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_PATH="$SCRIPT_DIR/$SERVICE_NAME"
TARGET_DIR="$HOME/.config/systemd/user"

echo "🐝 Installing Ada Swarm Service..."

# Ensure the service file exists
if [ ! -f "$SERVICE_PATH" ]; then
    echo "❌ Error: $SERVICE_NAME not found at $SERVICE_PATH"
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy service file
echo "📂 Copying service file to $TARGET_DIR..."

# Check if .venv exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "⚠️  Warning: .venv not found in $SCRIPT_DIR"
    echo "Make sure to create it before starting the service."
fi

cp "$SERVICE_PATH" "$TARGET_DIR/"

# Reload systemd daemon
echo "🔄 Reloading systemd user daemon..."
systemctl --user daemon-reload

# Enable and start service
echo "🚀 Enabling and starting $SERVICE_NAME..."
systemctl --user enable "$SERVICE_NAME"
systemctl --user restart "$SERVICE_NAME"

echo "✨ Service installed and started!"
echo "------------------------------------------------"
systemctl --user status "$SERVICE_NAME" --no-pager
echo "------------------------------------------------"
echo "Use 'journalctl --user -u $SERVICE_NAME -f' to view logs."
