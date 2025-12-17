# Codebase Specialist - Implementation Plan

## Vision

Enable Ada to read and understand her own source code, demonstrating that AI coding assistants are transparent and hackable.

**The Screenshot:** Ada in vim, suggesting improvements to her own code.  
**The Message:** "Hackable all the way down - use Continue.dev OR build your own."

---

## Goals

### Primary
1. **Ada can read her own code** - Bidirectional specialist for code lookup
2. **Safe and sandboxed** - Read-only, path restrictions, size limits
3. **Smart indexing** - Uses `.ai/codebase-map.json` as navigation aid
4. **Educational** - Shows how it works, no magic

### Secondary (Future)
1. Integration with Continue.dev (as backend provider)
2. Simple vim plugin (~100 lines) for DIY path
3. Documentation showing both paths
4. Reference implementation for others

---

## Architecture

### Component: Codebase Specialist

**Type:** Bidirectional specialist (LLM invokes via XML tag)

**Activation:**
```
User: "How does the specialist system work?"
Ada: <code_lookup>brain/specialists/protocol.py</code_lookup>
Specialist: Returns code with context
Ada: "The specialist system uses Protocol pattern..."
```

**Capabilities:**
- Read file by path
- Search for function/class definitions
- List files in directory
- Use codebase-map.json as index
- Return code with line numbers and context

### Data Flow

```
User message
    ↓
Brain prompt_builder assembles context
    ↓
LLM generates response with <code_lookup> tag
    ↓
Bidirectional handler detects tag
    ↓
CodebaseSpecialist.process(request)
    ↓
Read file, apply safety checks
    ↓
Return code snippet with context
    ↓
LLM continues response with code knowledge
    ↓
Stream to user
```

---

## Safety Design

### Critical Requirements

**NO WRITE ACCESS** - Ever. This specialist is READ-ONLY.

**Path Restrictions:**
- ✅ Allow: `/app/` (Ada's codebase)
- ✅ Allow: `/app/.ai/` (documentation)
- ❌ Deny: `/app/data/` (user data, secrets)
- ❌ Deny: `..` (path traversal)
- ❌ Deny: Absolute paths outside /app
- ❌ Deny: Symlinks that escape

**Size Limits:**
- Max file size: 50KB (prevent memory issues)
- Max files per request: 5 (prevent abuse)
- Max total output: 200KB per request

**Rate Limiting:**
- Max lookups per conversation: 20
- Throttle if excessive requests

**Content Filtering:**
- Strip potentially sensitive patterns (API keys, passwords)
- Warn if file contains credentials
- Redact environment variable values

### Security Checklist

- [ ] Path validation (no traversal)
- [ ] Size limits enforced
- [ ] Symlink resolution checked
- [ ] Directory listing bounded
- [ ] No execution capability
- [ ] No write capability
- [ ] Sandboxed in Docker
- [ ] Rate limiting implemented
- [ ] Logging for audit trail

---

## Implementation Phases

### Phase 1: Basic Read Capability (Week 1, Days 1-2)

**Goal:** Ada can read a single file by path

**Tasks:**
1. Create `brain/specialists/codebase_specialist.py`
2. Implement `BaseSpecialist` protocol
3. Add path validation and safety checks
4. Read file and return content with line numbers
5. Add basic tests

**Deliverable:** 
```python
result = specialist.process({
    "path": "brain/specialists/protocol.py"
})
# Returns: Code content with line numbers
```

### Phase 2: Smart Search (Week 1, Days 3-4)

**Goal:** Ada can search for functions/classes

**Tasks:**
1. Implement function/class search using regex
2. Use `.ai/codebase-map.json` as index
3. Add "find definition" capability
4. Add "list functions in file" capability
5. Add directory listing (bounded)

**Deliverable:**
```python
result = specialist.process({
    "search": "BaseSpecialist",
    "type": "class"
})
# Returns: File path + code snippet
```

### Phase 3: Bidirectional Integration (Week 1, Day 5)

**Goal:** LLM can invoke specialist mid-response

**Tasks:**
1. Add XML tag format: `<code_lookup path="..."/>`
2. Integrate with bidirectional handler
3. Test LLM invoking specialist
4. Add context injection
5. Add priority handling

**Deliverable:**
LLM can use `<code_lookup>` tags and get code back

### Phase 4: Polish & Documentation (Week 2, Days 1-2)

**Goal:** Production ready and documented

**Tasks:**
1. Error handling and edge cases
2. Logging and audit trail
3. Performance optimization (caching?)
4. Documentation in `docs/specialists.rst`
5. Update `.ai/specialist-registry.json`
6. Add to specialist overview docs

**Deliverable:** Fully documented, production-ready specialist

---

## Technical Specifications

### File: `brain/specialists/codebase_specialist.py`

**Class:** `CodebaseSpecialist(BaseSpecialist)`

**Methods:**
```python
def should_activate(self, context: dict) -> bool:
    # Always bidirectional, never context-triggered
    return False

def process(self, request: dict) -> SpecialistResult:
    # Main processing logic
    pass

def _validate_path(self, path: str) -> bool:
    # Security checks
    pass

def _read_file(self, path: str) -> str:
    # Safe file reading with size limits
    pass

def _search_definition(self, name: str, type: str) -> list:
    # Find function/class definitions
    pass

def _list_directory(self, path: str) -> list:
    # List files (bounded)
    pass

def _use_codebase_map(self, query: str) -> list:
    # Query .ai/codebase-map.json
    pass
```

**Request Format:**
```python
{
    "action": "read",  # or "search", "list", "find"
    "path": "brain/specialists/protocol.py",
    "query": "BaseSpecialist",  # for search
    "type": "class",  # or "function"
    "lines": [10, 50]  # optional line range
}
```

**Response Format:**
```python
SpecialistResult(
    specialist_name="codebase",
    content=f"""
File: brain/specialists/protocol.py
Lines: 1-50

```python
# @ai-indexable: specialist-protocol
# @ai-purpose: Base protocol for all specialists

class BaseSpecialist(Protocol):
    \"\"\"Base protocol for specialist plugins.\"\"\"
    
    def should_activate(self, context: dict) -> bool:
        ...
```

Function found at line 15.
    """,
    metadata={
        "file": "brain/specialists/protocol.py",
        "lines": [1, 50],
        "language": "python",
        "size_bytes": 2048
    }
)
```

### XML Tag Format (for bidirectional use)

```xml
<!-- Read a file -->
<code_lookup path="brain/specialists/protocol.py"/>

<!-- Read specific lines -->
<code_lookup path="brain/app.py" lines="1-50"/>

<!-- Search for definition -->
<code_lookup search="BaseSpecialist" type="class"/>

<!-- List directory -->
<code_lookup action="list" path="brain/specialists/"/>
```

### Safety Implementation

```python
ALLOWED_PATHS = ["/app/brain", "/app/.ai", "/app/scripts", "/app/docs"]
DENIED_PATHS = ["/app/data", "/app/.git", "/app/.env"]
MAX_FILE_SIZE = 50 * 1024  # 50KB
MAX_FILES_PER_REQUEST = 5
MAX_LOOKUPS_PER_CONVERSATION = 20

def _validate_path(self, path: str) -> tuple[bool, str]:
    """Validate path is safe to read."""
    abs_path = os.path.abspath(os.path.join("/app", path))
    
    # Check path traversal
    if not abs_path.startswith("/app/"):
        return False, "Path traversal detected"
    
    # Check denied paths
    for denied in DENIED_PATHS:
        if abs_path.startswith(denied):
            return False, f"Access denied to {denied}"
    
    # Check allowed paths
    allowed = any(abs_path.startswith(p) for p in ALLOWED_PATHS)
    if not allowed:
        return False, "Path not in allowed list"
    
    # Check symlinks
    if os.path.islink(abs_path):
        real_path = os.path.realpath(abs_path)
        if not real_path.startswith("/app/"):
            return False, "Symlink escape detected"
    
    return True, "OK"
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_codebase_specialist.py

def test_read_own_file():
    """Test reading protocol.py"""
    specialist = CodebaseSpecialist()
    result = specialist.process({"path": "brain/specialists/protocol.py"})
    assert "BaseSpecialist" in result.content
    assert result.metadata["language"] == "python"

def test_path_traversal_blocked():
    """Test security: path traversal blocked"""
    specialist = CodebaseSpecialist()
    with pytest.raises(SecurityError):
        specialist.process({"path": "../../etc/passwd"})

def test_denied_path_blocked():
    """Test security: data directory blocked"""
    specialist = CodebaseSpecialist()
    with pytest.raises(SecurityError):
        specialist.process({"path": "data/chroma/index"})

def test_file_size_limit():
    """Test security: large files rejected"""
    # Create test with >50KB file
    pass

def test_search_function():
    """Test finding function definition"""
    specialist = CodebaseSpecialist()
    result = specialist.process({
        "search": "build_prompt",
        "type": "function"
    })
    assert "brain/prompt_builder.py" in result.content
```

### Integration Tests

```python
def test_bidirectional_invocation():
    """Test LLM can invoke specialist"""
    # Send message that triggers code lookup
    # Verify specialist called
    # Verify code returned to LLM
    pass

def test_conversation_with_code():
    """Test full conversation with code lookups"""
    # "How does the specialist system work?"
    # Verify Ada uses <code_lookup>
    # Verify response includes code explanation
    pass
```

### Manual Testing

```bash
# Test via CLI
echo "How does the specialist system work in Ada?" | ada-cli

# Expected: Ada uses <code_lookup> and explains with code

# Test via web UI
# Navigate to http://localhost:5000
# Ask: "Show me the BaseSpecialist class"
# Verify Ada can read and explain her own code
```

---

## Risks and Mitigations

### Risk: Accidental Secret Exposure
**Mitigation:** 
- Block data/ directory completely
- Pattern matching for API keys/passwords
- Audit log of all file access
- Review what files contain before launch

### Risk: Path Traversal Attack
**Mitigation:**
- Strict path validation
- Resolve symlinks
- Whitelist approach (explicit allow list)
- Test extensively with malicious inputs

### Risk: Performance Impact
**Mitigation:**
- File size limits
- Rate limiting per conversation
- Caching of frequently accessed files
- Async file I/O

### Risk: LLM Prompt Injection
**Mitigation:**
- Specialist validates requests before executing
- Type checking on all inputs
- Malformed XML tags ignored
- Logging for audit

### Risk: Information Leakage
**Mitigation:**
- No execution of code (read only!)
- No access to environment variables
- No access to runtime memory
- Sandboxed in Docker container

---

## Success Criteria

### Must Have
- [ ] Ada can read her own source files
- [ ] Path security prevents escapes
- [ ] LLM can invoke via bidirectional tag
- [ ] Works in conversation flow
- [ ] Documented in specialist docs
- [ ] Test coverage >80%

### Should Have
- [ ] Smart search for functions/classes
- [ ] Uses codebase-map.json as index
- [ ] Good error messages
- [ ] Performance is acceptable (<500ms per lookup)
- [ ] Logging for debugging

### Nice to Have
- [ ] Syntax highlighting in responses
- [ ] "Related files" suggestions
- [ ] Import graph navigation
- [ ] Git blame integration
- [ ] Diff viewing capability

---

## Future Enhancements (Post-MVP)

### Phase 5: Continue.dev Integration
- Document Ada as backend provider
- Test with Continue.dev extension
- Create setup guide
- Contribute back any improvements

### Phase 6: Vim Plugin
- Simple `ada.vim` plugin (~100 lines)
- `:AdaChat`, `:AdaExplain`, `:AdaCode` commands
- Show DIY approach
- Document both paths

### Phase 7: Advanced Features
- Git integration (show history)
- Dependency graph visualization
- Cross-reference to documentation
- Test file suggestions

---

## Timeline

**Week 1:**
- Day 1-2: Basic read capability + safety
- Day 3-4: Smart search + codebase-map
- Day 5: Bidirectional integration

**Week 2:**
- Day 1-2: Polish + documentation
- Day 3: Testing + screenshots
- Day 4-5: Blog post / announcement

**Total:** ~10 days to MVP

---

## Open Questions

1. **Should we cache file contents?** Probably yes for performance, but invalidation?
2. **How to handle binary files?** Reject with helpful message?
3. **Should we support regex search?** Or just exact matches?
4. **Git integration now or later?** Later feels right.
5. **Maximum context window usage?** How much code can we show at once?
6. **Should specialist auto-suggest files?** Or only respond to requests?

---

## References

- Existing: `brain/specialists/docs_specialist.py` (similar pattern)
- Existing: `brain/specialists/bidirectional.py` (invocation pattern)
- Existing: `.ai/codebase-map.json` (navigation index)
- Docs: `docs/bidirectional.rst` (bidirectional guide)
- Tests: `tests/test_specialists.py` (test patterns)

---

**Status:** Planning phase  
**Created:** 2025-12-16  
**Next Step:** Review plan, then implement Phase 1
