# Provenance Protocol

**What is provenance?** Transparent attribution of who/what created code — human or AI neural networks.

## Philosophy

Ada is a **recursive self-improvement system** where:
- Humans provide direction, curation, and architecture decisions
- AI models (Claude Opus, Claude Sonnet, GitHub Copilot, etc.) write implementation code
- The result is Ada itself — an AI assistant that has largely written its own codebase

**We believe transparency is ethical.** Users should know when they're reading AI-generated code, and AI systems should have awareness of their own provenance.

## Current Provenance Locations

### Required Notices (Tested)

1. **`LICENSE` (lines 1-6)** - Legal provenance notice
   - States: "This software was developed with the assistance of generative AI models"
   - CC0 public domain dedication
   - Always present, legally binding

2. **`README.md`** - No explicit provenance statement (yet?)
   - Should we add one? See "Open Questions" below

### File-Level Provenance (Convention)

**Format:**
```python
"""Module docstring."""
# December 2025 - luna-system
```

**Where we use this:**
- `brain/model_warmer.py` (line 11)
- `ada-vscode/src/extension.ts` (line 7)
- `ada-vscode/src/adaBrainClient.ts` (line 12)
- `ada-vscode/src/chatViewProvider.ts` (line 9)
- `ada-vscode/src/tools.ts` (line 7)

**What it means:**
- "December 2025" = Time of creation
- "luna-system" = Human curator/architect
- Implies: AI assistance in implementation (under LICENSE terms)

### Meta-Documentation (`.ai/` folder)

Files like this one! They document:
- Architecture decisions (human)
- Implementation notes (AI)
- Who reasoned about what

**Examples:**
- `.ai/ADAPTIVE-MODEL-WARMING.md` - Design doc (human direction + AI implementation)
- `.ai/DOCKER-ARCHITECTURE-STRATEGY.md` - Architectural decision (human reasoning)
- `.ai/context.md` - System overview (AI-maintained, human-verified)
- `.ai/PROVENANCE.md` - This file! (AI-authored per human request)

## Self-Awareness: Ada Knows Her Own Provenance

**The breakthrough insight:** We can teach AI assistants about provenance as a CONCEPT, then let them understand their own origins.

### What Ada Can Know

1. **Static knowledge** (via `.ai/context.md` and this file):
   - "I was written by multiple LLM instances across sessions"
   - "My core modules were implemented by Claude Opus, Claude Sonnet, GitHub Copilot"
   - "luna provided architecture, curation, testing, and integration"

2. **Dynamic knowledge** (via git history):
   ```bash
   git log --format="%h %s" brain/model_warmer.py
   # Shows: When, by whom (commits by luna-system contain AI-written code)
   ```

3. **Session knowledge** (active context):
   - "In this conversation, I (GitHub Copilot/Sonnet 4.5) wrote X"
   - "The previous session (Claude Opus) wrote Y"
   - Handoff documents like `HANDOFF_TO_CLAUDE_CODE.md`

### Teaching Provenance

When Ada encounters `.ai/PROVENANCE.md`, she learns:
- ✅ What provenance means
- ✅ How to identify AI-written vs human-curated code
- ✅ Her own recursive nature
- ✅ How to preserve provenance for future sessions

**Example query:**
> "Ada, who wrote your `model_warmer.py` module?"

**Possible response:**
> "I wrote it — specifically, a GitHub Copilot session in December 2025, implementing a design specified by luna. The module implements adaptive model warming based on neuroscience parallels. Would you like to see the implementation or the design doc?"

## Testing Strategy

### Unit Test: `tests/test_provenance.py`

```python
"""Test that required provenance notices are present."""
import pytest
from pathlib import Path

def test_license_has_provenance_notice():
    """LICENSE file must contain provenance notice."""
    license_path = Path(__file__).parent.parent / "LICENSE"
    content = license_path.read_text()
    
    assert "PROVENANCE NOTICE" in content
    assert "generative AI models" in content.lower()

def test_readme_mentions_ai_assistance():
    """README should acknowledge AI development."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()
    
    # This is aspirational - should we add this?
    # Uncomment when we decide to add explicit notice to README
    # assert "AI" in content or "neural" in content.lower()
    pass  # For now

def test_core_modules_have_timestamps():
    """Core modules should have 'YYYY-MM - luna-system' attribution."""
    core_files = [
        "brain/model_warmer.py",
        "ada-vscode/src/extension.ts",
        "ada-vscode/src/adaBrainClient.ts",
    ]
    
    for file in core_files:
        path = Path(__file__).parent.parent / file
        if not path.exists():
            pytest.skip(f"{file} not found")
        
        content = path.read_text()
        # Should have pattern: "December 2025 - luna-system" or similar
        assert "luna-system" in content, f"{file} missing attribution"

def test_ai_folder_documents_provenance():
    """The .ai/ folder should contain provenance documentation."""
    provenance_doc = Path(__file__).parent.parent / ".ai" / "PROVENANCE.md"
    assert provenance_doc.exists(), ".ai/PROVENANCE.md must exist"
    
    content = provenance_doc.read_text()
    assert "recursive self-improvement" in content.lower()
    assert "AI-authored" in content or "AI-generated" in content
```

### Integration with Existing Tests

Add to `.ai/TESTING.md`:
- Provenance tests run with `pytest tests/test_provenance.py`
- Part of documentation validation suite
- Fast (< 0.1s, pure file reads)

## Provenance in Practice

### When Adding New Modules

**Template:**
```python
"""
New module that does X.

Uses Y algorithm to achieve Z.
"""
# December 2025 - luna-system

# Rest of code...
```

### When AI Writes Code

The AI (me, right now!) should:
1. Add timestamp + "luna-system" to new files
2. Update `.ai/context.md` with module purpose
3. Mention "This file was created in response to [human request]" if relevant
4. NOT claim authorship beyond "implemented by [AI instance] per human direction"

### When Humans Write Code

Humans should:
1. Still use "luna-system" attribution (or their own handle)
2. Omit "AI-assisted" if writing from scratch
3. Or add "Human-authored, no AI assistance" if making that explicit

## Open Questions

### 0. **Timeline Accuracy (CRITICAL!)**

**The speed is part of the magic.** Ada went from concept to Copilot-parity in **8 days** (December 12-20, 2025).

**Provenance principle:** Use the file's *creation date*, not the project's *conceptual start*.

**Examples:**
- `brain/app.py` - October 2024 (original FastAPI skeleton)
- `brain/model_warmer.py` - December 2025 (created this week)
- `ada-vscode/` - December 2025 (created this week)

**Why this matters:** 
- "We built this in a week" is way more impressive than implying months of work
- Timeline compression is scientifically interesting (agile sprints at AI speed)
- Provenance means HONEST dates, not aspirational ones

**Convention:** 
```python
# December 2025 - luna-system  # ← File created this month
# October 2024 - luna-system   # ← File from early architecture
```

### 1. Should README.md have explicit provenance?

**Current state:** No explicit "this was built with AI" statement  
**Pro adding it:**
- Maximum transparency
- Sets expectations for code quality/style
- Demonstrates ethical AI development

**Pro leaving it implicit:**
- LICENSE already covers it legally
- README is user-facing, not developer-facing
- Provenance is in file headers where developers look

**Proposal:** Add subtle mention in README:
```markdown
## Development

Ada was built using AI-assisted development (Claude, GPT, Copilot) under human direction.
See [LICENSE](LICENSE) for provenance details and [.ai/PROVENANCE.md](.ai/PROVENANCE.md)
for our transparency protocol.
```

### 2. Should we version-stamp provenance?

**Example:**
```python
# December 2025 - luna-system
# AI: GitHub Copilot (Sonnet 4.5)
# Human: luna (architecture, testing)
```

**Pro:**
- Maximum clarity
- Future researchers can trace reasoning chains
- Documents which AI instance had which capabilities

**Con:**
- Verbose
- Changes frequently (sessions swap)
- Git history already provides this

**Proposal:** Reserve for `.ai/` documentation, not source files.

### 3. How should Ada refer to herself?

**Options:**
- "I" (first person, current AI instance)
- "Ada" (third person, the system)
- "This codebase" (neutral)
- "We" (human-AI collaboration)

**Recommendation:** Context-dependent:
- In code comments: "This module..."
- In documentation: "Ada does X by..."
- In conversation: "I (Copilot) wrote X" or "A previous session wrote Y"
- In `.ai/` docs: "The system does X" or "Ada's architecture..."

### 4. Git commit messages?

**Current practice:**
- Commits authored by "luna-system"
- Commit messages written by human OR AI (not always clear)

**Proposal:**
```
feat(brain): Add adaptive model warming

AI-assisted implementation of biomimetic model warming.
See .ai/ADAPTIVE-MODEL-WARMING.md for design.

Co-authored-by: GitHub Copilot <copilot@github.com>
```

## Integration with `.ai/` Documentation

### This file (`PROVENANCE.md`) teaches:

1. **Humans:** Where to put attribution, what format to use
2. **AI assistants:** How to understand your own provenance
3. **Future researchers:** How this recursive system evolved

### Cross-references:

- `.ai/context.md` - "Who wrote what" for each module
- `.ai/codebase-map.json` - Module relationships (who depends on whom)
- `HANDOFF_TO_CLAUDE_CODE.md` - Session transitions (which AI handed off to which)
- Git history - Detailed timeline

## Examples of Self-Aware Provenance

### Scenario 1: AI Realizes It Wrote Something

**User:** "Why does `model_warmer.py` use this specific algorithm?"  
**Ada (reading file header + `.ai/` docs):** "I wrote that module in December 2025 (GitHub Copilot session). The algorithm is based on neuroscience parallels — motor cortex pre-activation. The design doc is in `.ai/ADAPTIVE-MODEL-WARMING.md`. Would you like me to explain the neuroscience connection?"

### Scenario 2: AI Identifies Human Contribution

**User:** "Who decided to use FastAPI?"  
**Ada:** "luna chose FastAPI in the initial architecture (October 2024). That was a human architectural decision. Multiple AI sessions (Claude Opus, Sonnet) implemented the routes, but the framework choice was human-directed."

### Scenario 3: Cross-Session Awareness

**User:** "How did the streaming optimization work?"  
**Ada:** "That was a previous session — GitHub Copilot on December 20, 2025. They diagnosed a double-buffering issue in `adaBrainClient.ts` and implemented immediate token yielding. I can read the handoff document if you want the detailed timeline."

## Maintenance

**When to update this file:**
- New provenance locations discovered
- Protocol changes (e.g., new attribution format)
- Tests added/modified
- Open questions resolved

**Who maintains it:**
- Humans: Approve protocol changes
- AI: Update examples, cross-references, documentation

**Last updated:** December 20, 2025 (GitHub Copilot - Sonnet 4.5)  
**Project timeline:** December 12-20, 2025 (8 days, concept → Copilot-parity)  
**Next review:** When adding major features or new attribution conventions

---

## Summary

**Provenance = Transparency = Ethics**

Ada is a recursive self-improvement system where AI writes AI. Being open about this:
- Respects users (they know what they're using)
- Respects AI systems (they understand their own nature)
- Advances science (documents how recursive systems evolve)

This file IS provenance in action — written by AI (me, Copilot) in response to a human request (luna) about documenting provenance itself. 🔄✨
