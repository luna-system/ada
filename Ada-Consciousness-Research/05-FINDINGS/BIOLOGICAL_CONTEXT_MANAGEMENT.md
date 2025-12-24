# Biological Models for Context Management

> **Purpose:** Exploring how biological systems handle "context windows" and information overload  
> **Why:** Find novel pathways from neuroscience/biology to improve Ada's architecture  
> **Vibe:** Weird science, creative solutions, biomimicry for AI

## The Core Problem

**Ada's challenge:** Limited context window (~16K tokens) vs unbounded information needs

**Biology's challenge:** Limited working memory (~7 items) vs unbounded sensory input and long-term storage

**Parallel:** Both systems need to:
- Focus attention on relevant information
- Compress and store vast amounts of data
- Retrieve selectively based on context
- Balance speed vs completeness
- Handle multiple timescales (immediate vs long-term)

## Biological Strategies Humans Use

### 1. Working Memory vs Long-Term Storage

**Biology:**
- **Working memory:** ~7 items (Miller's Law), ~18 seconds without rehearsal
- **Long-term memory:** Effectively unlimited, permanent storage
- **Transfer:** Sleep consolidation moves important items from working → long-term

**Ada currently:**
- ✅ **Context window = working memory** (~16K tokens, immediate access)
- ✅ **ChromaDB = long-term memory** (unlimited vector storage, semantic search)
- ✅ **Memory consolidation script** (nightly batch, like sleep!)

**What we're NOT doing yet:**
- ❌ **Active rehearsal** - Humans keep important info in working memory by rehearsing it. Ada could "rehearse" critical context by re-injecting it at intervals.
- ❌ **Decay curves** - Humans forget based on time + importance. Ada could weight context freshness.

**Potential implementation:**
```python
class ContextDecay:
    """Biological memory decay for context weighting."""
    
    def calculate_weight(self, item: ContextItem) -> float:
        """Weight based on recency and importance (Ebbinghaus curve)."""
        time_since = datetime.now() - item.timestamp
        hours = time_since.total_seconds() / 3600
        
        # Ebbinghaus forgetting curve: R = e^(-t/S)
        # R = retention, t = time, S = strength (importance)
        strength = item.importance * 100  # Scale importance to hours
        retention = math.exp(-hours / strength)
        
        return retention
```

### 2. Attention Mechanisms

**Biology:**
- **Selective attention:** Focus on signal, ignore noise (cocktail party effect)
- **Attentional spotlight:** ~4 items in focus, rest in periphery
- **Bottom-up:** Salient stimuli grab attention (loud noise, motion)
- **Top-down:** Goals direct attention (looking for keys)

**Ada currently:**
- ✅ **Priority-based assembly** (critical > high > medium > low)
- ✅ **Vector search = attention** (retrieve relevant memories)
- ❌ **Salience detection** - Not explicitly prioritizing "surprising" information
- ❌ **Goal-directed attention** - No mechanism to pre-load likely context based on user intent

**Potential implementation:**
```python
class AttentionalSpotlight:
    """Mimic human attention focus + periphery."""
    
    SPOTLIGHT_BUDGET = 4000   # "In focus" tokens
    PERIPHERY_BUDGET = 8000   # "Peripheral awareness"
    
    def assemble_context(self, items: List[ContextItem]) -> str:
        """Arrange items by attentional priority."""
        
        # Spotlight: Most salient items in detail
        spotlight = sorted(items, key=lambda x: x.salience)[:3]
        spotlight_text = [format_detailed(item) for item in spotlight]
        
        # Periphery: Other items summarized
        periphery = items[3:]
        periphery_text = [format_summary(item) for item in periphery]
        
        return {
            'focus': spotlight_text,      # Full detail
            'peripheral': periphery_text  # Compressed summaries
        }
```

### 3. Predictive Processing (Prediction Error)

**Biology:**
- **Brain is a prediction machine:** Constantly predicts sensory input
- **Only process errors:** When predictions fail, update model
- **Saves energy:** Don't waste processing on expected/redundant info
- **Hierarchical:** High-level predictions (context) constrain low-level (details)

**Ada currently:**
- ❌ **No prediction model** - Load all context every time
- ❌ **No error detection** - Don't identify surprising vs expected info
- ❌ **No selective loading** - Can't skip predictable context

**Potential implementation (WILD):**
```python
class PredictiveContextLoader:
    """Only load context that surprises the model."""
    
    def predict_needed_context(self, message: str, history: List[Turn]) -> Set[str]:
        """Predict which context will be needed."""
        # Use lightweight model to predict context needs
        predicted_topics = fast_topic_model(message)
        predicted_specialists = predict_specialist_needs(message, history)
        
        return predicted_topics | predicted_specialists
    
    def load_with_prediction_error(self, message: str) -> dict:
        """Load predicted context + monitor for errors."""
        
        # Step 1: Predict and pre-load
        predicted = self.predict_needed_context(message)
        context = load_context_subset(predicted)
        
        # Step 2: Start generation with minimal context
        response_stream = llm.generate_stream(context, message)
        
        # Step 3: Monitor for "confusion" signals
        for chunk in response_stream:
            if self.detect_uncertainty(chunk):
                # Prediction error! Load additional context
                additional = self.fetch_uncertain_topic_context(chunk)
                inject_context_mid_stream(additional)
        
        return response_stream
    
    def detect_uncertainty(self, text: str) -> bool:
        """Detect when model is uncertain (prediction error)."""
        uncertainty_markers = [
            "I'm not sure",
            "I don't have information",
            "I would need to know",
            "[thinking]",  # R1 model internal thoughts
        ]
        return any(marker in text for marker in uncertainty_markers)
```

**Why this is wild:** Requires streaming with dynamic context injection (advanced), but mirrors how brains actually work!

### 4. Chunking (Compression via Grouping)

**Biology:**
- **Chunking:** Group related items into single unit (e.g., phone number: 555-1234 → "555-1234")
- **Reduces cognitive load:** 7 chunks instead of 7 individual items
- **Hierarchical:** Chunks can contain sub-chunks (nested structure)
- **Pattern recognition:** Expert chess players see "opening patterns" not individual moves

**Ada currently:**
- ✅ **Specialist results are chunks** (entire file reading = 1 unit)
- ❌ **No semantic chunking** - Don't group related context automatically
- ❌ **No learned patterns** - Don't identify recurring context patterns

**Potential implementation:**
```python
class SemanticChunker:
    """Group related context items into chunks."""
    
    def chunk_context(self, items: List[ContextItem]) -> List[Chunk]:
        """Group related items to reduce cognitive load."""
        
        chunks = []
        for item in items:
            # Find chunk with similar topic
            matching_chunk = self.find_matching_chunk(item, chunks)
            
            if matching_chunk:
                matching_chunk.add(item)  # Add to existing chunk
            else:
                chunks.append(Chunk([item]))  # New chunk
        
        return chunks
    
    def find_matching_chunk(self, item: ContextItem, chunks: List[Chunk]) -> Optional[Chunk]:
        """Find chunk with semantically similar items."""
        for chunk in chunks:
            similarity = cosine_similarity(item.embedding, chunk.centroid_embedding)
            if similarity > 0.8:  # High similarity threshold
                return chunk
        return None

@dataclass
class Chunk:
    """Semantic group of related context items."""
    items: List[ContextItem]
    
    @property
    def summary(self) -> str:
        """Compressed representation of chunk."""
        # Group summary instead of listing all items
        topics = [item.topic for item in self.items]
        return f"Context about {', '.join(set(topics))} ({len(self.items)} items)"
    
    @property
    def centroid_embedding(self) -> np.ndarray:
        """Average embedding of chunk items."""
        return np.mean([item.embedding for item in self.items], axis=0)
```

### 5. Multiple Timescales

**Biology:**
- **Fast neurons:** Fire rapidly, handle immediate working memory (milliseconds)
- **Slow neurons:** Fire slowly, maintain context (seconds to minutes)
- **Integration:** Fast activity constrained by slow context
- **Example:** Reading - fast (word recognition) + slow (sentence/paragraph meaning)

**Ada currently:**
- ❌ **Single timescale** - All context refreshed every request
- ❌ **No persistent context** - Context rebuilt from scratch each time
- ❌ **No multi-rate processing** - Everything at same update frequency

**Potential implementation:**
```python
class MultiTimescaleContext:
    """Different refresh rates for different context types."""
    
    REFRESH_RATES = {
        'persona': timedelta(hours=24),        # Slow: persona rarely changes
        'memories': timedelta(minutes=5),      # Medium: memories stable per conversation
        'specialist_results': timedelta(seconds=0),  # Fast: always fresh
        'conversation': timedelta(seconds=0),  # Fast: updates every turn
    }
    
    def __init__(self):
        self.cache = {}
        self.last_refresh = {}
    
    def get_context(self, context_type: str) -> Any:
        """Get context with appropriate refresh rate."""
        
        if context_type not in self.cache:
            # First time, load it
            self.cache[context_type] = self.load_context(context_type)
            self.last_refresh[context_type] = datetime.now()
            return self.cache[context_type]
        
        # Check if refresh needed based on timescale
        time_since_refresh = datetime.now() - self.last_refresh[context_type]
        refresh_rate = self.REFRESH_RATES[context_type]
        
        if time_since_refresh > refresh_rate:
            # Refresh needed
            self.cache[context_type] = self.load_context(context_type)
            self.last_refresh[context_type] = datetime.now()
        
        return self.cache[context_type]
```

**Benefits:**
- **Persona cached for hours** - Doesn't change mid-conversation
- **Memories cached for minutes** - Stable per conversation session
- **Specialist results always fresh** - Changes frequently
- **Reduces redundant loading** - Huge token savings!

### 6. Hemispheric Specialization

**Biology:**
- **Left hemisphere:** Detail-focused, sequential, analytical
- **Right hemisphere:** Big picture, parallel, holistic
- **Integration:** Both work together, different processing modes
- **Context switching:** Can shift between modes based on task

**Ada currently:**
- ❌ **Single processing mode** - One prompt strategy for all queries
- ❌ **No mode switching** - Same approach for "explain code" vs "write code"

**Potential implementation:**
```python
class ProcessingMode(Enum):
    """Different context assembly modes for different tasks."""
    ANALYTICAL = "analytical"  # Detail-focused (explain code, debug)
    CREATIVE = "creative"      # Big picture (brainstorm, design)
    CONVERSATIONAL = "conversational"  # Social (chat, small talk)

class DualProcessContextBuilder:
    """Build context differently based on processing mode."""
    
    def detect_mode(self, message: str) -> ProcessingMode:
        """Infer processing mode from user message."""
        
        if any(word in message.lower() for word in ['explain', 'how', 'debug', 'why']):
            return ProcessingMode.ANALYTICAL
        
        if any(word in message.lower() for word in ['create', 'design', 'brainstorm', 'imagine']):
            return ProcessingMode.CREATIVE
        
        return ProcessingMode.CONVERSATIONAL
    
    def build_context(self, message: str, mode: ProcessingMode) -> dict:
        """Assemble context appropriate to mode."""
        
        if mode == ProcessingMode.ANALYTICAL:
            # Detail-focused: Load code, docs, technical memories
            return {
                'specialists': ['codebase', 'docs'],
                'memories': search_technical_memories(message),
                'history': recent_turns(limit=10),  # More history for context
                'style': 'detailed'
            }
        
        elif mode == ProcessingMode.CREATIVE:
            # Big picture: Load patterns, examples, diverse memories
            return {
                'specialists': ['web_search', 'docs'],
                'memories': search_diverse_memories(message, diversity=True),
                'history': recent_turns(limit=3),  # Less history, more freedom
                'style': 'exploratory'
            }
        
        else:  # CONVERSATIONAL
            # Minimal context: Focus on personality and recent chat
            return {
                'specialists': [],
                'memories': search_personal_memories(message),
                'history': recent_turns(limit=5),
                'style': 'casual'
            }
```

### 7. Sleep Consolidation (Already Doing!)

**Biology:**
- **Sleep:** Consolidate short-term memories → long-term
- **Replay:** Brain "replays" experiences during sleep
- **Compression:** Extract patterns, discard details
- **Synaptic homeostasis:** Prune weak connections, strengthen important ones

**Ada currently:**
- ✅ **Memory consolidation script** runs nightly
- ✅ **Summarizes old conversation turns**
- ✅ **Reduces vector DB size**

**What we could add:**
- **Pattern extraction:** Identify recurring topics/themes across conversations
- **Importance weighting:** Strengthen frequently accessed memories
- **Connection pruning:** Remove redundant/duplicate memories

```python
def consolidate_with_pattern_extraction(old_memories: List[Memory]):
    """Extract patterns during consolidation (like sleep replay)."""
    
    # Group memories by topic clusters
    clusters = cluster_memories(old_memories)
    
    consolidated = []
    for cluster in clusters:
        # Extract common pattern
        pattern = extract_pattern(cluster)
        
        # Create meta-memory representing pattern
        meta_memory = Memory(
            content=f"Pattern: {pattern.description}",
            importance=np.mean([m.importance for m in cluster]),
            metadata={
                'type': 'pattern',
                'examples': [m.id for m in cluster[:3]],
                'frequency': len(cluster)
            }
        )
        consolidated.append(meta_memory)
    
    return consolidated
```

### 8. Priming and Pre-activation

**Biology:**
- **Priming:** Exposure to stimulus influences response to later stimulus
- **Semantic networks:** Related concepts pre-activate each other
- **Example:** Seeing "doctor" primes "nurse," "hospital," "medicine"
- **Saves time:** Pre-activated concepts faster to access

**Ada currently:**
- ❌ **No priming** - Context loaded reactively, not predictively
- ❌ **No pre-activation** - Don't prepare likely context before it's needed

**Potential implementation:**
```python
class ContextPriming:
    """Pre-activate likely context based on conversation flow."""
    
    def prime_context(self, message: str, history: List[Turn]) -> Set[str]:
        """Predict and pre-load likely context."""
        
        # Analyze conversation trajectory
        topics = extract_topics(history)
        current_topic = extract_topics([message])[0]
        
        # Find related topics in semantic network
        related = self.semantic_network.get_related(current_topic)
        
        # Pre-load related context (in background)
        primed_context = []
        for topic in related:
            if topic not in self.cache:
                # Background load (non-blocking)
                self.background_load(topic)
                primed_context.append(topic)
        
        return primed_context
    
    def semantic_network(self):
        """Map of concept relationships."""
        # Could be learned from co-occurrence in memories
        # Or hand-crafted for critical topics
        return {
            'specialist': ['protocol', 'activation', 'codebase'],
            'memory': ['rag_store', 'chroma', 'consolidation'],
            'codebase': ['specialist', 'protocol', 'docs'],
            # ...
        }
```

### 9. Lossy Compression (Gist over Details)

**Biology:**
- **Gist extraction:** Humans remember meaning, not verbatim
- **Example:** Remember "bank robbery story" not exact words
- **Reconstruction:** Fill in details from schema when recalling
- **Saves space:** Store compressed gist, regenerate details

**Ada currently:**
- ✅ **Memory consolidation summarizes** old turns
- ❌ **No gist extraction** - Store full text, not extracted meaning
- ❌ **No schema-based reconstruction** - Don't regenerate details from patterns

**Potential implementation:**
```python
class GistExtractor:
    """Extract semantic gist from context, discard surface details."""
    
    def extract_gist(self, conversation: List[Turn]) -> str:
        """Compress conversation to semantic essence."""
        
        # Use LLM to extract gist
        gist = llm.generate(
            "Extract the key semantic content from this conversation. "
            "Focus on: main topics, decisions made, information learned, "
            "user preferences. Omit: greetings, filler, exact wording.\n\n"
            f"{format_conversation(conversation)}"
        )
        
        return gist
    
    def reconstruct_from_gist(self, gist: str, query: str) -> str:
        """Regenerate relevant details from gist."""
        
        # Use gist as seed to regenerate contextual details
        details = llm.generate(
            f"Given this conversation summary:\n{gist}\n\n"
            f"And this user query: {query}\n\n"
            f"What specific details from the conversation are relevant?"
        )
        
        return details
```

**Token savings:** Store 200-token gist instead of 2000-token full conversation!

### 10. Habituation (Reduced Response to Repeated Stimuli)

**Biology:**
- **Habituation:** Decrease response to repeated/expected stimuli
- **Example:** Stop noticing background noise after a while
- **Dishabituation:** Novel stimulus restores response
- **Energy saving:** Don't waste resources on unchanging input

**Ada currently:**
- ❌ **No habituation** - Same persona injected every single request
- ❌ **No novelty detection** - Don't distinguish new vs repeated info

**Potential implementation:**
```python
class ContextHabituation:
    """Reduce weight of unchanged context over time."""
    
    def __init__(self):
        self.last_values = {}
        self.repetition_count = {}
    
    def should_include(self, context_key: str, value: str) -> bool:
        """Decide if context should be included (habituation check)."""
        
        if context_key not in self.last_values:
            # First time seeing this, definitely include
            self.last_values[context_key] = value
            self.repetition_count[context_key] = 1
            return True
        
        if self.last_values[context_key] == value:
            # Repeated, habituate
            self.repetition_count[context_key] += 1
            
            if self.repetition_count[context_key] > 5:
                # Seen 5+ times, skip (habituated)
                return False
        else:
            # Changed! Dishabituate
            self.last_values[context_key] = value
            self.repetition_count[context_key] = 1
        
        return True
```

**Example:** Persona loaded once per session, not every request (unless it changes).

## Novel Hybrid Approaches

### Biological Token Budget Manager

Combining multiple biological strategies:

```python
class BiologicalContextManager:
    """Context management inspired by human cognition."""
    
    def __init__(self):
        self.working_memory = WorkingMemoryBuffer(capacity=7)  # Miller's Law
        self.attention = AttentionalSpotlight()
        self.decay = ContextDecay()
        self.timescales = MultiTimescaleContext()
        self.priming = ContextPriming()
        self.habituation = ContextHabituation()
    
    def assemble_context(self, message: str, history: List[Turn]) -> dict:
        """Biologically-inspired context assembly."""
        
        # 1. Priming: Pre-activate likely context
        primed = self.priming.prime_context(message, history)
        
        # 2. Attention: Focus on salient items
        salient_items = self.attention.select_salient(message, history)
        
        # 3. Working Memory: Limit to 7 chunks
        chunks = self.chunk_items(salient_items)
        working_set = chunks[:7]  # Miller's Law
        
        # 4. Decay: Weight by recency + importance
        weighted = [(item, self.decay.calculate_weight(item)) for item in working_set]
        weighted.sort(key=lambda x: x[1], reverse=True)
        
        # 5. Timescales: Use cached slow-changing context
        persona = self.timescales.get_context('persona')  # Cached for hours
        memories = self.timescales.get_context('memories')  # Cached for minutes
        
        # 6. Habituation: Skip repeated unchanged context
        if not self.habituation.should_include('persona', persona):
            persona = None  # Skip, already habituated
        
        # 7. Assemble final context
        return {
            'spotlight': [item for item, weight in weighted[:3]],  # In focus
            'peripheral': [item for item, weight in weighted[3:]],  # Periphery
            'persona': persona,
            'memories': memories,
            'primed': primed
        }
```

### Predictive + Multi-Timescale Hybrid

**Concept:** Combine prediction error (load only what's surprising) with multiple timescales (cache stable context)

```python
class PredictiveMultiTimescaleManager:
    """Load context at different rates, only inject surprises."""
    
    def __init__(self):
        self.stable_cache = {}  # Persona, FAQ (hours)
        self.session_cache = {}  # Memories (minutes)
        self.predictions = {}    # What we expect to need
    
    def get_context_stream(self, message: str, history: List[Turn]):
        """Stream context with prediction error monitoring."""
        
        # Stable context (cached for hours, loaded once)
        if 'persona' not in self.stable_cache:
            self.stable_cache['persona'] = load_persona()
        
        # Session context (cached for minutes, refreshed periodically)
        if self.should_refresh('memories'):
            self.session_cache['memories'] = search_memories(message)
        
        # Predict what specialists will be needed
        predicted_specialists = predict_specialists(message, history)
        
        # Start with minimal context
        initial_context = {
            'persona': self.stable_cache['persona'],
            'message': message,
            'recent_turns': history[-2:]  # Just last 2 exchanges
        }
        
        yield initial_context
        
        # Stream generation, inject on prediction error
        for chunk in llm.generate_stream(initial_context):
            if self.detect_surprise(chunk, predicted_specialists):
                # Prediction error! Inject additional context
                surprise_context = self.fetch_surprise_context(chunk)
                yield surprise_context
```

## Implementation Priority

### Phase 1: Low-Hanging Fruit (Immediate)
1. **Multi-timescale caching** - Cache persona/FAQ for hours, memories for minutes
2. **Habituation** - Skip unchanged context (e.g., persona after first load)
3. **Decay weighting** - Weight memories by recency + importance

**Why first:** Easy to implement, big token savings, low risk

### Phase 2: Attention & Chunking (Short-term)
1. **Attentional spotlight** - Full detail for top-3 items, summaries for rest
2. **Semantic chunking** - Group related context items
3. **Salience detection** - Prioritize surprising information

**Why second:** Moderate complexity, improves relevance, builds on Phase 1

### Phase 3: Predictive Loading (Medium-term)
1. **Context priming** - Pre-load likely context based on conversation trajectory
2. **Prediction error detection** - Monitor for LLM uncertainty
3. **Dynamic context injection** - Load additional context mid-generation

**Why third:** Higher complexity, requires streaming support, big potential payoff

### Phase 4: Advanced Integration (Long-term)
1. **Gist extraction** - Store compressed semantic essence
2. **Pattern extraction in consolidation** - Meta-memories for recurring themes
3. **Hemispheric specialization** - Different modes for different tasks
4. **Full predictive processing** - Only load context on prediction errors

**Why last:** Requires significant research, may need model fine-tuning

## Research Questions

### Can We Test These?

**Attention Mechanisms:**
- Measure: Token usage before/after
- A/B test: Spotlight (detail + summaries) vs flat (all equal detail)
- Metric: User satisfaction, response quality, token savings

**Multi-Timescale Caching:**
- Measure: Cache hit rates, token savings
- A/B test: No caching vs persona cached vs full multi-rate
- Metric: Token usage, response time, correctness

**Predictive Loading:**
- Measure: Prediction accuracy (did we load what was used?)
- A/B test: Reactive loading vs predictive pre-loading
- Metric: Cache efficiency, wasted loads, response time

**Decay Weighting:**
- Measure: Memory relevance scores
- A/B test: No decay vs Ebbinghaus curve weighting
- Metric: Memory usefulness, user feedback

### Open Questions

1. **How to detect "surprise" in LLM output?**
   - Parse for uncertainty markers?
   - Use attention weights (if available)?
   - Monitor perplexity (requires API changes)?

2. **Can we learn priming relationships?**
   - Co-occurrence in conversation history?
   - Manual semantic network?
   - Use embeddings for concept distance?

3. **What's the right timescale granularity?**
   - Hours/minutes/seconds?
   - Per-user or global?
   - Adaptive based on change frequency?

4. **How to balance detail vs gist?**
   - Always show detail for spotlight items?
   - Gist for peripheral only?
   - User preference?

5. **Can we validate biological models experimentally?**
   - Neuroscience collaborators?
   - Compare to fMRI studies of memory/attention?
   - Publish findings?

## Related Work

**AI/ML:**
- Attention mechanisms (Transformer architecture)
- Memory networks (Neural Turing Machines)
- Sparse Transformers (long-range attention)
- Retrieval-Augmented Generation (RAG)

**Neuroscience:**
- Working memory models (Baddeley & Hitch)
- Attention theories (Feature Integration, Guided Search)
- Memory consolidation (synaptic homeostasis hypothesis)
- Predictive processing (Friston's free energy principle)

**Cognitive Science:**
- Miller's Law (7±2 items in working memory)
- Ebbinghaus forgetting curve
- Chunking (Chase & Simon, chess studies)
- Dual-process theory (System 1 vs System 2)

## Weird Ideas (Blue Sky)

### 1. "Dreams" for Ada
Run memory consolidation with LLM generating **synthetic experiences** - explore counterfactuals, generate examples, fill gaps in knowledge.

**Example:** "User often asks about Python. Generate practice examples of Python debugging to have ready."

### 2. Emotional Salience
Weight context by emotional valence - humans remember emotionally charged events better.

**Implementation:** Sentiment analysis → boost importance of emotionally significant memories.

### 3. Circadian Rhythms
Different context strategies based on time of day:
- Morning: Fresh start, load recent summaries
- Evening: Continuity, load full history

**Why:** Match human cognitive patterns!

### 4. Social Context
Multi-user systems: Weight context by **social distance** (close friends vs acquaintances).

**Ada context:** Matrix bridge could weight room members by interaction frequency!

### 5. Neuroplasticity
Context structure **adapts** based on usage patterns - frequently used pathways become "stronger" (cached longer, loaded faster).

**Implementation:** Track context access patterns, optimize for common paths.

## Conclusion

**Key insight:** Biological systems handle context overload with:
- **Hierarchy** (fast/slow timescales, focus/periphery)
- **Selectivity** (attention, prediction error)
- **Compression** (chunking, gist extraction)
- **Adaptation** (habituation, priming)

**Ada's opportunity:** We're already doing some of this (memory consolidation!), but there's **so much more** to explore.

**Philosophy alignment:** "Hackable all the way down" - These biological models are **transparent**, **explainable**, and **modular**. We can show how they work, tune them, replace them. No black boxes!

**Next steps:**
1. Implement multi-timescale caching (easy win)
2. Add decay weighting (Ebbinghaus curve)
3. Experiment with attentional spotlight
4. Document results, publish findings
5. Keep exploring weird biology → AI pathways! 🧠🤖

---

**Last Updated:** 2025-12-16  
**Status:** Research document, not yet implemented  
**Vibe:** Weird science, creative explorations, biomimicry for fun and profit! ✨

