# Matrix Integration - TODO

## Phase 1: MVP (Minimum Viable Product)

### Setup
- [ ] Create `matrix-bridge/` directory structure
- [ ] Add matrix-nio to requirements
- [ ] Create Dockerfile for matrix-bridge service
- [ ] Add matrix-bridge service to compose.yaml

### Core Implementation
- [ ] `config.py` - Pydantic Settings for configuration
- [ ] `identity.py` - Bot transparency and ethical presentation
- [ ] `ada_client.py` - HTTP client for Ada's brain API
- [ ] `message_handler.py` - Process incoming Matrix messages
- [ ] `bridge.py` - Main bot loop with matrix-nio

### Bot Identity & Ethics (Critical!)
- [ ] Display name includes [Bot] indicator
- [ ] User ID follows bot naming pattern (@ada-bot)
- [ ] Profile bio clearly states AI assistant
- [ ] Set m.bot flag at protocol level
- [ ] Intro message on room join (with opt-out info)
- [ ] Never auto-join rooms (invitation-only)
- [ ] Document privacy policy in profile
- [ ] Implement !ada privacy commands
- [ ] Clear attribution when using external sources
- [ ] Respect room cultures that prefer no bots

### Features
- [ ] Connect to Matrix homeserver
- [ ] Login with access token
- [ ] Listen for room messages
- [ ] Detect mentions (@ada or "ada" in message)
- [ ] Respond to direct messages automatically
- [ ] Forward messages to Ada brain `/v1/chat/stream`
- [ ] Post responses back to Matrix room
- [ ] Typing indicators while processing
- [ ] Error handling and graceful degradation

### Testing
- [ ] Unit tests for message detection
- [ ] Test Ada brain client
- [ ] Manual testing in test room
- [ ] 24-hour stability test

### Documentation
- [ ] README.md in matrix-bridge/
- [ ] docs/matrix_integration.rst
- [ ] Update docs/getting_started.rst with Matrix setup
- [ ] Update .ai/codebase-map.json
- [ ] Update .ai/context.md

### Deployment
- [ ] Environment variables documented
- [ ] Docker Compose tested
- [ ] Health check endpoint
- [ ] Logging configured

---

## Phase 2: Conversation Context

- [ ] RoomContextManager class
- [ ] Track last N messages per room
- [ ] Include context in Ada brain requests
- [ ] Persist context to disk
- [ ] Load context on restart
- [ ] Test context across restarts

---

## Phase 3: Rich Features (Future)

### Image Support
- [ ] Listen for m.image events
- [ ] Download images from Matrix media repo
- [ ] POST to Ada's /v1/ocr/extract endpoint
- [ ] Include OCR results in message context

### Reactions
- [ ] React with 👍 when starting processing
- [ ] React with ✅ when done
- [ ] React with ❌ on errors

### Admin Commands
- [ ] !ada status - Show system health
- [ ] !ada clear - Clear room context
- [ ] !ada help - Show available commands
- [ ] !ada persona - Show current personality
- [ ] !ada rooms - List rooms Ada is in

### Threading
- [ ] Detect thread replies
- [ ] Maintain thread-specific context
- [ ] Only respond in threads Ada is participating in

### Markdown Formatting
- [ ] Convert Ada's markdown to Matrix HTML
- [ ] Support bold, italic, code blocks
- [ ] Proper link rendering

---

## Phase 4: Bidirectional (Optional)

- [ ] New specialist: matrix_specialist.py
- [ ] LLM can request to send Matrix messages
- [ ] Web UI users can trigger Matrix posts
- [ ] Cross-reference Matrix conversations in web chats

---

## Nice-to-Have Enhancements

- [ ] Multiple personas per room (room-specific configs)
- [ ] Room join/leave events (greet new users)
- [ ] Presence updates (show Ada as "online")
- [ ] Read receipts (mark messages as read)
- [ ] Edit support (update messages if Ada corrects herself)
- [ ] Encryption support (E2EE with matrix-nio)
- [ ] Metrics/monitoring (message count, response times)
- [ ] Rate limiting (don't spam rooms)
- [ ] Ignore list (skip certain users/rooms)
- [ ] Scheduled messages (periodic updates)

---

## Current Status

**Branch:** feature/matrix-specialist  
**Phase:** Planning & Design  
**Next Step:** Review design docs, get approval, start Phase 1 MVP

**Design Documents:**
- `.ai/MATRIX_DESIGN.md` - Full architectural design
- `.ai/MATRIX_IMPLEMENTATION.md` - Step-by-step implementation guide
- This file - Task tracker

---

## Timeline Estimate

- **Phase 1 (MVP):** 1-2 days focused work
- **Phase 2 (Context):** 1 day
- **Phase 3 (Rich features):** 2-3 days
- **Total to production-ready:** ~1 week

---

## Questions to Answer

1. **Bot Account Setup**
   - Use existing Matrix account or create dedicated @ada account?
   - Which rooms should Ada auto-join?
   - What permissions does Ada need?

2. **Behavior**
   - Respond to all messages mentioning "ada" (case-insensitive)?
   - Only respond to direct @ada mentions?
   - Always respond in DMs?
   - Rate limiting strategy?

3. **Memory/Context**
   - Should Matrix conversations be stored in Ada's RAG?
   - Per-room memories or global?
   - Privacy considerations for Matrix logs?

4. **Integration**
   - Should web UI show Matrix activity?
   - Cross-room context (Ada knows about multiple Matrix rooms)?
   - How to handle simultaneous chats (Matrix + web UI)?

---

**Notes:**
- Start simple (MVP), iterate based on usage
- Matrix is federated - consider cross-server implications
- Self-hosted gives full control - no external dependencies
- Aligns with xenofeminist values (decentralized, privacy-first)
