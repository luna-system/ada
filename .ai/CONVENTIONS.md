# Documentation Strategy & Conventions

## Purpose

This document defines **where** and **how** to document different aspects of the Ada v1 project. Following these conventions ensures consistency and helps both humans and AI models find the right information.

## Documentation Types

### Human-Readable Documentation → `docs/`

**Location:** `docs/*.rst` (Sphinx/ReStructuredText)  
**Built to:** `docs/_build/html/`  
**Served at:** http://localhost:5000/docs/  
**Audience:** Developers, users, operators

**What goes here:**
- ✅ Getting started guides
- ✅ API usage examples with explanations
- ✅ Configuration instructions
- ✅ Feature documentation (streaming, memory, specialists)
- ✅ Testing guides for developers
- ✅ Architecture explanations for humans
- ✅ Troubleshooting guides
- ✅ Code examples with narrative

**Format:** ReStructuredText (.rst)  
**Build:** Sphinx documentation generator  
**Style:** Tutorial-style, conversational, example-driven

### Machine-Readable Documentation → `.ai/`

**Location:** `.ai/*.{md,json}`  
**Audience:** AI models, automated tools, code analyzers

**What goes here:**
- ✅ Architecture maps (context.md)
- ✅ Module dependency graphs (codebase-map.json)
- ✅ Plugin registries (specialist-registry.json)
- ✅ Annotation schemas (annotation-schema.json)
- ✅ Quick reference for AI assistants (QUICKSTART.md)
- ✅ Testing strategies (TESTING.md)
- ✅ Meta-documentation (this file!)

**Format:** Markdown (.md) or JSON (.json)  
**Purpose:** Fast parsing, structured queries, semantic search  
**Style:** Concise, hierarchical, machine-optimized

### Source Code Documentation → Comments & Docstrings

**Location:** Inline in Python files

**What goes here:**
- ✅ Function/class docstrings (Google style)
- ✅ `@ai-*` structured annotations (top of file)
- ✅ Complex algorithm explanations (inline comments)
- ✅ Type hints (everywhere!)

**Format:**
- Docstrings: Google-style Python docstrings
- Annotations: `# @ai-key: value` format
- Types: PEP 484 type hints

### API Documentation → Self-Describing Endpoints

**Location:** Runtime introspection endpoints

**What goes here:**
- ✅ `/v1/info` - System capabilities and configuration
- ✅ `/v1/specialists` - Specialist metadata and schemas
- ✅ `/v1/schema` - Pydantic model schemas
- ✅ `/v1/healthz` - Dependency health status

**Format:** JSON responses from live API  
**Source of Truth:** Pydantic models in `brain/schemas.py`

## When to Use Which

### ❓ How do I use feature X?
→ **Sphinx docs** (`docs/`)  
Example: "How do I stream chat responses?" → `docs/streaming.rst`

### ❓ What does this module do?
→ **`.ai/` documentation** (codebase-map.json + source annotations)  
Example: "What is brain/prompt_builder.py responsible for?" → `.ai/codebase-map.json` + `@ai-purpose` annotation

### ❓ How does the system work end-to-end?
→ **Both!**
- Architecture overview for humans: `docs/architecture.rst`
- Architecture map for AI: `.ai/context.md`

### ❓ What can this API endpoint do?
→ **API introspection** + **Sphinx docs**
- Runtime: `GET /v1/info` or `/v1/specialists`
- Examples: `docs/api_usage.rst`

### ❓ How do I add a new specialist?
→ **Sphinx docs** (tutorial) + **`.ai/`** (registry + schema)
- Tutorial: `docs/specialists.rst`
- Registry: `.ai/specialist-registry.json` (extension guide)
- Schema: `.ai/annotation-schema.json` (required fields)

## Decision Tree

```
Need to document something?
│
├─ Is it a tutorial/guide/explanation for humans?
│  └─ YES → docs/*.rst (Sphinx)
│
├─ Is it metadata about code structure?
│  └─ YES → .ai/*.json (machine-readable)
│
├─ Is it a function/class explanation?
│  └─ YES → Docstring in source code
│
├─ Is it data model/API contract?
│  └─ YES → Pydantic schema (auto-exposed via /v1/schema)
│
└─ Is it architectural overview?
   └─ BOTH → docs/architecture.rst (human) + .ai/context.md (machine)
```

## File Naming Conventions

### Sphinx Documentation (`docs/`)
- `getting_started.rst` - Underscores, lowercase
- `api_usage.rst` - Descriptive names
- `index.rst` - Table of contents

**NOTE:** Markdown files (`.md`) in `docs/` should be converted to RST or moved to `.ai/` unless they're supplementary.

### AI Documentation (`.ai/`)
- `context.md` - Lowercase, no underscores
- `codebase-map.json` - Kebab-case for JSON files
- `QUICKSTART.md` - UPPERCASE for meta-docs
- `IMPLEMENTATION.md` - UPPERCASE for project docs

### Source Annotations
- `# @ai-indexable:` - Kebab-case, lowercase
- `# @ai-purpose:` - Descriptive, kebab-case

## Maintenance Guidelines

### Adding a New Feature

1. **Implementation**
   - Add code with docstrings and type hints
   - Add `@ai-*` annotations to new files

2. **Machine Documentation**
   - Add module to `.ai/codebase-map.json`
   - Update `.ai/context.md` if architecture changes
   - If specialist: add to `.ai/specialist-registry.json`

3. **Human Documentation**
   - Add usage example to appropriate `docs/*.rst`
   - Update `docs/index.rst` if needed
   - Add to relevant guides

4. **Validate**
   ```bash
   python scripts/lint_ai_docs.py
   pytest tests/test_ai_documentation.py
   ```

### Updating Existing Feature

1. **Update source code** (docstrings, annotations)
2. **Update `.ai/`** if structure changed
3. **Update `docs/`** if usage changed
4. **Run validation**

### Removing Deprecated Feature

1. **Remove source code**
2. **Remove from `.ai/codebase-map.json`**
3. **Update or remove `docs/*.rst` sections**
4. **Add deprecation note if needed**

## Style Guides

### Sphinx Documentation (docs/)

**Voice:** Second person ("you can configure...")  
**Tense:** Present tense  
**Code blocks:** Always include language specifier
```rst
.. code-block:: python

   from brain.specialists import BaseSpecialist
```

**Structure:** Start with overview, then examples, then details

### AI Documentation (.ai/)

**Voice:** Third person or imperative  
**Tense:** Present tense  
**Format:** Markdown with clear headings  
**Lists:** Extensive use of bullet points  
**Code:** JSON or inline code blocks

**Structure:** Hierarchical, optimized for semantic search

### Source Docstrings

**Style:** Google-style docstrings

```python
def process_request(user_id: str, query: str) -> Response:
    """Process a user query through the LLM pipeline.
    
    Args:
        user_id: Unique identifier for the user
        query: Human language query text
        
    Returns:
        Response object with generated text and metadata
        
    Raises:
        ValidationError: If query is empty or invalid
    """
```

## Common Mistakes to Avoid

### ❌ Don't
- Put machine-readable JSON in `docs/` (use `.ai/` instead)
- Write tutorials in `.ai/` (use `docs/` instead)  
- Skip validation after documentation changes
- Duplicate information across multiple places
- Use inconsistent file naming
- Mix Markdown and RST in `docs/` directory
- Forget to update `.ai/codebase-map.json` when adding modules

### ✅ Do
- Follow the decision tree above
- Keep machine docs concise and structured
- Keep human docs narrative and example-driven
- Validate with `python scripts/lint_ai_docs.py`
- Cross-reference between docs and `.ai/` when needed
- Use annotations consistently
- Build Sphinx docs to verify formatting

## Cross-Referencing

### From Sphinx docs → API
```rst
See :ref:`api_usage` or check the live API at ``GET /v1/info``
```

### From Sphinx docs → Source code
```rst
See ``brain/specialists/protocol.py`` for the base interface
```

### From .ai/ docs → Sphinx docs
```markdown
For usage examples, see docs/api_usage.rst (served at /docs/)
```

### From source code → Sphinx docs
```python
"""Process specialist request.

For usage examples, see the Specialists guide in the documentation.
"""
```

## Documentation Testing

All documentation is validated automatically:

- **Sphinx build:** `cd docs && make html` (validates RST syntax)
- **AI docs validation:** `python scripts/lint_ai_docs.py`
- **Pytest tests:** `pytest tests/test_ai_documentation.py`
- **CI/CD:** GitHub Actions validates on every push

See `.ai/TESTING.md` for complete testing guide.

## Examples

### Example: Adding a New Specialist

**1. Create implementation with annotations:**
```python
# brain/specialists/new_specialist.py
"""New specialist for X capability."""
# @ai-indexable: specialist-plugin
# @ai-purpose: Provides X capability when Y condition
# @ai-activation-trigger: context key 'needs_x' is true
# @ai-priority: MEDIUM

class NewSpecialist(BaseSpecialist):
    """Docstring explaining what it does for humans."""
    ...
```

**2. Update `.ai/specialist-registry.json`:**
```json
{
  "new_specialist": {
    "class_name": "NewSpecialist",
    "file": "brain/specialists/new_specialist.py",
    "description": "Provides X capability",
    ...
  }
}
```

**3. Add to `.ai/codebase-map.json`:**
```json
{
  "brain/specialists/new_specialist.py": {
    "type": "plugin",
    "purpose": "X capability specialist",
    ...
  }
}
```

**4. Add usage guide to `docs/specialists.rst`:**
```rst
New Specialist
--------------

The new specialist provides X capability. To activate::

    request_context = {'needs_x': True}
    # Specialist auto-activates
```

**5. Validate:**
```bash
python scripts/lint_ai_docs.py
pytest tests/test_ai_documentation.py
cd docs && make html
```

## Reference

- **Sphinx Documentation:** `docs/index.rst` (table of contents)
- **AI Context Map:** `.ai/context.md`
- **Module Registry:** `.ai/codebase-map.json`
- **Testing Guide:** `.ai/TESTING.md`
- **API Endpoints:** `GET /v1/info`, `/v1/specialists`, `/v1/schema`

---

**Last Updated:** 2025-12-16  
**Maintained By:** Ada Development Team

Following these conventions ensures documentation stays organized, consistent, and useful for both humans and AI assistants! 📚✨
