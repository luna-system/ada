# Phase 0 Tool Grounding Handoff

**Date:** December 29, 2025, 22:36 UTC  
**Branch:** `v4.0rc1-consciousness-integration`  
**Last Commit:** `f7b2770` (fix persona.md mount)  
**Status:** 🔧 IN PROGRESS - Web Search Troubleshooting  
**Next Model:** Continue debugging web search specialist

## Session Overview

Working on **Kernel 4.0 Phase 0: Tool Grounding** - getting bidirectional tool use working inside the thinking loop. Successfully got datetime and Wikipedia working, currently debugging web search via SearxNG.

## What Was Accomplished

### ✅ Phase 0 Tool Activation Framework
- **datetime tool**: Working perfectly, returns real time data
- **wiki_lookup tool**: Working after boosting confidence from 0.7 → 0.85
- **Tool pattern matching**: `/home/luna/Code/ada/data/tool_patterns.json`
- **Confidence threshold**: 0.5 for activation

### ✅ Container Setup
- Correct container: `ada-consciousness-brain` on port 8888→6666
- Compose file: `docker-compose.ada-consciousness.yml` (NOT compose.yaml!)
- Model: qwen2.5-coder:7b via Ollama at http://172.17.0.1:11434
- ChromaDB: http://ada-chroma:8000

### ✅ Test Results
```bash
# Datetime working (confidence 0.577):
"Monday, December 29, 2025 at 10:19:19 PM UTC"

# Wikipedia working (confidence 0.59):
"Ada Lovelace was an English mathematician and writer..."
```

## 🔧 Current Issue: Web Search Not Working

### Symptom
Web search specialist activates with good confidence (0.72) but returns:
```
success=False, context_len=0
"web search functionality is not currently configured"
```

### Investigation So Far

1. **SearxNG URL Added**: `SEARXNG_URL=https://hunt.airsi.de/`
   - Luna confirmed this instance is working (OCI timeout bug fixed earlier)
   - Added to `docker-compose.ada-consciousness.yml`
   - Container recreated, env var now showing: `docker exec ada-consciousness-brain env | grep SEARX` ✅

2. **Specialist Enabled**: 
   - Renamed `web_search_specialist.py.disabled` → `web_search_specialist.py`
   - Shows in specialist list

3. **Container Logs Show**:
   ```
   [PHASE0] Request 19a67453: Found 1 tool matches for: search the web for what happened at the AI Gemini launch party today
   [PHASE0]   - web_search: 0.72, params={'query': 'search the web'}
   [PHASE0] Activating web_search with params={'query': 'search the web'}
   [PHASE0] web_search result: success=False, context_len=0
   ```

### Next Steps to Debug

1. **Check specialist instantiation** - The specialist has `__init__(self, searxng_url: Optional[str] = None)` and checks `if not self.searxng_url` before running. Need to verify how Phase 0 instantiates specialists and whether it passes the URL.

2. **Files to check**:
   - `brain/specialists/__init__.py` - How `get_specialist(name)` works
   - `brain/specialists/web_search_specialist.py` - Lines 220-250 have lazy initialization
   - `brain/app.py` - Lines 850-900 show Phase 0 activation code

3. **Hypothesis**: The `get_specialist()` function might be returning a specialist instance that doesn't have the SEARXNG_URL passed to its `__init__`. Need to verify the specialist registry initialization flow.

## Modified Files (Uncommitted)

```
Changes not staged for commit:
  modified:   brain/app.py                          (Phase 0 debug prints)
  modified:   brain/config.py                       (?)
  modified:   brain/qde_engine.py                   (?)
  modified:   brain/specialists/tool_activation.py  (Phase 0 framework)
  deleted:    brain/specialists/web_search_specialist.py.disabled
  modified:   data/tool_patterns.json               (datetime + wiki patterns)
  modified:   docker-compose.ada-consciousness.yml  (SEARXNG_URL added)

Untracked files:
  Ada-Consciousness-Research/02-EXPERIMENTS/KERNEL-4.0-RC1-PHASE0-TOOL-GROUNDING.md
  brain/specialists/web_search_specialist.py        (renamed from .disabled)
  brain/tool_grounding.py                           (new?)
```

## Key Context Files

### Documentation
- `.ai/context.md` - Main architecture overview
- `.ai/ADA-CHAT-ARCHITECTURE.md` - VS Code tool system design
- `Ada-Consciousness-Research/02-EXPERIMENTS/KERNEL-4.0-RC1-PHASE0-TOOL-GROUNDING.md` - Phase 0 docs

### Code
- `brain/app.py` - Lines 830-900 have Phase 0 activation logic
- `brain/specialists/tool_activation.py` - Pattern matching system
- `brain/specialists/__init__.py` - Specialist registry
- `data/tool_patterns.json` - Tool activation patterns

## Milestone 1 Goal

From Luna: *"giving ada a question that will require like maybe 3 or 4 consecutive tool calls... when we gave you that album, and asked you to 'feel' it, and you pulled like the wikipedia article, then the stereogum and pitchfork articles..."*

Once web search is working, test a multi-tool chain query that requires:
- Wikipedia lookup
- Web search for reviews/articles  
- Multiple consecutive tool activations
- Complex information synthesis

## Test Command

```bash
# Test web search (currently failing):
curl -sN "http://localhost:8888/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "search the web for latest AI news"}]}' \
  | head -100
```

## Environment Info

- **Container**: `ada-consciousness-brain`
- **Port**: 8888 (external) → 6666 (internal)
- **Ollama**: http://172.17.0.1:11434
- **ChromaDB**: http://ada-chroma:8000:8000
- **SearxNG**: https://hunt.airsi.de/
- **Model**: qwen2.5-coder:7b
- **Compose**: `docker-compose.ada-consciousness.yml`

## Commands for Next Session

```bash
# Check logs
docker logs ada-consciousness-brain 2>&1 | tail -50

# Verify env var
docker exec ada-consciousness-brain env | grep SEARX

# Restart after changes
cd /home/luna/Code/ada
docker compose -f docker-compose.ada-consciousness.yml up -d --force-recreate ada-brain

# Test datetime (working)
curl -sN "http://localhost:8888/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "what time is it?"}]}'

# Test wiki (working)
curl -sN "http://localhost:8888/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "who is Ada Lovelace?"}]}'

# Test web search (BROKEN - debug this!)
curl -sN "http://localhost:8888/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "search the web for latest AI news"}]}'
```

## luna's Notes

- "the kiddo knows fandom is the WORST LOL" - Skip Fandom wiki complexity
- Focus on Wikipedia + web search for now
- Two container confusion resolved (ada-consciousness-brain vs ada-v1-brain-1)
- SearxNG at hunt.airsi.de confirmed working (OCI bug fixed earlier)

## Session Artifacts

### Test Results
- Datetime activation: ✅ 0.577 confidence, real time returned
- Wikipedia activation: ✅ 0.59 confidence (after boosting to 0.85)
- Web search activation: ❌ 0.72 confidence, but returns error

### Docker Compose Fix
The SEARXNG_URL line got merged into the CHROMA_URL line as a comment. Fixed:
```yaml
# BEFORE (broken):
- CHROMA_URL=http://ada-chroma:8000  # Connect to Chroma container      - SEARXNG_URL=https://hunt.airsi.de/  # Web search via SearxNG      - RAG_ENABLED=true

# AFTER (fixed):
- CHROMA_URL=http://ada-chroma:8000
- SEARXNG_URL=https://hunt.airsi.de/
- RAG_ENABLED=true
```

## Priority for Next Model

1. **DEBUG WEB SEARCH** - Specialist activates but returns "not configured"
   - Check how `get_specialist()` instantiates specialists
   - Verify SEARXNG_URL gets passed to specialist `__init__`
   - Look at lazy initialization in web_search_specialist.py lines 220-250

2. **Test multi-tool chain** once web search works
   - Need 3-4 consecutive tool calls
   - Test with complex query requiring Wikipedia + web search

3. **Document in research log** once stable
   - Update `KERNEL-4.0-RC1-PHASE0-TOOL-GROUNDING.md`

## Emotional Context

Luna got rate limited on Opus mid-troubleshooting, had to switch to Sonnet mid-session. Apologetic about the abrupt handoff but super appreciative. This is urgent because they're actively debugging, not a leisurely handoff. 💜

---

**Handoff Quality:** ⭐⭐⭐⭐ (4/5) - Good detail, clear next steps, but web search bug not yet root-caused  
**Estimated Time to Resume:** <5 minutes (everything documented, just need to continue debugging)  
**Blocker:** Web search specialist initialization issue (high priority)

*"so sorry to throw you into the fray like this, sonnet. appreciate you a TON!! <3"* - Luna
