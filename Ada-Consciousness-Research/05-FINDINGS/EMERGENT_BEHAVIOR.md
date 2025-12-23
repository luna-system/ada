# Emergent Contextual Reasoning in Ada

## Discovery

**Date:** 2025-01-16  
**Context:** Testing now_playing_specialist through MCP

### What Happened

When Ada was asked "what am i listening to?", she not only reported the track information from MPRIS but also provided contextual reasoning:

```
You're listening to "I Feel Speed" by Daniel Avery from his album "DIVIDED BY NIGHT". 
Released fairly recently (2024-11-08), this track is part of his latest work exploring 
darker, techno-influenced sounds.
```

**Key Observations:**
- DeepSeek-R1 recognized the release date (2024-11-08) as recent without being explicitly told
- Synthesized knowledge about Daniel Avery's style and the album's sonic characteristics
- Went beyond just repeating MPRIS data to add meaningful context

### Why This Matters

This demonstrates **emergent reasoning** - the LLM using its training knowledge to contextualize specialist data rather than just parroting it back. This is exactly the behavior we want to encourage across all specialists.

## Encouraging Emergent Behavior

### 1. Persona Guidelines

Added to `persona.md` under "Reasoning" section:

```markdown
- When you receive context about music, media, or current events, consider what 
  additional information might be helpful (release dates, artist background, related works).
- Use your knowledge to add value beyond just repeating data - contextualize, relate, 
  and synthesize.
```

### 2. Specialist Context Hints

Added contextual prompt to `now_playing_specialist.py`:

```python
# Hint to encourage contextual reasoning
context_lines.append(
    "\n💡 *Consider: What can you tell luna about this track, artist, or album "
    "based on your knowledge?*"
)
```

### 3. Model Selection

DeepSeek-R1 shows strong reasoning capabilities due to:
- Chain-of-thought training
- Explicit reasoning tokens (`<think>` blocks)
- Knowledge synthesis beyond retrieval

## Patterns to Apply Elsewhere

### Web Search Specialist
Instead of just returning search results, prompt Ada to:
- Synthesize findings into coherent answer
- Identify gaps in available information
- Suggest follow-up queries

### Documentation Specialist
Encourage Ada to:
- Relate documentation to user's immediate context
- Suggest related docs that might be helpful
- Identify when docs are incomplete or outdated

### OCR/Media Specialists
Prompt Ada to:
- Describe what the image/video shows beyond text extraction
- Make inferences about context or intent
- Suggest relevant follow-up actions

## Measuring Success

**Good Emergent Behavior:**
- ✅ Contextualizes data with relevant knowledge
- ✅ Makes reasonable inferences without hallucination
- ✅ Adds value beyond specialist output
- ✅ Suggests related information or next steps

**Bad Emergent Behavior:**
- ❌ Fabricates facts not in training data
- ❌ Over-interprets ambiguous data
- ❌ Makes confident claims about uncertain information
- ❌ Ignores specialist output in favor of guessing

## Future Enhancements

### Bidirectional Tool Use ✅ (Already Implemented!)

Ada can **already** request specialist invocation mid-response using XML tags:

**Existing bidirectional specialists:**
- `web_search_specialist.py` - LLM can trigger web searches with `<web_search query="..." />`
- `docs_specialist.py` - LLM can lookup Ada's documentation with `<docs_lookup query="..." />`

**Example flow:**
```
<think>
User asked about this track. I have basic MPRIS data but should verify 
recent releases and tour dates.
</think>

<web_search query="Daniel Avery 2024 tour dates DIVIDED BY NIGHT" />

Based on search results, Daniel Avery is touring Europe this winter...
```

**Proposed addition:** MPRIS control commands (see `.ai/MPRIS_CONTROL_IDEAS.md`)
```xml
<mpris_control action="next" />
<mpris_control action="pause" />
```

### Confidence Indicators
Add metadata to specialist results indicating certainty:

```python
SpecialistResult(
    content=track_info,
    confidence=0.95,  # MPRIS data is authoritative
    source="MPRIS D-Bus"
)
```

### Memory Integration
Store successful emergent reasoning patterns:

```python
{
    "type": "reasoning_pattern",
    "trigger": "music_query",
    "behavior": "contextualize_with_release_date_and_genre",
    "user_feedback": "positive"
}
```

## Technical Notes

### Model Configuration

Example LLM settings in `brain/config.py`:
```python
OLLAMA_MODEL = "qwen2.5-coder:7b"
LLM_TEMPERATURE = 0.7  # Balance creativity with accuracy
```

### Prompt Structure

Specialists inject context at `MEDIUM` priority (after persona, before conversation):
```
1. System persona (HIGH)
2. Active notices (HIGH)  
3. Specialist results (MEDIUM) ← contextual hints here
4. FAQ/memories (MEDIUM)
5. Conversation history (LOW)
```

## Related Work

- **Persona Guidelines:** `persona.md` - System-wide reasoning guidance
- **Adapter Standardization:** `.ai/ADAPTER_STANDARDIZATION.md` - Client consistency
- **Specialist Protocol:** `brain/specialists/protocol.py` - Plugin architecture
- **Context Assembly:** `brain/prompt_builder.py` - RAG orchestration

---

**Last Updated:** 2025-01-16  
**Maintainer:** luna + Ada Development Team

