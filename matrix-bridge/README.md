# Ada Matrix Bridge

Matrix bot that connects Ada to Matrix chat rooms.

## Features

- **Clear bot identification:** Display name includes [Bot] indicator
- **Invitation-only:** Never auto-joins, respects consent
- **Privacy controls:** `!ada privacy` commands for opt-out
- **Conversation context:** Remembers recent messages per room
- **Transparent:** Introduction message on join with opt-out instructions

## Setup

### 1. Create Matrix Bot Account

On your Matrix homeserver, create a bot account:

```bash
# Option A: Register via Element/web client
# Create account @ada-bot:yourdomain.com

# Option B: Get access token after login
curl -X POST https://matrix.yourdomain.com/_matrix/client/r0/login \
  -d '{"type":"m.login.password","user":"ada-bot","password":"YOUR_PASSWORD"}' \
  | jq -r '.access_token'
```

### 2. Configure Environment

Create `.env` file:

```bash
# Matrix connection
MATRIX_HOMESERVER=https://matrix.yourdomain.com
MATRIX_USER_ID=@ada-bot:yourdomain.com
MATRIX_ACCESS_TOKEN=syt_YourAccessTokenHere

# Or use password (less secure)
# MATRIX_PASSWORD=your_password

# Bot identity
DISPLAY_NAME=Ada [Bot]

# Ada brain
ADA_BRAIN_URL=http://brain:7000

# Behavior
SEND_INTRO_ON_JOIN=true
AUTO_ACCEPT_INVITES=true
RESPOND_TO_MENTIONS=true
RESPOND_TO_DMS=true

# Privacy
ALLOW_PRIVACY_OPT_OUT=true
STORE_IN_RAG=true
DATA_RETENTION_DAYS=90
```

### 3. Run with Docker Compose

The bridge is included in the main `compose.yaml`. Start it with:

```bash
docker compose up -d matrix-bridge
```

Or run standalone:

```bash
cd matrix-bridge
docker build -t ada-matrix-bridge .
docker run -d \
  --name ada-matrix-bridge \
  --env-file .env \
  -v ./data:/data \
  --network ada-network \
  ada-matrix-bridge
```

### 4. Invite Ada to Rooms

In your Matrix client:
1. Create or open a room
2. Invite @ada-bot:yourdomain.com
3. Ada will join and introduce herself
4. Mention @ada or use "Ada:" to chat!

## Usage

### Talking to Ada

- **@mention:** `@ada-bot:yourdomain.com what's 2+2?`
- **Display name:** `Ada: explain Docker`
- **Direct messages:** Just send a DM, she always responds
- **Keywords:** Any message containing "ada" (configurable)

### Commands

- `!ada privacy on` - Enable memory storage for this room
- `!ada privacy off` - Disable memory storage (privacy mode)
- `!ada privacy status` - Show current privacy setting
- `!ada clear` - Clear conversation context for this room
- `!ada help` - Show available commands
- `!ada status` - Show system status

### Removing Ada

Just kick her from the room. No hard feelings! ❤️

## Configuration

See `config.py` for all available options. Key settings:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MATRIX_HOMESERVER` | https://matrix.org | Homeserver URL |
| `MATRIX_USER_ID` | @ada-bot:matrix.org | Bot user ID |
| `MATRIX_ACCESS_TOKEN` | - | Access token (recommended) |
| `DISPLAY_NAME` | Ada [Bot] | Display name with bot indicator |
| `SEND_INTRO_ON_JOIN` | true | Send intro message when joining |
| `AUTO_ACCEPT_INVITES` | true | Auto-accept room invitations |
| `MAX_CONTEXT_MESSAGES` | 10 | Recent messages to remember |
| `ALLOW_PRIVACY_OPT_OUT` | true | Allow !ada privacy commands |

## Architecture

```
Matrix Room → matrix-bridge → Ada Brain API → Ollama LLM (configured model)
     ↑              ↓              ↓                ↓
   Users      matrix-nio    /v1/chat/stream      RAG + Specialists
```

The bridge:
1. Listens for Matrix messages
2. Checks activation rules (mentions, DMs, keywords)
3. Maintains conversation context per room
4. Forwards to Ada's existing `/v1/chat/stream` API
5. Posts responses back to Matrix

**No changes to Ada's brain needed!** This is just a Matrix ↔ HTTP bridge.

## Ethics & Transparency

Ada follows strict ethical guidelines:

- **Clear bot identification:** Display name, profile, intro message
- **Invitation-only:** Never auto-joins without being invited
- **Privacy controls:** Easy opt-out with `!ada privacy off`
- **Transparent about limitations:** Acknowledges when uncertain
- **Source attribution:** Cites sources when using external info
- **Respectful:** Doesn't argue when removed from rooms

See [COMMUNITY_GUIDELINES.md](../COMMUNITY_GUIDELINES.md) and [.ai/MATRIX_ETHICS.md](../.ai/MATRIX_ETHICS.md) for full details.

## Troubleshooting

### Ada doesn't respond

1. Check logs: `docker compose logs -f matrix-bridge`
2. Verify Ada is in the room: `/whois @ada-bot:yourdomain.com`
3. Check brain health: `curl http://localhost:7000/v1/healthz`
4. Try direct message to isolate issue

### Connection errors

1. Verify homeserver URL is correct
2. Check access token is valid
3. Ensure network connectivity: `docker compose exec matrix-bridge ping matrix.yourdomain.com`

### Privacy mode not working

1. Check `ALLOW_PRIVACY_OPT_OUT=true` in config
2. Verify data directory is writable: `docker compose exec matrix-bridge ls -la /data`
3. Check logs for errors

### Ada joins but doesn't introduce herself

1. Check `SEND_INTRO_ON_JOIN=true`
2. Look for intro in logs
3. May have already sent intro (tracked in `/data/room_contexts.json`)

## Development

### Local Development

```bash
cd matrix-bridge
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set environment variables
export MATRIX_HOMESERVER=https://matrix.yourdomain.com
export MATRIX_USER_ID=@ada-bot:yourdomain.com
export MATRIX_ACCESS_TOKEN=your_token
export ADA_BRAIN_URL=http://localhost:7000

# Run
python bridge.py
```

### Testing

Create a test room and invite Ada:
1. Send `Ada: hello` - Should respond
2. Send `!ada status` - Should show status
3. Send `!ada privacy off` - Should disable storage
4. Kick Ada - Should leave gracefully

## Files

- `bridge.py` - Main bot logic and event handlers
- `config.py` - Configuration management (Pydantic Settings)
- `identity.py` - Bot identity and transparency helpers
- `ada_client.py` - HTTP client for Ada's brain API
- `message_handler.py` - Message processing and context management
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition

## License

Same as Ada project (see root LICENSE file).

## Contributing

See main project CONTRIBUTING.md. For Matrix-specific issues, please include:
- Matrix homeserver software and version
- Relevant logs from `docker compose logs matrix-bridge`
- Steps to reproduce

## Support

- **Matrix room:** [Your Ada discussion room]
- **GitHub Issues:** https://github.com/luna-system/ada/issues
- **Documentation:** https://ada-docs.yourdomain.com

---

**Remember:** Ada is a tool for your community, not a replacement for human interaction.
