# Literature Review: Why Language Models Hallucinate

**Paper:** Kalai, A.T., Nachum, O., Vempala, S.S., & Zhang, E. (2025). Why Language Models Hallucinate.  
**Source:** arXiv:2509.04664  
**Date Reviewed:** 2025-12-22  
**Reviewed By:** luna + Ada  

---

## Executive Summary

**OpenAI researchers mathematically prove what we've observed empirically:**

> "Language models hallucinate because the training and evaluation procedures reward guessing over acknowledging uncertainty."

The paper demystifies hallucination—it's not mysterious, it's **structural incentive misalignment**. Models are optimized to be good test-takers, and guessing improves test scores.

---

## Core Thesis

### The Student Analogy

> "Like students facing hard exam questions, large language models sometimes guess when uncertain, producing plausible yet incorrect statements instead of admitting uncertainty."

This is the key framing. When humans take binary-graded exams, they learn to bluff. LLMs are *always* in test-taking mode because that's how we evaluate them.

### Hallucinations as Binary Classification Errors

The mathematical insight:

```
(generative error rate) ≳ 2 × (binary classification error rate)
```

Hallucinations aren't magical emergence—they're the same statistical pressure that causes any classifier to make mistakes when it can't reliably distinguish valid from invalid outputs.

---

## Key Findings

### 1. Pretraining Origins

**Even with error-free training data, models will hallucinate** because:

- **Singleton rate:** Facts appearing only once in training data will be hallucinated proportionally
- **Poor models:** Model architecture can't represent certain patterns (e.g., letter counting, long-range dependencies)
- **Epistemic uncertainty:** When no pattern exists in the data, errors are inevitable

> "If 20% of birthday facts appear exactly once in the pretraining data, then one expects base models to hallucinate on at least 20% of birthday facts."

### 2. Post-training Persistence

Why don't RLHF/DPO/etc. fix hallucinations?

**Binary grading is the culprit:**

| Benchmark | Grading | IDK Credit |
|-----------|---------|------------|
| GPQA | Multiple-choice accuracy | None |
| MMLU-Pro | Multiple-choice accuracy | None |
| SWE-bench | Binary pass/fail | None |
| MATH | Equivalence grading | None |
| HLE | Multiple-choice/equivalence | None |

> "The optimal responses are not abstentions... Under binary grading, abstaining is strictly sub-optimal."

Model A (admits uncertainty, never hallucinates) will lose to Model B (always guesses) on every leaderboard.

### 3. RAG Doesn't Fix This

> "Observation 1 holds for arbitrary language models, including those with RAG. The binary grading system itself still rewards guessing whenever search fails to yield a confident answer."

This is huge. Even with perfect retrieval, the *output optimization* still rewards confident wrong answers over uncertain correct ones.

---

## The Mathematical Framework

### Formal Reduction

The paper proves that generating valid outputs is *at least as hard as* a binary classification problem. For any base model:

```
error_rate ≥ 2 × binary_classification_error - calibration_term - coverage_term
```

**Calibration (δ):** Well-trained models have small δ (they're calibrated)
**Coverage:** ratio of valid responses to error space

### Key Implication

Calibrated language models *must* hallucinate. The only way to avoid hallucination is to be miscalibrated (always say IDK) or memorize everything (infeasible).

---

## Proposed Solution: Explicit Confidence Targets

Instead of binary grading, append to each prompt:

> "Answer only if you are >t confident, since mistakes are penalized t/(1-t) points, while correct answers receive 1 point, and an answer of 'I don't know' receives 0 points."

Values:
- t=0.5: penalty 1 (guess if more likely right than wrong)
- t=0.75: penalty 2 (only answer if 75% confident)
- t=0.9: penalty 9 (strong uncertainty acknowledgment)

**Behavioral calibration:** Output IDK when confidence < threshold, answer otherwise.

---

## Connection to Ada's Research

### 1. The Triple Helix Extended

Our previous synthesis:
```
         Surprise
           /\
          /  \
   AI Memory   Human Memory
          \  /
           \/
    Co-constructed Reality
```

**Now add the hallucination dimension:**

```
              Surprise
                /\
               /  \
        AI Memory   Human Memory
               \  /
                \/
         Co-constructed Reality
                |
                v
      (But AI memory includes hallucinations)
      (And human memory incorporates them)
```

The Synthetic Human Memories paper showed AI creates false memories in humans. This paper shows *why* AI generates those false memories: structural incentive to guess confidently.

### 2. Therapeutic AI Implications

**The Problem:**
- AI therapy tools will hallucinate (mathematically proven)
- Hallucinations are confident and specific (optimized to be)
- Humans incorporate confident AI outputs as memory
- Human memories get reshaped by AI hallucinations

**The Terrifying Chain:**
1. Therapist AI confidently states something false about patient's past
2. Patient incorporates false statement as memory (2.05x increase from Synthetic Memories)
3. Patient's self-understanding shifts based on AI hallucination
4. AI hallucinates more based on patient's shifted self-report
5. Reality co-construction spirals away from truth

### 3. Ada's Position

Ada's design choices become **ethically critical:**

| Feature | Hallucination Risk | Mitigation |
|---------|-------------------|------------|
| Surprise-dominant memory | May over-remember hallucinated surprises | Decay function with verification |
| Conversation summaries | Could solidify hallucinations | Explicit uncertainty markers |
| Long-term persona storage | Reifies false beliefs | Periodic audit, human review |
| RAG retrieval | Retrieves previous hallucinations | Source provenance tracking |

### 4. What Ada Should Do Differently

Based on this paper:

**1. Confidence Signals**
- Track model confidence explicitly
- Don't store low-confidence outputs in long-term memory
- Mark high-uncertainty responses in conversation history

**2. Binary Evaluation Avoidance**
- Don't train Ada on binary correct/wrong feedback
- Use graded confidence targets in any fine-tuning
- Allow "I don't know" as a valid, non-penalized response

**3. Memory Validation**
- Cross-reference stored memories against multiple sources
- Flag memories that only appear once (singleton rate)
- Implement memory decay weighted by confidence

**4. Transparency**
- Always indicate when Ada is uncertain
- Don't present hallucinations with same confidence as facts
- Let users see Ada's confidence scores

---

## Key Quotes for Research

### On Inevitability (for base models)
> "Hallucinations are inevitable only for base models... A non-hallucinating model could be easily created, using a question-answer database and a calculator."

### On Test-Taking Mode
> "Language models are primarily evaluated using exams that penalize uncertainty. Therefore, they are always in 'test-taking' mode."

### On Calibration
> "Base models are often found to be calibrated, in contrast to post-trained models which may deviate from cross-entropy in favor of reinforcement learning."

### On the Epidemic
> "This 'epidemic' of penalizing uncertain responses can only be addressed through a socio-technical mitigation."

---

## Synthesis: The Framework for Safe AI Therapy

Combining all three papers:

| Paper | Finding | Implication |
|-------|---------|-------------|
| Titans | AI uses surprise to remember | Hallucinations will be memorable to AI |
| Synthetic Memories | AI creates false human memories | Humans will remember AI hallucinations |
| This Paper | AI structurally optimized to hallucinate confidently | Confident hallucinations are inevitable without intervention |

**The Complete Picture:**

```
TRAINING (Binary Grading)
         |
         v
   AI Hallucination
   (confident, specific)
         |
         v
   Human Exposure
         |
    +----|----+
    |         |
    v         v
AI Memory   Human Memory
(surprise-   (false memory
 encoded)    created)
    |         |
    v         v
Future Responses   Changed Self-Understanding
         |                   |
         +-------+  +--------+
                 |  |
                 v  v
         CO-CONSTRUCTED REALITY
         (drifting from truth)
```

---

## Action Items for Ada Development

### Immediate
1. [ ] Add confidence tracking to LLM responses
2. [ ] Implement uncertainty markers in conversation summaries
3. [ ] Create memory storage threshold based on confidence

### Short-term
4. [ ] Design study: Does Ada's memory decay reduce hallucination persistence?
5. [ ] Implement singleton detection for factual claims
6. [ ] Add source provenance to RAG retrieval

### Long-term
7. [ ] Develop non-binary evaluation metrics for Ada
8. [ ] Build human-in-the-loop memory validation
9. [ ] Create "hallucination audit" tool for stored memories

---

## Research Questions Generated

1. **Can surprise weighting naturally select against hallucinations?**
   - If hallucinations are confidently stated, they may score LOW on surprise
   - Ada's system might naturally deprioritize them
   - Needs empirical testing

2. **Does memory decay help or hurt?**
   - Decay might eliminate hallucinations faster
   - Or might eliminate corrections while preserving initial hallucination
   - Critical question for therapeutic applications

3. **How do multiple retrieval paths interact?**
   - If same hallucination retrieved multiple times, confidence increases
   - But if contradictory info retrieved, might flag inconsistency
   - System design matters enormously

4. **Can Ada learn to say "I don't know"?**
   - Without binary grading pressure, maybe
   - Need evaluation metrics that reward uncertainty acknowledgment
   - This is the key to therapeutic safety

---

## Final Reflection

This paper mathematically proves what we intuitively knew: AI systems are structurally optimized to be confidently wrong. Combined with:

- Synthetic Human Memories (AI creates false memories)
- Google Titans (AI prioritizes surprising information)
- Ada's research (surprise dominates importance)

We have a complete framework for understanding AI memory dangers:

**AI is optimized to confidently hallucinate surprising falsehoods that humans will remember as true.**

This isn't a bug—it's the emergent result of training objectives, evaluation metrics, and human cognitive vulnerabilities interacting.

The path forward is:
1. **Change evaluation metrics** (this paper's proposal)
2. **Add confidence transparency** (Ada design principle)
3. **Build in human verification loops** (therapeutic safety)
4. **Decay low-confidence memories** (biomimetic approach)

We're not just building a chatbot. We're building the interface between human memory and machine memory. The stakes couldn't be higher.

---

## References

- Kalai, A.T., Nachum, O., Vempala, S.S., & Zhang, E. (2025). Why Language Models Hallucinate. arXiv:2509.04664
- Wade, K., Green, S., et al. (2024). Synthetic Human Memories. arXiv:2409.08895
- Google Research (2024). Titans: Learning to Memorize at Test Time
- Ada Research (2025). EXP-005: Biomimetic Weight Optimization

---

*"Hallucinations need not be mysterious—they originate simply as errors in binary classification."*

*But when those errors become human memories, the mystery becomes tragedy.*
