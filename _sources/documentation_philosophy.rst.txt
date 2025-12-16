==========================
Documentation Philosophy
==========================

Our Approach
============

Ada's documentation reflects core beliefs about how technical knowledge should be shared and preserved:

**Documentation is infrastructure, not afterthought.**

We treat documentation with the same rigor as code - tested, validated, versioned, and maintained as a first-class component of the system.

Core Principles
===============

1. Documentation Serves Multiple Audiences
-------------------------------------------

We maintain parallel documentation layers:

- **Human documentation** (Sphinx/RST) - For developers, operators, and contributors
- **Machine documentation** (``.ai/`` directory) - For AI assistants working with the codebase

Each layer is optimized for its audience without compromise. We don't force humans to read JSON schemas, and we don't expect AI to parse prose-heavy tutorials.

2. Context Over Comprehensiveness
----------------------------------

Every piece of documentation answers: **"What do you need to know RIGHT NOW?"**

We prioritize:

- Quick starts over exhaustive references
- Examples over abstract descriptions  
- "Why this way" over "here's the API"
- Decision context over just decisions

If you can't find what you need in 30 seconds, we've failed.

3. Empathy Creates Better Understanding
----------------------------------------

Technical documentation shouldn't be cold. We explain:

- **Why something seems right** before explaining why it's wrong
- **What problem this solves** before diving into how it works
- **Where you probably are** when you're reading this

This applies to both human readers and AI assistants. Understanding the reasoning behind a pattern creates stronger learning than memorizing rules.

See :doc:`empathetic_documentation` for how this emerged.

4. Living Documentation
-----------------------

Documentation that drifts from reality is worse than no documentation.

Our approach:

- **Automated validation** - Tests verify that documented code paths exist
- **CI integration** - Documentation checks run on every commit
- **Source annotations** - Key information lives in code comments (``@ai-*`` tags)
- **Pre-commit hooks** - Prevent inconsistencies before they're committed

When code changes, documentation breaks loudly.

5. Self-Referential Systems
----------------------------

Ada can read her own documentation via the ``docs`` specialist.

This isn't just clever - it's practical. When asked "How do I work?", Ada can search her Sphinx docs and provide accurate, up-to-date answers. The system documents itself to itself.

6. Transparency About Limitations
----------------------------------

We document what DOESN'T work, what we DON'T support, and what common approaches DON'T apply here.

The ``.ai/GOTCHAS.md`` file exists because "here's what to avoid" is as valuable as "here's what to do." Maybe more valuable.

Why This Matters
=================

Projects without documentation philosophy default to:

- ✗ Inconsistent formatting and structure
- ✗ Outdated examples that break
- ✗ Tribal knowledge trapped in team members' heads
- ✗ "Just read the code" attitude
- ✗ Documentation as punishment duty

Projects WITH documentation philosophy:

- ✓ New contributors onboard quickly
- ✓ Future maintainers understand decisions
- ✓ AI assistants provide accurate help
- ✓ Debugging is faster with clear references
- ✓ Writing docs is part of the craft

Our Opinionated Stances
========================

**Code comments should explain WHY, not WHAT**
   The code already shows what it does. Comments should capture reasoning, trade-offs, and context that isn't obvious from reading the implementation.

**Examples beat explanations**
   Show a working example first, then explain the details. People learn by doing.

**Machine-readable documentation is the future**
   As AI assistants become standard development tools, optimizing documentation for AI consumption isn't optional - it's necessary.

**Documentation shouldn't require a degree in RST/Markdown/LaTeX**
   Simple formatting, clear structure. Fancy rendering is secondary to clarity.

**If you can't test it, don't document it**
   Untestable documentation will drift. If it matters enough to document, it matters enough to validate.

**"Read the docs" should actually work**
   Documentation exists to be read, not to exist. If people keep asking questions that are "in the docs," the docs failed.

In Practice
===========

When contributing to Ada:

- Add human docs (RST) for features, architecture, usage
- Add machine docs (``.ai/``) for structural changes, new modules, specialists  
- Update ``codebase-map.json`` when module relationships change
- Add ``@ai-*`` annotations to significant functions/classes
- Run ``scripts/lint_ai_docs.py`` before committing
- Check that your docs answer "What would I need to know?"

The Goal
========

When someone - human or AI - needs to understand Ada, they should:

1. Find what they need quickly
2. Understand the context and reasoning
3. See working examples
4. Know what to avoid
5. Trust that it's current

That's it. Everything else is implementation detail.

---

*This philosophy emerged from building Ada collaboratively between human developers and AI assistants in 2025. It will evolve as we learn more about effective human-AI knowledge sharing.*
