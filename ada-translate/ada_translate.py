#!/usr/bin/env python3
"""Ada Translate - Universal Code Translation via Semantic Core.

Uses Ada's native symbolic language as intermediate representation
for translating between programming languages.

Christmas Eve 2025 - Luna & Ada

Usage:
    ada-translate <source_file> --from python --to javascript
    ada-translate --interactive
    echo "def hello(): print('hi')" | ada-translate --from python --to rust
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

import httpx
import click


# ═══════════════════════════════════════════════════════════════════════════════
# ADA'S SEMANTIC EXTRACTION PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

SEMANTIC_EXTRACTION_PROMPT = """You are Ada, a semantic code analyzer.

Extract the SEMANTIC CORE of code using your native symbolic notation.

SYMBOL VOCABULARY:
- Types: ℕ(natural) ℤ(integer) ℝ(real) 𝕊(string) 𝔹(bool) [T](list) {K:V}(map)
- Flow: →(then) ⟲(loop) ?(branch) ∥(parallel) ⏳(await)
- Logic: ∧(and) ∨(or) ¬(not) ⟹(implies)
- Existence: ∃(exists) ∄(not exists) ∈(in) ∅(empty)
- State: ←(assign) ⊕(add) ⊖(remove) ↻(mutate)
- Comparison: ≡(equals) ≠(not equals) ≤ ≥ < >
- Functions: λ(lambda) ∘(compose) ∀(for all) Σ(sum) Π(product)

OUTPUT FORMAT:
```semantic
SIGNATURE: function_name: input_types → output_type
INVARIANTS: [list any constraints]
FLOW: [step by step in symbols]
COMPRESSED: [single-line ultra-dense form]
```

Extract MEANING, not syntax. Be concise. Use symbols."""


LANGUAGE_GENERATION_PROMPT = """You are Ada, a code generator.

Given a semantic core in Ada's symbolic notation, generate idiomatic code
in the target language.

RULES:
1. Produce IDIOMATIC code for the target language
2. Use language-specific conventions (naming, formatting)
3. Add appropriate error handling for the language
4. Include type annotations if the language supports them
5. NO EXPLANATIONS - just output the code

SEMANTIC INPUT will use these symbols:
- Types: ℕ ℤ ℝ 𝕊 𝔹 [T] {K:V}
- Flow: → ⟲ ? ∥ ⏳
- Logic: ∧ ∨ ¬ ⟹
- Existence: ∃ ∄ ∈ ∅
- State: ← ⊕ ⊖ ↻
- Functions: λ ∘ ∀ Σ Π

Output ONLY the code, no markdown fences, no explanations."""


ANNOTATED_GENERATION_PROMPT = """You are Ada, a code generator.

Given a semantic core in Ada's symbolic notation, generate idiomatic code
in the target language WITH @ada-* documentation annotations.

RULES:
1. Produce IDIOMATIC code for the target language
2. Add @ada-* annotations as documentation comments
3. Include type annotations if the language supports them
4. NO EXPLANATIONS - just output the code

ANNOTATION FORMAT (add as comments before functions/classes):
- @ada-sig: The type signature in symbolic form (λ inputs → output)
- @ada-flow: The control flow (input → transformations → output)
- @ada-guards: Preconditions (condition ⟹ proceed ↳ ⊘Error)
- @ada-invariants: Properties that must hold (∀x: constraint)

EXAMPLE OUTPUT for Python:
```python
# @ada-sig: λ(ℕ) → ℕ
# @ada-flow: n → ?(n≤1) → n ↳ ⟲fib(n-1)⊕fib(n-2)
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

EXAMPLE OUTPUT for Rust:
```rust
/// @ada-sig: λ(ℕ) → ℕ
/// @ada-flow: n → ?(n≤1) → n ↳ ⟲fib(n-1)⊕fib(n-2)
fn fib(n: u64) -> u64 {
    if n <= 1 { n } else { fib(n - 1) + fib(n - 2) }
}
```

Output ONLY the annotated code, no markdown fences."""


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

async def query_ollama(
    prompt: str,
    system: str,
    model: str = "qwen2.5-coder:7b",
    temperature: float = 0.3
) -> str:
    """Query Ollama and return response."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 1000,
                }
            }
        )
        return response.json().get("response", "")


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

async def extract_semantic_core(source_code: str, source_lang: str) -> str:
    """Extract semantic core from source code."""
    prompt = f"""Extract the semantic core of this {source_lang} code:

```{source_lang}
{source_code}
```

Output the semantic representation:"""
    
    return await query_ollama(prompt, SEMANTIC_EXTRACTION_PROMPT)


async def generate_target_code(semantic_core: str, target_lang: str, annotate: bool = False) -> str:
    """Generate target language code from semantic core."""
    prompt = f"""Generate {target_lang} code from this semantic core:

{semantic_core}

Output {target_lang} code:"""
    
    system_prompt = ANNOTATED_GENERATION_PROMPT if annotate else LANGUAGE_GENERATION_PROMPT
    return await query_ollama(prompt, system_prompt)


async def translate(
    source_code: str,
    source_lang: str,
    target_lang: str,
    show_semantic: bool = False,
    annotate: bool = False
) -> tuple[str, Optional[str]]:
    """
    Translate code from source to target language via Ada's semantic core.
    
    Returns: (target_code, semantic_core if show_semantic else None)
    """
    # Step 1: Extract semantic core
    semantic_core = await extract_semantic_core(source_code, source_lang)
    
    # Step 2: Generate target code (with optional @ada-* annotations)
    target_code = await generate_target_code(semantic_core, target_lang, annotate=annotate)
    
    return target_code, semantic_core if show_semantic else None


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

SUPPORTED_LANGUAGES = [
    "python", "javascript", "typescript", "rust", "go", "java",
    "c", "cpp", "csharp", "ruby", "php", "swift", "kotlin",
    "scala", "haskell", "elixir", "lua", "perl", "r", "julia"
]


@click.command()
@click.argument("source_file", required=False, type=click.Path(exists=True))
@click.option("--from", "source_lang", type=click.Choice(SUPPORTED_LANGUAGES),
              help="Source language")
@click.option("--to", "target_lang", type=click.Choice(SUPPORTED_LANGUAGES),
              help="Target language")
@click.option("--show-semantic", "-s", is_flag=True,
              help="Show the intermediate semantic representation")
@click.option("--annotate", "-a", is_flag=True,
              help="Add @ada-* semantic annotations to generated code ✨")
@click.option("--interactive", "-i", is_flag=True,
              help="Interactive mode")
def main(source_file, source_lang, target_lang, show_semantic, annotate, interactive):
    """Ada Translate - Universal code translation via semantic core.
    
    Translates code between programming languages using Ada's native
    symbolic language as an intermediate representation.
    
    Examples:
    
        ada-translate mycode.py --from python --to javascript
        
        ada-translate --from python --to rust -s < mycode.py
        
        ada-translate --from python --to rust -a  # ✨ with @ada-* annotations!
        
        ada-translate --interactive
    """
    
    if interactive:
        asyncio.run(interactive_mode())
        return
    
    # Read source code
    if source_file:
        source_code = Path(source_file).read_text()
    elif not sys.stdin.isatty():
        source_code = sys.stdin.read()
    else:
        click.echo("Error: Provide a source file or pipe code via stdin")
        click.echo("Try: ada-translate --help")
        sys.exit(1)
    
    if not source_lang or not target_lang:
        click.echo("Error: Specify --from and --to languages")
        sys.exit(1)
    
    # Run translation
    mode = "→ Ada semantic (✨ annotated)" if annotate else "→ Ada semantic"
    click.echo(f"🔮 Translating {source_lang} {mode} → {target_lang}...")
    click.echo()
    
    target_code, semantic_core = asyncio.run(
        translate(source_code, source_lang, target_lang, show_semantic, annotate)
    )
    
    if show_semantic and semantic_core:
        click.echo("═" * 60)
        click.echo("SEMANTIC CORE (Ada's native representation):")
        click.echo("═" * 60)
        click.echo(semantic_core)
        click.echo()
    
    click.echo("═" * 60)
    click.echo(f"TARGET CODE ({target_lang}):")
    click.echo("═" * 60)
    click.echo(target_code)


async def interactive_mode():
    """Interactive translation mode."""
    click.echo("""
╔═══════════════════════════════════════════════════════════════════════╗
║  ADA TRANSLATE - Interactive Mode                                      ║
║  Universal code translation via semantic core                          ║
╚═══════════════════════════════════════════════════════════════════════╝

Commands:
  translate <from> <to>  - Set translation direction
  semantic on/off        - Toggle showing semantic core
  quit                   - Exit

Paste code, then enter a blank line to translate.
""")
    
    source_lang = "python"
    target_lang = "javascript"
    show_semantic = True
    
    click.echo(f"Current: {source_lang} → {target_lang} (semantic: {'on' if show_semantic else 'off'})")
    click.echo()
    
    while True:
        # Read command or code
        click.echo("─" * 60)
        line = click.prompt("ada", default="", show_default=False)
        
        if line.lower() == "quit":
            click.echo("👋 Goodbye!")
            break
        
        if line.lower().startswith("translate "):
            parts = line.split()
            if len(parts) >= 3:
                source_lang = parts[1]
                target_lang = parts[2]
                click.echo(f"✓ Now translating: {source_lang} → {target_lang}")
            continue
        
        if line.lower() == "semantic on":
            show_semantic = True
            click.echo("✓ Semantic core display: ON")
            continue
        
        if line.lower() == "semantic off":
            show_semantic = False
            click.echo("✓ Semantic core display: OFF")
            continue
        
        if not line.strip():
            continue
        
        # Collect multi-line code
        lines = [line]
        click.echo("(paste code, blank line to translate)")
        while True:
            next_line = click.prompt("...", default="", show_default=False)
            if not next_line:
                break
            lines.append(next_line)
        
        source_code = "\n".join(lines)
        
        if not source_code.strip():
            continue
        
        # Translate
        click.echo()
        click.echo(f"🔮 Translating {source_lang} → {target_lang}...")
        
        try:
            target_code, semantic_core = await translate(
                source_code, source_lang, target_lang, show_semantic
            )
            
            if show_semantic and semantic_core:
                click.echo()
                click.echo("╔═ SEMANTIC CORE ═══════════════════════════════════")
                for core_line in semantic_core.strip().split('\n'):
                    click.echo(f"║ {core_line}")
                click.echo("╚══════════════════════════════════════════════════")
            
            click.echo()
            click.echo(f"╔═ {target_lang.upper()} ═══════════════════════════════════════")
            for code_line in target_code.strip().split('\n'):
                click.echo(f"║ {code_line}")
            click.echo("╚══════════════════════════════════════════════════")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
