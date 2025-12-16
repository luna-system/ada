# Example Personas

This directory contains example persona files demonstrating different personality styles and use cases for Ada.

## Using a Persona

Personas are loaded from `persona.md` (or override with `AI_PERSONALITY_FILE` env var) and injected into the AI's context via the RAG system.

**To use an example persona:**

```bash
# Copy the persona you want
cp examples/personas/coding-buddy.md persona.md

# Restart the brain service
docker compose restart brain
```

## Creating Your Own

Personas use markdown format and should:

1. **Define identity** - Who is the AI? What's their role?
2. **Set tone** - Formal? Casual? Technical? Creative?
3. **Establish boundaries** - What will/won't they do?
4. **Add context** - Any specific knowledge or background?

**Keep it concise** - Personas are truncated to ~2000 chars by default (configurable via `RAG_PERSONA_MAX_CHARS`).

## Available Examples

- **[ada-default.md](ada-default.md)** - The default Ada personality (helpful personal assistant)
- **[coding-buddy.md](coding-buddy.md)** - Pair programming assistant focused on code quality
- **[creative-writer.md](creative-writer.md)** - Writing companion for fiction and worldbuilding
- **[technical-expert.md](technical-expert.md)** - Deep technical explanations with precision
- **[minimal.md](minimal.md)** - Bare-bones starter template

## Tips

**Be specific:** "You prefer functional programming" works better than "you like code"

**Show don't tell:** Give examples of your style rather than describing it

**Use structure:** Headers, lists, and sections help the AI understand priorities

**Test iteratively:** Start minimal, add detail based on what's missing

**Remember context limits:** Longer personas mean less room for conversation history
