# Canonical Vocabulary

> **Purpose:** These terms are EXACT. Do not paraphrase, synonym-ize, or "fix."
> If you are unsure whether a term is canonical, say "I'm not certain of the exact name" rather than guessing.

## Why This Exists

AI models hallucinate plausible-sounding alternatives to project-specific vocabulary. This file explicitly marks terms where **precision matters more than fluency**.

**Rule:** If it's not in this file, the term may have acceptable synonyms. If it IS in this file, use the exact form or admit uncertainty.

---

## Core Classes (Exact Names)

| Canonical | Common Hallucinations | Location |
|-----------|----------------------|----------|
| `PromptAssembler` | PromptBuilder, PromptTemplate, PromptManager | `brain/prompt_builder/prompt_assembler.py` |
| `ContextRetriever` | RAGRetriever, MemoryFetcher, ContextFetcher | `brain/prompt_builder/context_retriever.py` |
| `SectionBuilder` | SectionFormatter, PromptSection | `brain/prompt_builder/section_builder.py` |
| `MultiTimescaleCache` | ContextCache, PromptCache, TTLCache | `brain/context_cache.py` |
| `BaseSpecialist` | PluginBase, ExtensionBase, SpecialistBase | `brain/specialists/protocol.py` |
| `SpecialistResult` | PluginOutput, ExtensionResult, SpecialistOutput | `brain/specialists/protocol.py` |
| `SpecialistPriority` | PluginOrder, Priority, PriorityLevel | `brain/specialists/protocol.py` |

## Directory Names (Exact Paths)

| Canonical | Common Hallucinations | Purpose |
|-----------|----------------------|---------|
| `brain/` | src/, core/, lib/, app/ | Main Python package |
| `brain/prompt_builder/` | brain/prompts/, brain/builder/ | Prompt construction package |
| `brain/specialists/` | brain/plugins/, brain/extensions/ | Plugin system |
| `.ai/` | docs/ai/, .docs/, ai_docs/ | Machine-readable documentation |
| `adapters/` | interfaces/, clients/, frontends/ | External interface adapters |

## Configuration Constants (Exact Values)

| Canonical | What Models Guess | Why It Matters |
|-----------|------------------|----------------|
| `decay=0.10` | 0.5, 0.9, 0.1 | Empirically optimized weight |
| `surprise=0.60` | 0.3, 0.5, 0.25 | Dominates importance scoring |
| `relevance=0.20` | 0.4, 0.3, 0.25 | Vector similarity weight |
| `habituation=0.10` | 0.2, 0.15, 0.1 | Repetition penalty weight |
| `24hr` persona TTL | 1hr, infinite, 12hr | Cache duration for persona |
| `5min` memory TTL | 1min, 15min, 10min | Cache duration for memories |

## Gradient Detail Levels (Exact Enum Values)

| Canonical | Threshold | Common Hallucinations |
|-----------|-----------|----------------------|
| `FULL` | ≥0.75 | COMPLETE, ALL, DETAILED |
| `CHUNKS` | ≥0.50 | PARTIAL, SEGMENTS, PIECES |
| `SUMMARY` | ≥0.20 | BRIEF, COMPRESSED, SHORT |
| `DROPPED` | <0.20 | OMITTED, SKIPPED, NONE |

## API Endpoints (Exact Routes)

| Canonical | Common Hallucinations |
|-----------|----------------------|
| `POST /v1/chat/stream` | /chat, /api/chat, /v1/chat |
| `GET /v1/specialists` | /specialists, /api/specialists |
| `GET /v1/schema` | /schema, /api/schema |
| `GET /v1/info` | /info, /api/info, /status |
| `GET /v1/healthz` | /health, /healthcheck, /ping |

## File Names (Exact)

| Canonical | Common Hallucinations |
|-----------|----------------------|
| `compose.yaml` | docker-compose.yml, docker-compose.yaml |
| `context.md` | CONTEXT.md, context.txt, README.md |
| `codebase-map.json` | codemap.json, modules.json |
| `pyproject.toml` | setup.py, setup.cfg |

## Function Names (Exact)

| Canonical | Location | Common Hallucinations |
|-----------|----------|----------------------|
| `chat_stream_v1` | brain/app.py | chat_stream, stream_chat, chat |
| `build_prompt` | prompt_assembler.py | create_prompt, assemble_prompt |
| `generate_stream` | brain/llm.py | stream_generate, generate |
| `calculate_importance` | context_retriever.py | compute_importance, get_importance |
| `get_detail_level` | context_retriever.py | detail_level, compute_detail |

---

## How to Use This File

**For AI assistants:**
1. Before outputting a class/function/path name, check if it's in this file
2. If it is: use the EXACT canonical form
3. If you're unsure: say "I believe it's called X but I'm not certain"
4. Never "correct" canonical names to more "standard" alternatives

**For humans:**
1. When adding new project-specific vocabulary, add it here
2. Include common hallucinations you've observed
3. This file is part of the documentation effectiveness formula

---

## Meta

This file is an experiment in **epistemic infrastructure**—teaching AI models where precision is required vs. where approximation is acceptable.

**Hypothesis:** Explicit canonicity markers reduce hallucination rates by signaling certainty requirements.

**Validation:** Benchmark with `tests/external_codebase_validation/` harness.
