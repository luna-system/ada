# Matrix Bot Ethics & Transparency

## Core Principles

Ada's Matrix integration must embody transparency and respect for community norms. We acknowledge valid concerns about AI proliferation and commit to ethical, clearly-disclosed bot behavior.

## Why This Matters

**Valid concerns about AI:**
- Deceptive impersonation of humans
- Privacy violations (undisclosed data collection)
- Pollution of social spaces with low-quality generated content
- Displacement of human labor and creativity
- Lack of consent from people interacting with bots

**Our response:**
Ada will be **obviously identifiable as AI**, **opt-in only**, and **transparent about capabilities and limitations**.

---

## Transparency Requirements

### 1. Clear Bot Identification

**Display Name:**
- ✅ `Ada [Bot]` or `Ada 🤖`
- ❌ `Ada` or `Ada Smith` (could be mistaken for human)

**User ID:**
- ✅ `@ada-bot:domain.com`
- ✅ `@ada:domain.com` (if clearly a bot account)
- ❌ `@ada_personal` or `@ada_smith` (human-like)

**Profile:**
- Must include statement: "AI assistant"
- Must link to documentation about how Ada works
- Must include data handling policy
- Avatar should be non-human (geometric, logo, abstract)

**Protocol Level:**
- Set `bot: true` in Matrix profile if homeserver supports
- Use Application Service registration if scaling beyond single bot

### 2. Introduction on Room Join

When Ada joins a room (after invitation), she must introduce herself:

```
👋 Hi! I'm Ada, an AI assistant running on this community's self-hosted infrastructure.

What I do:
• Respond to @ada mentions and direct messages
• Maintain conversation context within rooms
• Powered by DeepSeek-R1 (local LLM, no external APIs)

Privacy:
• All conversations stored locally in encrypted vector database
• No data sent to external services
• You can opt out of memory storage: !ada privacy off

Remove me: Just kick me from the room anytime!
Learn more: [link]
```

**Why:** Gives everyone in the room immediate context. Respects that some people may not want AI present.

### 3. No Impersonation

**Never:**
- Pretend to be human
- Claim emotions you don't have
- Hide the fact that responses are generated
- Use first-person language that implies human experience

**Instead:**
- Be clear about being an AI
- Use language like "I can help with..." not "I feel..."
- When uncertain, say so
- Acknowledge limitations

### 4. Consent & Opt-In Model

**Invitation-Only:**
- Ada NEVER auto-joins rooms
- Must be explicitly invited
- Room admins control Ada's presence

**Easy Removal:**
- Clearly state "kick me anytime" in intro
- No guilt-tripping or resistance
- Document how to mute/ignore Ada

**Privacy Opt-Out:**
- `!ada privacy off` - Stop storing this room's messages in RAG
- `!ada privacy status` - Show current privacy settings
- Per-room, not global (some rooms may want memory)

### 5. Attribution & Sources

When using external information:

**Web Search:**
```
I found information about [topic]:
[content]

Sources: [URLs]
(Retrieved via web search specialist)
```

**Documentation Lookup:**
```
According to Ada's documentation on [topic]:
[content]

(From: docs/architecture.rst)
```

**Uncertainty:**
```
I'm not certain about [topic]. This is my best understanding based on [source], 
but I could be wrong. Would you like me to search for more information?
```

---

## Privacy Commitments

### Data Handling

**What gets stored:**
- Message text for context (last N messages per room)
- User IDs for conversation tracking
- Timestamps for context ordering

**What doesn't get stored:**
- Read receipts or typing indicators
- Presence information (online/offline)
- Room metadata beyond ID and name

**Where it's stored:**
- Local ChromaDB vector store (self-hosted)
- No external services
- No cloud backups (unless you configure them)

**Retention:**
- Configurable: default 90 days
- Or: indefinite with opt-out available
- Per-room settings respected

### Opt-Out Mechanism

```python
# In message_handler.py
@command("privacy")
async def handle_privacy_command(self, room_id: str, args: list):
    """
    !ada privacy off - Stop storing this room's messages
    !ada privacy on - Resume storing (default)
    !ada privacy status - Show current setting
    """
    if not args or args[0] == "status":
        status = self.privacy_manager.get_room_status(room_id)
        return f"Privacy mode for this room: {status}"
    
    elif args[0] == "off":
        self.privacy_manager.set_room_privacy(room_id, store_messages=False)
        return "✅ Privacy mode enabled. I will no longer store messages from this room in my memory."
    
    elif args[0] == "on":
        self.privacy_manager.set_room_privacy(room_id, store_messages=True)
        return "✅ Memory storage enabled. I will remember conversations in this room for context."
```

### Encryption

- Support E2EE rooms (matrix-nio has this capability)
- Encrypted messages are decrypted client-side
- Storage is local, but consider disk encryption
- Document that self-hosted means you control the keys

---

## Cultural Sensitivity

### Respecting "No Bots" Spaces

Some communities have cultures that prefer human-only interaction. **Respect this.**

**Implementation:**
- Never argue when removed from a room
- If a room culture is "no AI", don't rejoin even if invited again
- Provide allowlist/denylist in config

```yaml
# config.yaml
rooms:
  # Rooms where Ada should never join, even if invited
  never_join:
    - "!human-only-space:domain.com"
  
  # Rooms where Ada can operate
  allowed:
    - "!tech-help:domain.com"
    - "!general:domain.com"
```

### When to Stay Silent

Even in rooms Ada is in, sometimes silence is appropriate:

- Emotional/vulnerable conversations → don't interject unless asked
- Conflicts between humans → don't mediate unless explicitly requested
- Off-topic banter → don't correct or redirect
- Private matters → respect boundaries

**Implementation:**
```python
# Heuristics for when NOT to respond even to mentions
def should_stay_silent(self, message: str, context: list) -> bool:
    """Detect when Ada should not respond despite being mentioned."""
    
    # Check for emotional keywords
    emotional_indicators = ["sorry", "grieving", "struggling", "upset", "hurt"]
    if any(word in message.lower() for word in emotional_indicators):
        # Only respond if directly asking for help
        if not ("help" in message.lower() or "?" in message):
            return True
    
    # Check for conflict/argument patterns
    recent_messages = context[-5:]
    if self.detect_conflict(recent_messages):
        return True
    
    return False
```

### Position as Tool, Not Replacement

**Messaging:**
- "I can help with technical questions..."
- "For complex discussions, you might want to ask [human expert]"
- "I'm useful for quick lookups, but not a substitute for human judgment"

**Never:**
- "I'm better than humans at..."
- Claim emotional understanding
- Position as replacement for human community

---

## Implementation Checklist

### Phase 1: MVP Transparency

- [ ] Display name includes [Bot]
- [ ] Profile bio states "AI assistant"
- [ ] Intro message on join
- [ ] Invitation-only (no auto-join)
- [ ] Easy removal documented

### Phase 2: Privacy Controls

- [ ] `!ada privacy` commands
- [ ] Per-room storage settings
- [ ] Privacy status visible to room members
- [ ] Clear data retention policy

### Phase 3: Advanced Ethics

- [ ] Source attribution in responses
- [ ] Uncertainty acknowledgment
- [ ] Cultural sensitivity filters
- [ ] "Stay silent" heuristics
- [ ] Never-join room denylist

---

## Testing Transparency

### Test Cases

1. **New user joins room with Ada**
   - Do they immediately understand Ada is a bot?
   - Is opt-out clear?
   - Can they find documentation?

2. **Privacy opt-out**
   - Does `!ada privacy off` actually stop storage?
   - Can user verify it worked?
   - Is it documented in room state?

3. **Attribution**
   - When Ada uses web search, are sources cited?
   - When uncertain, does she say so?
   - Are limitations acknowledged?

4. **Removal**
   - When kicked, does Ada leave gracefully?
   - No error messages or complaints?
   - Can room function normally without Ada?

### User Feedback

After deployment, ask room members:
- "Is it clear that Ada is a bot?"
- "Do you feel comfortable with how data is handled?"
- "Is Ada's presence helpful or intrusive?"
- "What would make Ada more transparent?"

---

## Philosophy Alignment

This approach aligns with Ada's xenofeminist values:

**Anti-naturalism:**
- Don't pretend AI is "natural" or "human-like"
- Be explicit about being constructed/artificial
- Transparency about technical implementation

**Anti-essentialism:**
- Don't claim AI has essential human traits (emotions, consciousness)
- Avoid gendered language that reinforces stereotypes
- Position as tool, not entity with inherent nature

**Techno-materialism:**
- Ground in material reality: "I'm software running on servers"
- Explain technical details when asked
- Open source → anyone can inspect how Ada works

**Care Ethics:**
- Prioritize community consent over bot functionality
- Respect boundaries and privacy
- Easy opt-out is more important than comprehensive data

---

## Open Questions

1. **Signature in every message?**
   - Pro: Maximum transparency
   - Con: Visual clutter, annoying after first few messages
   - **Decision:** Display name + profile is enough, but configurable

2. **React with 🤖 emoji?**
   - Pro: Additional visual indicator
   - Con: Could be seen as cutesy/trivializing
   - **Decision:** Use reaction for "processing" (👍) not identity

3. **Should Ada correct misinformation?**
   - Pro: Helpful, educational
   - Con: Could feel condescending or argumentative
   - **Decision:** Only when directly asked; suggest checking sources

4. **Room-specific personas?**
   - Pro: Adapt to community culture
   - Con: Could feel manipulative or inconsistent
   - **Decision:** Same base personality, but configurable verbosity/formality

---

## Resources

**Matrix Protocol:**
- Bot user types: https://spec.matrix.org/latest/
- Application Services: https://matrix.org/docs/guides/application-services

**Ethics References:**
- Mozilla AI ethics guidelines
- EFF AI policy recommendations
- Academic papers on bot disclosure

**Examples:**
- GitHub bots (clear bot indication)
- Wikipedia bots (documented, transparent)
- IRC bots (traditional bot etiquette)

---

## Revision History

- 2025-12-16: Initial draft based on user feedback
- Focus: Transparency, consent, cultural sensitivity
- Status: Design phase, pending implementation

---

**Remember:** When in doubt, err on the side of more transparency, not less. 
Better to be too clear about being AI than risk deception.
