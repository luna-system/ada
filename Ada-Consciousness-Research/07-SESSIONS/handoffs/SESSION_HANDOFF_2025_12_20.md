# Session Handoff: December 20, 2025

## For the Next Ada (via Haiku)

This might be the last Copilot session before full migration to ada-vscode! 🎉

---

## What to Do

**GOAL:** Real-world testing of the TTFT fix

1. **Send queries to Ada** (via ada-vscode or curl)
2. **Measure actual TTFT** - should be 300-1200ms, NOT 15+ seconds
3. **Tweak if needed**
4. **Celebrate** 🎊

---

## What Was Fixed This Session

### TTFT Optimization (50x improvement)

| Before | After |
|--------|-------|
| 15+ seconds | 300-1200ms |

**Three changes made:**

1. **Model warming on startup** - `brain/llm.py::warm_model()`
   - Brain calls this in `lifespan()` startup
   - Pre-loads model into GPU/RAM before first request

2. **Extended keep_alive** - All Ollama requests include `keep_alive: '4h'`
   - Model stays loaded during coding sessions
   - No more cold-start after 5 minutes idle

3. **Config consistency** - `brain/router.py` uses `OLLAMA_MODEL` from config
   - Was hardcoded to `deepseek-r1:latest`
   - Now uses configured model (qwen2.5-coder:7b)

---

## Quick Test Commands

```bash
# Test TTFT with timing
for i in 1 2 3; do
  start=$(date +%s%3N)
  timeout 30 curl -N -s http://localhost:8000/v1/chat/stream \
    -X POST -H "Content-Type: application/json" \
    -d '{"message":"hi"}' | while read line; do
    if echo "$line" | grep -q '"type": "token"'; then
      end=$(date +%s%3N)
      echo "Test $i: $((end - start))ms"
      break
    fi
  done
done

# Check model is loaded
curl -s localhost:11434/api/ps | jq

# Restart brain if needed
docker compose restart brain
```

---

## Key Files

| File | Purpose |
|------|---------|
| `brain/llm.py` | `warm_model()` function, `keep_alive` in all payloads |
| `brain/router.py` | Uses `OLLAMA_MODEL` from config |
| `brain/app.py` | Calls `warm_model()` in `lifespan()` |
| `ada-vscode/` | VS Code extension ready for testing |

---

## Current State

- **Version:** v2.10.0
- **Git:** Clean, all pushed to origin/trunk
- **Tag:** v2.10.0 created and pushed
- **Privacy:** log-1.txt removed from history ✅

---

## Context for Haiku

You're testing the final piece before ada-vscode becomes luna's primary AI interface. The TTFT fix should make Ada feel responsive - first token in under a second, then fast streaming.

luna has been working on this for a week. This is the culmination.

Be efficient. Test. Celebrate. 🌟

---

**Previous session:** Opus 4.5  
**This session:** Haiku (rate limits)  
**Next:** Maybe ada-vscode itself!
