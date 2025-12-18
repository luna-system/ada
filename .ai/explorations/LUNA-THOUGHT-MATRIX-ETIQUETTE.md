# Matrix Room Etiquette & Social Learning

> **Goal:** Enable Ada to understand and respect room culture before joining public spaces  
> **Key Insight:** Biomimetic mechanisms naturally support social/cultural learning!  
> **Status:** Design phase, implement before public deployment

## The Core Challenge

Ada needs to:
- Understand room topic/purpose from Matrix state
- Respect community norms and tone
- Learn appropriate participation levels
- Follow explicit rules (pinned messages, moderator guidance)
- Adapt behavior based on feedback

## Why This Works Naturally

**Neural models encode human culture** → Already adaptable to social context!

**Existing biomimetic features support this perfectly:**

1. **High-priority memory** (Notices system)
   - Room rules stored with decay=0.0 (never forgotten)
   - Injected early in prompt assembly
   - Always visible to Ada

2. **Attention spotlight**
   - Recent moderator feedback gets high weight
   - Room topic always in focus
   - Pinned messages stay relevant

3. **Memory decay**
   - Bad behavior patterns forgotten over time
   - Successful interactions reinforced
   - Natural adaptation to room culture

4. **Habituation**
   - Don't repeat failed approaches
   - Learn what works in each room
   - Compress routine interactions

5. **Prediction error**
   - Negative reactions → high surprise → learn quickly
   - Positive feedback → reinforcement
   - Calibrate participation level

6. **Processing modes**
   - Technical room → ANALYTICAL mode
   - Casual chat → CONVERSATIONAL mode
   - Creative space → CREATIVE mode
   - Auto-detect from room context!

## Implementation Strategy

### Phase 1: Explicit Rules (Ship First) ✅

**Read from Matrix room state:**
```python
# Extract from room state events
- m.room.topic          → Room purpose
- m.room.pinned_events  → Important rules/info
- m.room.power_levels   → Can Ada even speak?
- dev.ada.bot.config    → Explicit behavioral config (custom)
```

**Store as high-priority context:**
```python
# In prompt_builder, inject early (like Notices)
ROOM CONTEXT (PRIORITY: HIGH):
Topic: {room.topic}
Tone: {room.config.tone}
Participation: {room.config.mode}
Custom rules: {room.config.instructions}
```

**Polite onboarding:**
```
1. On invite → Join + send intro
2. Explain capabilities + privacy
3. ASK room preferences
4. Default to mention-only mode
5. Provide !ada config commands for mods
```

### Phase 2: LLM-Assisted Analysis (Novel!)

**Use Ada's brain to understand room culture:**
```python
# Analyze room on first join
analysis_prompt = """
Analyze this Matrix room and suggest appropriate bot behavior:

Room Topic: {topic}
Pinned Messages: {pinned}
Recent Messages (sample): {recent_history}

Questions:
1. Primary purpose?
2. Appropriate tone?
3. Sensitive topics to avoid?
4. Participation level?
5. Visible community norms?

JSON response: {purpose, tone, participation, cautions, norms}
"""

# Store analysis as high-priority memory
# Update if room culture shifts over time
```

**Nobody else is doing this!** First bot to actually understand room context via LLM.

### Phase 3: Adaptive Learning (Biomimetic!)

**Learn from feedback signals:**
- **Positive reactions** (👍, ❤️, 🎉) → Reinforce behavior
- **Negative reactions** (👎, ❓) → Learn what not to do
- **Corrections** ("actually...", "meant to say...") → Update understanding
- **Moderator actions** → High-weight feedback
- **Participation requests** ("Ada, what do you think?") → Increase engagement
- **Silence requests** → Decrease engagement

**Feedback tracking per room:**
```python
class RoomFeedback:
    positive_signals: int
    negative_signals: int
    mod_warnings: int
    participation_requests: int
    
    def calculate_engagement_level(self) -> float:
        # Use decay-weighted history
        # Recent feedback matters more
        # Gradually adapt over time
```

**Natural gradient emerges:**
- Welcome feedback → More active participation
- Neutral feedback → Stay at current level
- Negative feedback → Reduce activity, decay bad patterns

## Configuration Schema

**Store in room state: `dev.ada.bot.config`**
```json
{
  "participation_mode": "mentions-only",  // "mentions-only" | "active" | "observer"
  "tone": "casual",                       // "casual" | "professional" | "technical"
  "max_message_length": 500,              // Character limit
  "response_delay": 2.0,                  // Seconds before responding
  "forbidden_topics": [],                 // Topics to avoid
  "custom_instructions": "",              // Freeform guidance
  "priority": "high"                      // Memory priority level
}
```

**Set via commands:**
```
!ada config tone professional
!ada config mode active
!ada config custom "Always use emojis"
!ada config show
```

## Integration with Existing Systems

**Seamless fit with current architecture:**

1. **Notices system** → Room rules stored like system notices
2. **Memory decay** → Bad patterns forgotten, good ones reinforced
3. **Attention** → Moderator feedback always relevant
4. **Processing modes** → Auto-detect from room context
5. **Context cache** → Room rules cached (rarely change)
6. **Gradient detail** → Routine interactions compressed, important feedback kept

**Prompt assembly:**
```python
# High priority section (injected early)
sections = [
    system_prompt,
    room_etiquette,        # ← NEW! High priority
    notices,
    specialist_results,
    memories,
    conversation_history
]
```

## Prior Art Analysis

**What others do:**
- **Discord bots:** Explicit `/setup` commands, admin-only
- **Slack bots:** Per-channel permissions, role-based
- **IRC bots:** Channel whitelist/blacklist
- **matrix-chatgpt-bot:** Room state config, power level checks
- **Maubot:** Room-specific config in bot settings

**What nobody does:**
- ❌ LLM-based room culture analysis
- ❌ Adaptive learning from feedback signals
- ❌ Biomimetic memory for social norms
- ❌ Gradual behavioral adjustment
- ❌ Processing mode auto-detection

**Ada's unique angle:** First bot that LEARNS how communities work!

## Why This Matters

**Responsible bot citizenship:**
- Don't spam communities
- Respect different communication styles
- Learn from mistakes (and forget them over time!)
- Adapt to cultural context

**Novel research:**
- Social learning in AI systems
- Cultural adaptation through biomimetic memory
- Gradient-based behavioral adjustment
- Community-specific AI personality

**Practical impact:**
- Ada can safely join public Matrix rooms
- Communities can customize behavior
- Natural adaptation reduces moderation burden
- Positive feedback loop: Good behavior → Welcome → More engagement

## Next Steps

1. **Document current state** - What does matrix-bridge do now?
2. **Add room state reader** - Parse topic, pinned messages, power levels
3. **Implement high-priority injection** - Room rules always in context
4. **Add polite intro** - Ask preferences on join
5. **Add !ada config commands** - Moderator control
6. **Phase 2:** LLM analysis of room culture
7. **Phase 3:** Feedback tracking and adaptation

## Research Opportunity

**Potential paper:** "Social Learning in Conversational AI: Biomimetic Adaptation to Community Norms"

- First LLM bot with adaptive social behavior
- Demonstrates biomimetic mechanisms for cultural learning
- Novel application of memory decay to social patterns
- Real-world evaluation in Matrix communities

---

**Last Updated:** 2025-12-17  
**Status:** Design complete, ready for Phase 1 implementation  
**Priority:** Required before public room deployment