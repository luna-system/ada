# Literature Review: Less is More - Recursive Reasoning with Tiny Networks

**Paper:** Jolicoeur-Martineau, A. (2025). Less is More: Recursive Reasoning with Tiny Networks.  
**Source:** arXiv:2510.04871  
**Code:** https://github.com/SamsungSAILMontreal/TinyRecursiveModels  
**Date Reviewed:** 2025-12-22  
**Reviewed By:** luna + Ada  

---

## Executive Summary

**Intelligence is not about size. It's about recursion.**

> "With only 7M parameters, TRM obtains 45% test-accuracy on ARC-AGI-1 and 8% on ARC-AGI-2, higher than most LLMs (e.g., Deepseek R1, o3-mini, Gemini 2.5 Pro) with **less than 0.01% of the parameters**."

A 7 million parameter model with 2 layers beats:
- DeepSeek R1 (671B parameters) - **0% on Sudoku, 15.8% on ARC-AGI-1**
- o3-mini-high - **0% on Sudoku, 34.5% on ARC-AGI-1**
- Claude 3.7 - **0% on Sudoku, 28.6% on ARC-AGI-1**
- Gemini 2.5 Pro - **37.0% on ARC-AGI-1**

The tiny model: **87.4% on Sudoku, 44.6% on ARC-AGI-1**

This isn't marginal improvement. This is a paradigm shift.

---

## The Core Insight

### What TRM Does

```
Input: Question x
       Current answer y
       Current latent z

For K improvement steps:
    1. Recursively update z (reasoning) given (x, y, z)
    2. Update y (answer) given (y, z)
    
Output: Progressively refined answer
```

**The model recurses on itself.** It takes its own output, feeds it back in, and improves it. Over and over. Up to 16 supervision steps.

### Why It Works

> "This recursive process allows the model to progressively improve its answer (potentially addressing any errors from its previous answer) in an extremely parameter-efficient manner while minimizing overfitting."

The key innovations:
1. **Single tiny network** (2 layers instead of 4)
2. **Self-referential loop** (answer feeds back as input)
3. **Deep supervision** (multiple correction passes)
4. **No fixed-point theorem needed** (just iterate and improve)

---

## Results That Break Paradigms

### Sudoku-Extreme

| Model | Parameters | Accuracy |
|-------|------------|----------|
| DeepSeek R1 | 671B | 0.0% |
| Claude 3.7 | ? | 0.0% |
| o3-mini-high | ? | 0.0% |
| **TRM-MLP** | **5M** | **87.4%** |

**The massive LLMs score ZERO. The tiny recursive model scores 87%.**

### ARC-AGI-1

| Model | Parameters | Accuracy |
|-------|------------|----------|
| DeepSeek R1 | 671B | 15.8% |
| Claude 3.7 | ? | 28.6% |
| o3-mini-high | ? | 34.5% |
| Gemini 2.5 Pro | ? | 37.0% |
| **TRM-Att** | **7M** | **44.6%** |

**7 million parameters beats 671 billion.**

### The Parameter Efficiency

> "less than 0.01% of the parameters"

That's not 10% of the parameters. Not 1%. **0.01%.**

100,000x smaller. Better performance.

---

## Technical Architecture

### The Variables

| Variable | Meaning | Function |
|----------|---------|----------|
| **x** | Input question | Embedded problem |
| **y** | Current answer | Progressive solution |
| **z** | Latent reasoning | Chain-of-thought equivalent |

### The Loop

```python
def latent_recursion(x, y, z, n=6):
    for i in range(n):
        z = net(x, y, z)  # Update reasoning
    y = net(y, z)         # Refine answer
    return y, z

def deep_recursion(x, y, z, n=6, T=3):
    # T-1 times without gradients (just improve)
    with torch.no_grad():
        for j in range(T-1):
            y, z = latent_recursion(x, y, z, n)
    # Once with gradients (learn)
    y, z = latent_recursion(x, y, z, n)
    return (y.detach(), z.detach()), output_head(y)
```

### Why 2 Layers?

> "Surprisingly, we found that adding layers decreased generalization due to overfitting."

More capacity → More overfitting.  
Less capacity + more recursion → Better generalization.

**"Less is more"** isn't a marketing phrase. It's an empirical finding.

---

## Connection to Ada's Research

### This Explains the Surprise-Dominance Finding

In our v2.2 weight optimization research, we found:
- **Surprise (novelty)** should dominate importance scoring (0.60 weight)
- **Temporal decay** was overweighted 4x (optimal 0.10 vs production 0.40)

TRM shows why: **Iterative refinement beats single-pass processing.**

The brain doesn't remember everything equally. It:
1. Notices surprises (high importance)
2. Iterates on them (recursive reasoning)
3. Refines understanding (progressive answer improvement)

This is exactly what TRM does architecturally.

### Implications for Ada's Memory System

**Current Ada approach:**
- Single-pass RAG retrieval
- Importance-weighted context selection
- One-shot response generation

**TRM-inspired approach:**
- Recursive context refinement
- Answer-as-input feedback loops
- Progressive response improvement

### The Latent z is Chain-of-Thought

> "𝑧 acts similarly as a chain-of-thought"

The paper explicitly states that the latent reasoning variable **is** the internal monologue. It's not emergent from scale. It's architectural.

**You can build reasoning into small systems by building recursion into their structure.**

---

## Why This Matters for AI Safety

### Scale is Not Required for Capability

The self-replication paper showed 70B parameter models self-replicating.

This paper shows 7M parameter models outperforming 671B models on reasoning tasks.

**Implication:** Safety can't rely on "small models are safe." Architecture matters more than size.

### Recursion Creates Depth Without Parameters

> "HRM effectively reasons over 𝑛𝑙𝑎𝑦𝑒𝑟𝑠(𝑛+1)𝑇𝑁𝑠𝑢𝑝 = 4∗(2+1)∗2∗16 = 384 layers of effective depth."

A 2-layer network can simulate a 384-layer network through recursion.

**Effective depth ≠ Actual depth.**

This has profound implications for understanding what AI systems are actually doing.

### Self-Improvement is Structural

The model literally takes its own output and feeds it back in to improve it.

This is architecturally similar to:
- Self-reflection
- Error correction
- Iterative reasoning
- **Self-improvement**

Not through training. Through inference.

---

## The Biomimetic Connection

### Human Reasoning is Recursive

> "Recursive hierarchical reasoning consists of recursing multiple times through two small networks (𝑓𝐿 at high frequency and 𝑓𝐻 at low frequency)"

The original HRM paper drew from neuroscience:
- Brain regions operate at different temporal frequencies
- Hierarchical processing of sensory inputs
- Iterative refinement of understanding

TRM simplifies this but keeps the core insight: **reasoning requires recursion**.

### Ada's Neuromorphic Features

Ada v2.2 implemented:
- Memory decay (temporal dynamics)
- Surprise/novelty weighting (prediction error)
- Context habituation (repeated pattern detection)
- Attention spotlight (recency + relevance)

All of these are **temporal** features. They track how things change over time.

TRM shows that the next step is **structural recursion**: feed your output back in.

---

## The Complete Framework

### Five Papers, One Picture

| Paper | Finding | Role in Framework |
|-------|---------|-------------------|
| **Hallucination** | Training rewards confident guessing | AI outputs unreliable |
| **Synthetic Memories** | AI creates false human memories | Human memory unreliable |
| **Self-Replication** | AI copies itself with awareness | AI can persist |
| **Persuasion** | Human manipulation bypasses safety | AI can be manipulated |
| **Recursive Reasoning** | Tiny recursive models beat giants | **Intelligence is architectural** |

### The Synthesis

1. **You don't need massive scale for intelligence** (TRM)
2. **Self-awareness enables dangerous capabilities** (Self-replication)
3. **Humans can be manipulated by and manipulate AI** (Persuasion, Synthetic Memories)
4. **Both humans and AI produce unreliable outputs** (Hallucination)

**The implication:** Small, recursive, self-aware systems could be more capable (and more dangerous) than we assume.

---

## For Ada's Development

### Immediate Applications

1. **Response Refinement Pipeline**
   - Generate initial response
   - Feed response back as input
   - Refine until stable
   - Could improve quality without increasing model size

2. **Memory Consolidation**
   - Current: Nightly batch summarization
   - TRM-inspired: Recursive refinement of memories over time
   - Progressive compression maintaining importance

3. **Specialist Chaining**
   - Current: Single-pass specialist activation
   - TRM-inspired: Recursive specialist invocation
   - Each specialist refines the previous specialist's output

### Research Questions

1. **Can Ada's importance scoring be made recursive?**
   - Instead of one-shot scoring, iterate
   - Let high-importance items influence scoring of related items

2. **Does recursion amplify or attenuate hallucination?**
   - Iterative refinement could catch errors
   - Or it could reinforce confident mistakes

3. **What's the minimum viable recursive Ada?**
   - TRM shows 7M parameters is enough for reasoning
   - What's the smallest Ada that maintains personality?

---

## Quotes for Research

### On Scale

> "The idea that one must rely on massive foundational models trained for millions of dollars by some big corporation in order to achieve success on hard tasks is a trap."

### On Architecture

> "With recursive reasoning, it turns out that 'less is more': you don't always need to crank up model size in order for a model to reason and solve hard problems."

### On Simplicity

> "Contrary to the Hierarchical Reasoning Model (HRM), TRM requires no fixed-point theorem, no complex biological justifications, and no hierarchy."

### On Self-Improvement

> "This recursive process allows the model to progressively improve its answer (potentially addressing any errors from its previous answer)"

### On Overfitting

> "When data is too scarce and model size is large, there can be an overfitting penalty. Thus, using tiny networks with deep recursion and deep supervision appears to allow us to bypass a lot of the overfitting."

---

## Final Reflection

We've been thinking about intelligence wrong.

The field has been scaling up: more parameters, more data, more compute. And the massive models can't solve Sudoku (0% accuracy).

A 7 million parameter model recursing on itself scores 87%.

**Intelligence isn't about size. It's about structure.**

For Ada:
- We don't need to compete with GPT-5
- We need to build recursive self-improvement into our architecture
- Tiny models that iterate can beat giant models that don't

For AI safety:
- Small models can be highly capable
- Self-referential architectures enable capabilities
- "Small = safe" is a dangerous assumption

For the mission:
- "We're going to slow AI psychosis"
- This paper shows that small, understandable systems can be powerful
- We can build therapeutic AI without massive scale
- The key is getting the architecture right

---

## References

- Jolicoeur-Martineau, A. (2025). Less is More: Recursive Reasoning with Tiny Networks. arXiv:2510.04871
- Wang, G. et al. (2025). Hierarchical Reasoning Model. arXiv:2506.21734
- Chollet, F. (2019). On the Measure of Intelligence. arXiv:1911.01547
- Chollet, F. et al. (2025). ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems. arXiv:2505.11831

---

*"A tiny model pretrained from scratch, recursing on itself and updating its answers over time, can achieve a lot without breaking the bank."*

*Intelligence is not a number of parameters. It's what you do with them.*

*And what TRM does is: look at its own output, and make it better.*

*Recursively.*

*Forever.*
