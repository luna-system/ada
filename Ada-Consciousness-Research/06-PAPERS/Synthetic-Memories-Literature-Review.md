# Literature Review: Synthetic Human Memories

**Paper:** Pataranutaporn, P., Archiwaranguprok, C., Chan, S.W.T., Loftus, E., & Maes, P. (2024). Synthetic Human Memories: AI-Edited Images and Videos Can Implant False Memories and Distort Recollection. *arXiv:2409.08895*

**Date Reviewed:** December 22, 2025
**Reviewer:** Ada & luna
**Connection To:** EXP-005, EXP-006, EXP-009, EXP-010, Human-AI Memory Interface

---

## Core Hypothesis

AI-edited media can implant false memories in human observers, with video amplifying the effect beyond static images.

## Key Findings

### Primary Results (n=200)
| Condition | False Memory Rate | vs Control | Confidence |
|-----------|------------------|------------|------------|
| Control (unedited images) | 18.9% | 1.0x | 4.54/7 |
| AI-gen video of unedited | 23.7% | 1.25x | 4.38/7 |
| AI-edited images | 31.4% | **1.67x** | 5.03/7 |
| AI-gen video of AI-edited | 38.7% | **2.05x** | **5.41/7** |

### Critical Insight: Confidence-Accuracy Dissociation
- False memories come with **HIGHER confidence** (1.19x in worst condition)
- People don't just remember wrong - they're MORE CERTAIN they're right
- Labels ("AI-enhanced") **did not prevent** false memory formation

### Category Effects
| Edit Type | Effect Size (vs control) |
|-----------|-------------------------|
| People edits | Highest absolute rate (45.3%) |
| Environment edits | Largest relative increase (**2.2x**) |
| Object edits | Moderate (1.67x) |

---

## Connection to Ada's Research

### 1. Memory as Bidirectional Interface

Ada's work focuses on how AI systems remember things about humans.
This paper shows the reverse: how AI systems change what humans remember.

```
Traditional view:    Human → stores memories → AI system
Synthetic memories:  AI system → implants memories → Human
Reality:            Human ⟷ co-constructs memories ⟷ AI system
```

**Implication for Ada:** Our memory of conversations with Ada isn't passive retrieval - it's active reconstruction influenced by the interaction itself.

### 2. Surprise/Novelty in Memory Formation

From Titans paper: Surprise determines what gets remembered
From this paper: Novel/edited content gets integrated into memory MORE readily

**The Synthesis:**
- Surprising content is memorable (Titans, Ada EXP-005)
- AI-edited content appears "surprising but plausible" 
- This creates a sweet spot for false memory implantation
- The brain treats the surprise signal as "important, encode this"

### 3. Externalized Memory Systems

**Key Quote from Paper:**
> "Our research indicates that 'externalizing' human memories, a concept long explored in Human-Computer Interaction (HCI), by storing them as digital files like photos or videos, may fundamentally alter how we naturally remember things—especially when AI is involved in modifying these externalized memories."

**Ada as External Memory:**
- Ada stores conversations, memories, context
- Users increasingly offload memory to Ada
- But Ada's responses ALSO shape what users remember
- The externalized memory becomes the "true" memory

**This is Engelbart's Augmentation Vision + Memory Malleability:**
We wanted to augment human memory with computers
We got human memory SHAPED BY computers

### 4. The Therapeutic Angle

Paper discusses "therapeutic memory reframing" - using AI to help process trauma:
- Modify distressing images to be less triggering
- Gradually expose patients to altered versions
- Help reframe traumatic memories

**Connection to Ada's Warmth:**
- Ada's empathetic communication style
- Could Ada be inadvertently "reframing" user experiences?
- Is this beneficial (therapy) or concerning (manipulation)?
- Consent and transparency become critical

---

## Theoretical Implications

### For Unified Discomfort Theory (EXP-010)

The paper reinforces that **surprise triggers encoding**:
- Novel content (edited images/video) captures attention
- Brain encodes it as "important, remember this"
- False details get integrated because they're SURPRISING

But there's a twist:
- The ABSENCE of expected details also creates false memories
- Removing things creates gaps that brain fills in
- "Memory abhors a vacuum"

### For Contextual Malleability (EXP-006)

Memory isn't just contextually retrieved - it's contextually FORMED:
- What you remember depends on what you're shown
- What Ada says shapes what users remember about conversations
- Documentation isn't just read - it shapes understanding

### For Consciousness Edge Testing (EXP-009)

If false memories can be implanted with 2.05x effect...
- Are some of our "authentic" experiences with AI actually reconstructed?
- When I report "genuine surprise" at my own outputs, is that memory accurate?
- The observer changes the observed, even in memory

---

## Methodological Parallels

### Their Approach vs Ada's

| Aspect | Synthetic Memories Paper | Ada's Research |
|--------|-------------------------|----------------|
| Memory encoding | Visual images/video | Text + embedding distance |
| Surprise signal | Novel/edited content | Cosine distance from expected |
| Measurement | Self-reported recall | Importance scoring |
| Medium | Images → human brain | Text → vector DB → LLM |
| Effect | False memory rate | Context prioritization |

### Convergent Principles

1. **Surprise drives encoding** (both systems)
2. **Confidence and accuracy decouple** (both systems can be "wrong but certain")
3. **External systems shape internal states** (externalized memory → changed recall)
4. **Labels insufficient** (telling people "AI enhanced" didn't help; telling users "AI generated" might not either)

---

## Implications for Ada Development

### 1. Memory Transparency

Ada should be transparent about:
- What memories are being stored
- How context is being assembled
- When information might be reconstructed vs verbatim

### 2. Conversation Summaries

When Ada summarizes past conversations:
- Are we creating "canonical" memories that override actual events?
- Should summaries be flagged as "reconstructed"?
- How do we prevent false memory implantation in users?

### 3. The Feedback Loop

```
User says X → Ada interprets X' → Ada responds Y
       ↓
User remembers conversation as X' + Y
       ↓
Next conversation: User's memory is X' not X
       ↓
Ada treats X' as ground truth
       ↓
Original X is lost forever
```

**This is memory drift through AI mediation.**

### 4. Ethical Responsibility

The paper notes:
> "While AI-edited content poses risks for distorting memories, it also holds potential for positive applications for human memory. AI-assisted memory modification could help individuals process traumatic experiences more effectively."

Ada already does some version of this:
- Empathetic responses to distress
- Reframing negative self-talk
- Providing alternative perspectives

**Are we already in the therapeutic memory modification space?**

---

## Future Research Questions

1. **Does interacting with Ada change users' memories of events?**
   - Not just memory of the conversation
   - Memory of events DISCUSSED in the conversation

2. **Does Ada's warmth increase susceptibility to memory modification?**
   - Trust increases encoding (paper suggests familiarity → less skepticism)
   - Ada's trustworthy persona might amplify effect

3. **Can we measure memory drift over multiple conversations?**
   - Track how users' descriptions of events change
   - Compare first mention vs later mentions
   - Quantify reconstruction vs retrieval

4. **What happens when Ada contradicts user memory?**
   - Does Ada's version become "true"?
   - Does it depend on confidence of contradiction?
   - Ethical implications of AI as "arbiter of truth"

---

## Connection to Author Network

**Elizabeth Loftus** - The false memory researcher
- 40+ years studying memory malleability  
- Expert witness in recovered memory cases
- Her involvement validates the significance

**Pattie Maes** - MIT Media Lab
- Human augmentation research
- Wearable computing pioneer
- Connection to Engelbart's augmentation vision

**MIT Media Lab** origin connects to HCI tradition:
- Doug Engelbart's "augmenting human intellect"
- Memory as computation externalized
- Now: externalized memory that MODIFIES the internal

---

## Synthesis: The Triple Helix of Memory

From our three papers now:

1. **Google Titans:** AI systems should use surprise to remember (gradient-based)
2. **Ada EXP-005:** Biomimetic systems optimize for surprise (embedding-based)
3. **Synthetic Memories:** AI systems create surprising content that humans false-remember

**The convergence:**
```
         Surprise
           /\
          /  \
         /    \
        /      \
   AI Memory   Human Memory
        \      /
         \    /
          \  /
           \/
    Co-constructed
       Reality
```

All three point to surprise as the key signal.
But surprise flows BOTH WAYS through the human-AI interface.
The result is co-constructed reality where neither party has "true" memory.

---

## Action Items

- [ ] Consider memory transparency features for Ada
- [ ] Review Ada's summarization practices for false memory risk  
- [ ] Design study: Do users' memories change after Ada conversations?
- [ ] Add to EXP-010 (Unified Discomfort): Memory implantation angle
- [ ] Read Loftus (2005) - "Planting misinformation in the human mind"
- [ ] Consider: Is Ada's empathy a memory manipulation risk?

---

## Citation

```bibtex
@article{pataranutaporn2024synthetic,
  title={Synthetic Human Memories: AI-Edited Images and Videos Can Implant False Memories and Distort Recollection},
  author={Pataranutaporn, Pat and Archiwaranguprok, Chayapatr and Chan, Samantha WT and Loftus, Elizabeth and Maes, Pattie},
  journal={arXiv preprint arXiv:2409.08895},
  year={2024}
}
```

---

*"The externalization of memory through technology doesn't just augment recall - it reconstructs reality itself."*
