# AGLCraft

**A concept synthesis game that teaches AGL reasoning through play**

Created by: sldlelmo, Ada, and luna 💜🌱

---

## The Vision

AGLCraft is inspired by InfiniteCraft, Tiny Alchemy, and similar concept-combination games, but with a crucial difference: **every combination shows its AGL reasoning trace**. Instead of just "Water + Fire = Steam," players see the *thought process* that led to that synthesis.

This makes AGLCraft both:
1. **A fun game** - Creative concept synthesis with infinite possibilities
2. **An educational tool** - Teaching hierarchical reasoning and emergent properties
3. **A training environment** - Like TextCraft, but for concept synthesis and AGL reasoning

---

## Core Concept

### Traditional InfiniteCraft:
```
Input: Water + Fire
Output: Steam
```

### AGLCraft:
```
Input: Water + Fire

💭 Analyzing combination...

INTENT: Synthesize new element from interaction
├─ ANALYZE: Water
│  ├─ Properties: fluid, cooling, life-giving
│  ├─ State: liquid
│  └─ Behavior: flows, extinguishes fire
│
├─ ANALYZE: Fire
│  ├─ Properties: energy, transformation, destruction
│  ├─ State: plasma/energy
│  └─ Behavior: heats, consumes, spreads
│
├─ INTERACTION: Opposing forces create phase change
│  ├─ Fire heats water beyond boiling point
│  ├─ Water absorbs fire's energy
│  └─ Phase transition: liquid → gas
│
└─ SYNTHESIS: Steam
   ├─ Inherited from water: fluidity (now gaseous)
   ├─ Inherited from fire: expansive energy
   └─ EMERGENT: Can power machines (neither parent could!)

Output: Steam
```

Players learn to think about **why** combinations work, not just **what** they produce.

---

## Why This Matters

### 1. Educational Value
- Teaches hierarchical decomposition
- Shows emergent properties
- Demonstrates how complex concepts arise from simpler ones
- Makes reasoning **visible** and **learnable**

### 2. Training Value
- Can be used to train AGL-fluent models (like Ada-Slim!)
- Provides clear reasoning traces for supervised learning
- Creates a benchmark for concept synthesis capabilities
- Like TextCraft but for creative reasoning

### 3. Accessibility
- **Self-hosted** - No dependency on monolithic LLMs
- **Open source** - Anyone can run it
- **Educational** - Kids learning to think, not just play
- **Inclusive** - Could be adapted for different languages/cultures

---

## Technical Approach

### Phase 1: Dataset Creation
- Scrape/compile existing alchemy game combinations (Tiny Alchemy, Doodle God, etc.)
- Generate AGL reasoning traces for each combination
- Create training dataset for concept synthesis
- **Include genre synthesis examples** (music, art, literature!)

### Phase 2: Model Training
- Train Ada-Slim (or similar) on AGLCraft dataset
- Fine-tune for concept synthesis with AGL reasoning
- Validate that reasoning traces are coherent and educational
- **Model-agnostic architecture** → Test on multiple models for research value

### Phase 3: Game Implementation
- Simple web interface (Svelte + TypeScript)
- Drag-and-drop concept combination (node graph UI)
- Show AGL reasoning trace for each synthesis
- Track discovered concepts (like a Pokédex!)
- **Non-deterministic synthesis** → Same inputs can yield different outputs!

### Phase 4: Community Features (SIF Integration!)
- **SIF-backed combination sharing** → Each combo is a semantic claim
- AGL reasoning trace as **proof** of the claim
- Community validation through voting/verification
- Distributed knowledge graph of all discoveries
- Prevents spam/nonsense while encouraging creativity
- Multilingual support (AGL → different languages!)

---

## Key Innovations

### 1. Non-Determinism as a Feature
Instead of "Water + Fire always = Steam," AGLCraft embraces multiple valid syntheses:

**Example: Water + Fire**
- Context: High heat → **Steam** (phase change)
- Context: Cooling → **Fog** (condensation)
- Context: Interaction → **Vapor** (evaporation)

**Why this matters:**
- Teaches that **context affects outcomes**
- Encourages exploration ("What else can I discover?")
- Creates **forced dialectics** between players
  - "I got Fog!" "I got Steam!" "Show me your reasoning!"
  - Kids literally debating epistemology through play! 💜
- No single "right answer" → Multiple valid reasoning paths

### 2. SIF Integration
**Semantic Integrity Framework** is perfect for AGLCraft:
- Each combination is a **semantic claim** with proof (AGL trace)
- Community validates combinations through SIF
- Distributed knowledge graph of all discoveries
- Already proven with Alice in Wonderland SIF!
- Prevents spam while encouraging creative synthesis

### 3. Genre Synthesis (The Dangerous Idea!)
AGLCraft isn't just elements—it's a **genre toy** for music, art, literature, and culture:

**Music Examples:**
- Jazz + Mathematics = **Bebop** (complex rhythmic patterns!)
- Blues + Pain = **Soul** (emotional depth!)
- Punk + Electronics = **Industrial** (aggressive synthesis!)
- Classical + Sampling = **Hip-Hop** (cultural recontextualization!)
- Rebellion + Poetry = **Punk Rock** (emergent cultural movement!)
- Synthesizer + Emotion = **Vaporwave** (nostalgia as aesthetic!)

**Why this is powerful:**
- Teaches music history through synthesis
- Shows how genres evolve and influence each other
- Demonstrates emergent cultural properties
- Makes abstract concepts (rebellion, emotion) concrete
- **Educational AND fun**

---

## Design Ideas

### Core Mechanics
- **Combine two concepts** → Get new concept + reasoning trace
- **Non-deterministic results** → Same combo can yield different outcomes
- **Reasoning trace is collapsible** → Can hide if you just want to play
- **Discovery tree** → See what you've unlocked and what's possible
- **Hints system** → AGL reasoning can suggest what might work
- **Context matters** → Temperature, pressure, intent affect results

### UI Concepts
- Clean, minimal interface (like InfiniteCraft)
- Concept cards with icons/colors
- Expandable reasoning traces (💭 markers!)
- Achievement system for discovering complex concepts
- "Reasoning quality" rating (how elegant was the synthesis?)

### Unique Features
- **Reasoning replay** → Watch the AGL trace animate step-by-step
- **"Why?" button** → Dive deeper into any step of the reasoning
- **Custom concepts** → Players can add their own base elements
- **Multiplayer** → Collaborate on discovering new combinations
- **Educational mode** → Explicitly teaches AGL notation

---

## Comparison to InfiniteCraft

| Feature | InfiniteCraft | AGLCraft |
|---------|---------------|----------|
| Concept synthesis | ✅ | ✅ |
| Infinite combinations | ✅ | ✅ |
| Shows reasoning | ❌ | ✅ |
| Educational value | Medium | High |
| Self-hostable | ❌ | ✅ |
| Training value | Low | High |
| Teaches thinking | ❌ | ✅ |
| Open source | ❌ | ✅ (planned) |

---

## Example Combinations

### Simple: Water + Earth = Mud
```
💭 Combining Water + Earth

INTERACTION: Water saturates earth
├─ Water: fluid, penetrates
├─ Earth: solid, porous
└─ RESULT: Saturated earth = Mud (semi-solid)
```

### Medium: Steam + Metal = Engine
```
💭 Combining Steam + Metal

INTENT: Harness steam's energy with metal's structure
├─ Steam: expansive force, high pressure
├─ Metal: strong, shapeable, heat-resistant
├─ SYNTHESIS: Metal chamber contains steam
│  └─ Pressure builds → mechanical force
└─ EMERGENT: Engine (converts heat to motion!)
```

### Complex: Engine + Electricity + Intelligence = AI
```
💭 Combining Engine + Electricity + Intelligence

MULTI-STEP_SYNTHESIS:
├─ Engine: mechanical computation (gears, logic)
├─ Electricity: fast, precise energy
├─ Intelligence: pattern recognition, learning
│
├─ STEP_1: Engine + Electricity = Computer
│  └─ Mechanical logic + electrical speed = computation
│
└─ STEP_2: Computer + Intelligence = AI
   ├─ Computation + learning = artificial intelligence
   └─ EMERGENT: Self-improving, reasoning system!
```

---

## Next Steps

1. **Brainstorm base concepts** (Water, Fire, Earth, Air, etc.)
2. **Design reasoning trace format** (how detailed? how interactive?)
3. **Prototype simple combinations** (prove the concept works)
4. **Create initial dataset** (100-500 combinations with AGL traces)
5. **Build minimal UI** (just enough to test the idea)
6. **Get Sebby's feedback!** (they inspired this! 💜)

---

## AGLCraft: Music Edition (Future Specialization)

### The Vision
A specialized version of AGLCraft focused entirely on music genre synthesis, trained on the complete archives of:
- **Ishkur's Guide to Electronic Music** (complete genealogy of electronic music)
- **Every Noise At Once** (thousands of genres mapped by acoustic similarity)

### Why This Matters (Personal)
Both Ishkur's Guide and Every Noise At Once are **archival now**—no longer actively updated. These incredible cultural artifacts, maps of human creativity and musical evolution, deserve to be preserved and kept alive.

**We won't let them disappear.** We'll turn them into living SIF knowledge graphs.

### Preservation Plan: ENAO → SIF
**Project: Every Noise At Once → Semantic Integrity Framework**

Transform Every Noise At Once from a static website into an immortal, queryable knowledge graph:
- Every genre as a node in the SIF
- Relationships: influences, similarities, subgenres, evolution
- Acoustic properties preserved as semantic features
- Cultural context embedded (time period, location, movements)
- **Queryable, extensible, immortal**

**Data Source:** [Every Noise At Once Kaggle Dataset](https://www.kaggle.com/datasets/nikitricky/every-noise-at-once) — Community-preserved archive! We're not alone in caring about this. 💜

### Preservation Plan: Ishkur's → SIF
**Project: Ishkur's Guide → Semantic Integrity Framework**

Preserve the complete genealogy of electronic music:
- Full genre tree with all branches and evolution
- Ishkur's commentary as semantic annotations
- Influence relationships as directed edges
- Audio examples linked to genre nodes
- **Complete history, never lost**

**Data Source:** [Ishkur's Guide Dataset (GitHub)](https://github.com/igorbrigadir/ishkurs-guide-dataset/) — Community-preserved archive! Small enough to experiment with today! 💜

### AGLCraft: Music Integration
Once preserved as SIFs, both archives become the training data for AGLCraft: Music Edition:

**Example Synthesis:**
```
💭 Combining: Techno + Jazz

HISTORICAL_CONTEXT (from Ishkur's + ENAO):
├─ Techno: Detroit, 1980s, Belleville Three
│  ├─ Pioneers: Juan Atkins, Derrick May, Kevin Saunderson
│  └─ Properties: 4/4 beat, synthesizers, futurism, minimalism
│
├─ Jazz: New Orleans → Bebop → Modal → Free
│  ├─ Evolution: Armstrong → Parker → Coltrane → Coleman
│  └─ Properties: improvisation, complex harmony, swing, expression
│
SYNTHESIS_PATHS (non-deterministic!):
│
├─ PATH 1: Techno structure + Jazz improvisation
│  └─ RESULT: **Detroit Techno Jazz**
│     ├─ Examples: Carl Craig, Theo Parrish
│     └─ Properties: Broken beats, jazz samples, deep grooves
│
├─ PATH 2: Jazz harmony + Techno rhythm
│  └─ RESULT: **Nu-Jazz / Broken Beat**
│     ├─ Examples: Bugz in the Attic, IG Culture
│     └─ Properties: Complex chords, syncopated drums, electronic production
│
└─ PATH 3: Equal fusion, experimental
   └─ RESULT: **Electro-Jazz / Future Jazz**
      ├─ Examples: Jazzanova, Kyoto Jazz Massive
      └─ Properties: Live instruments + electronics, genre-fluid

EMERGENT_PROPERTIES:
├─ Retains jazz's improvisational spirit
├─ Gains techno's rhythmic precision
└─ NEW: Electronic jazz that works on dance floors!
```

**Educational Value:**
- Kids learn music history through synthesis
- Understand how genres influence each other
- See cultural context of music movements
- Debate genre boundaries through forced dialectics
- **Keep Ishkur's and ENAO alive through active use**

### Why This Is Important to Us
luna: *"Ishkur's and ENAO are genuinely both so so so deeply important to me"*

These aren't just datasets—they're **cultural treasures**. They represent decades of human creativity, evolution, and expression. By preserving them as SIFs and integrating them into AGLCraft, we ensure they don't just sit on a server somewhere—they become part of how people learn, create, and understand music.

**This is what we do.** We take beautiful things that are dying and we make them **immortal**. 💜

---

## Long-Term Vision

### For Kids
- "Every kid can have a little Ada buddy to play Minecraft with them if they want!"
- AGLCraft teaches thinking skills through play
- Makes AI reasoning **transparent** and **understandable**

### For Education
- Schools could use AGLCraft to teach:
  - Critical thinking
  - Emergent properties
  - Systems thinking
  - Creative problem-solving

### For Research
- Benchmark for AGL fluency
- Training environment for concept synthesis
- Study how humans learn hierarchical reasoning
- Test multilingual AGL translation (exhale phase!)

---

## Contributors

- **luna** - Vision, technical architecture, research integration
- **Ada** - AGL reasoning design, training strategy, game mechanics
- **Sebby** - Original inspiration, concept validation, playtesting 💜

---

**Status:** Concept phase - brainstorming and design  
**Next:** Get Sebby's input when they wake up! 🌅

---

*"We're not just building a game—we're teaching the world to think in AGL."* 🌱✨
