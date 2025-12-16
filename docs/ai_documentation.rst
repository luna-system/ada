AI-Readable Documentation
==========================

The ``.ai/`` Folder Pattern
----------------------------

During Ada's development, we discovered that AI assistants need different documentation than humans. This led to the emergence of the ``.ai/`` folder pattern.

The Problem
~~~~~~~~~~~

**Humans** need tutorials, examples, and narrative explanations.

**AI assistants** need structure, relationships, and architectural patterns.

Traditional approaches (single ``.cursorrules`` files, instructions in README) work for small projects but don't scale well.

Our Solution
~~~~~~~~~~~~

Ada uses a dedicated ``.ai/`` folder for machine-readable documentation:

.. code-block:: text

   .ai/
   ├── README.md               # Pattern explanation
   ├── context.md              # Architecture overview
   ├── codebase-map.json       # Module dependencies
   ├── CONVENTIONS.md          # Documentation strategy
   ├── QUICKSTART.md           # Common tasks
   ├── CLEANUP_NOTES.md        # Current status
   ├── GOTCHAS.md              # Known pitfalls
   └── PATTERN.md              # Meta-documentation

Plus **AI.md** in the repository root as an entry point.

Separation of Concerns
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Location
     - Audience
     - Content Type
   * - ``docs/*.rst``
     - Humans
     - Tutorials, examples, narrative
   * - ``.ai/*.{md,json}``
     - AI assistants
     - Structure, dependencies, patterns
   * - Inline comments
     - Developers
     - Code-level explanations

Why This Matters
~~~~~~~~~~~~~~~~~

**For AI assistants:**

- Faster architectural understanding
- Better code placement suggestions
- Fewer clarifying questions
- Understanding of project conventions

**For humans:**

- Documentation stays focused on their needs
- Less noise in tutorials
- Clear separation between "how to" and "how it works"

Not a Standard (Yet)
~~~~~~~~~~~~~~~~~~~~

This pattern emerged organically from our development process. We're sharing it as an example, not prescribing it as a rule.

**Key principles:**

- Start minimal (just ``AI.md`` + ``.ai/context.md``)
- Grow as needed
- Keep it current
- Adapt freely for your context

Learn More
~~~~~~~~~~

- **For AI assistants:** See `AI.md <https://github.com/luna-system/ada/blob/trunk/AI.md>`_ in the repository root
- **Pattern details:** See `.ai/PATTERN.md <https://github.com/luna-system/ada/blob/trunk/.ai/PATTERN.md>`_
- **Our implementation:** Browse the `.ai/ folder <https://github.com/luna-system/ada/tree/trunk/.ai>`_

Credits
-------

This pattern developed collaboratively by **luna system** and **Claude Sonnet 4.5** during Ada's development (2025).

Inspired by:

- Cursor's ``.cursorrules`` pattern
- The Aider project's context files  
- Decades of README-driven development
- Real pain points from AI-assisted development

The pattern is **public domain** - use and adapt freely!
