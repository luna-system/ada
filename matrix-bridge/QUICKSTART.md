# Matrix Bridge - Quick Start

You're ready to connect Ada to Matrix! Here's what to do next:

## 1. Create Matrix Bot Account

On your Matrix homeserver:

### Option A: Via Element/Web Client
1. Open https://matrix.yourdomain.com (or app.element.io for matrix.org)
2. Register new account: `@ada-bot:yourdomain.com`
3. Log in and go to Settings → Security & Privacy
4. Create access token or use password

### Option B: Via API
```bash
# Get access token
curl -X POST https://matrix.yourdomain.com/_matrix/client/r0/login \
  -H "Content-Type: application/json" \
  -d '{
    "type": "m.login.password",
    "user": "ada-bot",
    "password": "YOUR_PASSWORD"
  }' | jq -r '.access_token'
```

Save the access token!

## 2. Configure Environment

Add to your `.env` file:

```bash
# Matrix Bridge Configuration
MATRIX_HOMESERVER=https://matrix.yourdomain.com
MATRIX_USER_ID=@ada-bot:yourdomain.com
MATRIX_ACCESS_TOKEN=syt_your_access_token_here
```

See `matrix-bridge/.env.example` for more options.

## 3. Start the Bridge

```bash
# Build and start
docker compose up -d matrix-bridge

# Watch logs
docker compose logs -f matrix-bridge
```

You should see:
```
Starting Ada Matrix Bridge
Homeserver: https://matrix.yourdomain.com
User: @ada-bot:yourdomain.com
Display name: Ada [Bot]
✅ Ada brain is healthy
✅ Logged in
✅ Profile set: Ada [Bot]
🤖 Ada is now online and listening
```

## 4. Invite Ada to a Room

In your Matrix client:
1. Create a test room (or use existing)
2. Invite @ada-bot:yourdomain.com
3. Ada joins and introduces herself
4. Try: `Ada: what's 2+2?`

## 5. Test Commands

```
Ada: hello                  # Chat with her
!ada help                   # Show commands
!ada status                 # Check system status
!ada privacy status         # Check privacy setting
!ada privacy off            # Disable memory storage
!ada clear                  # Clear context
```

## Troubleshooting

### Ada doesn't join
- Check logs: `docker compose logs matrix-bridge`
- Verify access token is valid
- Check homeserver URL

### Ada joins but doesn't respond
- Try direct message to isolate issue
- Check: `docker compose logs brain` for errors
- Verify brain is healthy: `curl http://localhost:7000/v1/healthz`

### Connection errors
```bash
# Test network connectivity
docker compose exec matrix-bridge ping matrix.yourdomain.com

# Check if brain is reachable
docker compose exec matrix-bridge curl http://brain:7000/v1/healthz
```

## What's Next?

Now that Phase 1 MVP is working, you can:

### Phase 2: Enhanced Features (Optional)
- [ ] Image OCR support (upload images to Ada in Matrix)
- [ ] Reactions and rich formatting
- [ ] Thread support
- [ ] Multiple room personas

### Documentation
- Update README.md with Matrix room link
- Add Matrix badge/link to docs
- Document community guidelines in Matrix room topic

### Community
- Announce Matrix space to community
- Get feedback on Ada's behavior
- Iterate based on usage

## Files Created

**Design documents (`.ai/`):**
- `MATRIX_DESIGN.md` - Full architecture
- `MATRIX_IMPLEMENTATION.md` - Implementation guide
- `MATRIX_ETHICS.md` - Ethical AI guidelines
- `MATRIX_TODO.md` - Task tracker

**Community:**
- `COMMUNITY_GUIDELINES.md` - Full guidelines
- `COMMUNITY_QUICK.md` - Short version

**Implementation (`matrix-bridge/`):**
- `bridge.py` - Main bot logic (297 lines)
- `config.py` - Configuration (169 lines)
- `identity.py` - Transparency helpers (55 lines)
- `ada_client.py` - Ada brain HTTP client (117 lines)
- `message_handler.py` - Context & commands (183 lines)
- `Dockerfile` - Container
- `README.md` - Full documentation
- `.env.example` - Configuration template

**Total:** ~2,900 lines of code and documentation

## Stats

```
3 commits on feature/matrix-specialist:
- Design documents (1,548 lines)
- Community guidelines (145 lines)
- MVP implementation (1,214 lines)

Total: 2,906 new lines
```

---

**You're all set!** Once you've created the bot account and configured `.env`, just start the bridge and invite Ada to rooms. 

The design emphasizes transparency and ethics, so Ada will be clearly identifiable as AI and easy to opt out of.

Have fun! 🚀🤖✨
