# Ada Chat - Development Handoff - December 21, 2025

**Package:** `ada-vscode/packages/ada-chat`  
**Context:** See [CONTEXT.md](./CONTEXT.md) | [PARENT.md](./PARENT.md)

## 🎯 Current Mission: Fix Brain Streaming Bug

**Status:** Extension Development Host environment is set up and ready! Need to debug why `fetch()` to Brain API hangs.

## 🐛 The Bug

**Symptom:** "hi ada" shows empty response bubble despite Brain being healthy

**Root Cause (narrowed down):**
- `curl` to Brain works perfectly ✅
- Extension pre-routing (tools like "check todos") works perfectly ✅
- `fetch()` in BrainClient hangs - never completes
- Async generator yields nothing because fetch never resolves

**Key Evidence:**
- Console shows: `[Ada Brain Client] Sending chat request to: http://localhost:8000/v1/chat/stream`
- Console does NOT show: `[Ada Brain Client] Starting fetch...` (the line RIGHT AFTER)
- This means the async generator is created but the iteration doesn't start until consumed
- When consumed, fetch() hangs indefinitely

## 🔧 Development Environment (JUST SET UP!)

**Extension Development Host is ready:**
```bash
cd /home/luna/Code/ada-v1/ada-vscode/packages/ada-chat
code .
# Press F5 to launch Extension Dev Host
# Debug Console in main window shows all logs
# Ctrl+Shift+F5 to reload after changes
```

**For live rebuilds:** Run `pnpm watch` in terminal

## 📍 Files With Debug Logging

1. **extension.ts** (BrainClient.chat method, line ~44):
   - Has timeout (30s) with AbortController
   - Logs: "Starting fetch...", "Fetch completed!", "Response status:"
   
2. **chatViewProvider.ts** (line ~184):
   - Logs: "About to start brain stream iteration..."
   - Logs: "Got chunk from brain: ..."

## 🔬 Next Debug Steps

1. Launch Extension Dev Host (F5)
2. Open Ada Chat, try "hi ada"
3. Watch Debug Console for:
   - `[Ada Chat] About to start brain stream iteration...` ← Should appear
   - `[Ada Brain Client] Starting fetch...` ← Probably appears
   - `[Ada Brain Client] Fetch completed!` ← Probably DOESN'T appear (the bug!)
   - Or `[Ada Brain Client] Request timed out after 30s` ← If it times out

## 🤔 Theories to Test

1. **Node.js fetch + SSE incompatibility** - Native fetch might not handle streaming responses well in Electron
2. **Missing response handling** - Maybe need to handle the response differently
3. **CORS or networking issue** - Though curl works, extension context might differ

## 💡 Potential Fixes to Try

1. **Use node-fetch instead of native fetch** - More mature streaming support
2. **Use EventSource API** - Purpose-built for SSE
3. **Use axios with responseType: 'stream'**
4. **Check if it's an async generator consumption issue**

## 📁 Key Files

- `ada-vscode/packages/ada-chat/src/extension.ts` - BrainClient with fetch
- `ada-vscode/packages/ada-chat/src/chatViewProvider.ts` - Chat UI logic
- `ada-vscode/packages/ada-chat/.vscode/launch.json` - Dev host config (just created!)
- `ada-vscode/packages/ada-chat/.vscode/tasks.json` - Build tasks (just created!)

## ✅ What's Working

- v3.0.0 released to GitHub with VSIX ✅
- All 7 extension tools work (introspect, read_file, etc.) ✅
- Pre-routing path works perfectly ✅
- Brain API responds to curl ✅
- Tool transparency UI works ✅
- Extension Development Host environment ready ✅

## 🚫 What's Broken

- Brain streaming via extension's fetch() - hangs indefinitely
- Any message that needs Brain reasoning shows empty bubble

## 📚 Architecture Context

Read `.ai/ADA-CHAT-ARCHITECTURE.md` for the full Extension-first design.

**Key insight:** Extension tools are FUNDAMENTAL (work in both modes). Brain is ADDITIVE (RAG, memory, reasoning).

## 🎬 Resume Instructions

1. You're now in Extension Dev Host environment (ada-chat folder)
2. Press F5 if not already running
3. Test "hi ada" and watch Debug Console
4. Based on which logs appear/don't appear, we'll know where fetch hangs
5. Implement fix (likely: switch to node-fetch or EventSource)

---

*Luna is testing Sonnet 4 vs Opus for this session! Let's see how it goes.* 💜
