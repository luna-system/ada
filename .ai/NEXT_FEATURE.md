# Next Feature: Token Budget Monitoring Integration (v2.0 Phase 2)

## Status: ✅ COMPLETED (2025-12-17)

**Completed Today:**
- ✅ Unified Astro docs site with garden landing page
- ✅ Frontend fully decoupled as independent adapter
- ✅ GitHub Actions workflow updated for new architecture
- ✅ All formatting and deployment issues resolved
- ✅ **Token Budget Monitoring integrated into PromptAssembler**

**Current Branch:** `trunk` (all changes pushed)
**Last Commit:** 62846f0 - Token monitoring integration

---

## What's Next: Token Monitoring Integration

### Overview
We have **TokenBudgetMonitor** already implemented (`brain/token_monitor.py`) but it's only used in the legacy prompt builder. We need to integrate it into the new modular PromptAssembler architecture.

### Why This Matters
- **v2.1 gave us caching** - reduced redundant RAG queries
- **v2.0 Phase 2 gives us visibility** - understand what's using tokens
- **v2.0 Phase 3 will optimize** - intelligently trim context based on data

This is the observation phase before optimization. Biomimetic approach: measure before acting.

### Implementation Plan

#### 1. **Integrate into PromptAssembler** (brain/prompt_builder/prompt_assembler.py)
```python
class PromptAssembler:
    def __init__(self, ...):
        self.token_monitor = TokenBudgetMonitor(
            max_tokens=config.LLM_MAX_CONTEXT  # Need to add this to config
        )
    
    def build_prompt(self, ...):
        # Track each component as we build
        self.token_monitor.track("persona", persona_section)
        self.token_monitor.track("memories", memory_section)
        # ... etc
        
        # Log breakdown at end
        breakdown = self.token_monitor.get_breakdown()
        logger.info(f"Token usage: {breakdown.total_tokens} ({breakdown.percentage_used:.1f}%)")
```

#### 2. **Add Configuration** (brain/config.py)
```python
class Config(BaseSettings):
    # Existing...
    
    # Token monitoring
    LLM_MAX_CONTEXT: int = 128000  # Default for deepseek-r1
    TOKEN_WARNING_THRESHOLD: float = 0.8  # Warn at 80% usage
```

#### 3. **Expose in API** (brain/app.py)
Add token stats to streaming chunks:
```python
{
    "type": "token_stats",
    "total_tokens": 45000,
    "breakdown": {
        "persona": {"tokens": 2000, "percentage": 4.4},
        "memories": {"tokens": 15000, "percentage": 33.3},
        ...
    }
}
```

#### 4. **Update Adapters** (optional, can do later)
- CLI: Show token usage after response
- Web UI: Display token breakdown in sidebar
- MCP: Include in tool response metadata

### Files to Modify

**Core Changes:**
1. `brain/config.py` - Add LLM_MAX_CONTEXT, TOKEN_WARNING_THRESHOLD
2. `brain/prompt_builder/prompt_assembler.py` - Integrate TokenBudgetMonitor
3. `brain/app.py` - Emit token stats in stream (optional)

**Documentation:**
4. `docs/token_monitoring.rst` - Already exists! Just needs integration examples
5. `.ai/context.md` - Update with monitoring integration status

### Testing Plan

```bash
# 1. Test basic integration
ada-cli "Tell me about memory" --verbose
# Should see token breakdown in logs

# 2. Test high-context scenario
ada-cli "Summarize our last 50 conversations"
# Should trigger warning if >80% context used

# 3. Verify cache + monitoring work together
# Second query should show cached sections = 0 tokens from RAG
```

### Expected Outcomes

**Immediate Benefits:**
- Visibility into token usage patterns
- Warnings when approaching context limits
- Foundation for Phase 3 optimization

**Data We'll Learn:**
- Which components dominate token budget?
- How effective is caching at reducing queries?
- When do we hit context limits?

**Next Steps After This:**
- Phase 3: Intelligent context trimming based on token data
- Adaptive memory retrieval (fewer memories when token budget tight)
- Specialist result summarization when needed

---

## Quick Start Commands

```bash
# Check current branch
git status

# Make sure we're on trunk
git checkout trunk

# Pull latest (already pushed, but just in case)
git pull origin trunk

# Create feature branch for token monitoring
git checkout -b feature/token-monitoring-integration

# Start coding!
code brain/config.py brain/prompt_builder/prompt_assembler.py
```

---

## Context Notes

**From TODO.md:**
- MCP enhancements on the list but lower priority
- Pause/resume specialists (Phase 2) is in codebase but not integrated
- Token monitoring is natural next step in v2.0 roadmap

**Architecture State:**
- Caching system: ✅ Shipped (v2.1.0)
- Token monitoring: ✅ Implemented, ⏳ Needs integration
- Context optimization: ⏳ Waiting for monitoring data

**No Blockers:**
- All dependencies installed (tiktoken already in requirements)
- TokenBudgetMonitor thoroughly tested
- Clean separation of concerns in new architecture

---

## Alternative Features (If You Want Something Different)

1. **MCP Streaming** - Add streaming support to MCP chat tool
2. **Specialist as MCP Tools** - Expose specialists as individual MCP tools  
3. **Matrix Bot Enhancements** - Better context management per room
4. **Multi-user Support** - Authentication + separate memories

Token monitoring is recommended because it:
- Builds on v2.1 caching work
- Small, focused feature (1-2 hour implementation)
- High impact for Phase 3
- No new dependencies needed

---

**Ready to rock when you are! 🌱💜**

*Generated: 2025-12-17 16:35 after garden landing page deployment*
