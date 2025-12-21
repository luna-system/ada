# Moonshot: Live Coding with Ada on Twitch

## Core Idea

Stream VSCode coding sessions to Twitch showing real-time AI pair programming with Ada.

**Purpose:** Show people what's possible with privacy-first local AI RIGHT NOW.

## The Setup

- VSCode with Ada via MCP integration
- Silent coding session (or chill music)
- Ada responding to questions in real-time
- Viewers see the actual workflow
- No corporate AI services, no surveillance, just local models

**The vibe:** Lo-fi beats to code/relax to, but with AI pair programming

## Moonshot Within the Moonshot

**Ada manages Twitch chat** 🤯

- Matrix bridge already proves Ada can handle chat protocols
- Twitch has IRC interface (similar to Matrix)
- Ada could:
  - Answer viewer questions about the code
  - Explain what we're building
  - Handle "!commands" for info
  - Be transparently identified as a bot (ethical presentation)

**Implementation:**
```
Twitch IRC → twitch-bridge (similar to matrix-bridge) → Ada brain API
```

Same pattern as Matrix integration, just different protocol.

## Why This Matters

**Most people think "good AI" requires:**
- Corporate cloud services
- Surveillance and data collection
- Expensive hardware
- Proprietary systems

**This stream proves:**
- ✅ Local AI works beautifully
- ✅ No data leaves your machine
- ✅ Runs on modest hardware
- ✅ Open source, hackable
- ✅ Actually helps with real work

**The educational angle:** People seeing Ada in action > any amount of documentation

## Technical Notes

**Streaming requirements:**
- OBS Studio (free, FOSS)
- Twitch account
- Screen capture of VSCode
- Optional: Webcam for reaction cam (or just code)

**Ada integration points:**
- MCP server already working in VSCode
- Could show web UI in PIP (picture-in-picture)
- Matrix bridge as proof of concept for Twitch bridge

**Bandwidth/Hardware:**
- Modern internet can handle 1080p 60fps stream
- Ada runs locally (no streaming impact)
- OBS is lightweight

## Potential Content Ideas

1. **Building Ada Features** - Meta: AI pair programming on AI features
2. **Community PRs** - Review/merge contributions live with Ada's help
3. **Bug Hunts** - Debugging sessions with Ada providing context
4. **Architecture Discussions** - Explore codebase with Ada's code specialist (once built)
5. **Documentation Sprints** - Write docs with Ada's help, show the process

## Chat Interaction Examples

**Viewer:** "What model is Ada using?"  
**Ada (in chat):** "I'm running a local Ollama model (configured by Luna). Luna can switch models depending on the task — right now we're using the configured default (often qwen2.5-coder:7b) for development work."

**Viewer:** "!help"  
**Ada (in chat):** "Available commands: !model, !specs, !github, !docs, !privacy | I'm Ada, a privacy-first AI assistant. Everything runs locally on Luna's machine. Ask me about the code we're writing!"

**Viewer:** "How does the caching work?"  
**Ada (in chat):** "We're implementing multi-timescale caching in this session. Persona/FAQ get cached for 24 hours since they change rarely. Memories refresh every 5 minutes. Want me to explain the implementation details?"

## Ethical Considerations

**Bot transparency:**
- Ada clearly identified in chat
- "🤖" emoji in username
- Regular reminders that she's AI
- Users can opt-out of interaction

**Privacy for viewers:**
- No logging of chat (beyond Twitch's own)
- Ada doesn't store viewer data
- Explicit that this is demonstration/educational

**Content moderation:**
- Ada should defer to Luna for moderation decisions
- Clear boundaries on what Ada responds to
- Twitch TOS compliance

## Next Steps (When We Want To Do This)

1. [ ] Set up Twitch account
2. [ ] Configure OBS for VSCode streaming
3. [ ] Test stream quality/setup
4. [ ] Build twitch-bridge (adapt matrix-bridge code)
5. [ ] Test Ada in Twitch chat
6. [ ] Announce stream, go live!
7. [ ] Archive VODs for people in different timezones

## Meta

**Category:** Planning (moonshot, community, education)  
**Status:** Future exploration, highly experimental, thoroughly fun  
**Audience:** Us, potential contributors, privacy-focused AI community  
**Signed:** Luna & Sonnet, December 2025 💜

---

*"Showing beats telling. Let them see what's possible."*
