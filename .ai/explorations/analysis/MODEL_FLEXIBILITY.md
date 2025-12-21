# Model Flexibility & Use-Case Optimization

> **Insight:** Ada's architecture shouldn't assume one model for everything  
> **Opportunity:** Different use cases → different models → better efficiency  
> **Goal:** Make model choice pluggable, not hardcoded

## The Human Time Constraint

**Key insight:** The bottleneck isn't hardware, it's **human attention span**

**Attention thresholds:**
- ✅ **<1s:** Feels instant (flow state maintained)
- ✅ **1-3s:** Acceptable (brief pause, attention held)
- ⚠️ **3-10s:** Noticeable (mind starts to wander)
- ❌ **>10s:** Frustrating (task switching kicks in, you check your phone)

**Example (optional DeepSeek-R1:14B):**
- Simple query: ~2-5s ✅
- With specialists: ~5-10s ⚠️
- Complex reasoning: ~10-20s ❌

**Implication:** We need to stay under 10s for most interactions, or humans will context-switch!

## Use Case → Model Matrix

Different tasks need different capabilities:

### Use Case 1: Quick Code Reference
**Task:** "What does this function do?"

**Needs:**
- Fast response (<3s)
- Code understanding
- Basic explanation

**Optimal model:**
- CodeLlama 7B (code-specialized, small)
- Qwen2.5-Coder 7B (also great)
- DeepSeek-Coder 6.7B

**Why not R1?**
- R1 is overkill (reasoning not needed)
- 14B params = slower
- Code models understand syntax better anyway

**Speed gain:** 3-5x faster!

### Use Case 2: Pair Programming
**Task:** "Suggest how to fix this bug"

**Needs:**
- Fast iteration (<5s)
- Code generation
- Basic reasoning

**Optimal model:**
- Qwen2.5-Coder 7B-Instruct
- CodeLlama 13B-Instruct
- StarCoder2 15B

**Why not R1?**
- Pair programming is conversational (fast back-and-forth)
- Don't need deep reasoning, need quick suggestions
- Smaller = faster = better flow

**Speed gain:** 2-3x faster

### Use Case 3: Deep Reasoning
**Task:** "Design a new architecture for X"

**Needs:**
- Strong reasoning
- Multi-step planning
- Complex problem solving

**Optimal model:**
- DeepSeek-R1:14B (optional)
- Qwen QwQ-32B (if you have RAM)
- Claude/GPT via API (if acceptable)

**Why R1?**
- This is what R1 is FOR
- Reasoning traces = transparent thinking
- Worth the wait (10-20s acceptable for complex tasks)

### Use Case 4: Casual Chat
**Task:** "Hey Ada, how are you?"

**Needs:**
- Fast response (<2s)
- Personality/warmth
- No deep reasoning

**Optimal model:**
- Llama 3.2 3B-Instruct
- Phi-3.5 Mini 3.8B
- Gemma 2 2B-Instruct

**Why not R1?**
- Social chat doesn't need reasoning
- Persona matters more than smarts
- Tiny models = instant responses = better UX

**Speed gain:** 5-10x faster!

### Use Case 5: Memory Consolidation (Batch)
**Task:** Nightly summarization of conversations

**Needs:**
- Good summarization
- No time pressure (batch job)
- Cost efficiency

**Optimal model:**
- Larger models OK (can take minutes)
- Mixtral 8x7B (quality summaries)
- Even API models acceptable (non-interactive)

**Why different?**
- Batch = no human waiting
- Quality > speed
- Can use bigger/better models

## Historical Anti-Pattern: Hardcoded Model

**brain/llm.py:**
```python
def generate_stream(prompt: str) -> Iterator[str]:
    """Generate using Ollama."""
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": "qwen2.5-coder:7b",  # ← HARDCODED (anti-pattern)
            "prompt": prompt,
            "stream": True
        }
    )
```

**Problem:**
- Every request uses R1
- No way to optimize per use-case
- Codebase specialist will be slow even for simple reads

## Proposed: Model Router

**Make model selection contextual:**

```python
# brain/llm.py
from enum import Enum
from typing import Optional

class UseCase(Enum):
    """Different use cases with different model needs."""
    REASONING = "reasoning"        # Deep thought (R1)
    CODE = "code"                   # Code tasks (CodeLlama)
    CHAT = "chat"                   # Social (small model)
    CONSOLIDATION = "consolidation" # Batch (big model OK)
    GENERAL = "general"             # Default (medium model)

class ModelRouter:
    """Route use cases to appropriate models."""
    
    # Model registry with profiles
    MODELS = {
        # Fast models (1-3s)
        "llama3.2:3b": {
            "params": "3B",
            "speed": "fast",
            "use_cases": [UseCase.CHAT],
            "strengths": ["conversation", "persona"]
        },
        "qwen2.5-coder:7b": {
            "params": "7B", 
            "speed": "fast",
            "use_cases": [UseCase.CODE],
            "strengths": ["code-understanding", "syntax"]
        },
        
        # Medium models (3-5s)
        "codellama:13b": {
            "params": "13B",
            "speed": "medium",
            "use_cases": [UseCase.CODE, UseCase.GENERAL],
            "strengths": ["code-generation", "explanation"]
        },
        
        # Reasoning models (5-15s)
        "deepseek-r1:14b": {
            "params": "14B",
            "speed": "slow",
            "use_cases": [UseCase.REASONING],
            "strengths": ["reasoning", "planning", "problem-solving"]
        },
        
        # Batch models (any speed)
        "mixtral:8x7b": {
            "params": "47B",
            "speed": "very-slow",
            "use_cases": [UseCase.CONSOLIDATION],
            "strengths": ["summarization", "quality"]
        }
    }
    
    def select_model(self, use_case: UseCase, context: dict) -> str:
        """Select optimal model for use case."""
        
        # Find models that support this use case
        candidates = [
            model for model, info in self.MODELS.items()
            if use_case in info['use_cases']
        ]
        
        if not candidates:
            # Fall back to general-purpose
            return self.get_default_model()
        
        # If multiple candidates, pick based on context
        if len(candidates) > 1:
            # Prefer faster models unless quality needed
            if context.get('prefer_speed', True):
                return min(candidates, key=lambda m: self._speed_score(m))
            else:
                return max(candidates, key=lambda m: self._quality_score(m))
        
        return candidates[0]
    
    def get_default_model(self) -> str:
        """Default model for general use."""
        return "qwen2.5-coder:7b"  # Example default
    
    def _speed_score(self, model: str) -> int:
        """Lower = faster."""
        speed_map = {"fast": 1, "medium": 2, "slow": 3, "very-slow": 4}
        return speed_map.get(self.MODELS[model]['speed'], 99)
    
    def _quality_score(self, model: str) -> int:
        """Higher = better quality (rough heuristic: param count)."""
        params = self.MODELS[model]['params']
        # Extract number (e.g., "14B" → 14)
        return int(params.replace('B', '').replace('x', ''))
```

**Updated generate function:**
```python
def generate_stream(
    prompt: str, 
    use_case: UseCase = UseCase.GENERAL,
    prefer_speed: bool = True
) -> Iterator[str]:
    """Generate using appropriate model for use case."""
    
    router = ModelRouter()
    model = router.select_model(use_case, {'prefer_speed': prefer_speed})
    
    logger.info(f"Using model {model} for use case {use_case}")
    
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": True
        }
    )
    
    for line in response.iter_lines():
        # ... existing streaming logic
        yield chunk
```

## Integration Points

### Codebase Specialist
```python
# brain/specialists/codebase_specialist.py
class CodebaseSpecialist(BaseSpecialist):
    def process(self, request: dict) -> SpecialistResult:
        """Read code and explain using code-optimized model."""
        
        code = self._read_file(request['path'])
        
        # Use fast code model, not R1!
        explanation = llm.generate(
            f"Explain this code:\n{code}",
            use_case=UseCase.CODE,
            prefer_speed=True  # Fast iteration
        )
        
        return SpecialistResult(content=explanation)
```

**Impact:** Code reading 3-5x faster!

### Chat Endpoint
```python
# brain/app.py
@router.post("/v1/chat/stream")
async def chat_stream_v1(request: ChatRequest):
    """Route to appropriate model based on message."""
    
    # Detect use case from message
    use_case = detect_use_case(request.message)
    
    # Simple chat → fast model
    if use_case == UseCase.CHAT:
        prompt = build_lightweight_prompt(request)
        model_choice = UseCase.CHAT
    
    # Code question → code model
    elif use_case == UseCase.CODE:
        prompt = build_code_prompt(request)
        model_choice = UseCase.CODE
    
    # Complex reasoning → R1
    elif use_case == UseCase.REASONING:
        prompt = build_full_prompt(request)
        model_choice = UseCase.REASONING
    
    # Generate with appropriate model
    for chunk in llm.generate_stream(prompt, use_case=model_choice):
        yield chunk
```

### Use Case Detection
```python
def detect_use_case(message: str) -> UseCase:
    """Infer use case from message content."""
    
    message_lower = message.lower()
    
    # Code indicators
    code_keywords = ['function', 'class', 'def ', 'import', 'explain code', 'how does']
    if any(kw in message_lower for kw in code_keywords):
        return UseCase.CODE
    
    # Reasoning indicators  
    reasoning_keywords = ['design', 'architecture', 'plan', 'strategy', 'should i', 'compare']
    if any(kw in message_lower for kw in reasoning_keywords):
        return UseCase.REASONING
    
    # Chat indicators
    chat_keywords = ['hi', 'hello', 'how are you', 'thanks', 'bye']
    if any(kw in message_lower for kw in chat_keywords):
        return UseCase.CHAT
    
    # Default: general
    return UseCase.GENERAL
```

## Configuration

**Make it user-configurable:**

```python
# brain/config.py
class Config(BaseSettings):
    # ... existing config ...
    
    # Model selection
    MODEL_CHAT: str = "llama3.2:3b"
    MODEL_CODE: str = "qwen2.5-coder:7b"
    MODEL_REASONING: str = "qwen2.5-coder:7b"
    MODEL_GENERAL: str = "qwen2.5-coder:7b"
    MODEL_CONSOLIDATION: str = "mixtral:8x7b"
    
    # Use case detection
    AUTO_DETECT_USE_CASE: bool = True
    PREFER_SPEED_OVER_QUALITY: bool = True  # Default to fast
    
    # Fallback behavior
    FALLBACK_TO_GENERAL_MODEL: bool = True  # If specialized model unavailable
```

**User can override:**
```bash
# Use one model for everything
export MODEL_CHAT="qwen2.5-coder:7b"
export MODEL_CODE="qwen2.5-coder:7b"

# Or optimize for speed
export MODEL_CHAT="llama3.2:3b"
export MODEL_CODE="qwen2.5-coder:7b"
export PREFER_SPEED_OVER_QUALITY=true
```

## Speed Comparisons (Estimated)

**Based on typical 7B vs 14B performance:**

| Use Case | Current (R1:14B) | Optimized Model | Speedup |
|----------|------------------|-----------------|---------|
| Casual chat | 3-5s | Llama3.2:3B (1-2s) | 3-5x ⚡ |
| Code explanation | 4-6s | Qwen2.5-Coder:7B (1-3s) | 2-4x ⚡ |
| Pair programming | 5-8s | CodeLlama:13B (2-4s) | 2-3x ⚡ |
| Deep reasoning | 10-15s | R1:14B (10-15s) | 1x (same) |
| Memory consolidation | 20-30s | Mixtral:8x7B (30-60s) | 0.5-1x (batch, doesn't matter) |

**Net effect:** Most interactions 2-5x faster, while keeping quality where it matters!

## Hardware Impact

**Smaller models = better on ALL hardware tiers:**

### Tier 1: Raspberry Pi (2-4GB RAM)
- Llama3.2:3B - Works great! ✅
- Qwen2.5-Coder:7B - Works! ✅
- CodeLlama:13B - Tight but possible ⚠️
- DeepSeek-R1:14B - Slow but works ⚠️

**Benefit:** Can run fast models 3-5x faster than R1

### Tier 2: Desktop (8-16GB RAM)
- All models work comfortably
- Can run multiple models simultaneously
- Swap based on use case with minimal overhead

### Tier 3: Server (16GB+ RAM)
- Can load all models into RAM (model warm pool)
- Zero-latency model switching
- Run different models in parallel

## Implementation Strategy

### Phase 1: Add Model Router (Week 1)
1. Create `ModelRouter` class
2. Add use case detection
3. Update `llm.generate_stream()` signature
4. Test with current model (no behavior change)

### Phase 2: Add Fast Models (Week 2)
1. Pull Llama3.2:3B and Qwen2.5-Coder:7B
2. Update config with model choices
3. Enable use case detection
4. Test speed improvements

### Phase 3: Optimize Specialists (Week 3)
1. Update codebase_specialist to use CODE model
2. Update chat detection to use CHAT model
3. Keep reasoning for complex queries
4. Measure actual speedups

### Phase 4: Advanced Routing (Week 4)
1. Add quality vs speed preference
2. Add model warm pool (pre-load models)
3. Add fallback logic
4. User documentation

## Architectural Benefits

**This generalizes Ada from "an AI assistant" to "an AI framework":**

1. **Pluggable models** - Swap models without changing code
2. **Use-case optimization** - Right model for right task
3. **Hardware flexibility** - Choose models based on available RAM
4. **Future-proof** - New models drop in easily
5. **Transparent** - Users see which model for which task

**Philosophical alignment:**
- ✅ **Hackable** - Model choice is explicit config
- ✅ **Accessible** - Can use tiny models on low-end hardware
- ✅ **Transparent** - Shows which model handling what
- ✅ **No vendor lock** - Not tied to one model/provider

## Connection to Other Work

**Multi-timescale caching + Model routing = Synergy!**

```python
# Cache persona at session start with tiny model
persona_summary = llm.generate(
    "Summarize persona in one sentence",
    use_case=UseCase.CHAT  # Fast model
)

# Cache code context with code model
code_context = codebase_specialist.process(
    {'path': 'brain/specialists/protocol.py'},
    model=UseCase.CODE  # Code-optimized model
)

# Deep reasoning only when needed
architecture_plan = llm.generate(
    "Design a graph database integration",
    use_case=UseCase.REASONING  # R1 for heavy lifting
)
```

**Each layer uses optimal model for its needs!**

## Open Questions

1. **Model availability:** What if user doesn't have fast models pulled?
   - **Answer:** Fallback to general model, log warning

2. **Context switching overhead:** Does swapping models cost time?
   - **Answer:** Ollama loads models on-demand (~1-2s first call, then cached)

3. **Quality trade-offs:** Will users notice smaller models for simple tasks?
   - **Answer:** Make it configurable, default to smart routing

4. **Model warm pool:** Pre-load all models in RAM?
   - **Answer:** Optional for Tier 3 hardware, not default

5. **Specialist-specific models:** Should each specialist choose its own?
   - **Answer:** Yes! Codebase → code model, Web search → reasoning model

## Next Steps

1. **Try it manually** - Run same prompt with R1 vs Qwen2.5-Coder:7B, compare
2. **Measure timing** - Get real numbers on your hardware
3. **Implement router** - Start with simple use case detection
4. **Test with codebase_specialist** - This is the perfect first use case!

---

**Last Updated:** 2025-12-17  
**Status:** Design doc, ready to implement  
**Impact:** 2-5x faster responses for most interactions! ⚡✨

**Key insight:** Ada doesn't need to be "smart" all the time, just smart when it matters! 🧠
