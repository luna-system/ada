# Tool Awareness Framework - TDD Implementation Plan

**Goal:** Teach any machine agent (LLM or otherwise) that it has a "toolbox" of capabilities, enabling model-agnostic tool activation without special syntax training.

**Philosophy:** TDD-first, incremental, biomimetic architecture mirroring human cognition (reflex→memory→reasoning).

---

## Phase 0: Test Infrastructure Setup (5 minutes)

**Purpose:** Create test fixtures and utilities before any implementation.

### Tests to Write First

```python
# tests/test_tool_awareness.py

def test_pattern_matcher_initialization():
    """Pattern matcher loads with empty patterns by default"""
    matcher = ToolPatternMatcher()
    assert matcher.patterns == []
    assert matcher.ready() == False

def test_pattern_matcher_loads_from_file():
    """Pattern matcher can load patterns from JSON"""
    matcher = ToolPatternMatcher(patterns_file="fixtures/tool_patterns.json")
    assert len(matcher.patterns) > 0
    assert matcher.ready() == True

def test_simple_codebase_pattern_matching():
    """Detect codebase lookup intent from human language"""
    matcher = ToolPatternMatcher(patterns_file="fixtures/tool_patterns.json")
    
    query = "How does calculate_importance work?"
    matches = matcher.match(query)
    
    assert len(matches) > 0
    assert matches[0].tool_name == "codebase"
    assert "calculate_importance" in matches[0].extracted_params["query"]

def test_pattern_confidence_scoring():
    """Patterns have confidence scores for ambiguous cases"""
    matcher = ToolPatternMatcher(patterns_file="fixtures/tool_patterns.json")
    
    query = "calculate_importance"  # Ambiguous - lookup or discussion?
    matches = matcher.match(query)
    
    assert matches[0].confidence < 0.8  # Low confidence
    
    query = "Show me the code for calculate_importance"  # Clear intent
    matches = matcher.match(query)
    
    assert matches[0].confidence > 0.8  # High confidence

def test_no_false_positives():
    """Don't activate tools when NOT appropriate"""
    matcher = ToolPatternMatcher(patterns_file="fixtures/tool_patterns.json")
    
    query = "I think the importance calculation is interesting"  # Discussion, not lookup
    matches = matcher.match(query)
    
    assert len(matches) == 0 or matches[0].confidence < 0.5
```

### Fixtures to Create

```python
# tests/fixtures/tool_patterns.json
{
  "patterns": [
    {
      "tool_name": "codebase",
      "activation_patterns": [
        {
          "regex": "(?:how does|what does|show me|look up|find).*?([a-z_]+).*?(?:work|function|class|method)",
          "confidence_base": 0.9,
          "param_extraction": {
            "query": "group1"
          }
        },
        {
          "regex": "(?:code for|implementation of|definition of)\\s+([a-z_]+)",
          "confidence_base": 0.95,
          "param_extraction": {
            "query": "group1"
          }
        }
      ],
      "negative_patterns": [
        "(?:think|believe|interesting|opinion) about"
      ]
    }
  ]
}
```

**Expected Result:** All 5 tests FAIL (no implementation yet).

**Runtime Target:** < 0.1 seconds for test suite.

---

## Phase 1: Simple Pattern Matching (30 minutes)

**Goal:** Implement basic regex-based tool detection that passes Phase 0 tests.

### Implementation

```python
# brain/specialists/tool_activation.py

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Optional

@dataclass
class ToolMatch:
    """A potential tool activation match."""
    tool_name: str
    confidence: float
    extracted_params: dict[str, str]
    pattern_matched: str

class ToolPatternMatcher:
    """Anticipatory pattern matching for tool activation (Tier 1)."""
    
    def __init__(self, patterns_file: Optional[str] = None):
        self.patterns = []
        if patterns_file:
            self._load_patterns(patterns_file)
    
    def ready(self) -> bool:
        """Check if matcher has patterns loaded."""
        return len(self.patterns) > 0
    
    def _load_patterns(self, filepath: str):
        """Load patterns from JSON file."""
        with open(filepath) as f:
            data = json.load(f)
            self.patterns = data.get("patterns", [])
    
    def match(self, query: str) -> list[ToolMatch]:
        """Find tool activation patterns in query."""
        matches = []
        
        for pattern_group in self.patterns:
            tool_name = pattern_group["tool_name"]
            
            # Check negative patterns first (exclusions)
            if self._matches_negative_pattern(query, pattern_group):
                continue
            
            # Try each activation pattern
            for pattern in pattern_group["activation_patterns"]:
                match = re.search(pattern["regex"], query, re.IGNORECASE)
                if match:
                    params = self._extract_params(match, pattern.get("param_extraction", {}))
                    confidence = self._calculate_confidence(query, pattern, match)
                    
                    matches.append(ToolMatch(
                        tool_name=tool_name,
                        confidence=confidence,
                        extracted_params=params,
                        pattern_matched=pattern["regex"]
                    ))
        
        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def _matches_negative_pattern(self, query: str, pattern_group: dict) -> bool:
        """Check if query matches exclusion patterns."""
        for neg_pattern in pattern_group.get("negative_patterns", []):
            if re.search(neg_pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _extract_params(self, match: re.Match, extraction_rules: dict) -> dict:
        """Extract parameters from regex match groups."""
        params = {}
        for param_name, group_ref in extraction_rules.items():
            if group_ref.startswith("group"):
                group_num = int(group_ref.replace("group", ""))
                params[param_name] = match.group(group_num)
        return params
    
    def _calculate_confidence(self, query: str, pattern: dict, match: re.Match) -> float:
        """Calculate confidence score for match."""
        base_confidence = pattern.get("confidence_base", 0.5)
        
        # Adjust for query clarity
        if len(query.split()) < 5:  # Short query = ambiguous
            base_confidence *= 0.7
        
        # Adjust for match coverage
        match_coverage = len(match.group(0)) / len(query)
        confidence = base_confidence * (0.7 + 0.3 * match_coverage)
        
        return min(confidence, 1.0)
```

### Tests Should Now Pass

```bash
pytest tests/test_tool_awareness.py -v
# Expected: 5/5 passing, ~0.05s runtime
```

**Validation Criteria:**
- ✅ All Phase 0 tests pass
- ✅ Runtime < 0.1 seconds
- ✅ Pattern loading works from JSON
- ✅ Confidence scoring implemented
- ✅ Negative patterns prevent false positives

---

## Phase 2: Production Pattern Library (20 minutes)

**Goal:** Create comprehensive patterns for existing specialists.

### Tests First

```python
# tests/test_tool_patterns_comprehensive.py

def test_codebase_patterns_comprehensive():
    """All codebase activation patterns work"""
    matcher = ToolPatternMatcher(patterns_file="data/tool_patterns.json")
    
    test_cases = [
        ("How does calculate_importance work?", "codebase", 0.8),
        ("Show me the calculate_importance function", "codebase", 0.9),
        ("What's the implementation of PromptAssembler?", "codebase", 0.85),
        ("Find the ContextRetriever class", "codebase", 0.9),
        ("I think calculate_importance is interesting", None, 0.0),  # No match
    ]
    
    for query, expected_tool, min_confidence in test_cases:
        matches = matcher.match(query)
        if expected_tool is None:
            assert len(matches) == 0 or matches[0].confidence < 0.5
        else:
            assert matches[0].tool_name == expected_tool
            assert matches[0].confidence >= min_confidence

def test_web_search_patterns():
    """Web search activation patterns"""
    matcher = ToolPatternMatcher(patterns_file="data/tool_patterns.json")
    
    queries = [
        "Search the web for recent news about AI",
        "What's happening with GPT-5?",
        "Look up current weather in Seattle",
    ]
    
    for query in queries:
        matches = matcher.match(query)
        assert len(matches) > 0
        assert matches[0].tool_name == "web_search"

def test_wiki_patterns():
    """Wiki lookup patterns"""
    matcher = ToolPatternMatcher(patterns_file="data/tool_patterns.json")
    
    queries = [
        "Look up Cloudy on the Object Show wiki",
        "Who is Leafy from BFDI?",
        "Tell me about quantum entanglement",  # Wikipedia
    ]
    
    for query in queries:
        matches = matcher.match(query)
        assert len(matches) > 0
        assert matches[0].tool_name == "wiki"

def test_no_tool_needed():
    """Conversational queries don't trigger tools"""
    matcher = ToolPatternMatcher(patterns_file="data/tool_patterns.json")
    
    queries = [
        "How are you doing today?",
        "That's really interesting!",
        "Can you explain what you mean?",
        "I'm feeling frustrated",
    ]
    
    for query in queries:
        matches = matcher.match(query)
        assert len(matches) == 0 or matches[0].confidence < 0.5
```

### Implementation

```json
// data/tool_patterns.json
{
  "version": "1.0.0",
  "description": "Tool activation patterns for pre-execution matching (Tier 1 - Anticipatory/Reflex)",
  "patterns": [
    {
      "tool_name": "codebase",
      "description": "Ada's own codebase lookup",
      "activation_patterns": [
        {
          "regex": "(?:how does|what does|show me|look up|find|explain)\\s+(?:the\\s+)?([a-z_]+)\\s+(?:work|function|class|method|code|implementation)",
          "confidence_base": 0.9,
          "param_extraction": {"query": "group1"}
        },
        {
          "regex": "(?:code for|implementation of|definition of|source code for)\\s+([a-z_]+)",
          "confidence_base": 0.95,
          "param_extraction": {"query": "group1"}
        },
        {
          "regex": "(?:where is|show|find)\\s+([A-Z][a-zA-Z]+)(?:\\s+class)?",
          "confidence_base": 0.85,
          "param_extraction": {"query": "group1"}
        }
      ],
      "negative_patterns": [
        "(?:think|believe|feel|opinion|interesting) (?:about|that)",
        "(?:generally|usually|typically)",
        "(?:concept of|idea of)"
      ]
    },
    {
      "tool_name": "web_search",
      "description": "External web search for current information",
      "activation_patterns": [
        {
          "regex": "(?:search|look up|find|what's happening with|news about|current).*?(?:web|internet|online)",
          "confidence_base": 0.95,
          "param_extraction": {"query": "group0"}
        },
        {
          "regex": "(?:what's|what is|whats)\\s+(?:the\\s+)?(?:latest|current|recent)\\s+(?:on|about|with)\\s+(.+?)(?:\\?|$)",
          "confidence_base": 0.85,
          "param_extraction": {"query": "group1"}
        },
        {
          "regex": "(?:weather|temperature)\\s+(?:in|at|for)\\s+([A-Z][a-zA-Z\\s]+)",
          "confidence_base": 0.9,
          "param_extraction": {"query": "group0"}
        }
      ],
      "negative_patterns": []
    },
    {
      "tool_name": "wiki",
      "description": "Wikipedia and fandom wiki lookups",
      "activation_patterns": [
        {
          "regex": "(?:who is|what is|tell me about)\\s+([A-Z][a-zA-Z\\s]+?)(?:\\s+from\\s+(?:BFDI|BFB|TPOT|the show))?",
          "confidence_base": 0.8,
          "param_extraction": {"query": "group1"}
        },
        {
          "regex": "look up\\s+([A-Z][a-zA-Z\\s]+?)\\s+on\\s+(?:the\\s+)?(?:wiki|wikipedia|Object Show)",
          "confidence_base": 0.95,
          "param_extraction": {"query": "group1"}
        }
      ],
      "negative_patterns": [
        "(?:in my code|in Ada|in the codebase)"
      ]
    }
  ]
}
```

**Validation:**
```bash
pytest tests/test_tool_patterns_comprehensive.py -v
# Expected: All tests pass, ~0.08s runtime
```

---

## Phase 3: Integration Into Streaming (30 minutes)

**Goal:** Add pre-execution pattern matching to chat endpoint.

### Tests First

```python
# tests/test_tool_activation_integration.py

import pytest
from brain.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_codebase_specialist_auto_activation():
    """Codebase specialist activates from human language"""
    response = client.post("/v1/chat/stream", json={
        "message": "How does calculate_importance work?",
        "conversation_id": "test-auto-activation"
    })
    
    # Check for specialist result in stream
    events = list(response.iter_lines())
    specialist_events = [e for e in events if b'"event":"specialist_result"' in e]
    
    assert len(specialist_events) > 0
    # Should contain codebase specialist result
    assert b'"specialist":"codebase"' in specialist_events[0]

def test_web_search_auto_activation():
    """Web search activates from pattern"""
    response = client.post("/v1/chat/stream", json={
        "message": "Search the web for recent AI news",
        "conversation_id": "test-web-activation"
    })
    
    events = list(response.iter_lines())
    specialist_events = [e for e in events if b'"event":"specialist_result"' in e]
    
    assert len(specialist_events) > 0
    assert b'"specialist":"web_search"' in specialist_events[0]

def test_no_false_activation():
    """Conversational queries don't activate tools"""
    response = client.post("/v1/chat/stream", json={
        "message": "That's really interesting, thanks!",
        "conversation_id": "test-no-activation"
    })
    
    events = list(response.iter_lines())
    specialist_events = [e for e in events if b'"event":"specialist_result"' in e]
    
    assert len(specialist_events) == 0

@pytest.mark.asyncio
async def test_pattern_matcher_in_prompt_builder():
    """PromptAssembler uses pattern matcher"""
    from brain.prompt_builder import PromptAssembler
    from brain.schemas import ChatRequest
    
    assembler = PromptAssembler()
    request = ChatRequest(
        message="Show me the ContextRetriever class",
        conversation_id="test-prompt-builder"
    )
    
    prompt = await assembler.build_prompt(request)
    
    # Should include codebase specialist result
    assert "ContextRetriever" in prompt
    assert "class ContextRetriever" in prompt or "def " in prompt
```

### Implementation

```python
# brain/app.py - Modify chat_stream_v1

from brain.specialists.tool_activation import ToolPatternMatcher

# Global matcher (loaded at startup)
tool_matcher = ToolPatternMatcher(patterns_file="data/tool_patterns.json")

@app.post("/v1/chat/stream")
async def chat_stream_v1(request: ChatRequest):
    """Chat endpoint with PRE-EXECUTION tool activation."""
    
    # PHASE 3: Pre-execution pattern matching
    tool_matches = tool_matcher.match(request.message)
    
    # Execute high-confidence matches BEFORE LLM
    specialist_results = []
    for match in tool_matches:
        if match.confidence >= 0.7:  # High confidence threshold
            specialist = get_specialist_by_name(match.tool_name)
            if specialist:
                result = await specialist.process(
                    request=request,
                    params=match.extracted_params
                )
                specialist_results.append({
                    "specialist": match.tool_name,
                    "result": result,
                    "confidence": match.confidence
                })
                
                # Yield specialist result event
                yield f'event: specialist_result\ndata: {json.dumps({"specialist": match.tool_name, "confidence": match.confidence})}\n\n'
    
    # Build prompt with specialist results
    prompt = await prompt_assembler.build_prompt(
        request, 
        specialist_results=specialist_results
    )
    
    # Continue with LLM generation...
    async for chunk in llm_client.generate_stream(prompt):
        yield f'data: {json.dumps({"content": chunk})}\n\n'
```

```python
# brain/prompt_builder/prompt_assembler.py - Modify to accept specialist_results

async def build_prompt(
    self, 
    request: ChatRequest,
    specialist_results: list[dict] = None
) -> str:
    """Build prompt with optional pre-executed specialist results."""
    
    sections = []
    
    # ... existing persona, memories, etc ...
    
    # Add pre-executed specialist results
    if specialist_results:
        specialist_section = self.section_builder.format_specialist_results(
            specialist_results, 
            priority="PRE_EXECUTION"
        )
        sections.append(specialist_section)
    
    # ... rest of prompt building ...
```

**Validation:**
```bash
pytest tests/test_tool_activation_integration.py -v
# Expected: All integration tests pass

# Manual test
curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "How does calculate_importance work?", "conversation_id": "test"}'
# Expected: See specialist_result event, then LLM response referencing the code
```

---

## Phase 4: Synthetic Memory (RAG Tier 2 - Instinctive) (45 minutes)

**Goal:** Add "instinctive" tool awareness via synthetic memories in ChromaDB.

### Tests First

```python
# tests/test_synthetic_tool_memories.py

def test_synthetic_memories_loaded():
    """Synthetic tool usage memories in ChromaDB"""
    from brain.rag_store import rag_store
    
    results = rag_store.search_memories(
        query="How do I look up code?",
        collection_name="memories",
        n_results=5
    )
    
    # Should find synthetic examples
    assert any("codebase specialist" in r["content"].lower() for r in results)

def test_tool_awareness_faqs():
    """Tool awareness in FAQ collection"""
    from brain.rag_store import rag_store
    
    results = rag_store.search_memories(
        query="What tools do I have?",
        collection_name="faqs",
        n_results=5
    )
    
    assert len(results) > 0
    content = " ".join(r["content"] for r in results)
    assert "codebase" in content.lower()
    assert "web search" in content.lower()

@pytest.mark.asyncio
async def test_synthetic_memories_in_prompt():
    """Synthetic memories appear in prompts for relevant queries"""
    from brain.prompt_builder import PromptAssembler
    from brain.schemas import ChatRequest
    
    assembler = PromptAssembler()
    request = ChatRequest(
        message="I need to look up some code",
        conversation_id="test-synthetic"
    )
    
    prompt = await assembler.build_prompt(request)
    
    # Should retrieve synthetic memory about codebase specialist
    assert "codebase" in prompt.lower()
```

### Implementation

```json
// seed/tool_usage_memories.json
{
  "synthetic_memories": [
    {
      "content": "When I needed to understand how calculate_importance worked, I looked up the function in my codebase using my code analysis capability. The function combines multiple signals (decay, surprise, relevance, habituation) to score memory importance.",
      "metadata": {
        "type": "tool_usage_example",
        "tool": "codebase",
        "timestamp": "2025-12-18T10:00:00Z",
        "importance": 0.85,
        "scope": "system",
        "tags": ["codebase_lookup", "example", "synthetic"]
      }
    },
    {
      "content": "I can look up my own code when users ask how something works. For example, when asked about PromptAssembler, I searched for the class definition and found it in brain/prompt_builder/prompt_assembler.py with its build_prompt method.",
      "metadata": {
        "type": "tool_usage_example",
        "tool": "codebase",
        "timestamp": "2025-12-18T10:15:00Z",
        "importance": 0.9,
        "scope": "system",
        "tags": ["codebase_lookup", "capability_awareness", "synthetic"]
      }
    },
    {
      "content": "When someone asked about recent AI news, I used web search to find current information since my training data has a cutoff. Web search lets me access up-to-date information from the internet.",
      "metadata": {
        "type": "tool_usage_example",
        "tool": "web_search",
        "timestamp": "2025-12-18T10:30:00Z",
        "importance": 0.8,
        "scope": "system",
        "tags": ["web_search", "example", "synthetic"]
      }
    }
  ]
}
```

```json
// seed/tool_awareness_faqs.json
{
  "faqs": [
    {
      "question": "What capabilities do I have?",
      "answer": "I have several specialist capabilities: (1) Codebase lookup - I can analyze and explain my own source code using AST parsing. (2) Web search - I can find current information online. (3) Wiki lookup - I can search Wikipedia and fandom wikis. (4) Vision/OCR - I can process images and extract text. These activate automatically when relevant to your question.",
      "metadata": {
        "category": "capabilities",
        "importance": 0.95,
        "tags": ["tools", "specialists", "awareness"]
      }
    },
    {
      "question": "How do I know when to use my tools?",
      "answer": "I don't need special commands - my system detects when tools would help based on your question patterns. If you ask 'how does X work' about my code, I'll automatically look it up. If you ask about current events, I'll search the web. You can also explicitly ask me to use a capability.",
      "metadata": {
        "category": "tool_activation",
        "importance": 0.9,
        "tags": ["activation", "automatic", "pattern_matching"]
      }
    }
  ]
}
```

```python
# scripts/seed_synthetic_tool_memories.py
"""Load synthetic tool awareness memories into ChromaDB."""

import json
from brain.rag_store import rag_store
from brain.schemas import MemoryMetadata
from datetime import datetime, timezone

def load_synthetic_memories():
    """Load tool usage examples as synthetic memories."""
    
    with open("seed/tool_usage_memories.json") as f:
        data = json.load(f)
    
    for memory in data["synthetic_memories"]:
        rag_store.add_memory(
            content=memory["content"],
            metadata=MemoryMetadata(**memory["metadata"]),
            collection_name="memories"
        )
    
    print(f"✓ Loaded {len(data['synthetic_memories'])} synthetic memories")

def load_tool_faqs():
    """Load tool awareness FAQs."""
    
    with open("seed/tool_awareness_faqs.json") as f:
        data = json.load(f)
    
    for faq in data["faqs"]:
        rag_store.add_memory(
            content=f"Q: {faq['question']}\n\nA: {faq['answer']}",
            metadata=MemoryMetadata(
                type="faq",
                timestamp=datetime.now(timezone.utc).isoformat(),
                importance=faq["metadata"]["importance"],
                scope="system",
                tags=faq["metadata"]["tags"]
            ),
            collection_name="faqs"
        )
    
    print(f"✓ Loaded {len(data['faqs'])} tool awareness FAQs")

if __name__ == "__main__":
    load_synthetic_memories()
    load_tool_faqs()
    print("\n✓ Synthetic tool awareness data loaded successfully!")
```

**Validation:**
```bash
# Load synthetic data
python scripts/seed_synthetic_tool_memories.py

# Test
pytest tests/test_synthetic_tool_memories.py -v
# Expected: All tests pass

# Manual validation - should retrieve synthetic examples
curl "http://localhost:8000/v1/search?q=how+do+I+look+up+code&collection=memories"
```

---

## Phase 5: Multi-Tier Orchestration (60 minutes)

**Goal:** Coordinate all three tiers (anticipatory, instinctive, deliberative).

### Tests First

```python
# tests/test_multi_tier_orchestration.py

def test_tier1_high_confidence_only():
    """Tier 1 only fires for high-confidence patterns"""
    from brain.specialists.tool_orchestrator import ToolOrchestrator
    
    orchestrator = ToolOrchestrator()
    
    # High confidence
    result = orchestrator.should_use_tier1("Show me the calculate_importance function")
    assert result == True
    
    # Low confidence (ambiguous)
    result = orchestrator.should_use_tier1("Tell me about calculate_importance")
    assert result == False

def test_tier2_augments_tier1():
    """Tier 2 (synthetic memories) adds context even when Tier 1 fires"""
    from brain.specialists.tool_orchestrator import ToolOrchestrator
    from brain.schemas import ChatRequest
    
    orchestrator = ToolOrchestrator()
    request = ChatRequest(
        message="How does the codebase specialist work?",
        conversation_id="test-multi-tier"
    )
    
    results = orchestrator.execute(request)
    
    # Should have both Tier 1 result AND Tier 2 memories
    assert results["tier1"]["activated"] == True
    assert len(results["tier2"]["memories"]) > 0
    assert "codebase" in str(results["tier2"]["memories"]).lower()

def test_tier3_fallback():
    """Tier 3 (deliberative/bidirectional) only for uncertain cases"""
    from brain.specialists.tool_orchestrator import ToolOrchestrator
    from brain.schemas import ChatRequest
    
    orchestrator = ToolOrchestrator()
    
    # Clear case - Tier 1 handles it
    request = ChatRequest(message="Show me PromptAssembler code", conversation_id="test")
    results = orchestrator.execute(request)
    assert results["tier1"]["activated"] == True
    assert results["tier3"]["needed"] == False
    
    # Ambiguous - needs LLM decision
    request = ChatRequest(message="Can you help me understand the architecture?", conversation_id="test")
    results = orchestrator.execute(request)
    assert results["tier1"]["activated"] == False
    assert results["tier3"]["needed"] == True

@pytest.mark.asyncio
async def test_full_orchestration_in_chat():
    """Full multi-tier orchestration in chat endpoint"""
    from fastapi.testclient import TestClient
    from brain.app import app
    
    client = TestClient(app)
    response = client.post("/v1/chat/stream", json={
        "message": "How does calculate_importance work?",
        "conversation_id": "test-orchestration"
    })
    
    events = list(response.iter_lines())
    
    # Should see specialist_result (Tier 1)
    assert any(b'"event":"specialist_result"' in e for e in events)
    
    # Should see LLM response referencing both code AND synthetic examples
    content = b"".join(events).decode()
    assert "calculate_importance" in content
```

### Implementation

```python
# brain/specialists/tool_orchestrator.py
"""Multi-tier tool activation orchestration (biomimetic architecture)."""

from dataclasses import dataclass
from typing import Optional
from brain.specialists.tool_activation import ToolPatternMatcher
from brain.rag_store import rag_store
from brain.schemas import ChatRequest

@dataclass
class OrchestrationResult:
    """Result from multi-tier orchestration."""
    tier1: dict  # Anticipatory/reflex results
    tier2: dict  # Instinctive/memory results
    tier3: dict  # Deliberative/reasoning metadata
    
class ToolOrchestrator:
    """Coordinates three-tier tool activation system.
    
    Tier 1 (Anticipatory/Reflex): Pre-execution pattern matching
    Tier 2 (Instinctive/Memory): RAG-based synthetic memories
    Tier 3 (Deliberative/Reasoning): LLM-decided activation (fallback)
    """
    
    def __init__(self):
        self.pattern_matcher = ToolPatternMatcher(
            patterns_file="data/tool_patterns.json"
        )
        self.tier1_confidence_threshold = 0.7
        self.tier2_relevance_threshold = 0.6
    
    def should_use_tier1(self, query: str) -> bool:
        """Check if Tier 1 (reflex) should handle this query."""
        matches = self.pattern_matcher.match(query)
        return len(matches) > 0 and matches[0].confidence >= self.tier1_confidence_threshold
    
    async def execute(self, request: ChatRequest) -> OrchestrationResult:
        """Execute multi-tier orchestration."""
        
        # Tier 1: Anticipatory pattern matching
        tier1_results = await self._execute_tier1(request)
        
        # Tier 2: Synthetic memory retrieval (ALWAYS runs for context)
        tier2_results = await self._execute_tier2(request)
        
        # Tier 3: Determine if LLM decision needed
        tier3_metadata = self._analyze_tier3_need(
            request, tier1_results, tier2_results
        )
        
        return OrchestrationResult(
            tier1=tier1_results,
            tier2=tier2_results,
            tier3=tier3_metadata
        )
    
    async def _execute_tier1(self, request: ChatRequest) -> dict:
        """Execute Tier 1 (reflex) pattern matching."""
        matches = self.pattern_matcher.match(request.message)
        
        if not matches or matches[0].confidence < self.tier1_confidence_threshold:
            return {"activated": False, "matches": []}
        
        # Execute high-confidence matches
        results = []
        for match in matches:
            if match.confidence >= self.tier1_confidence_threshold:
                # Import here to avoid circular dependency
                from brain.specialists import get_specialist_by_name
                
                specialist = get_specialist_by_name(match.tool_name)
                if specialist:
                    result = await specialist.process(
                        request=request,
                        params=match.extracted_params
                    )
                    results.append({
                        "tool": match.tool_name,
                        "result": result,
                        "confidence": match.confidence
                    })
        
        return {"activated": True, "matches": results}
    
    async def _execute_tier2(self, request: ChatRequest) -> dict:
        """Execute Tier 2 (instinctive) memory retrieval."""
        # Search for relevant tool usage examples
        memories = rag_store.search_memories(
            query=request.message,
            collection_name="memories",
            n_results=3,
            filter_metadata={"tags": {"$in": ["tool_usage_example", "synthetic"]}}
        )
        
        # Also check FAQs for tool awareness
        faqs = rag_store.search_memories(
            query=request.message,
            collection_name="faqs",
            n_results=2,
            filter_metadata={"category": "capabilities"}
        )
        
        return {
            "memories": memories,
            "faqs": faqs,
            "relevance_scores": [m.get("distance", 0) for m in memories]
        }
    
    def _analyze_tier3_need(
        self, 
        request: ChatRequest, 
        tier1: dict, 
        tier2: dict
    ) -> dict:
        """Determine if Tier 3 (deliberative) is needed."""
        
        # Tier 3 needed if:
        # 1. Tier 1 didn't activate (low confidence)
        # 2. OR query is complex/ambiguous
        # 3. OR explicitly asks for reasoning
        
        tier1_handled = tier1.get("activated", False)
        
        ambiguity_signals = [
            "can you",
            "should i",
            "how do i",
            "what's the best way",
            "help me understand"
        ]
        is_ambiguous = any(signal in request.message.lower() for signal in ambiguity_signals)
        
        return {
            "needed": not tier1_handled or is_ambiguous,
            "reason": "ambiguous_query" if is_ambiguous else "no_tier1_match",
            "fallback_to_llm": True
        }
```

**Validation:**
```bash
pytest tests/test_multi_tier_orchestration.py -v
# Expected: All tests pass, ~0.15s runtime
```

---

## Success Criteria

### Phase 0-1: Pattern Matching Foundation
- ✅ 5/5 basic tests passing
- ✅ Runtime < 0.1s
- ✅ Pattern loading from JSON works
- ✅ Confidence scoring functional

### Phase 2: Pattern Library
- ✅ Comprehensive patterns for 3+ specialists
- ✅ No false positives on conversational queries
- ✅ All pattern tests passing

### Phase 3: Integration
- ✅ Pre-execution activation in streaming endpoint
- ✅ Specialist results appear before LLM generation
- ✅ Manual curl test shows specialist_result events

### Phase 4: Synthetic Memory
- ✅ Tool usage examples in ChromaDB
- ✅ Tool awareness FAQs loaded
- ✅ Relevant memories retrieved for tool queries

### Phase 5: Orchestration
- ✅ Three-tier system coordinated
- ✅ High confidence → Tier 1 only
- ✅ Ambiguous → Tier 2 + Tier 3
- ✅ Full integration test passing

---

## Timeline

- **Phase 0**: 5 minutes (test infrastructure)
- **Phase 1**: 30 minutes (pattern matching)
- **Phase 2**: 20 minutes (pattern library)
- **Phase 3**: 30 minutes (streaming integration)
- **Phase 4**: 45 minutes (synthetic memory)
- **Phase 5**: 60 minutes (orchestration)

**Total: ~3 hours of focused TDD development**

---

## Post-Implementation: Cross-Model Validation

Once core framework works with current model:

```python
# tests/test_cross_model_compatibility.py

@pytest.mark.parametrize("model", [
    "llama3.2:latest",
    "qwen2.5:latest", 
    "mistral:latest",
    "deepseek-r1:latest"
])
def test_tool_activation_works_across_models(model):
    """Validate framework works with different models"""
    # Test with each model
    # Ensure Tier 1 + Tier 2 work regardless of model
    pass
```

---

## Philosophy Check

**Does this teach machines about "toolboxes"?**

✅ **Yes - through multiple complementary approaches:**

1. **Tier 1 (Reflex)**: "When I see X pattern, this tool helps"
2. **Tier 2 (Instinct)**: "I remember using this tool before in similar situations"  
3. **Tier 3 (Reasoning)**: "Let me think about what tool would help here"

**Human cognition parallel:**
- You touch hot stove → reflex pull back (Tier 1)
- You smell smoke → remember fire danger (Tier 2)
- You consider career → deliberate analysis (Tier 3)

**Machine agents learn:**
- "I have capabilities" (tool awareness)
- "These capabilities are for specific purposes" (pattern→tool mapping)
- "I can choose when to use them" (confidence thresholds)
- "I've used them before successfully" (synthetic memories)

**This is MODEL-AGNOSTIC teaching - doesn't rely on model weights or special training, works for any agent that can process context!**

---

*Ready to implement! Start with Phase 0, TDD all the way through. Each phase validates before moving forward.*
