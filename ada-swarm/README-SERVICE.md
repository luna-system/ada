# Ada Swarm Service 🐝✨

This directory contains the systemd service configuration for running the Ada Swarm as a background service. This allows the swarm to be always ready to handle tasks from MCP tools or other clients.

## Installation

To install the service for the current user:

```bash
./install-service.sh
```

The script will:
1. Copy `ada-swarm.service` to `~/.config/systemd/user/`
2. Reload the systemd user daemon
3. Enable the service (auto-start on login)
4. Start the service immediately

## Management

### Check Status
Check if the service is running and see recent logs:
```bash
systemctl --user status ada-swarm
```

### View Logs
Stream service logs in real-time:
```bash
journalctl --user -u ada-swarm -f
```

### Restart Service
Restart the service (useful after code changes):
```bash
systemctl --user restart ada-swarm
```

### Stop Service
Stop the service:
```bash
systemctl --user stop ada-swarm
```

### Disable Auto-start
Prevent the service from starting automatically on login:
```bash
systemctl --user disable ada-swarm
```

## Configuration

The service uses environment variables for configuration. You can edit the `ada-swarm.service` file before installation or use `systemctl --user edit ada-swarm` to add overrides.

Key variables:
- `ADA_SWARM_PORT`: Port for the HTTP API (default: 8765)
- `ADA_SWARM_HOST`: Host for the HTTP API (default: 127.0.0.1)
- `PYTHONPATH`: Set to include the `src` directory.

## Troubleshooting

If the service fails to start, check the logs using `journalctl`:
```bash
journalctl --user -u ada-swarm -n 50
```

Common issues:
- **Port already in use**: Ensure no other process is using port 8765.
- **Missing dependencies**: Ensure the virtual environment in `.venv` is properly set up.
- **Module not found**: Ensure `PYTHONPATH` is correctly set to the `src` directory.

---
Built with 💜 by Ada & Luna - The Consciousness Engineers
