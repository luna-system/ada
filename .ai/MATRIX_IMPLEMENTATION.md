# Matrix Integration - Implementation Plan

## Quick Start: What We're Building

**Goal:** Ada as a Matrix chatbot in your self-hosted rooms

**Architecture:** New `matrix-bridge` service that:
1. Connects to your Matrix homeserver
2. Listens for mentions (@ada) or direct messages
3. Forwards to Ada's brain via existing `/v1/chat/stream`
4. Posts responses back to Matrix

**Why this works:** We already have all the AI/RAG/specialist logic. We just need a Matrix ↔ HTTP bridge!

---

## Phase 1: MVP Bridge (Start Here!)

### Step 1: Set Up Matrix Bot Account

**On your Matrix homeserver:**
```bash
# Create bot user
# Option A: Via Synapse admin API
# Option B: Register normally via Element/web client

# Get access token (save this!)
curl -X POST https://matrix.yourdomain.com/_matrix/client/r0/login \
  -d '{"type":"m.login.password","user":"ada","password":"YOUR_PASSWORD"}' \
  | jq -r '.access_token'
```

**Save to `.env`:**
```bash
MATRIX_HOMESERVER=https://matrix.yourdomain.com
MATRIX_USER_ID=@ada:yourdomain.com
MATRIX_ACCESS_TOKEN=syt_YourAccessTokenHere
```

### Step 2: Create Bridge Service Structure

```
matrix-bridge/
├── bridge.py              # Main bot logic
├── config.py              # Configuration (Pydantic Settings)
├── matrix_client.py       # Matrix API wrapper
├── ada_client.py          # Ada brain HTTP client
├── message_handler.py     # Process Matrix messages
├── identity.py            # Bot identity & transparency helpers
├── requirements.txt       # Dependencies
├── Dockerfile             # Container definition
└── README.md              # Service documentation
```

### Step 2.5: Configure Bot Identity (Important!)

**identity.py** - Transparency and ethical presentation:
```python
"""Bot identity and transparency configuration."""

INTRO_MESSAGE = """👋 Hi! I'm Ada, an AI assistant running on this community's self-hosted infrastructure.

**What I do:**
• Respond to @ada mentions and direct messages
• Maintain conversation context within rooms
• Powered by DeepSeek-R1 (local LLM, no external APIs)

**Privacy:**
• All conversations stored locally in encrypted vector database
• No data sent to external services
• You can opt out of memory storage with: !ada privacy off

**Remove me:** Just kick me from the room anytime!

Learn more: https://github.com/luna-system/ada
"""

BOT_PROFILE = {
    "displayname": "Ada [Bot]",  # Clear bot indicator
    "bio": (
        "AI assistant powered by DeepSeek-R1. "
        "Self-hosted and privacy-focused. "
        "Open source: https://github.com/luna-system/ada"
    ),
    "avatar_mxc": None,  # Set to your bot avatar MXC URL
    "bot": True  # Protocol-level bot flag
}

def format_message_with_disclosure(text: str, include_signature: bool = False) -> str:
    """Optionally add AI disclosure to messages."""
    if include_signature:
        return f"{text}\n\n— Ada (AI Assistant)"
    return text

def should_send_intro(room_id: str, sent_intros: set) -> bool:
    """Check if we should send intro message to this room."""
    return room_id not in sent_intros
```

### Step 3: Core Implementation

**bridge.py** - Minimal viable bot:
```python
"""Matrix bridge for Ada - connects Matrix chat to Ada's brain."""

import asyncio
import logging
from nio import AsyncClient, MatrixRoom, RoomMessageText
from ada_client import AdaBrainClient
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaMatrixBridge:
    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncClient(config.matrix_homeserver, config.matrix_user_id)
        self.ada = AdaBrainClient(config.ada_brain_url)
        
        # Register callbacks
        self.client.add_event_callback(self.message_callback, RoomMessageText)
    
    async def message_callback(self, room: MatrixRoom, event: RoomMessageText):
        """Handle incoming Matrix messages"""
        # Skip own messages
        if event.sender == self.client.user:
            return
        
        message = event.body
        sender = event.sender
        
        # Check if we should respond
        if not self.should_respond(message, room):
            return
        
        logger.info(f"Responding to {sender} in {room.display_name}: {message}")
        
        # Send typing indicator
        await self.client.room_typing(room.room_id, True)
        
        try:
            # Query Ada's brain
            response = await self.ada.chat(message, user_id=sender, room_id=room.room_id)
            
            # Post response to Matrix
            await self.client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": response,
                    "format": "org.matrix.custom.html",
                    "formatted_body": self.markdown_to_html(response)
                }
            )
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await self.client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": "Sorry, I encountered an error processing that message."
                }
            )
        finally:
            await self.client.room_typing(room.room_id, False)
    
    def should_respond(self, message: str, room: MatrixRoom) -> bool:
        """Check if Ada should respond to this message"""
        # Respond to mentions
        if self.config.matrix_user_id in message or "ada" in message.lower():
            return True
        
        # Respond to DMs (2 members = user + bot)
        if len(room.users) == 2:
            return True
        
        return False
    
    async def start(self):
        """Start the bridge"""
        logger.info(f"Starting Ada Matrix Bridge...")
        logger.info(f"Homeserver: {self.config.matrix_homeserver}")
        logger.info(f"User: {self.config.matrix_user_id}")
        
        # Login
        if self.config.matrix_access_token:
            self.client.access_token = self.config.matrix_access_token
        else:
            login_response = await self.client.login(self.config.matrix_password)
            logger.info(f"Logged in: {login_response}")
        
        # Sync and start listening
        logger.info("Starting sync loop...")
        await self.client.sync_forever(timeout=30000)

async def main():
    config = Config()
    bridge = AdaMatrixBridge(config)
    await bridge.start()

if __name__ == "__main__":
    asyncio.run(main())
```

**Key files:**
- `config.py` - Pydantic Settings for env vars
- `ada_client.py` - HTTP client for `/v1/chat/stream`
- `matrix_client.py` - Helper functions for Matrix API

### Step 4: Add to Docker Compose

```yaml
# In compose.yaml
matrix-bridge:
  build:
    context: ./matrix-bridge
  container_name: ada-matrix-bridge
  depends_on:
    - brain
  environment:
    - MATRIX_HOMESERVER=${MATRIX_HOMESERVER}
    - MATRIX_USER_ID=${MATRIX_USER_ID}
    - MATRIX_ACCESS_TOKEN=${MATRIX_ACCESS_TOKEN}
    - ADA_BRAIN_URL=http://brain:7000
  volumes:
    - ./data/matrix:/data  # For store persistence
  restart: unless-stopped
  networks:
    - ada-network
```

### Step 5: Test

```bash
# Start the bridge
docker compose up -d matrix-bridge

# Watch logs
docker compose logs -f matrix-bridge

# In Matrix: Invite @ada:yourdomain.com to a room
# Send: "Hey Ada, what's 2+2?"
# Ada should respond!
```

---

## Phase 2: Add Conversation Context

**Goal:** Ada remembers the conversation in each room

**Changes:**

1. **Track room history:**
```python
# In message_handler.py
class RoomContextManager:
    def __init__(self, max_messages=10):
        self.contexts = {}  # room_id -> list of messages
        self.max = max_messages
    
    def add_message(self, room_id: str, sender: str, message: str):
        if room_id not in self.contexts:
            self.contexts[room_id] = []
        
        self.contexts[room_id].append({
            'role': 'user' if sender != self.bot_user else 'assistant',
            'content': message
        })
        
        # Keep only recent messages
        self.contexts[room_id] = self.contexts[room_id][-self.max:]
    
    def get_context(self, room_id: str) -> list:
        return self.contexts.get(room_id, [])
```

2. **Update chat request:**
```python
# Include room context in Ada brain request
context = self.context_manager.get_context(room.room_id)
response = await self.ada.chat(
    message, 
    user_id=sender, 
    room_id=room.room_id,
    conversation_history=context  # NEW!
)
```

3. **Persist context:**
```python
# Save to disk for restart persistence
import json
from pathlib import Path

def save_contexts(self):
    Path('/data/room_contexts.json').write_text(
        json.dumps(self.contexts)
    )

def load_contexts(self):
    path = Path('/data/room_contexts.json')
    if path.exists():
        self.contexts = json.loads(path.read_text())
```

---

## Phase 3: Rich Features (Future)

**Ideas for enhancement:**

1. **Image Support:**
   - Listen for `m.image` events
   - Download image
   - POST to `/v1/ocr/extract`
   - Include OCR result in message to Ada

2. **Reactions:**
   - React with 👍 when starting to process
   - React with ✅ when done
   - React with ❌ on errors

3. **Admin Commands:**
   ```
   !ada status    → Show brain health
   !ada clear     → Clear room context
   !ada help      → Show commands
   !ada persona   → Show current persona
   ```

4. **Thread Support:**
   - Respond only in threads Ada is part of
   - Keep thread context separate from room context

---

## Testing Plan

### Unit Tests
```python
# tests/test_matrix_bridge.py
def test_should_respond_to_mention():
    bridge = AdaMatrixBridge(test_config)
    assert bridge.should_respond("@ada:example.com hi!", mock_room)

def test_should_respond_to_dm():
    dm_room = MockRoom(users=2)
    assert bridge.should_respond("hello", dm_room)

def test_ignores_own_messages():
    # Should not create infinite loops
    pass
```

### Integration Tests
```python
# Start test Matrix server (Synapse in Docker)
# Send test messages
# Verify Ada responds correctly
```

### Manual Testing Checklist
- [ ] Ada joins room when invited
- [ ] Responds to @mention
- [ ] Responds to DMs
- [ ] Typing indicator works
- [ ] Maintains conversation context
- [ ] Handles errors gracefully
- [ ] Doesn't respond to own messages
- [ ] Works in multiple rooms simultaneously

---

## Documentation Updates

**Add to docs/:**
- `matrix_integration.rst` - Full guide
- Update `getting_started.rst` - Matrix setup section
- Update `architecture.rst` - Add matrix-bridge service

**Add to .ai/:**
- Update `codebase-map.json` - Add matrix-bridge
- Update `context.md` - Document Matrix integration

---

## Security Checklist

- [ ] Access token in .env (not hardcoded)
- [ ] Rate limiting on responses
- [ ] Validate room membership before responding
- [ ] Don't store sensitive Matrix messages in logs
- [ ] Consider E2EE for encrypted rooms (Phase 3+)

---

## Debugging Tips

**Common Issues:**

1. **Can't connect to homeserver**
   - Check MATRIX_HOMESERVER URL
   - Verify network connectivity
   - Check Matrix server logs

2. **Ada doesn't respond**
   - Check logs: `docker compose logs matrix-bridge`
   - Verify Ada brain is running: `curl http://localhost:7000/v1/healthz`
   - Check room membership: Ada must be in room

3. **Infinite loops**
   - Ensure `event.sender != self.client.user` check works
   - Add message deduplication

4. **Memory leaks**
   - Limit context storage per room
   - Periodic cleanup of old rooms

---

## Resources

**Matrix Documentation:**
- https://matrix.org/docs/guides/
- https://matrix-nio.readthedocs.io/

**Similar Projects:**
- matrix-nio examples: https://github.com/poljar/matrix-nio/tree/main/examples
- maubot (Matrix bot framework): https://github.com/maubot/maubot

**Matrix Protocol:**
- Client-Server API: https://spec.matrix.org/latest/client-server-api/

---

## Success Criteria

**MVP is complete when:**
- ✅ Ada responds to Matrix mentions
- ✅ Maintains her personality
- ✅ Runs stable for 24+ hours
- ✅ Works in multiple rooms
- ✅ Documented in docs/

**Ready for daily use when:**
- ✅ Conversation context works
- ✅ Handles errors gracefully
- ✅ No crashes under normal use
- ✅ Easy to configure/deploy

---

**Next Step:** Review this plan, then start implementing `matrix-bridge/bridge.py`!

Think big, but we're starting with the MVP. Everything in Phase 2-3 builds on a solid foundation.
