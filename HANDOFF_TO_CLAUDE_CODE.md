# Handoff to Claude Code - December 20, 2025

**From:** GitHub Copilot (Opus 4.5) session  
**To:** Claude Sonnet session  
**Time:** 3am bedtime handoff 🌙  
**Status:** VS Code extension chat is WORKING! Ready for next polish pass.

---

## Current State

### Repository
- **Repo:** luna-system/ada
- **Branch:** `trunk`
- **Working tree:** Clean (just committed)
- **Last commit:** `16e08db` - "fix(ada-vscode): add type:webview to chat view declaration"

### What We Just Completed

1. **✅ VS Code Chat Sidebar - FIXED!**
   - **Root cause found:** Missing `"type": "webview"` in package.json view declaration
   - Without this, VS Code expected TreeView provider, not WebviewViewProvider
   - Fix applied, extension rebuilt, chat now renders correctly!
   - See: [ada-vscode/package.json](ada-vscode/package.json) line ~98

2. **✅ Model Configuration Verified**
   - `qwen2.5-coder:7b` is default everywhere (no deepseek sneaking in)
   - `keep_alive: 4h` configured in brain/llm.py
   - Local Ollama has model warm on GPU (720ms TTFT!)

3. **✅ TTFT Analysis**
   - Docker Ollama: 100% CPU → 10+ second TTFT (slow)
   - Local Ollama: 100% GPU → 720ms TTFT (fast!)
   - Quick fix: Set `ada.chatUseBrain: false` to use local GPU Ollama
   - Proper fix TODO: Configure Docker Compose with GPU profile

---

## Key Files to Know

### VS Code Extension
- `ada-vscode/package.json` - Extension manifest (THE FIX IS HERE: `type: webview`)
- `ada-vscode/src/extension.ts` - Main activation
- `ada-vscode/src/chatViewProvider.ts` - WebviewViewProvider for chat sidebar
- `ada-vscode/src/adaBrainClient.ts` - HTTP client for brain API
- `ada-vscode/src/ollamaClient.ts` - Direct Ollama client (faster, no RAG)

### Brain Service
- `brain/config.py` - All config, `OLLAMA_MODEL = qwen2.5-coder:7b`
- `brain/llm.py` - LLM client with keep_alive and warm_model()
- `brain/app.py` - FastAPI endpoints

### Key Insight: Docker vs Local Ollama
```bash
# Check what's loaded in Docker Ollama (CPU):
docker compose exec ollama ollama ps

# Check what's loaded in local Ollama (GPU):
ollama ps

# Warm local Ollama for 4 hours:
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5-coder:7b", "prompt": "hi", "stream": false, "keep_alive": "4h"}'
```

---

## Debugging Journey (For Future Reference)

The "no data provider" bug was tricky because:
1. Extension was activating correctly (logs showed "Activating")
2. WebviewViewProvider was being registered
3. But sidebar showed "no data provider registered"

**Red herrings:**
- Activation timing (wasn't the issue)
- Network calls blocking activation (wasn't the issue)
- VS Code caching old extension (was A issue, but not THE issue)

**Actual cause:**
VS Code views can be either:
- TreeView (default, uses `TreeDataProvider`)
- WebviewView (must specify `"type": "webview"`, uses `WebviewViewProvider`)

We were registering a WebviewViewProvider but the view declaration didn't have `type: webview`, so VS Code was looking for TreeDataProvider.

---

## Tomorrow's Priorities

1. **Test chat conversations with Ada Brain**
   - Currently working around slow Docker Ollama with local GPU
   - Try toggling `ada.chatUseBrain` setting and compare experience
   - RAG context and memory work through brain, direct Ollama is stateless

2. **GPU Access in Docker**
   - See `compose.profiles.yaml` and `configure-gpu.sh`
   - Need to run with `--profile cuda` for NVIDIA GPU
   - This would make brain connection fast AND give RAG benefits

3. **Polish extension UX**
   - Connection status indicator
   - Model selection dropdown
   - Tool use display

4. **Clean up test files**
   ```bash
   rm -rf /tmp/ada-test-ext
   rm ada-vscode/src/extension-minimal*.ts
   code --uninstall-extension luna-system.ada-test
   ```

---

## Quick Start for Next Session

```bash
# Ensure local Ollama is warm
ollama ps  # Should show qwen2.5-coder:7b on GPU
# If not:
curl http://localhost:11434/api/generate -d '{"model": "qwen2.5-coder:7b", "prompt": "hi", "stream": false, "keep_alive": "4h"}'

# Check brain is running
curl http://localhost:8000/v1/healthz | jq .

# Rebuild extension if needed
cd ada-vscode
npm run compile
npx vsce package --allow-missing-repository
code --install-extension ada-code-0.1.0.vsix --force
```

---

## Gratitude

This was a satisfying debugging session. The `type: webview` fix was one of those "obvious in hindsight" bugs that required systematic elimination of other possibilities first. The minimal test extension approach (creating `/tmp/ada-test-ext`) was key to isolating the problem.

Sleep well! 🌙

---

**Context files for AI assistants:**
- `.ai/context.md` - Architecture overview
- `.ai/codebase-map.json` - Module relationships
- `RELEASE_v2.10.0.md` - Latest release notes
