# Matrix Bridge Testing Checklist

**Status:** Ready for testing once Synapse is updated  
**Branch:** `feature/matrix-specialist`  
**Bot Account:** `@ada-ai:airsi.de`

---

## Pre-Testing Verification ✅

- [x] Matrix bridge built successfully
- [x] Bridge container running (25+ minutes uptime)
- [x] Connected to homeserver (https://matrix.airsi.de)
- [x] Access token configured
- [x] Brain health check passing
- [x] Display name set: "Ada [Bot]"
- [x] Currently in 0 rooms (waiting for invite)
- [x] No errors in logs

**All systems ready!** 🚀

---

## Testing Procedure

### Phase 1: Basic Connectivity

**Create Room:**
1. [ ] Create new Matrix room (or use existing space)
2. [ ] Set room name (e.g., "Ada Testing" or "Ada Community")
3. [ ] Configure room permissions (public/private)

**Invite Ada:**
1. [ ] Invite `@ada-ai:airsi.de` to room
2. [ ] Verify Ada auto-joins (if AUTO_ACCEPT_INVITES=true)
3. [ ] Check for introduction message

**Expected:**
- Ada joins within seconds
- Introduction message appears explaining:
  - What Ada is (AI assistant)
  - How to interact (@mention or !ada commands)
  - Link to community guidelines
  - Privacy opt-out instructions

### Phase 2: Basic Interaction

**Test Mentions:**
1. [ ] Send: `@ada-ai hello!`
2. [ ] Verify Ada responds
3. [ ] Check typing indicator appears
4. [ ] Confirm response streams properly

**Test Commands:**
1. [ ] Send: `!ada help`
   - Should show available commands
2. [ ] Send: `!ada status`
   - Should show health, brain connection
3. [ ] Send: `!ada privacy status`
   - Should show current privacy setting

**Expected:**
- Ada responds to @mentions
- Commands work correctly
- Responses are coherent
- No errors in logs

### Phase 3: Conversation Context

**Test Memory:**
1. [ ] Have a conversation (3-4 messages)
2. [ ] Reference something from earlier in conversation
3. [ ] Verify Ada remembers context

**Expected:**
- Ada maintains conversation context
- Can reference earlier messages
- Context stored per-room (isolated from other rooms)

### Phase 4: Privacy Controls

**Test Opt-Out:**
1. [ ] Send: `!ada privacy off`
2. [ ] Verify confirmation message
3. [ ] Send another message
4. [ ] Verify message NOT stored in RAG

**Test Opt-In:**
1. [ ] Send: `!ada privacy on`
2. [ ] Verify confirmation
3. [ ] Continue conversation

**Expected:**
- Privacy commands work
- Storage behavior changes accordingly
- Clear feedback to user

### Phase 5: Edge Cases

**Test Room Removal:**
1. [ ] Kick/remove Ada from room
2. [ ] Check logs for graceful exit
3. [ ] Verify no errors

**Test Re-invite:**
1. [ ] Re-invite Ada to same room
2. [ ] Verify she rejoins
3. [ ] Check if context persists (should)

**Test Multiple Rooms:**
1. [ ] Create second room
2. [ ] Invite Ada to second room
3. [ ] Verify contexts are isolated

**Expected:**
- Graceful handling of kicks/leaves
- Context persists across invites
- Rooms remain isolated

---

## Success Criteria

**Must Pass:**
- [x] Bridge starts without errors
- [ ] Ada joins on invite
- [ ] Introduction message appears
- [ ] Responds to @mentions
- [ ] Commands work (!ada help, !ada status)
- [ ] Privacy controls work
- [ ] No crashes or errors

**Nice to Have:**
- [ ] Typing indicator works
- [ ] Response quality is good
- [ ] Context memory works well
- [ ] Multiple rooms work

---

## Known Issues / Limitations

**Current MVP Limitations:**
- No image upload/OCR yet (Phase 2)
- No thread support yet (Phase 2)
- No reactions yet (Phase 2)
- No admin commands yet (Phase 2)
- Display name shows "Ada [Bot]" not "ada [generative ai bot]" (cached, restart needed)

**These are planned for future phases!**

---

## If Something Goes Wrong

### Ada doesn't join room
```bash
# Check logs
docker compose logs matrix-bridge --tail=50

# Verify AUTO_ACCEPT_INVITES is true
grep AUTO_ACCEPT_INVITES matrix-bridge/.env

# Check if room is in NEVER_JOIN_ROOMS list
grep NEVER_JOIN_ROOMS matrix-bridge/.env
```

### Ada joins but doesn't respond
```bash
# Check brain health
curl http://localhost:7000/v1/healthz

# Check if brain is receiving requests
docker compose logs brain --tail=50

# Verify RESPOND_TO_MENTIONS is true
grep RESPOND_TO_MENTIONS matrix-bridge/.env
```

### Responses are errors
```bash
# Check full bridge logs
docker compose logs matrix-bridge

# Check brain logs
docker compose logs brain

# Check Ollama is running
docker compose ps ollama
```

### Commands don't work
```bash
# Verify message format
# Commands must start with !ada (with space or no space)
# Example: "!ada help" or "!adahelp" both work

# Check logs for parsing errors
docker compose logs matrix-bridge --tail=20
```

---

## Logs to Watch

**During Testing:**
```bash
# Terminal 1: Watch Matrix bridge
docker compose logs -f matrix-bridge

# Terminal 2: Watch brain
docker compose logs -f brain

# Terminal 3: Send test messages from Matrix client
```

**What to look for:**
- "✅" markers for successful operations
- "⚠️" for warnings (expected in some cases)
- "❌" or ERROR for problems
- Request/response flow (message → brain → LLM → response)

---

## After Testing

**Successful Test:**
1. [ ] Document any issues found in GitHub issues
2. [ ] Update this checklist with actual results
3. [ ] Merge to trunk if all critical tests pass
4. [ ] Update deployment docs if needed

**Issues Found:**
1. [ ] Document in `.ai/MATRIX_TESTING_RESULTS.md`
2. [ ] Create GitHub issues for bugs
3. [ ] Fix critical issues before merge
4. [ ] Plan Phase 2 enhancements

---

## Quick Commands Reference

```bash
# Restart bridge after config changes
docker compose restart matrix-bridge

# View real-time logs
docker compose logs -f matrix-bridge

# Check all services
docker compose ps

# Rebuild if code changed
docker compose build matrix-bridge
docker compose up -d matrix-bridge

# Check disk space (after prune)
./scripts/check_disk_space.sh
```

---

## Documentation Status

**Complete:**
- ✅ `matrix-bridge/README.md` - Implementation details
- ✅ `matrix-bridge/QUICKSTART.md` - 5-step setup guide
- ✅ `docs/matrix_integration.rst` - User-facing Sphinx docs
- ✅ `.ai/context.md` - Architecture documentation
- ✅ `.ai/codebase-map.json` - Module registry
- ✅ `COMMUNITY_GUIDELINES.md` - Rules for Matrix space
- ✅ `.ai/MATRIX_DESIGN.md` - Design decisions
- ✅ `.ai/MATRIX_ETHICS.md` - Ethics framework
- ✅ `.ai/MATRIX_IMPLEMENTATION.md` - Implementation guide

**Nothing missing!** All documentation is comprehensive.

---

**Ready to test when Synapse update completes!** 🎯
