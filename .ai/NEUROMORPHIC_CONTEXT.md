# Neuromorphic Context Management

> **Status:** Research & Design Phase  
> **Goal:** Replace batch summarization with continuous gradient degradation  
> **Foundation:** Biomimetic Phases 1-4 (memory decay, habituation, prediction error, attention)

## Problem Statement

**Current limitation:** Conversation context hits token limits → batch summarization → jarring transition, lost nuance

**Desired behavior:** Smooth, continuous context management mimicking human memory gradient

## Neuroscience Foundation

### Dual-Process Architecture

**Fast System (Working Memory):**
- Prefrontal cortex: 4-7 chunks, high-resolution
- Fades in seconds-minutes without rehearsal
- → Last 5-10 turns verbatim

**Slow System (Consolidation):**
- Hippocampus: Continuous replay & compression
- Happens during offline processing + ongoing
- Takes hours-days to fully consolidate
- → Background summarization of aging context

### Continuous Degradation Mechanism

Brain doesn't batch summarize - uses **continuous temporal gradient**:

1. **Every ~200ms:** Working memory refresh (attention filter)
2. **Every few seconds:** Hippocampal sampling
3. **Every ~10 minutes:** Compression begins (forgetting curve)
4. **During downtime:** Major consolidation

**Key insight:** Strong synapses (important) stay strong, weak synapses (noise) gradually weaken

### Multi-Signal Importance

What gets kept vs compressed:

- **Emotional salience** → Keep detailed (amygdala)
- **Novelty/surprise** → Keep detailed (dopamine) ← `prediction_error.py`
- **Repeated patterns** → Compress (habituation) ← `context_habituation.py`
- **Recency** → More detailed (temporal gradient) ← `memory_decay.py`

## Current State

**Ada's existing assets:**

```python
# Already implemented (Phases 1-4):
- context_cache.py           # Multi-timescale caching (24hr personas, 5min memories)
- memory_decay.py            # Exponential decay with temperature modulation
- context_habituation.py     # Reduces weight of repeated patterns
- attention_spotlight.py     # Prioritizes recent + relevant
- prediction_error.py        # Boosts surprising/novel content
- semantic_chunking.py       # Breaks context into semantic units
- processing_modes.py        # ANALYTICAL/CREATIVE/CONVERSATIONAL modes

# RAG retrieval:
- Vector search (ChromaDB)   # Associative memory (similarity-based)
- k=10 recent turns          # Simple temporal window
```

**What's missing:** Continuous importance-based gradient, hybrid retrieval, background consolidation

## Solution Architecture

### Importance Scoring System

```python
def calculate_importance(turn, query, temperature=1.0):
    """
    Multi-signal importance (like brain's relevance signals).
    
    Returns 0.0-1.0 importance score.
    """
    age = calculate_age(turn)
    
    # Multiple relevance signals
    decay_score = memory_decay.calculate(age)           # Recency (0.4 weight)
    surprise_score = prediction_error.calculate(turn)   # Novelty (0.3 weight)
    semantic_relevance = vector_similarity(turn, query) # Relevance (0.2 weight)
    habituation_penalty = context_habituation.check(turn) # Uniqueness (0.1 weight)
    
    # Combined importance with temperature modulation
    importance = (
        decay_score * 0.4 +
        surprise_score * 0.3 +
        semantic_relevance * 0.2 +
        (1 - habituation_penalty) * 0.1
    ) * temperature
    
    return importance
```

### Gradient Detail Levels

Three levels of context representation:

```
FULL (1.0 tokens):     Complete turn text, verbatim
CHUNKS (0.3 tokens):   Semantic chunks only (key points)
SUMMARY (0.1 tokens):  Single-sentence summary
DROPPED (0.0 tokens):  Omitted entirely (forgotten)
```

**Decision thresholds:**

```python
# Working memory (always full detail)
if age <= 5:
    detail_level = FULL

# Importance-based gradient
elif importance > 0.7:
    detail_level = FULL      # High importance - keep verbatim
elif importance > 0.4:
    detail_level = CHUNKS    # Medium - semantic chunks
elif importance > 0.2:
    detail_level = SUMMARY   # Low - compressed
else:
    detail_level = DROPPED   # Forgotten
```

### Background Consolidation

Mimics hippocampal replay - runs periodically:

```python
def consolidate_aging_turns(conversation_id):
    """
    Pre-compute summaries/chunks for turns transitioning to long-term.
    
    Run every ~10 turns (like hippocampal replay).
    """
    # Turns in transition zone (age 5-20)
    turns = get_turns_between_ages(min_age=5, max_age=20)
    
    for turn in turns:
        importance = calculate_importance(turn)
        
        if importance > 0.2:  # Worth keeping
            # Pre-compute semantic chunks
            if not turn.has_chunks:
                turn.chunks = semantic_chunking.process(turn)
            
            # Pre-compute summary
            if not turn.has_summary:
                turn.summary = llm.summarize(turn.text)
            
            # Store back to ChromaDB
            rag_store.update_turn(turn)
```

### Replay Mechanism

Strengthens important patterns (like LTP in brain):

```python
def replay_consolidation(conversation_id):
    """
    Extract themes, boost importance of matching turns.
    
    Mimics how sleep strengthens relevant memories.
    """
    recent_turns = get_recent_turns(k=10)
    
    # Extract key topics/decisions
    themes = llm.extract_themes(recent_turns)
    
    # Boost turns that match themes
    for turn in recent_turns:
        if matches_theme(turn, themes):
            turn.importance_boost += 0.2  # Reinforcement
            rag_store.update_turn(turn)
```

## GraphRAG Integration

### The Two Memory Systems

**Associative (Current - Vector Search):**
- Similarity-based, fuzzy matching
- Mediated by hippocampus + cortex
- "This reminds me of..."
- Good for: Themes, analogies, vibes

**Relational (GraphRAG):**
- Causal chains, structured relationships
- Mediated by prefrontal cortex
- "This led to that"
- Good for: Reasoning chains, project context

**Brain uses BOTH systems!** So should Ada.

### Graph Structure

**Nodes:**
- Conversation turns (temporal)
- Topics/entities (semantic)
- Code files/functions (technical)
- Decisions/solutions (pragmatic)

**Edges with temporal decay:**

```python
class TemporalEdge:
    source: Node
    target: Node
    type: EdgeType  # CAUSED_BY, SOLVED_BY, RELATES_TO, FOLLOWED_BY, etc.
    timestamp: datetime
    strength: float  # 0.0-1.0, decays over time
    reinforcement_count: int  # How many times traversed
    
def apply_edge_decay(edge):
    """Edges decay like synaptic connections!"""
    age_hours = (now() - edge.timestamp).hours
    
    # Same decay formula as memory_decay.py
    decay_score = memory_decay.calculate(age_hours)
    
    # Stronger edges (reinforced) decay slower
    reinforcement_factor = min(edge.reinforcement_count / 10, 1.0)
    
    edge.strength = decay_score * (0.5 + 0.5 * reinforcement_factor)
```

### Hybrid Retrieval Strategy

Blend vector + graph with biomimetic weighting:

```python
def retrieve_context(query, conversation_id, mode='balanced'):
    """
    Combine associative (vector) and relational (graph) retrieval.
    
    mode: 'balanced', 'exploratory' (favor vector), 'analytical' (favor graph)
    """
    # 1. Associative retrieval
    vector_results = vector_search(query, k=20)
    
    # 2. Relational retrieval
    graph_results = graph_search(query, conversation_id)
    
    # 3. Apply biomimetic weighting to BOTH
    for result in vector_results:
        result.importance = calculate_importance(result)
        result.score = result.similarity * result.importance
    
    for result in graph_results:
        result.importance = calculate_importance(result)
        result.score = result.graph_relevance * result.importance
    
    # 4. Adaptive blending based on mode
    if mode == 'exploratory':  # CREATIVE mode
        vector_weight, graph_weight = 0.7, 0.3
    elif mode == 'analytical':  # ANALYTICAL mode
        vector_weight, graph_weight = 0.3, 0.7
    else:  # CONVERSATIONAL mode
        vector_weight, graph_weight = 0.5, 0.5
    
    # 5. Merge and sort by weighted importance
    return blend_results(vector_results, graph_results, weights)
```

## Implementation Phases

### Phase 1: Importance-Based Gradient (Foundation)

**Goal:** Add importance scoring and gradient detail levels

**Changes:**
- Add `calculate_importance()` to context_retriever
- Implement FULL/CHUNKS/SUMMARY detail levels
- Use importance thresholds to decide detail level
- Keep token budget constant initially

**Tests:**
- TDD: Test importance scoring with known scenarios
- Validate high-importance turns get FULL detail
- Validate low-importance turns get SUMMARY/DROPPED

**Success metric:** Important context kept, noise compressed

### Phase 2: Background Consolidation

**Goal:** Pre-compute summaries/chunks for aging turns

**Changes:**
- Add `consolidate_aging_turns()` background task
- Run every ~10 turns or periodically
- Store chunks/summaries in ChromaDB metadata
- Add replay mechanism for theme extraction

**Tests:**
- Verify summaries generated correctly
- Test semantic chunking quality
- Validate consolidation timing

**Success metric:** No lag when assembling context (pre-computed)

### Phase 3: Lightweight Graph Layer

**Goal:** Test graph concept with minimal implementation

**Changes:**
- Track temporal edges (FOLLOWED_BY)
- Track topic edges (MENTIONS entity)
- Simple graph traversal for context chains
- Apply decay to edge weights

**Tests:**
- Verify conversation flow captured
- Test edge decay over time
- Validate context chain retrieval

**Success metric:** Graph provides useful context beyond vector search

### Phase 4: Full GraphRAG

**Goal:** Rich entity/relationship extraction

**Changes:**
- LLM-based entity extraction
- Relationship extraction (CAUSED_BY, SOLVED_BY, etc.)
- Subgraph retrieval with importance weighting
- Hybrid vector+graph retrieval

**Tests:**
- Entity extraction accuracy
- Relationship quality
- Hybrid retrieval relevance

**Success metric:** Graph reasoning chains improve complex queries

### Phase 5: Adaptive Retrieval

**Goal:** Tune vector/graph balance based on query type

**Changes:**
- Integrate with ProcessingMode system
- CREATIVE → favor vector (associative)
- ANALYTICAL → favor graph (relational)
- Query analysis to auto-detect mode

**Tests:**
- Mode detection accuracy
- Retrieval quality per mode
- User preference validation

**Success metric:** Context adapts intelligently to query type

## Configuration Knobs

**Temporal parameters:**
```python
WORKING_MEMORY_SIZE = 5          # Turns kept verbatim (0.4-2.0 optimal range)
SHORT_TERM_WINDOW = 20           # Decay starts (10-50 optimal)
CONSOLIDATION_FREQUENCY = 10     # Turns between background runs (5-20 optimal)
```

**Importance thresholds:**
```python
FULL_DETAIL_THRESHOLD = 0.7      # Keep verbatim above this
CHUNKS_THRESHOLD = 0.4           # Semantic chunks above this
SUMMARY_THRESHOLD = 0.2          # Summary above this, drop below
```

**Signal weights:**
```python
DECAY_WEIGHT = 0.4               # Recency importance
SURPRISE_WEIGHT = 0.3            # Novelty importance
RELEVANCE_WEIGHT = 0.2           # Query similarity importance
HABITUATION_WEIGHT = 0.1         # Uniqueness importance
```

**Graph parameters:**
```python
VECTOR_GRAPH_BALANCE = 0.5       # 0.0=pure vector, 1.0=pure graph
EDGE_DECAY_RATE = 0.05          # How fast edges weaken
REINFORCEMENT_THRESHOLD = 3      # Traversals before edge strengthens
```

**Temperature modulation:**
```python
BASE_TEMPERATURE = 1.0           # Default detail level
ANALYTICAL_TEMP = 1.3            # More detail for complex queries
CREATIVE_TEMP = 0.8              # Less detail for exploratory queries
```

## Research Notes

### Novel Contribution

**Temporal graph decay with biomimetic weighting is unexplored territory.**

Existing GraphRAG implementations use static graphs. Ada's approach:
- Edges decay over time (synaptic weakening)
- Reinforcement strengthens edges (LTP mechanism)
- Multi-signal importance applies to both vector and graph results
- Processing mode modulates retrieval strategy

**Potential publication:** "Neuromorphic Knowledge Graphs: Applying Biological Memory Dynamics to Graph Retrieval"

### Key Insights

1. **No cliff edge:** Importance degrades smoothly, no batch summarization
2. **Multiple signals:** Like brain - decay + surprise + relevance + habituation
3. **Background processing:** Consolidation happens continuously
4. **Temperature modulation:** Can keep more detail when "excited" (debugging)
5. **Dual retrieval:** Associative (vector) + relational (graph) = complete

### Open Questions

- **Optimal thresholds:** What importance values work best for FULL/CHUNKS/SUMMARY?
- **Consolidation frequency:** How often to run background replay?
- **Graph density:** How many edges before performance degrades?
- **Edge type utility:** Which relationship types provide most value?
- **Mode detection:** Can we auto-detect query type reliably?

### Future Directions

**Phase 6+:**
- Cross-conversation graph links (shared entities across sessions)
- Meta-learning optimal parameters per user
- Emotional salience signals (sentiment analysis)
- Working memory capacity adaptation (dynamic WORKING_MEMORY_SIZE)
- Predictive pre-fetching (anticipate next query needs)

## References

**Biological memory systems:**
- Eichenbaum (2017) - Hippocampal-cortical interactions
- Stickgold & Walker (2013) - Sleep consolidation mechanisms
- Fusi et al. (2005) - Cascade models of synaptic plasticity

**GraphRAG implementations:**
- Microsoft GraphRAG (2024)
- LlamaIndex Knowledge Graphs
- Neo4j + Vector Search hybrid approaches

**Ada's biomimetic features:**
- `.ai/PHASE2_BIOMIMETIC.md` - Implementation details
- `docs/biomimetic_features.rst` - User-facing documentation
- `docs/memory_augmentation.rst` - Research background

## Ecosystem & Collaboration

### Spiritual Kin Projects

**Ink & Switch (inkandswitch.com)** - PRIMARY INSPIRATION
- Local-first software manifesto aligns perfectly with Ada
- Research through making (Automerge, Pushpin, Cambria)
- Beautiful documentation style (visual essays, research notebooks)
- Philosophy: Own your data, work offline, collaborate without servers
- **Synergy:** They do collaboration, Ada does memory/AI
- **Potential:** Biomimetic CRDTs, distributed memory sync, local-first AI infrastructure
- **Action:** Read "Local-First Software" essay, follow research notes

**PrivateGPT (github.com/imartinez/privateGPT)**
- 100% local document Q&A
- Shares privacy-first philosophy
- Different focus (documents vs conversational memory)

**LocalAI, Ollama**
- Local LLM infrastructure (Ada uses Ollama!)
- Pragmatic, hackable tools
- Complementary to Ada's memory research

### Projects Doing Similar Things (But Not Quite)

**Neuromorphic Systems:**
- Nengo - Spiking neural networks (academic, simulation)
- SpiNNaker - Hardware brain simulation (university research)
- Intel Loihi - Chip-level neuromorphic (corporate, closed)
- **Gap:** None doing biomimetic LLM memory systems in production

**RAG Systems:**
- LangChain, LlamaIndex, Haystack - Modular RAG frameworks
- **Gap:** No temporal decay, no biomimetic weighting, static graphs

**Memory/PKM:**
- Roam Research, Obsidian, Memex projects
- **Gap:** Not AI-native, no neuromorphic principles

### Ada's Unique Position

**First to combine:**
- ✅ Biomimetic memory (decay, habituation, prediction error) in production LLM
- ✅ Temporal graph decay (unexplored research territory)
- ✅ Privacy-first + social (Matrix bridge)
- ✅ Local-first + neuromorphic + working code
- ✅ CCRU vibes + pragmatic engineering

**OpenCollective Opportunity:**
- Research in public (document experiments, share insights)
- Hackable infrastructure (plugin system, exposed knobs)
- Novel territory (temporal graph decay, neuromorphic RAG)
- Funding pitch: "The only AI system that forgets like a brain"

### Potential Collaborations

**Research Papers:**
- "Temporal Knowledge Graphs with Synaptic Decay"
- "Neuromorphic RAG: Beyond Static Context"
- "Local-First AI Memory Systems" (with Ink & Switch?)
- "Biomimetic CRDTs: Data Structures That Forget"

**Technical Integration:**
- Automerge (CRDT) + Ada → Multi-device memory sync
- Neovim/Obsidian plugins → PKM integration
- Matrix ecosystem → Federated AI memory

**Community:**
- Local-First Software community (localfirstweb.dev)
- Biomimetic AI working group (new?)
- Context management meetups
- Memory researchers collaboration

### Alignment with "Seven Ideals" (Ink & Switch)

| Local-First Ideal | Ada Implementation |
|-------------------|-------------------|
| Fast (no server) | Local LLM, no API calls |
| Multi-device | Matrix bridge (multi-interface), MCP (multiple editors) |
| Offline | Fully offline-capable |
| Collaboration | Social (Matrix) with privacy preservation |
| Longevity | Local storage, no cloud dependency |
| Privacy | Core value, no telemetry |
| User control | Hackable, exposed configuration knobs |

### Strategic Position

**Ada as "Ink & Switch for AI Systems"**
- Small, focused research project
- Working code + beautiful documentation
- Open process, research in public
- Infrastructure, not just apps
- Philosophy meets practice

**Next Steps:**
- Study Ink & Switch's research methodology
- Document Ada's research process publicly
- Reach out to local-first community
- Consider OpenCollective structure
- Publish temporal graph decay research

---

**Last Updated:** 2025-12-17  
**Next Steps:** Implement Phase 1 (TDD approach), engage with local-first community  
**Status:** Ready for prototyping + community building 🚀
