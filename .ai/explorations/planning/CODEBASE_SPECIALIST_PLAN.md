# Codebase Specialist - Incremental Implementation Plan

**Goal:** Give Ada deep understanding of her own codebase for self-reference, debugging, and architectural awareness.

**Status:** 🎯 Planning Phase  
**Approach:** Incremental - Build MVP, test, expand in phases

---

## 🧠 What We Already Have (Infrastructure Audit)

### 1. **Specialist Framework** ✅
- `brain/specialists/protocol.py` - Base protocol with priority system
- 6 existing specialists: docs, wiki, web_search, ocr, listenbrainz, now_playing
- Bidirectional activation (LLM can request specialist mid-response)
- Context injection with priorities (CRITICAL → HIGH → MEDIUM → LOW)

### 2. **Docs Specialist** ✅ (Adjacent to codebase!)
- Already searches Sphinx HTML documentation
- HTML text extraction
- Keyword-based search with relevance scoring
- Bidirectional activation via `<docs_lookup>` tags
- **This is 70% of what we need!**

### 3. **Structured Metadata** ✅
- `.ai/codebase-map.json` - Module dependencies, purposes, functions
- `.ai/specialist-registry.json` - Specialist metadata
- Source code `@ai-*` annotations
- We have the GRAPH already documented!

### 4. **RAG Infrastructure** ✅
- `brain/rag_store.py` - ChromaDB vector storage
- Already handles: persona, FAQs, memories, conversation turns, summaries
- Embedding model: nomic-embed-text
- Semantic search working

### 5. **Token Monitoring** ✅
- `brain/token_monitor.py` - Track usage by component
- Can measure code context token costs

---

## 🎯 What We Want to Build (Features)

### Phase 1: MVP - "Find Function" 📍
**The smallest useful thing**

**User asks:** "How does the OCR specialist work?"  
**Ada responds:** [searches codebase] "The OCR specialist (brain/specialists/ocr_specialist.py) activates when uploaded_image_path is in context. It uses Tesseract via brain/ocr.py..."

**Implementation:**
1. Parse Python files to AST (Abstract Syntax Tree)
2. Extract: functions, classes, docstrings, imports
3. Build simple keyword index (function name → file location)
4. When LLM uses `<code_lookup>function_name</code_lookup>`, return definition + docstring
5. Inject into context as HIGH priority specialist result

**Why this first?**
- Simplest: Just keyword matching, no embeddings yet
- Immediately useful: Ada can look up her own functions
- Builds on docs_specialist pattern we already have
- Tests the specialist integration flow
- ~200 lines of code max

**Test cases:**
- Look up `calculate_importance` → returns context_retriever.py implementation
- Look up `SpecialistResult` → returns protocol.py dataclass
- Look up nonexistent function → graceful "not found"

---

### Phase 2: Semantic Code Search 🔍
**RAG over code chunks**

**Upgrade from Phase 1:** Keywords → Vector embeddings

**User asks:** "How do we handle streaming responses?"  
**Ada responds:** [semantic search] "Streaming is handled by llm.py::generate_stream() which yields chunks via Server-Sent Events in app.py::chat_stream_v1()..."

**Implementation:**
1. Chunk Python files by:
   - Function/method definitions
   - Class definitions
   - Module-level docstrings
2. Embed each chunk with nomic-embed-text
3. Store in ChromaDB (new collection: `code_chunks`)
4. Semantic search on user query
5. Return top-k relevant code chunks with file/line context

**Why second?**
- Natural extension of Phase 1
- Reuses RAG infrastructure
- Semantic search >>> keyword matching
- Still relatively simple (~300 lines)

**Test cases:**
- Query "streaming" → finds llm.py generate_stream + app.py SSE handler
- Query "specialist activation" → finds protocol.py should_activate pattern
- Query "memory importance" → finds context_retriever.py multi-signal scoring

---

### Phase 3: Cross-Reference Graph 🕸️
**"Who calls this? Who depends on this?"**

**User asks:** "What uses the RagStore?"  
**Ada responds:** "RagStore (rag_store.py) is used by: app.py (memory storage), prompt_builder/context_retriever.py (search), consolidate_memories.py (summarization)..."

**Implementation:**
1. Build call graph from AST analysis:
   - Function calls
   - Class instantiations  
   - Import statements
2. Store in graph structure (NetworkX or simple dict)
3. Queries:
   - "Who calls X?" (reverse lookup)
   - "What does X call?" (forward lookup)
   - "Dependency chain from X to Y"
4. Bidirectional specialist: `<code_graph>show_callers:RagStore</code_graph>`

**Why third?**
- Builds on Phase 1 AST parsing
- Adds relationship understanding
- Critical for debugging ("What breaks if I change this?")
- ~400 lines including graph builder

**Test cases:**
- Find callers of `build_prompt()` → lists app.py, tests
- Find dependencies of `SpecialistResult` → all specialist implementations
- Find import chain: app.py → llm.py → config.py

---

### Phase 4: Architecture Understanding 🏗️
**"How does data flow through the system?"**

**User asks:** "How does a chat request flow through Ada?"  
**Ada responds:** [analyzes data flow] "1. HTTP POST to /v1/chat/stream → 2. app.py validates with ChatRequest schema → 3. prompt_builder assembles context → 4. Specialists activate → 5. llm.generate_stream() → 6. SSE response"

**Implementation:**
1. Enhance cross-reference graph with:
   - Data flow analysis (input → transformation → output)
   - Endpoint → handler → service mapping
   - Schema → usage tracking
2. Add pattern recognition:
   - Request/response cycles
   - Specialist activation chains
   - Error handling paths
3. Generate flow diagrams as text (ASCII or Mermaid)

**Why fourth?**
- Requires Phase 3 graph infrastructure
- Higher-level understanding
- Useful for onboarding, debugging, refactoring
- ~500 lines including flow analyzer

**Test cases:**
- Trace request: POST /v1/chat/stream → full pipeline
- Trace specialist: OCR activation → context injection → LLM
- Trace data: User message → vector search → context → response

---

### Phase 5: Pattern Recognition 🎨
**"Find similar code, detect anti-patterns"**

**User asks:** "Show me other specialists like OCR"  
**Ada responds:** "OCR follows the context-triggered pattern (should_activate checks uploaded_image_path). Similar specialists: now_playing (media_info), listenbrainz (media_info)..."

**Implementation:**
1. Pattern templates:
   - Specialist activation patterns
   - Error handling patterns
   - API endpoint patterns
   - Data validation patterns
2. Similarity detection:
   - AST structural similarity
   - Naming convention analysis
   - Code flow similarity
3. Anti-pattern detection:
   - Missing error handling
   - Circular dependencies
   - Unused imports

**Why fifth?**
- Requires understanding from Phases 1-4
- Most sophisticated analysis
- Helps with code quality and consistency
- ~600 lines including pattern matchers

**Test cases:**
- Find specialists with HIGH priority → OCR, docs
- Find functions without error handling → flag them
- Find similar code to `should_activate()` → all specialist implementations

---

## 🚀 Phase 1 MVP - Detailed Implementation Plan

### Files to Create:

**1. `brain/specialists/codebase_specialist.py`** (~200 lines)
```python
class CodebaseSpecialist(BaseSpecialist):
    """Look up functions, classes, and modules in Ada's codebase."""
    
    def __init__(self):
        self.index = {}  # function_name → (file, line, code)
        self._build_index()
    
    def _build_index(self):
        """Walk brain/ directory, parse Python files, extract definitions."""
        # Use ast module: ast.parse(), ast.FunctionDef, ast.ClassDef
        pass
    
    def should_activate(self, request_context: dict) -> bool:
        """Bidirectional only - never auto-activate."""
        return False
    
    async def process(self, request_context: dict) -> SpecialistResult:
        """Look up function/class by name, return definition + docstring."""
        query = request_context.get('query', '')
        results = self._search_index(query)
        return SpecialistResult(
            success=True,
            specialist_name="codebase",
            context_text=self._format_results(results),
            data={"results": results}
        )
```

**2. `tests/test_codebase_specialist.py`** (~150 lines)
```python
def test_lookup_function():
    """Test finding a known function."""
    specialist = CodebaseSpecialist()
    result = await specialist.process({'query': 'calculate_importance'})
    assert result.success
    assert 'context_retriever.py' in result.context_text
    assert 'calculate_importance' in result.context_text

def test_lookup_class():
    """Test finding a known class."""
    specialist = CodebaseSpecialist()
    result = await specialist.process({'query': 'SpecialistResult'})
    assert result.success
    assert 'protocol.py' in result.context_text

def test_not_found():
    """Test graceful handling of nonexistent items."""
    specialist = CodebaseSpecialist()
    result = await specialist.process({'query': 'nonexistent_function'})
    assert not result.success
    assert 'not found' in result.error.lower()
```

**3. Integration with bidirectional system:**
- Add `<code_lookup>` tag support to `brain/specialists/bidirectional.py`
- Register CodebaseSpecialist in `brain/specialists/__init__.py`
- Test with real LLM: "Look up the build_prompt function using <code_lookup>build_prompt</code_lookup>"

---

## 📊 Success Metrics

### Phase 1 (MVP):
- ✅ Can look up any function/class in brain/ directory
- ✅ Returns file location + definition + docstring
- ✅ Bidirectional activation works (LLM can request mid-response)
- ✅ 10+ test cases passing
- ✅ Response time < 100ms for lookup

### Phase 2 (Semantic Search):
- ✅ Can find code by semantic query (not just exact names)
- ✅ RAG search returns relevant code chunks
- ✅ Top-3 accuracy > 80% on test queries
- ✅ ChromaDB integration working
- ✅ Response time < 500ms for search

### Phase 3 (Cross-Reference):
- ✅ Can answer "who calls X" and "what does X call"
- ✅ Call graph covers all brain/ modules
- ✅ Dependency chains accurate
- ✅ Response time < 200ms for graph queries

### Phase 4 (Architecture):
- ✅ Can trace full request flow
- ✅ Data flow diagrams generated correctly
- ✅ Endpoint → service mapping complete
- ✅ Flow analysis covers 90%+ of codebase

### Phase 5 (Patterns):
- ✅ Can identify similar code patterns
- ✅ Anti-pattern detection finds real issues
- ✅ Pattern templates cover common cases
- ✅ Similarity matching > 75% accuracy

---

## 🎬 Getting Started (Tonight!)

### Step 1: Create Phase 1 branch
```bash
git checkout -b feature/codebase-specialist-phase1
```

### Step 2: Scaffold basic structure
```bash
touch brain/specialists/codebase_specialist.py
touch tests/test_codebase_specialist.py
```

### Step 3: Implement minimal AST parser
- Parse single Python file
- Extract function definitions
- Return as dict

### Step 4: Build keyword index
- Walk brain/ directory
- Index all functions/classes
- Simple dict: name → location

### Step 5: Implement lookup
- Query index by name
- Return code snippet + context
- Format for LLM injection

### Step 6: Write tests (TDD!)
- Test lookup of known function
- Test lookup of known class
- Test not found case
- Test bidirectional activation

### Step 7: Integrate with bidirectional system
- Add `<code_lookup>` tag parser
- Register in specialist loader
- Test with real LLM

### Step 8: Document and merge
- Add to specialist-registry.json
- Update codebase-map.json
- Write docs/codebase_specialist.rst
- Merge to trunk!

---

## 🤔 Design Decisions

### Why AST over regex?
- AST is reliable (Python's own parser!)
- Handles all edge cases (multiline strings, nested functions)
- Gives us line numbers for free
- Enables deeper analysis in later phases

### Why keyword index first?
- Simple and fast
- Tests the integration flow
- Immediate value (can look up exact names)
- Easy to upgrade to semantic search later

### Why bidirectional only?
- Codebase lookup shouldn't auto-activate
- User (or LLM) requests it explicitly
- Avoids context pollution
- Keeps Phase 1 simple

### Why ChromaDB for Phase 2?
- Already have the infrastructure
- Same embedding model as memories
- Proven to work well
- Easy to add new collections

### Why NetworkX for Phase 3?
- Standard Python graph library
- Rich query capabilities
- Can export to various formats
- Visualization potential

---

## 📚 Resources & References

### Python AST:
- Docs: https://docs.python.org/3/library/ast.html
- Tutorial: https://greentreesnakes.readthedocs.io/
- Our use: Extract function/class definitions, docstrings, imports

### Code Analysis Libraries:
- `ast` (stdlib) - Phase 1 ✅
- `astroid` - More powerful AST, Phase 3+
- `rope` - Refactoring tools (maybe Phase 5)
- `jedi` - Code completion (maybe Phase 5)

### Graph Libraries:
- `networkx` - Graph analysis, Phase 3 ✅
- `graphviz` - Visualization (optional)

### Similar Projects:
- Sourcegraph - Inspiration for features
- CodeSearchNet - Dataset and ideas
- tree-sitter - Multi-language parsing (future)

---

## 🚧 Known Challenges

### Phase 1:
- **Dynamic imports:** Won't catch runtime imports (acceptable for MVP)
- **Generated code:** Decorators, metaclasses may be tricky (skip for now)
- **External deps:** Only index brain/, not libraries (correct for now)

### Phase 2:
- **Chunk size:** Too small = no context, too large = poor matching
- **Embedding quality:** Code embeddings different from text (test and tune)
- **Update latency:** Index rebuild on code changes (acceptable for Phase 2)

### Phase 3:
- **Indirect calls:** Function passed as argument (hard to trace statically)
- **Dynamic dispatch:** Method calls on unknown types (best effort)
- **Circular deps:** Need cycle detection (NetworkX handles this)

### Phase 4:
- **Async flows:** Harder to trace than sync (document limitations)
- **External services:** ChromaDB, Ollama (show boundaries)
- **Error paths:** Many possible paths (focus on happy path first)

### Phase 5:
- **Pattern definition:** What counts as "similar"? (Start conservative)
- **False positives:** Over-matching patterns (tune thresholds)
- **Performance:** AST comparison expensive (cache aggressively)

---

## 🎯 Success Criteria

**MVP is done when:**
1. ✅ Ada can look up any function in brain/ by exact name
2. ✅ Results include file, line number, definition, and docstring
3. ✅ Bidirectional activation works (<code_lookup> tag)
4. ✅ All tests passing (10+ test cases)
5. ✅ Response time < 100ms
6. ✅ Documentation complete
7. ✅ Merged to trunk with passing CI

**We know we're ready for Phase 2 when:**
- Phase 1 working smoothly in production
- Users asking semantic questions ("how do specialists work?")
- Exact name lookup feels limiting
- We have confidence in the architecture

---

## 💡 Future Ideas (Phase 6+)

- **Multi-language support:** JavaScript (frontend), Bash (scripts)
- **Git history analysis:** "When did this change?" "Who wrote this?"
- **Test coverage mapping:** "What tests cover this function?"
- **Performance profiling:** "What's slow?" from runtime data
- **Refactoring suggestions:** "This function is too complex"
- **Documentation generation:** Auto-update docs from code
- **Interactive exploration:** "Show me the call tree" with UI

---

## 🎊 Why This Matters

**For Ada:**
- Self-awareness: Can explain her own architecture
- Debugging: Can trace issues through code
- Learning: Can see patterns and improve
- Autonomy: Less reliant on external documentation

**For Users:**
- Faster onboarding: Ask Ada about her code
- Better debugging: Ada helps trace issues
- Code review: Ada can explain changes
- Documentation: Always up-to-date from source

**For Development:**
- Quality: Pattern detection catches issues
- Consistency: See what patterns exist
- Refactoring: Understand impact of changes
- Testing: See what's covered

---

**Let's build Ada a brain for her own code! Starting with Phase 1 MVP tonight! 🚀🧠**
