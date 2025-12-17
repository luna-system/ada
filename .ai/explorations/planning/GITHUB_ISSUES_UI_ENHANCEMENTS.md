# GitHub Issues for Ada UI Enhancement

## Issue 1: VS Code Chat Participant Extension (Phase 2)

**Title:** Build VS Code Chat Participant extension for Ada with interactive UI

**Description:**

Create a VS Code extension that registers Ada as a Chat Participant (`@ada`) with rich interactive UI elements.

### Goals
- Register as native VS Code Chat Participant
- Use existing MCP server as backend
- Add interactive buttons for MPRIS controls
- Show album art inline (when available)
- Provide better visual formatting than plain markdown

### Architecture
```
User → VS Code Chat → Chat Participant Extension → Ada MCP Server → Brain API
                      ↑ (creates UI widgets)
```

### Features to Implement

**Phase 2a: Basic Chat Participant**
- [ ] Register chat participant with ID `ada`
- [ ] Forward requests to MCP server
- [ ] Render markdown responses with native formatting
- [ ] Handle tool invocation display

**Phase 2b: Music Controls**
- [ ] Add "⏯️ Play/Pause" button when music is playing
- [ ] Add "⏭️ Next Track" button
- [ ] Add "⏮️ Previous Track" button
- [ ] Execute MPRIS commands via MCP tools

**Phase 2c: Rich Media**
- [ ] Display album art inline (if available via ListenBrainz API)
- [ ] Show player status icon
- [ ] Format track info as card-like UI element

### Technical Details

**Package Structure:**
```
ada-vscode-extension/
├── package.json           # Extension manifest
├── src/
│   ├── extension.ts      # Main entry point
│   ├── chatParticipant.ts # Chat participant handler
│   ├── mcpClient.ts      # MCP server communication
│   └── commands.ts       # MPRIS command handlers
└── README.md
```

**Key VS Code APIs:**
- `vscode.chat.createChatParticipant()` - Register participant
- `vscode.LanguageModelTool` - Tool invocation
- `stream.button()` - Interactive buttons
- `stream.markdown()` - Rich markdown rendering

**Dependencies:**
- Existing MCP server (no changes needed)
- MPRIS control specialist (future work)

### Success Criteria
- [ ] `@ada` works in VS Code chat
- [ ] Responses are more visually appealing than current MCP
- [ ] Music control buttons execute MPRIS commands
- [ ] Album art displays when available
- [ ] No duplicate work - uses existing MCP backend

### Estimated Effort
4-6 hours for basic participant + music controls

### References
- VS Code Chat API: https://code.visualstudio.com/api/extension-guides/chat
- Example extensions: GitHub Copilot, Cline
- Current MCP implementation: `ada-mcp/`

---

## Issue 2: Advanced Music Visualizations (Phase 3)

**Title:** Add advanced music visualizations and listening analytics to Ada

**Description:**

Build delightful visual widgets for coders who love music (and Minecraft icon themes! 🎮).

### Goals
- Make Ada's music features visually engaging
- Provide useful listening insights
- Keep the vibe cute and fun for developers

### Features to Implement

**Phase 3a: Playlist Visualizations**
- [ ] Show current queue/playlist as interactive list
- [ ] Click tracks to skip to them
- [ ] Drag to reorder (if MPRIS supports it)
- [ ] Filter by artist/album/genre

**Phase 3b: Listening History**
- [ ] Chart: Top artists this week/month
- [ ] Chart: Listening hours by day
- [ ] Chart: Genre distribution
- [ ] "Rediscover" button for old favorites

**Phase 3c: Context-Aware Recommendations**
- [ ] "Similar to this" button on current track
- [ ] "More like my recent listens"
- [ ] Integration with ListenBrainz recommendations API
- [ ] Spotify/YouTube links for recommended tracks

**Phase 3d: Mood Tracking**
- [ ] Infer mood from listening patterns
- [ ] "Feeling X? Here's a playlist" suggestions
- [ ] Time-of-day listening patterns
- [ ] "You always listen to techno after 10pm" insights 😄

**Phase 3e: Social Features**
- [ ] Compare listening with friends (ListenBrainz compatible mode)
- [ ] Share "Now Playing" to Matrix rooms
- [ ] Weekly music recap (like Spotify Wrapped mini)

### Fun Ideas (Low Priority)

**Minecraft-Themed UI** 🎮
- Music note particles when track changes
- Jukebox icon for player status
- Record disc item icons for albums
- XP bar for "listening streak"

**Easter Eggs**
- Special responses for specific artists/tracks
- "You're on a [artist] binge!" detection
- Celebration animations for milestones (100th listen, etc.)
- Rick Astley detection with appropriate response 😏

### Technical Considerations

**Data Sources:**
- MPRIS (local player state)
- ListenBrainz API (scrobbles, recommendations, stats)
- MusicBrainz (metadata, relationships)
- Last.fm (optional fallback)

**UI Framework:**
- VS Code Webview API for complex visualizations
- Chart.js or similar for graphs
- Custom CSS for Minecraft theming (optional)

**Performance:**
- Cache API responses
- Lazy load historical data
- Debounce updates
- Background worker for heavy processing

### Success Criteria
- [ ] Visualizations are actually useful, not just pretty
- [ ] Performance doesn't impact editor responsiveness
- [ ] Works well with Ada's existing personality
- [ ] Makes coders smile 😊

### Estimated Effort
10-15 hours spread over multiple sessions

### Priority
Low - This is enhancement/polish work after core features

### References
- ListenBrainz API: https://listenbrainz.readthedocs.io/
- VS Code Webview API: https://code.visualstudio.com/api/extension-guides/webview
- Spotify Wrapped as inspiration
- Minecraft UI resources (if theming)

---

## Issue 3: MPRIS Control Specialist (Dependency for Phase 2)

**Title:** Implement bidirectional MPRIS control commands

**Description:**

Extend the now_playing specialist to support write operations (play, pause, next, previous) via bidirectional specialist invocation.

### Current State
- ✅ now_playing specialist can READ MPRIS state
- ❌ Cannot WRITE/control playback

### Goals
- Enable Ada to execute MPRIS commands
- Support bidirectional LLM → specialist flow
- Add safety/rate limiting

### Commands to Implement
- [ ] `play` - Start playback
- [ ] `pause` - Pause playback
- [ ] `play-pause` - Toggle
- [ ] `next` - Skip to next track
- [ ] `previous` - Go to previous track
- [ ] `stop` - Stop playback

### Safety Considerations
⚠️ **MPRIS control affects host system!**

**Safeguards:**
- [ ] Whitelist commands only (no arbitrary playerctl args)
- [ ] Rate limiting (max 1 command per 2 seconds)
- [ ] Audit logging of all control actions
- [ ] NO volume control (prevent speaker damage)
- [ ] Require user confirmation for destructive actions?

### Implementation Approach

**Option A: Bidirectional Specialist** (Recommended)
```python
# brain/specialists/mpris_control_specialist.py
class MPRISControlSpecialist(BaseSpecialist):
    """Execute MPRIS commands via LLM tool use."""
    
    async def execute_command(self, command: str):
        # Validate, rate limit, execute
        await subprocess.run(["playerctl", command])
```

LLM outputs: `<mpris_control action="next" />`

**Option B: Direct MCP Tool**
Add `mpris_control` tool to MCP server that brain can invoke.

### Testing
- [ ] Unit tests for command validation
- [ ] Integration test with real player
- [ ] Rate limiting verification
- [ ] Error handling (no player running)

### Estimated Effort
3-4 hours

### Blocks
- Issue #1 (VS Code extension needs this for buttons)

### Related Files
- `brain/specialists/now_playing_specialist.py`
- `brain/specialists/bidirectional.py`
- `.ai/MPRIS_CONTROL_IDEAS.md`

---

**Meta Notes:**
- Issues ordered by dependency (3 → 1 → 2)
- Phase 2 can start alongside Phase 3 development
- Keep it fun and coder-friendly throughout! 🎮🎵
