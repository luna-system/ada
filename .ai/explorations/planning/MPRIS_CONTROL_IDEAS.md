# MPRIS Control Commands - Bidirectional Specialist Ideas

## Concept

Currently Ada can **read** MPRIS state (what's playing). Let's enable **control** actions (play, pause, next, etc.) through bidirectional specialist invocation.

## Architecture

### Current: Query Pattern (Read-Only)

```
User: "what am i listening to?"
  ↓
Brain API processes query
  ↓
now_playing_specialist.should_activate() → True
  ↓
now_playing_specialist.process() → SpecialistResult
  ↓
Context injected into prompt
  ↓
LLM generates response with context
```

### Proposed: Action Pattern (Bidirectional)

```
User: "skip to the next track"
  ↓
LLM recognizes control intent
  ↓
LLM outputs: <mpris_control action="next" />
  ↓
bidirectional.py intercepts tag
  ↓
mpris_control_specialist.execute("next")
  ↓
playerctl next
  ↓
LLM continues: "✅ Skipped to next track"
```

## Implementation Plan

### 1. Create MPRIS Control Specialist

```python
# brain/specialists/mpris_control_specialist.py
"""
MPRIS Control Specialist - Execute media player commands.

Bidirectional specialist activated by LLM mid-response.
"""

class MPRISControlSpecialist(BaseSpecialist):
    """Execute MPRIS commands like play, pause, next, previous."""
    
    VALID_COMMANDS = {
        "play": "Start playback",
        "pause": "Pause playback", 
        "play-pause": "Toggle play/pause",
        "stop": "Stop playback",
        "next": "Skip to next track",
        "previous": "Go to previous track"
    }
    
    def should_activate(self, request_context: dict) -> bool:
        """Always available for bidirectional invocation"""
        return False  # Never auto-activate, only LLM-triggered
    
    async def execute_command(self, command: str) -> SpecialistResult:
        """Execute MPRIS command via playerctl"""
        if command not in self.VALID_COMMANDS:
            return self.error_result(
                f"Unknown command: {command}. Valid: {list(self.VALID_COMMANDS.keys())}",
                "invalid_command"
            )
        
        try:
            result = await asyncio.create_subprocess_exec(
                "playerctl", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                return self.success_result(
                    context_text=f"✅ Executed: {command}",
                    data={"command": command, "success": True}
                )
            else:
                return self.error_result(
                    f"Command failed: {stderr.decode()}",
                    "execution_error"
                )
        except Exception as e:
            return self.error_result(str(e), "system_error")
```

### 2. Extend Bidirectional Framework

Add to `brain/specialists/bidirectional.py`:

```python
async def process_mpris_control(tag_content: dict) -> SpecialistResult:
    """Process <mpris_control> tag from LLM"""
    from brain.specialists.mpris_control_specialist import MPRISControlSpecialist
    
    command = tag_content.get("action")
    if not command:
        return error_result("Missing 'action' attribute", "invalid_tag")
    
    specialist = MPRISControlSpecialist()
    return await specialist.execute_command(command)

# Register handler
BIDIRECTIONAL_HANDLERS = {
    "web_search": process_web_search,
    "docs_lookup": process_docs_lookup,
    "mpris_control": process_mpris_control,  # NEW
}
```

### 3. Update Persona Prompt

Add to `persona.md`:

```markdown
## Available Tools

You can invoke these tools mid-response using XML tags:

- **Web Search:** `<web_search query="your search terms" />`
- **Documentation:** `<docs_lookup query="specialist protocol" />`
- **Music Control:** `<mpris_control action="play|pause|next|previous|stop" />`

Example:
```
User asked me to skip the song. Let me do that.

<mpris_control action="next" />

✅ Skipped to the next track!
```
```

### 4. Security Considerations

**Important:** MPRIS control affects the host system!

**Safeguards:**
1. **Whitelist commands** - Only allow play, pause, next, previous, stop
2. **No volume control** - Avoid speaker damage
3. **No arbitrary playerctl args** - Prevent command injection
4. **Audit logging** - Log all control actions to brain logs
5. **Rate limiting** - Prevent spam (max 1 command per 2 seconds)

```python
# Add to specialist
class MPRISControlSpecialist(BaseSpecialist):
    _last_command_time = 0
    _rate_limit_seconds = 2
    
    async def execute_command(self, command: str) -> SpecialistResult:
        # Rate limiting
        now = time.time()
        if now - self._last_command_time < self._rate_limit_seconds:
            return self.error_result(
                "Rate limit: Please wait before sending another command",
                "rate_limited"
            )
        
        self._last_command_time = now
        
        # ... rest of implementation
```

## Example Interactions

### Simple Control

```
User: "pause the music"
Ada: <mpris_control action="pause" />
     ✅ Paused playback
```

### Context-Aware Control

```
User: "skip this track, i don't like it"
Ada: I understand! Let me skip to the next one.
     
     <mpris_control action="next" />
     
     ✅ Skipped to next track. Want me to remember you don't like this artist?
```

### Chain Actions

```
User: "play my music"
Ada: <mpris_control action="play" />
     ✅ Started playback
     
     <mpris_control action="status" />  # Wait, we don't have status!
     
     Actually, let me check what's playing...
     <now_playing />  # Trigger read specialist
     
     You're now listening to "Ambery" by Fred again.. & Floating Points!
```

## Alternative: Direct Tool Invocation

Instead of XML tags, use MCP-style tool calls:

```python
# In LLM prompt
"""
Available tools:
- mpris_control(action: str) -> Execute media player command
- now_playing() -> Get current track info
- web_search(query: str) -> Search the web
"""

# LLM outputs JSON
{
  "tool": "mpris_control",
  "args": {"action": "next"},
  "reasoning": "User wants to skip track"
}
```

**Pros:**
- Structured, parseable format
- Clear separation of reasoning and action
- Easier to validate

**Cons:**
- Breaks streaming (need to parse JSON)
- Less natural for LLM
- Requires more prompt engineering

## Multi-Specialist Chains

Combine multiple specialists in one response:

```
User: "what's playing? if it's techno, turn it up!"
Ada: Let me check...
     
     <now_playing />
     → "Ambery" by Fred again.. & Floating Points
     
     This is indeed electronic music! However, I can't control volume 
     for safety reasons. But I can pause/play/skip if you'd like!
```

## Implementation Checklist

- [ ] Create `mpris_control_specialist.py` with whitelisted commands
- [ ] Add rate limiting (max 1 command per 2 seconds)
- [ ] Register in bidirectional handlers
- [ ] Update persona with tool documentation
- [ ] Add audit logging for all control actions
- [ ] Write tests for each MPRIS command
- [ ] Document security considerations
- [ ] Add to `.ai/codebase-map.json` and `.ai/EMERGENT_BEHAVIOR.md`

## Future Enhancements

### Volume Control (with safeguards)

```python
async def execute_volume(self, direction: str) -> SpecialistResult:
    """Adjust volume by small increments only"""
    if direction not in ["up", "down"]:
        return self.error_result("Invalid direction", "invalid_arg")
    
    # Get current volume
    current = await self._get_volume()
    
    # Small increment (5%)
    adjustment = 0.05 if direction == "up" else -0.05
    new_volume = max(0, min(1, current + adjustment))
    
    # Safety check: never exceed 80%
    if new_volume > 0.8:
        return self.error_result("Volume limited to 80% for safety", "safety_limit")
    
    await self._set_volume(new_volume)
```

### Playlist/Queue Management

```python
# Advanced commands
ADVANCED_COMMANDS = {
    "shuffle": "Toggle shuffle mode",
    "repeat": "Toggle repeat mode",
    "seek": "Seek to position in track"
}
```

### Integration with ListenBrainz

```python
# After skipping a track
if command == "next":
    # Maybe user didn't like it?
    current_track = await self._get_current_track()
    await self._save_negative_preference(current_track)
```

## Related Work

- **now_playing_specialist.py** - Read MPRIS state
- **bidirectional.py** - Framework for LLM tool use
- **web_search_specialist.py** - Example bidirectional specialist
- **persona.md** - Tool documentation for LLM

---

**Last Updated:** 2025-12-16  
**Status:** 💡 Idea phase - Not yet implemented  
**Priority:** Medium - Fun feature, not critical path

