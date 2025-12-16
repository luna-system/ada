# Matrix Specialist - Design Document

## Vision

Enable Ada to participate in Matrix rooms as a chatbot, responding to mentions and direct messages while maintaining her personality and RAG capabilities.

## Architecture Options

### Option 1: Bidirectional Specialist (Reactive)
**Pattern:** Like web_search_specialist - LLM can request to send Matrix messages

**Pros:**
- Fits existing specialist pattern
- LLM decides when to engage
- Simple integration

**Cons:**
- Only works during active chat sessions
- Can't respond to Matrix messages independently
- Requires user to be chatting with Ada via web UI

### Option 2: Matrix Bridge Service (Active)
**Pattern:** Separate long-running service that bridges Matrix ↔ Ada's chat API

**Pros:**
- Ada can respond to Matrix messages directly
- Always-on presence in Matrix rooms
- Independent of web UI sessions
- True chatbot experience

**Cons:**
- More complex - new service in compose.yaml
- Needs state management (which rooms, last seen, etc.)
- Authentication complexity

### Option 3: Hybrid Approach
**Pattern:** Bridge service + specialist for Ada-initiated messages

**Pros:**
- Best of both worlds
- Ada can be in Matrix, and reference Matrix in web chats
- Clean separation of concerns

**Cons:**
- Most complex initially
- Two components to maintain

## Recommended: Start with Option 2 (Bridge Service)

### Why?
- Aligns with your use case: Ada as Matrix bot
- Self-hosted Matrix + self-hosted Ada = full control
- Can add Option 3 capabilities later if needed
- Most valuable immediate feature

## Technical Stack

### Matrix SDK Options
1. **matrix-nio** (asyncio-based, modern)
   - Encrypted room support
   - Well-maintained
   - Good async integration with FastAPI

2. **matrix-client** (older, simpler)
   - Easier to start with
   - Less feature-complete

**Recommendation:** `matrix-nio` for future-proofing

## Architecture Design

```
┌─────────────────────────────────────────────────────────┐
│                     Matrix Homeserver                    │
│                   (your self-hosted)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Matrix Client-Server API
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Matrix Bridge Service                       │
│  ┌────────────────────────────────────────────────┐    │
│  │  matrix-nio Client                              │    │
│  │  - Listen for mentions/DMs                      │    │
│  │  - Room membership management                   │    │
│  │  - Message formatting (markdown ↔ Matrix)       │    │
│  └────────────────┬───────────────────────────────┘    │
│                   │                                      │
│  ┌────────────────▼───────────────────────────────┐    │
│  │  HTTP Client → Ada Brain                        │    │
│  │  - POST /v1/chat/stream                         │    │
│  │  - Stream SSE responses                         │    │
│  │  - Maintain conversation context per room       │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                  │
                  │ Internal HTTP
                  │
┌─────────────────▼───────────────────────────────────────┐
│                  Ada Brain (FastAPI)                     │
│  - Existing /v1/chat/stream endpoint                     │
│  - RAG context (persona, memories, etc.)                 │
│  - Specialists (OCR, web search, docs, etc.)             │
└─────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Minimal Viable Bot (MVP)
**Goal:** Ada responds to Matrix messages

**Features:**
- Connect to Matrix homeserver
- Join specified rooms
- Listen for mentions (@ada or "Ada:")
- Send message to Ada's /v1/chat/stream
- Post response back to Matrix
- No memory/context between messages (stateless)

**Files:**
- `matrix-bridge/bridge.py` - Main bot logic
- `matrix-bridge/Dockerfile` - Container
- `compose.yaml` - Add matrix-bridge service
- `matrix-bridge/config.yaml` - Bot configuration

**Config Needs:**
- Matrix homeserver URL
- Bot username/password (or access token)
- Room IDs to join (via invitation only - opt-in!)
- Ada brain URL (http://brain:7000)
- Bot identity settings (display name, avatar, bio)
- Privacy/disclosure preferences

### Phase 2: Conversation Context
**Goal:** Ada remembers conversation within rooms

**Features:**
- Track conversation history per room
- Pass recent messages as context to Ada
- Store/retrieve room-specific memories in RAG
- Handle typing indicators

**Changes:**
- Room-scoped conversation storage
- `/v1/chat/stream` context includes room_id
- RAG queries filtered by room scope

### Phase 3: Rich Interactions
**Goal:** Use Ada's full capabilities in Matrix

**Features:**
- React to messages (emoji reactions)
- Send formatted messages (markdown → Matrix formatting)
- Handle image uploads (OCR specialist)
- Thread support (reply to specific messages)
- Admin commands (!ada config, !ada status)

### Phase 4: Bidirectional Specialist (Optional)
**Goal:** Ada can mention Matrix from web UI

**Features:**
- New specialist: matrix_specialist
- Ada can ask "should I post this to Matrix?"
- Web UI users can trigger Matrix posts
- Cross-pollinate conversations

## Configuration Example

```yaml
# matrix-bridge/config.yaml
matrix:
  homeserver: "https://matrix.yourdomain.com"
  user_id: "@ada-bot:yourdomain.com"  # Bot-pattern naming
  password: "${MATRIX_PASSWORD}"  # or access_token
  device_name: "Ada Brain Bridge"
  
identity:
  # Clear bot identification
  display_name: "Ada [Bot]"  # or "Ada 🤖"
  avatar_url: ""  # MXC URL to bot avatar
  profile_bio: |
    AI assistant powered by DeepSeek-R1.
    Self-hosted and privacy-focused.
    Learn more: https://github.com/luna-system/ada
  
  # Transparency settings
  send_intro_on_join: true
  message_signature: false  # Add "— Ada (AI)" to every message?
  bot_flag: true  # Set m.bot type at protocol level
  
rooms:
  # NEVER auto-join! Only join when invited (opt-in model)
  # This list is for auto-accept when invited
  allowed_rooms:
    - "!roomid1:yourdomain.com"
    - "!roomid2:yourdomain.com"
  # Or use "*" to accept all invitations
  auto_accept_invites: true

activation:
  # How to trigger Ada
  respond_to:
    mention: true          # @ada
    display_name: true     # "Ada:" at start of message
    direct_message: true   # DMs always respond
    keywords: []           # Optional: ["ada", "hey ada"]
    
ada:
  brain_url: "http://brain:7000"
  stream_endpoint: "/v1/chat/stream"
  timeout: 120  # seconds
  
behavior:
  typing_indicator: true
  reaction_acknowledgment: "👍"  # React when processing
  max_context_messages: 10        # Include last N messages
  
privacy:
  # Ethical data handling
  store_in_rag: true  # Store conversations in vector DB
  allow_opt_out: true  # Users can disable with !ada privacy off
  respect_room_privacy: true
  data_retention_days: 90  # Optional: auto-delete old messages
```

## Environment Variables

Add to compose.yaml:

```yaml
matrix-bridge:
  environment:
    - MATRIX_HOMESERVER=${MATRIX_HOMESERVER}
    - MATRIX_USER_ID=${MATRIX_USER_ID}
    - MATRIX_PASSWORD=${MATRIX_PASSWORD}
    - ADA_BRAIN_URL=http://brain:7000
```

## Bot Identity & Transparency

**Critical:** Ada should be obviously identifiable as an AI bot, not impersonating a human.

### Matrix Bot Identification

1. **Display Name**
   - Format: `Ada [Bot]` or `Ada 🤖` 
   - Clear bot indicator in name

2. **User ID**
   - Use bot-pattern naming: `@ada-bot:yourdomain.com` or `@ada:yourdomain.com`
   - Avoid human-like names (@firstname)

3. **Profile/Avatar**
   - Non-human avatar (geometric, abstract, logo)
   - Profile description: "AI assistant powered by local LLM. Self-hosted by [your community]."
   - Link to documentation about how Ada works

4. **Matrix Bot Type Flag**
   - Set `m.bot` user type in profile (if supported by homeserver)
   - Marks account as automated at protocol level

5. **Message Signatures**
   - Optional footer: `— Ada (AI Assistant)`
   - Or use display name to carry this info

### Room Join Behavior

**Ethical considerations:**

1. **Opt-in, not opt-out**
   - Never auto-join rooms without invitation
   - Respect that some people don't want AI in their spaces
   - Make it easy to remove Ada from rooms

2. **Introduction Message**
   - When joining a room, post intro message:
     ```
     Hi! I'm Ada, an AI assistant running on this community's self-hosted infrastructure.
     
     I respond to @ada mentions and direct messages. I'm powered by DeepSeek-R1 
     and maintain conversation context within this room.
     
     Learn more: [link to docs]
     Remove me anytime: just kick me from the room!
     ```

3. **Room-Specific Config**
   - Some rooms might want Ada always-listening
   - Others might want mention-only
   - Some might want her completely silent (lurk mode)

### AI Disclosure in Responses

**Options for making generation transparent:**

1. **Subtle Approach** (Recommended)
   - Display name already indicates bot status
   - Profile clearly states AI assistant
   - No additional markers in every message

2. **Explicit Approach** (If community prefers)
   - Message footer: `[AI-generated response]`
   - Or: `— Generated by Ada using DeepSeek-R1`

3. **Configurable per Room**
   - Some rooms want explicit markers
   - Others find it cluttered
   - Make it a config option

### Cultural Sensitivity

**Addressing valid AI concerns:**

1. **Privacy Transparency**
   - Clear about what's stored: "Conversations stored locally in vector DB"
   - Opt-out mechanism: `!ada privacy off` disables RAG storage for room
   - Never send data to external services (it's all self-hosted!)

2. **Capability Limitations**
   - Don't overstate abilities
   - Be clear about being LLM-based (not AGI)
   - Admit uncertainty when appropriate

3. **Consent & Control**
   - Users can mute/block Ada
   - Room admins can kick Ada
   - No sneaky behavior or deception

4. **Attribution When Using External Info**
   - If web search specialist used: cite sources
   - If docs lookup: mention what docs
   - Make reasoning transparent

5. **Respect Community Norms**
   - If a room culture is "no bots", don't push it
   - Some spaces want human-only interaction - respect that
   - Position Ada as tool, not replacement for human community

### Implementation in Code

```python
# In config.py
class Config(BaseSettings):
    # Bot identity
    matrix_display_name: str = "Ada [Bot]"
    matrix_avatar_url: str = ""  # URL to bot avatar
    matrix_profile_description: str = (
        "AI assistant powered by DeepSeek-R1. "
        "Self-hosted and privacy-focused. "
        "Docs: https://your-docs-url.com"
    )
    
    # Disclosure settings
    message_signature: bool = False  # Add "— Ada (AI)" to messages?
    intro_message_on_join: bool = True
    
    # Privacy settings
    respect_room_privacy: bool = True
    allow_rag_opt_out: bool = True
```

```python
# In bridge.py
async def on_room_join(self, room: MatrixRoom):
    """Send introduction when joining new room"""
    if self.config.intro_message_on_join:
        await self.send_message(
            room.room_id,
            "👋 Hi! I'm Ada, an AI assistant. I respond to @mentions "
            "and DMs. I'm self-hosted and privacy-focused. "
            f"Learn more: {self.config.docs_url} "
            "Remove me anytime by kicking me from the room!"
        )
```

### Matrix Profile Setup

```python
async def setup_profile(self):
    """Configure bot profile for transparency"""
    await self.client.set_displayname(self.config.matrix_display_name)
    
    if self.config.matrix_avatar_url:
        await self.client.set_avatar(self.config.matrix_avatar_url)
    
    # Set profile description (if homeserver supports)
    await self.client.room_put_state(
        self.client.user_id,
        "m.room.member",
        {
            "displayname": self.config.matrix_display_name,
            "avatar_url": self.config.matrix_avatar_url,
            "bio": self.config.matrix_profile_description,
            "bot": True  # Mark as bot at protocol level
        }
    )
```

## Security Considerations

1. **Bot Account**
   - Dedicated Matrix account for Ada
   - Limit to specific rooms
   - Consider application service (AS) for larger scale

2. **Authentication**
   - Store access token securely (not password)
   - Refresh token handling
   - Room access controls

3. **Rate Limiting**
   - Respect Matrix homeserver limits
   - Queue messages if Ada's brain is slow
   - Don't respond to every message (avoid loops)

4. **Privacy**
   - Matrix room content stored in Ada's RAG?
   - Configurable per-room privacy levels
   - Encryption support (matrix-nio E2EE)
   - Clear disclosure about data storage
   - Opt-out mechanisms for users who prefer not to be stored

## Testing Strategy

1. **Unit Tests**
   - Message parsing
   - Context assembly
   - Response formatting

2. **Integration Tests**
   - Mock Matrix server
   - Test room joins/leaves
   - Test message flow

3. **Manual Testing**
   - Create test room
   - Invite Ada
   - Verify responses

## Dependencies

```txt
# matrix-bridge/requirements.txt
matrix-nio[e2e]==0.24.0
aiohttp==3.9.1
pyyaml==6.0.1
httpx==0.27.0
```

## Open Questions

1. **Conversation Scope**
   - Per-room memories vs. global Ada memory?
   - Should Ada remember across rooms?
   - Room-specific personas?

2. **Activation Patterns**
   - Only on mention, or follow conversations?
   - Configurable per-room?
   - Thread-aware (reply only to threads she's in)?

3. **Identity**
   - Same Ada personality in Matrix as web UI?
   - Different persona per room?
   - How to handle multiple simultaneous chats?

4. **Specialist Integration**
   - Can Matrix users trigger OCR (upload images)?
   - Web search from Matrix?
   - Docs lookup from Matrix?

## Success Metrics

**Phase 1 Complete When:**
- [ ] Ada joins Matrix room
- [ ] Responds to @ada mentions
- [ ] Maintains her personality
- [ ] No crashes for 24 hours

**Phase 2 Complete When:**
- [ ] Ada remembers conversation in room
- [ ] Context-aware responses
- [ ] Room-scoped memories work

**Phase 3 Complete When:**
- [ ] Rich formatting works
- [ ] Image OCR from Matrix uploads
- [ ] Admin commands functional

## Next Steps

1. Research: Check matrix-nio examples
2. Design: Finalize config structure
3. Implement: MVP bridge service
4. Test: Set up test Matrix room
5. Deploy: Add to compose.yaml
6. Document: Update docs/ with Matrix setup

## Timeline Estimate

- **MVP (Phase 1):** 1-2 days of focused work
- **Context (Phase 2):** 1 day
- **Rich features (Phase 3):** 2-3 days
- **Total:** ~1 week for full-featured Matrix bot

## Philosophy Alignment

This aligns with Ada's xenofeminist values:
- **Self-hosted:** Full control, no corporate surveillance
- **Federated:** Matrix is decentralized
- **Open protocols:** Matrix is open standard
- **Accessible:** Makes Ada available where you actually communicate
- **Privacy-first:** Your Matrix, your data, your Ada

---

**Status:** Design phase (2025-12-16)  
**Next:** Review design, get approval, start Phase 1 MVP
