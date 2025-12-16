# Documentation Specialist - Usage Guide

## Overview

The Documentation Specialist enables Ada to search and reference her own Sphinx documentation during conversations. This creates a meta-capability where Ada can look up her own features, API details, and usage instructions.

## How It Works

**Type:** Bidirectional Specialist  
**Activation:** LLM-initiated via `<docs>query</docs>` XML tag  
**Priority:** HIGH (results shown prominently in context)

### Data Flow

```
User asks Ada a question
    ↓
Ada realizes she needs to check her docs
    ↓
Ada outputs: <docs>streaming API</docs>
    ↓
Documentation Specialist searches docs/_build/html/
    ↓
Relevant documentation excerpts injected into context
    ↓
Ada continues with accurate documentation-based answer
```

## XML Tag Syntax

Ada can use the `<docs>` tag during generation:

```xml
<docs>topic to search</docs>
```

**Examples:**
- `<docs>streaming SSE</docs>` - Find streaming documentation
- `<docs>specialist plugins</docs>` - Look up specialist system
- `<docs>RAG memory</docs>` - Search memory/RAG docs

## What Gets Searched

The specialist searches **built Sphinx HTML documentation**:
- Location: `docs/_build/html/*.html`
- Files: api_usage, specialists, architecture, streaming, etc.
- Format: Plain text extracted from HTML

### Search Algorithm

1. **Parse HTML** - Extract clean text from HTML files
2. **Calculate relevance** - Count query term occurrences
3. **Extract excerpts** - Show context around matched terms
4. **Sort results** - Best matches first
5. **Return top 3** - Most relevant sections

## Example Usage

### Scenario: User Asks About Streaming

**User:** "How does your streaming work?"

**Ada's internal process:**
```
Let me check my documentation... <docs>streaming SSE</docs>

[Specialist executes, finds streaming.rst content]

Based on my documentation, I use Server-Sent Events (SSE) for streaming...
```

**Output to user:** Clear answer based on actual documentation

## Configuration

### Default Setup

```python
# Specialist auto-discovers docs location
docs_specialist = DocumentationSpecialist()
# Uses: project_root/docs/_build/html
```

### Custom Location

```python
from pathlib import Path

docs_specialist = DocumentationSpecialist(
    docs_dir=Path("/custom/path/to/built/docs")
)
```

## Search Features

### Basic Search
```python
result = await specialist.process({
    'query': 'streaming'
})
```

### Section-Specific Search
```python
result = await specialist.process({
    'query': 'API endpoints',
    'section': 'api_usage'  # Only search api_usage.html
})
```

## Response Format

### Success Response

```python
{
    'success': True,
    'specialist_name': 'docs',
    'context_text': """
        📚 **Documentation Lookup: 'streaming'**
        Found 3 relevant section(s):
        
        **1. Streaming Guide** (from `streaming.rst`)
           ...Server-Sent Events (SSE) enable real-time token delivery...
        
        **2. API Usage** (from `api_usage.rst`)
           ...POST /v1/chat/stream endpoint accepts...
    """,
    'data': {
        'query': 'streaming',
        'results': [
            {
                'file': 'streaming',
                'title': 'Streaming Guide',
                'excerpt': '...relevant text...',
                'relevance': 15
            }
        ]
    }
}
```

### No Results Response

```python
{
    'success': True,
    'context_text': """
        📚 Searched documentation for 'xyz' but found no relevant sections.
        The documentation may not cover this topic yet.
    """,
    'data': {
        'query': 'xyz',
        'results': [],
        'message': 'No relevant sections found'
    }
}
```

## Testing

### Manual Test

```bash
# Run the test script
python scripts/test_docs_specialist.py
```

### Integration Test

```python
import asyncio
from brain.specialists.docs_specialist import DocumentationSpecialist

async def test():
    specialist = DocumentationSpecialist()
    result = await specialist.process({'query': 'specialists'})
    print(f"Found {len(result.data['results'])} results")
    print(result.context_text)

asyncio.run(test())
```

## Requirements

### Build Documentation First

```bash
# Docs must be built before specialist can search them
cd docs
make html

# Verify build
ls -la _build/html/*.html
```

### Dependencies

- **Python stdlib only** - No extra packages needed
- `pathlib` - File system operations
- `html.parser.HTMLParser` - HTML text extraction
- `re` - Pattern matching

## Limitations

### Current Limitations

1. **Requires built docs** - Won't work if `make html` hasn't been run
2. **HTML only** - Searches built HTML, not source RST
3. **Text search** - Simple term matching, not semantic
4. **Top 3 results** - Only returns best 3 matches

### Future Enhancements

Potential improvements:
- Semantic search using embeddings
- Search source RST files directly
- Configurable result count
- Cached search results
- Fuzzy matching for typos

## Integration Points

### In Prompt Builder

The specialist is automatically available when:
1. Ada is in bidirectional mode
2. Docs are built (`docs/_build/html exists`)
3. Ada emits `<docs>` tag during generation

### System Prompt Addition

To make Ada aware of this capability, add to system prompt:

```
You have access to your own documentation via the <docs> tag.
When you need to reference your capabilities, API details, or features,
you can look them up: <docs>topic</docs>

Example: <docs>streaming API</docs> to find streaming documentation.
```

## Troubleshooting

### "Documentation not built" Error

**Error:** `Documentation not built. Run 'cd docs && make html'`

**Solution:**
```bash
cd docs
make html
```

### No Results Found

**Possible causes:**
1. Topic not covered in docs
2. Search terms too specific/unusual
3. HTML files missing

**Solutions:**
- Try broader search terms
- Check `docs/_build/html/` contents
- Rebuild docs: `cd docs && make html`

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'brain.specialists'`

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/ada-v1
python scripts/test_docs_specialist.py
```

## Registry Information

**Registered as:** `docs`  
**File:** `brain/specialists/docs_specialist.py`  
**Class:** `DocumentationSpecialist`  
**Priority:** HIGH  
**Icon:** 📚

See `.ai/specialist-registry.json` for complete metadata.

---

**Last Updated:** 2025-12-16  
**Status:** ✅ Production Ready  
**Testing:** ✅ Validated
