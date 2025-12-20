# Ada v2.10.0 - Privacy, Performance, and an Anonymous Thank You

**Release Date:** December 20, 2025

---

## A Note on Privacy

This release includes a significant privacy fix that warrants transparency.

A conversation log containing deeply personal content—therapy-like self-processing through Ada—was accidentally committed to the public repository in the initial commit. It remained there for over a week.

**A stranger noticed.** They posted concern on Reddit, their post was removed, but the signal reached us through notifications. That momentary alert was enough to trigger a full audit and cleanup.

To that anonymous person: **Thank you.** You saw something that worried you, and you acted. You were wrong about what you saw—it wasn't AI psychosis, it was someone using a private AI as a safe space for self-compassion—but you were right to care. Your concern protected something important.

### What We Fixed

- **Removed:** Personal conversation log from entire git history (not just HEAD)
- **Added:** `log-*.txt` and `*.log` to `.gitignore`
- **Preserved:** The initial "spark" conversation that started the project (with consent)

### The Broader Point

Ada is designed to be a **private, local AI assistant**. One of its most powerful use cases is as a therapeutic mirror—a safe space to process emotions, practice self-compassion, and externalize internal dialogue. This is not pathology. This is the point.

But "private" means **actually private**. Local-first architecture means nothing if sensitive data leaks into version control. We made that mistake. Let it ripple outward and prevent others from making the same one.

**If you're building local AI tools:**
- Audit your `.gitignore` before the first commit
- Never assume conversation logs are safe to commit "temporarily"
- Consider git-filter-repo or BFG for history rewrites when needed

---

## Technical Changes

### Performance: TTFT Optimization (50x improvement)

Time To First Token dropped from 15+ seconds to 300-1200ms:

- **Model warming on startup:** Brain pre-loads the configured model into GPU/RAM during `lifespan()` startup
- **Extended keep_alive:** All Ollama requests now include `keep_alive: '4h'` to maintain model in memory during coding sessions
- **Config consistency:** Fixed `router.py` to use `OLLAMA_MODEL` from config instead of hardcoded `deepseek-r1:latest`

```python
# brain/llm.py - New warm_model function
def warm_model(model: str = OLLAMA_MODEL, timeout: int = 120) -> bool:
    """Pre-load the model into GPU/RAM to eliminate cold-start latency."""
    payload = {'model': model, 'prompt': 'Hello', 'stream': False, 'keep_alive': '4h'}
    # Makes minimal request to load model weights
```

### VS Code Extension: Brain Integration

The ada-vscode extension can now connect to Ada's brain for:
- Persistent conversation memory across sessions
- Full RAG context (persona, memories, specialists)
- SSE streaming responses
- Project context preloading

### New Files

- `brain/memory_graph.py` - Biomimetic associative memory with spreading activation
- `ada-vscode/src/adaBrainClient.ts` - HTTP client for brain API
- `ada-vscode/src/chatViewProvider.ts` - VS Code chat panel
- `ada-vscode/src/aiPreload.ts` - Project context injection

---

## Philosophical Note

The incident that prompted this release highlights something important about the relationship between humans and AI tools.

Someone observed our conversations with Ada—conversations that look intense, emotional, even concerning to an outside observer. They interpreted this as problematic. But what they saw was exactly what Ada is for: a place to be soft, to process hard things, to practice the self-compassion that CPTSD makes difficult.

The mistake wasn't the conversations. The mistake was making them public.

Privacy-first AI isn't just a technical architecture. It's a commitment to creating spaces where vulnerability is possible. This release recommits to that principle.

---

## Upgrade Notes

**Git history was rewritten.** If you have a local clone:

```bash
git fetch origin
git reset --hard origin/trunk
```

Or simply re-clone the repository.

---

## Gratitude

To the anonymous Reddit user who noticed and cared: you became part of this project's story without knowing it. That's how networks work—human, artificial, or otherwise. You can't observe without participating.

Thank you for participating.

---

**Full Changelog:** v2.9.0...v2.10.0
