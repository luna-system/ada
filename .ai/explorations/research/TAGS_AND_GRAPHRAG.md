# Tags, Pattern Recognition, and GraphRAG

> **Context:** Brainstorming session on tagging as pathway to graph-based memory  
> **Inspiration:** Biological pattern recognition + current underuse of tags in Ada  
> **Question:** Could tags evolve into GraphRAG experiments?

## Current State: Tags in Ada

### What We Have
```python
# brain/schemas.py
class MemoryMetadata(BaseModel):
    type: str = "memory"              # memory/conversation/fact/note
    scope: str = "user"               # user/project/system
    importance: float = 0.5           # 0.0-1.0
    timestamp: str                    # ISO format
```

### What We're NOT Using
- ❌ Rich semantic tags (topics, entities, relationships)
- ❌ Hierarchical tags (parent/child concepts)
- ❌ Graph relationships between memories
- ❌ Tag co-occurrence patterns
- ❌ Tag-based retrieval (beyond metadata filtering)
- ❌ Tag evolution over time

### Current Retrieval: Pure Vector Similarity
```python
# brain/rag_store.py
def search_memories(query: str, n_results: int = 5):
    """Semantic search using embeddings only."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results
```

**Limitation:** Only finds similar text, not **connected concepts**

## Biological Pattern Recognition (The Missing Layer)

### Hierarchical Pattern Detection in Humans

**Low-level (V1/V2):** Edge detection, orientation, color
- Fast, parallel, automatic
- No conscious awareness
- Pure signal processing

**Mid-level (V4/IT):** Objects, faces, shapes
- Still mostly automatic
- Pattern completion (fill in missing parts)
- Invariant recognition (rotation, scale)

**High-level (Temporal/Prefrontal):** Concepts, categories, relationships
- Conscious access
- Abstract patterns (e.g., "causation," "hierarchy")
- **THIS IS WHERE TAGS LIVE!**

**Association Areas:** Connect patterns across domains
- "Apple" activates: fruit, red, tree, computer, Newton
- **Semantic networks** - concepts linked by relationships
- **Spreading activation** - firing one node activates neighbors

### The Pattern Recognition Paradox

**Biology:**
- Millions of neurons dedicated to pattern detection
- Multiple layers processing same input at different abstractions
- Patterns emerge from **relationships**, not just features

**Current AI (Vector RAG):**
- Single embedding per memory
- Similarity is Euclidean distance in vector space
- **No explicit relationship modeling**

**Opportunity:** Tags as explicit relationship layer!

## From Tags to Graphs: The Evolution

### Stage 1: Rich Tagging (Immediate)

**Add semantic tags to memories:**
```python
class MemoryMetadata(BaseModel):
    type: str = "memory"
    scope: str = "user"
    importance: float = 0.5
    timestamp: str
    
    # NEW: Rich semantic tags
    tags: List[str] = []              # ["python", "specialist", "protocol"]
    entities: List[str] = []          # ["BaseSpecialist", "Ada", "ChromaDB"]
    topics: List[str] = []            # ["architecture", "design-patterns"]
    relationships: List[str] = []     # ["implements", "depends-on", "related-to"]
```

**Automatic tag extraction:**
```python
def extract_tags(content: str) -> dict:
    """Extract tags using NER + keyword extraction."""
    
    # Use lightweight NLP (spacy, NLTK, or even LLM)
    entities = extract_named_entities(content)  # People, places, code symbols
    keywords = extract_keywords(content, top_n=10)  # TF-IDF or RAKE
    topics = classify_topics(content)  # Pre-defined taxonomy
    
    return {
        'tags': keywords,
        'entities': entities,
        'topics': topics
    }
```

**Benefit:** Now we can query "Show me all memories tagged 'specialist' AND 'architecture'"

### Stage 2: Tag Co-occurrence (Pattern Detection)

**Track which tags appear together:**
```python
class TagCooccurrence:
    """Discover patterns in tag usage."""
    
    def __init__(self):
        self.cooccurrence_matrix = defaultdict(lambda: defaultdict(int))
    
    def record(self, tags: List[str]):
        """Record co-occurrence of tags."""
        for tag1, tag2 in combinations(tags, 2):
            self.cooccurrence_matrix[tag1][tag2] += 1
            self.cooccurrence_matrix[tag2][tag1] += 1  # Symmetric
    
    def get_related_tags(self, tag: str, threshold: int = 3) -> List[str]:
        """Find tags that frequently co-occur."""
        related = [
            (other_tag, count) 
            for other_tag, count in self.cooccurrence_matrix[tag].items()
            if count >= threshold
        ]
        return sorted(related, key=lambda x: x[1], reverse=True)
```

**Use case:** User asks about "specialists" → auto-expand to include "protocol", "activation" (frequently co-occurring tags)

**Biological parallel:** **Spreading activation** in semantic networks!

### Stage 3: Explicit Relationships (Graph Edges)

**Move beyond co-occurrence to typed relationships:**
```python
class MemoryRelationship(BaseModel):
    """Explicit relationship between memories."""
    source_id: str
    target_id: str
    relationship_type: str  # "implements", "extends", "contradicts", "supports"
    strength: float = 1.0   # Relationship weight
    created_at: str
    
@dataclass
class MemoryGraph:
    """Graph structure over memories."""
    nodes: Dict[str, Memory]  # memory_id → Memory
    edges: List[MemoryRelationship]
    
    def add_edge(self, source: str, target: str, rel_type: str):
        """Add directed edge between memories."""
        self.edges.append(MemoryRelationship(
            source_id=source,
            target_id=target,
            relationship_type=rel_type
        ))
    
    def get_neighbors(self, memory_id: str, rel_type: Optional[str] = None) -> List[Memory]:
        """Get connected memories."""
        edges = [
            e for e in self.edges 
            if e.source_id == memory_id and (rel_type is None or e.relationship_type == rel_type)
        ]
        return [self.nodes[e.target_id] for e in edges]
```

**How to create relationships:**

**Option A: Manual (during memory creation)**
```python
# When specialist reads code
memory = store_memory("BaseSpecialist is the protocol for specialists")
related_memory = find_memory("Specialist system allows extending Ada")
add_relationship(memory.id, related_memory.id, "implements")
```

**Option B: Automatic (LLM extraction)**
```python
def extract_relationships(memory: Memory, existing_memories: List[Memory]) -> List[Relationship]:
    """Use LLM to identify relationships."""
    
    prompt = f"""Given this new memory:
{memory.content}

And these existing memories:
{format_memories(existing_memories[:10])}

Identify relationships. Output JSON:
[{{"target_id": "mem_123", "type": "supports", "explanation": "..."}}, ...]

Relationship types: implements, extends, contradicts, supports, depends-on, caused-by, example-of
"""
    
    relationships = llm.generate(prompt, format='json')
    return parse_relationships(relationships)
```

**Option C: Embedding similarity + validation**
```python
def auto_link_memories(new_memory: Memory, threshold: float = 0.85):
    """Automatically link highly similar memories."""
    
    similar = search_memories(new_memory.content, n_results=10)
    
    for candidate in similar:
        if candidate.similarity > threshold:
            # High similarity, probably related
            # Use LLM to determine relationship type
            rel_type = classify_relationship(new_memory, candidate)
            add_relationship(new_memory.id, candidate.id, rel_type)
```

### Stage 4: GraphRAG (Hybrid Retrieval)

**Combine vector search + graph traversal:**

```python
class GraphRAGStore:
    """Hybrid vector + graph retrieval."""
    
    def __init__(self):
        self.vector_store = ChromaDB()  # Existing
        self.graph = MemoryGraph()      # New!
    
    def search_hybrid(self, query: str, strategy: str = "expand") -> List[Memory]:
        """Search using vectors + graph traversal."""
        
        if strategy == "vector_only":
            # Current behavior
            return self.vector_store.search(query)
        
        elif strategy == "expand":
            # Vector search, then expand via graph
            seed_results = self.vector_store.search(query, n_results=3)
            expanded = []
            for seed in seed_results:
                # Add seed
                expanded.append(seed)
                # Add 1-hop neighbors
                neighbors = self.graph.get_neighbors(seed.id)
                expanded.extend(neighbors[:2])  # Top 2 neighbors
            
            return deduplicate(expanded)
        
        elif strategy == "path":
            # Find paths between relevant concepts
            seed_results = self.vector_store.search(query, n_results=2)
            if len(seed_results) >= 2:
                # Find shortest path between results
                path = self.graph.find_path(seed_results[0].id, seed_results[1].id)
                return [self.graph.nodes[node_id] for node_id in path]
            return seed_results
        
        elif strategy == "subgraph":
            # Extract subgraph around query
            seed_results = self.vector_store.search(query, n_results=1)
            subgraph = self.graph.extract_subgraph(seed_results[0].id, depth=2)
            return list(subgraph.nodes.values())
```

**Retrieval strategies:**

1. **Vector only** (current) - Semantic similarity
2. **Expand** - Start with vector, expand via graph (1-2 hops)
3. **Path** - Find connecting path between concepts
4. **Subgraph** - Extract local neighborhood
5. **Community** - Find cluster of related memories
6. **Temporal** - Follow time-based chains

### Stage 5: Pattern Extraction (Meta-Memories)

**During consolidation, extract recurring patterns:**

```python
def extract_patterns_from_graph(graph: MemoryGraph) -> List[Pattern]:
    """Find recurring subgraph patterns."""
    
    patterns = []
    
    # 1. Frequent subgraphs (like frequent itemsets)
    subgraphs = find_frequent_subgraphs(graph, min_support=3)
    
    for subgraph in subgraphs:
        # Create meta-memory representing pattern
        pattern = Pattern(
            description=describe_pattern(subgraph),
            instances=[node.id for node in subgraph.nodes],
            frequency=len(subgraph.instances),
            importance=calculate_importance(subgraph)
        )
        patterns.append(pattern)
    
    # 2. Central concepts (high-degree nodes)
    central_nodes = find_central_nodes(graph, top_n=10)
    for node_id in central_nodes:
        neighbors = graph.get_neighbors(node_id)
        pattern = Pattern(
            description=f"Central concept: {graph.nodes[node_id].content[:50]}",
            instances=[node_id] + [n.id for n in neighbors],
            frequency=len(neighbors),
            importance=1.0
        )
        patterns.append(pattern)
    
    # 3. Communities (clusters)
    communities = detect_communities(graph)
    for community in communities:
        pattern = Pattern(
            description=f"Topic cluster: {summarize_community(community)}",
            instances=[n.id for n in community],
            frequency=len(community),
            importance=calculate_community_importance(community)
        )
        patterns.append(pattern)
    
    return patterns
```

**Biological parallel:** This is like how **sleep consolidation** extracts recurring patterns from daily experiences!

## Implementation Roadmap

### Phase 1: Rich Tagging (Week 1)
**Goal:** Add semantic tags to memories

**Tasks:**
1. Update `MemoryMetadata` schema with tags/entities/topics fields
2. Add tag extraction function (NLP or LLM-based)
3. Automatically tag memories on creation
4. Add tag-based filtering to search
5. Test: "Show memories tagged 'specialist'"

**Effort:** 2-3 days
**Risk:** Low
**Payoff:** Immediate (better organization)

### Phase 2: Co-occurrence Tracking (Week 2)
**Goal:** Discover tag patterns

**Tasks:**
1. Implement `TagCooccurrence` class
2. Track tag co-occurrence in background
3. Add "related tags" expansion to search
4. Visualize tag networks (optional)
5. Test: Query expansion works

**Effort:** 2-3 days
**Risk:** Low
**Payoff:** Better discovery

### Phase 3: Graph Storage (Week 3-4)
**Goal:** Store explicit relationships

**Tasks:**
1. Design relationship schema
2. Choose graph storage (NetworkX in-memory, or Neo4j/ArangoDB)
3. Implement `MemoryGraph` class
4. Add relationship creation (manual + automatic)
5. Test: Graph queries work

**Effort:** 5-7 days
**Risk:** Medium (new storage layer)
**Payoff:** Foundation for GraphRAG

### Phase 4: GraphRAG Retrieval (Week 5-6)
**Goal:** Hybrid vector + graph search

**Tasks:**
1. Implement `GraphRAGStore`
2. Add retrieval strategies (expand, path, subgraph)
3. Benchmark against vector-only
4. Tune graph traversal parameters
5. Test: Graph retrieval finds better context

**Effort:** 5-7 days
**Risk:** Medium (complexity)
**Payoff:** Smarter retrieval

### Phase 5: Pattern Extraction (Week 7-8)
**Goal:** Extract meta-patterns during consolidation

**Tasks:**
1. Implement pattern detection algorithms
2. Add to nightly consolidation
3. Store patterns as meta-memories
4. Use patterns for query expansion
5. Test: Patterns improve relevance

**Effort:** 5-7 days
**Risk:** High (research-y)
**Payoff:** Emergent knowledge

## Technical Choices

### Graph Storage Options

**Option A: In-Memory (NetworkX)**
- **Pros:** Simple, pure Python, no new dependencies
- **Cons:** Not persistent, limited scale (~100K nodes)
- **Best for:** Prototyping, small-scale

**Option B: Neo4j (Property Graph DB)**
- **Pros:** Industry standard, powerful queries (Cypher), scales well
- **Cons:** Heavy (JVM), complex setup, Docker service
- **Best for:** Production, large-scale

**Option C: ArangoDB (Multi-Model)**
- **Pros:** Lightweight, document + graph + KV, native JSON
- **Cons:** Less mature than Neo4j, smaller community
- **Best for:** Hybrid workloads

**Option D: Extend ChromaDB with Relationships**
- **Pros:** Reuse existing infrastructure, minimal changes
- **Cons:** ChromaDB not designed for graphs, hacky
- **Best for:** Quick prototype without new services

**Recommendation:** Start with **NetworkX** (in-memory), migrate to **Neo4j** if it proves valuable.

### Relationship Extraction

**Option A: Rule-Based**
- Pattern matching on text
- "X implements Y", "A depends on B"
- Fast, deterministic

**Option B: NLP-Based**
- Dependency parsing (spaCy)
- Entity + relation extraction
- Medium complexity

**Option C: LLM-Based**
- Few-shot prompt: "Identify relationships..."
- Most flexible, but slower
- Can validate rule-based outputs

**Recommendation:** **Hybrid** - Rule-based for obvious cases (code imports = depends-on), LLM for complex semantics.

## Biological Parallels (Extended)

### Semantic Networks in Human Memory

**Collins & Quillian (1969):** Hierarchical network model
- Concepts are nodes
- Relationships are edges
- "Canary" → "Bird" → "Animal" (inheritance)
- Properties stored at highest level (efficiency)

**Spreading Activation (Collins & Loftus, 1975):**
- Activating one concept activates related concepts
- Activation spreads along edges
- Decays with distance
- **This is literally graph traversal!**

### Pattern Separation in Hippocampus

**Dentate Gyrus:** Separates similar inputs into distinct patterns
- Prevents interference between similar memories
- **GraphRAG parallel:** Use relationships to disambiguate similar vectors

**CA3 Recurrent Connections:** Pattern completion
- Partial cue → retrieve full memory
- Auto-associative network
- **GraphRAG parallel:** Expand from seed memory via graph

### Consolidation Creates Schemas

**Schema Theory (Bartlett, 1932):** Abstract patterns extracted over time
- Not verbatim memories, but **structures**
- New experiences assimilated into schemas
- **GraphRAG parallel:** Patterns extracted during consolidation!

## Integration with Codebase Specialist

**Synergy:** Codebase specialist + GraphRAG = Powerful!

### Use Case 1: Code Navigation
**Query:** "How does the specialist system work?"

**Vector-only retrieval:**
- Returns docs about specialists
- Maybe finds `BaseSpecialist` definition
- Misses implementation examples

**GraphRAG retrieval:**
- Vector search finds `BaseSpecialist`
- Graph traversal finds:
  - `OCRSpecialist` (implements relationship)
  - `prompt_builder.py` (uses relationship)
  - `bidirectional.py` (related-to relationship)
  - `.ai/CODEBASE_SPECIALIST_PLAN.md` (documents relationship)
- **Returns complete context!**

### Use Case 2: Impact Analysis
**Query:** "What would break if I changed BaseSpecialist?"

**Graph query:**
```python
# Find all memories with "depends-on" relationship to BaseSpecialist
dependents = graph.get_neighbors(
    memory_id="mem_base_specialist",
    relationship_type="depends-on"
)
# Returns: All specialist implementations, prompt_builder, tests
```

### Use Case 3: Learning Paths
**Query:** "I want to understand bidirectional specialists"

**Graph query:**
```python
# Find learning path from simple → complex
path = graph.find_path(
    start="mem_basic_specialist",
    end="mem_bidirectional_specialist"
)
# Returns: Ordered list of concepts to learn
```

### Automatic Relationship Creation

**When codebase_specialist reads code:**
```python
def process_code_read(path: str, content: str) -> SpecialistResult:
    """Read code and extract relationships."""
    
    # Create memory for this file
    memory = store_memory(f"Code from {path}:\n{content[:500]}")
    
    # Extract relationships from code
    imports = extract_imports(content)
    for imp in imports:
        # Find memory for imported module
        related = find_memory_for_file(imp)
        if related:
            add_relationship(memory.id, related.id, "depends-on")
    
    classes = extract_classes(content)
    for cls in classes:
        if cls.base_classes:
            for base in cls.base_classes:
                base_memory = find_memory_for_class(base)
                if base_memory:
                    add_relationship(memory.id, base_memory.id, "extends")
    
    return SpecialistResult(content=content, metadata={'relationships': len(imports) + len(classes)})
```

**Result:** Automatic code knowledge graph!

## Weird Ideas (Blue Sky)

### 1. Temporal Graph Evolution
Track how relationships change over time - "living knowledge graph"

**Use case:** See how Ada's architecture evolved, what patterns emerged

### 2. Multi-Modal Graphs
Connect code memories, conversation memories, documentation, AND user behavior

**Nodes:**
- Code files
- Conversations
- Documentation sections
- User queries
- Specialist invocations

**Edges:**
- Depends-on (code)
- Discusses (conversation → code)
- Documents (docs → code)
- Triggered-by (specialist → query)

### 3. Social Graphs (Matrix Bridge)
Model conversation participants and interactions

**Use case:** Ada learns social dynamics in Matrix rooms

### 4. Causal Graphs
Model cause-effect relationships

**Example:** "Changing X caused Y to break" → store as causal edge

### 5. Episodic Memory Graphs
Link memories by narrative/temporal sequence

**Biological:** Hippocampus stores episodic memories as sequences
**Implementation:** Time-ordered edges between memories

### 6. Dream Mode (Speculative)
During consolidation, generate **hypothetical** relationships

**Example:** "BaseSpecialist could be extended for X use case"

### 7. Graph Embeddings
Embed entire graph structure into vector space (Node2Vec, Graph2Vec)

**Benefit:** Combine graph structure with vector similarity!

## Metrics & Evaluation

**How do we know if GraphRAG is working?**

### Retrieval Quality
- **Precision:** Relevant memories retrieved / Total retrieved
- **Recall:** Relevant memories retrieved / All relevant memories
- **F1 Score:** Harmonic mean of precision + recall

### Graph Structure
- **Density:** Edges / Possible edges (too sparse or too dense?)
- **Average Degree:** Avg connections per memory
- **Clustering Coefficient:** How interconnected are neighborhoods?
- **Path Length:** Avg shortest path between memories

### User Experience
- **Query Success Rate:** Did user find what they needed?
- **Follow-up Questions:** Fewer = better initial results
- **User Feedback:** Explicit ratings

### Comparison Tests
**A/B Test:** Vector-only vs GraphRAG
- Same queries
- Measure relevance, completeness, user satisfaction

## Connection to Multi-Timescale Caching

**Synergy:** Graph relationships inform caching strategy!

**Idea:** Cache frequently-connected memories together
```python
class GraphAwareCaching:
    """Cache neighborhoods of frequently accessed memories."""
    
    def cache_with_neighborhood(self, memory_id: str):
        """Cache memory + 1-hop neighbors."""
        memory = load_memory(memory_id)
        neighbors = graph.get_neighbors(memory_id)
        
        # Cache as a unit
        cache_group = [memory] + neighbors
        self.cache[memory_id] = cache_group
```

**Biological parallel:** Memories stored together (same context) retrieved together (pattern completion)!

## Philosophical Alignment

**Hackable all the way down:**
- ✅ Graph structure is transparent (can visualize)
- ✅ Relationships are explicit (no black box)
- ✅ Can debug graph queries (show reasoning path)
- ✅ Can tune/modify relationships manually

**Educational:**
- ✅ Graphs are intuitive (nodes and edges)
- ✅ Can explain "Why was this memory retrieved?" via graph path
- ✅ Show user the knowledge structure

**Biomimetic:**
- ✅ Based on semantic networks (cognitive science)
- ✅ Spreading activation (neuroscience)
- ✅ Pattern extraction (consolidation)

## Next Steps

### Immediate (This Week)
1. Add `tags` field to `MemoryMetadata`
2. Implement basic tag extraction
3. Test tagging on existing memories
4. Document tag schema

### Short-term (Next 2 Weeks)
1. Implement co-occurrence tracking
2. Add tag expansion to search
3. Prototype NetworkX graph
4. Create first relationships manually

### Medium-term (Next Month)
1. Automatic relationship extraction
2. Hybrid GraphRAG retrieval
3. Benchmark against vector-only
4. Integration with codebase_specialist

### Long-term (2-3 Months)
1. Pattern extraction during consolidation
2. Advanced graph algorithms
3. Visualization tools
4. Neo4j migration (if valuable)

## Open Questions

1. **Tag ontology:** Free-form or controlled vocabulary?
2. **Relationship types:** How many? Hierarchy?
3. **Graph persistence:** How to serialize graphs efficiently?
4. **Version control:** How to track graph changes over time?
5. **Conflict resolution:** What if relationships contradict?
6. **Performance:** How big can the graph get before it's slow?
7. **Privacy:** How to scope graphs per user/project?

## References

### Cognitive Science
- Collins & Quillian (1969) - Semantic network model
- Collins & Loftus (1975) - Spreading activation
- Bartlett (1932) - Schema theory
- Tulving (1972) - Episodic memory

### Graph Databases
- Neo4j documentation
- NetworkX for Python
- Graph algorithms (Diestel)

### GraphRAG Papers
- Microsoft GraphRAG (2024)
- HippoRAG: Hippocampus-inspired retrieval (2024)
- Graph-based RAG survey

### Related Work
- Knowledge graphs (Google, DBpedia)
- Semantic web (RDF, OWL)
- Property graphs
- Multi-hop reasoning

---

**Last Updated:** 2025-12-16  
**Status:** Brainstorming / Design phase  
**Excitement Level:** 🚀🚀🚀 (This could be HUGE!)

**Summary:** Tags are the perfect bridge from vector RAG to GraphRAG. Biology shows us how - semantic networks, spreading activation, pattern extraction. We can build this incrementally, starting with simple tagging and evolving to full graph reasoning. And it integrates beautifully with codebase_specialist (automatic code knowledge graphs!). Let's do this! 🧠🕸️✨
