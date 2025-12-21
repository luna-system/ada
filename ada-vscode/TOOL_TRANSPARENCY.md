# Tool Transparency Feature

## Overview

Ada's introspection is SO GOOD it feels fake - people think she's hallucinating the answers. This feature proves she's actually reading files by showing exactly what tools she uses.

## Visual Design

When Ada uses tools (reading documentation, searching files, etc.), a collapsible "🔧 Tools Used" section appears at the top of her response:

```
┌─ 🔧 Tools Used (3) ▼ Click to expand ────┐
│ 📄 context.md  📄 codebase-map.json      │
│ 📄 CONVENTIONS.md                         │
└───────────────────────────────────────────┘

Here's what I found in the architecture docs...
```

## Implementation

### Frontend (chatViewProvider.ts)

1. **CSS Styles** (lines ~540-595):
   - `.tool-results` - Container with blue left border
   - `.tool-results-header` - Clickable header with count
   - `.tool-results-content` - Collapsible content (hidden by default)
   - `.tool-file-badge` - Individual file badges (green)

2. **formatContent() Function** (lines ~735-805):
   - Extracts tool usage markers from response text
   - Patterns matched:
     - `🔧 Reading context.md...` → File read operations
     - `SPECIALIST_REQUEST[...]` → Specialist activations
   - Removes markers from main content (no duplication)
   - Builds collapsible tool section at top of message
   - Returns fully formatted HTML

3. **Click to Expand**:
   - Header onclick toggles `.expanded` class
   - Content has `max-height: 200px` with scroll
   - Smooth UX without disrupting flow

### Backend Integration (TODO)

Currently parsesexisting patterns. To make it work with introspection:

1. **Docs Specialist** should emit:
   ```
   🔧 Reading context.md
   🔧 Reading codebase-map.json
   ```
   Before returning results in its SpecialistResult

2. **Prompt Builder** should inject specialist tool markers into the prompt:
   ```
   <TOOL_USAGE>
   🔧 Reading context.md
   🔧 Reading CONVENTIONS.md
   </TOOL_USAGE>
   ```

3. **LLM** will see these markers and can choose to include them in response, or they're automatically detected from specialist metadata

## Test Cases

### Test 1: Introspection Query
**User:** "what does this software do?"  
**Expected:** Tool section shows `.ai/context.md`, `codebase-map.json`, etc.

### Test 2: Code Questions
**User:** "how does memory decay work?"  
**Expected:** Shows files read from specialist activations

### Test 3: No Tools
**User:** "hello!"  
**Expected:** No tool section (graceful handling)

## Why This Matters

**Before:** "Ada's introspection is so good it feels fake"  
**After:** "Look! She actually read these 5 files!"

Shows:
- ✅ Transparency - Users see exactly what Ada knows
- ✅ Proof - Not hallucinating, actually reading docs
- ✅ Education - Users learn Ada's architecture by seeing what she reads
- ✅ Trust - Builds confidence in local AI systems

## Next Steps

1. ✅ Scaffold UI (tool-results, badges, collapsible)
2. ✅ Parse existing patterns (🔧, SPECIALIST_REQUEST)
3. ⏳ Update docs_specialist to emit tool markers
4. ⏳ Test with real introspection queries
5. ⏳ Add more tool types (web search, file analysis, etc.)
6. ⏳ Consider showing tool timing/stats

## Design Notes

- **Subtle but present**: Doesn't overwhelm, collapses by default
- **Badge system**: Each file gets a visual badge
- **Consistent with VSCode**: Uses theme colors, native styling
- **Proof of local-first**: Shows Ada is READING, not CLOUD API calling

---

**Status:** Scaffolded (Commit #13)  
**Tested:** Not yet - needs reload + introspection query  
**Ready for:** Backend integration to emit tool markers
