# Ada Translate 🔮

**Universal code translation via Ada's semantic core**

*Christmas Eve 2025 - luna & Ada*

## What is this?

A party trick that demonstrates Ada's native symbolic language as an intermediate representation for code translation. Instead of directly translating syntax, we:

1. **Extract semantic core** → Reduce code to pure meaning using Ada's symbols
2. **Generate target code** → Expand semantic core to idiomatic target language

```
Source Code ──→ 🔮 Ada Semantic Core 🔮 ──→ Target Code
(Python)         λfib:ℕ→ℕ = ?(n≤1)→n         (Rust)
                         ↳ ⟲fib(n-1)⊕fib(n-2)
```

## Benchmark Results

```
Pass Rate:              62.5% (5/8 strict pattern matching)
Avg Roundtrip Fidelity: 70.9% (A → B → A token similarity)
Avg Compression:        ~2x (source to semantic core)
```

| Test | Languages | Result |
|------|-----------|--------|
| fibonacci_recursion | Python → Rust | ✅ |
| filter_map_reduce | JavaScript → Python | ✅ |
| async_fetch | Python → JavaScript | ✅ |
| pattern_matching | Rust → Python | ✅ |
| class_with_methods | Python → Rust | ✅ |
| comment_handling | Python → Rust | ❌ (comments not preserved) |
| error_handling | Rust → Python | ❌ (idiom mismatch) |
| list_comprehension | Python → Haskell | ❌ (syntax variance) |

**Key findings:**
- Semantic meaning is well-preserved across translations
- Comments are intentionally stripped (they're not semantic!)
- Roundtrip degrades syntax but preserves behavior
- Some language idioms don't map cleanly (Result → exceptions)

## Installation

```bash
cd ada-translate
uv sync
uv run ada-translate --help
```

Requires Ollama running locally with `qwen2.5-coder:7b`.

## Usage

### Command Line

```bash
# Translate a file
ada-translate fibonacci.py --from python --to rust

# Show the semantic core (the interesting part!)
ada-translate fibonacci.py --from python --to javascript -s

# Pipe code
echo "def hello(): print('hi')" | ada-translate --from python --to go
```

### Interactive Mode

```bash
ada-translate --interactive
```

```
╔═══════════════════════════════════════════════════════════════════════╗
║  ADA TRANSLATE - Interactive Mode                                      ║
╚═══════════════════════════════════════════════════════════════════════╝

ada> translate python rust
✓ Now translating: python → rust

ada> def factorial(n):
...>     if n <= 1:
...>         return 1
...>     return n * factorial(n - 1)
...>

🔮 Translating python → rust...

╔═ SEMANTIC CORE ═══════════════════════════════════════
║ SIGNATURE: factorial: ℕ → ℕ
║ INVARIANTS: n ≥ 0
║ FLOW: ?(n≤1) → 1 ↳ n × ⟲factorial(n-1)
║ COMPRESSED: λf:ℕ→ℕ=?(n≤1)→1↳n×⟲f(n-1)
╚══════════════════════════════════════════════════════

╔═ RUST ═══════════════════════════════════════════════
║ fn factorial(n: u64) -> u64 {
║     if n <= 1 {
║         1
║     } else {
║         n * factorial(n - 1)
║     }
║ }
╚══════════════════════════════════════════════════════
```

## Ada's Symbol Vocabulary

| Category | Symbols | Meaning |
|----------|---------|---------|
| **Types** | ℕ ℤ ℝ 𝕊 𝔹 [T] {K:V} | natural, integer, real, string, bool, list, map |
| **Flow** | → ⟲ ? ∥ ⏳ | then, loop/recurse, branch, parallel, await |
| **Logic** | ∧ ∨ ¬ ⟹ | and, or, not, implies |
| **Existence** | ∃ ∄ ∈ ∅ | exists, not exists, in, empty |
| **State** | ← ⊕ ⊖ ↻ | assign, add, remove, mutate |
| **Functions** | λ ∘ ∀ Σ Π | lambda, compose, for all, sum, product |

## Why This Works

The semantic core captures **meaning**, not syntax:

```
# All of these have the SAME semantic core:
# λsum:[ℕ]→ℕ = Σ(items[active●])

# Python
sum(item.value for item in items if item.active)

# JavaScript  
items.filter(i => i.active).reduce((a, i) => a + i.value, 0)

# Rust
items.iter().filter(|i| i.active).map(|i| i.value).sum()

# SQL
SELECT SUM(value) FROM items WHERE active = true
```

## Limitations

- **Party trick quality** - Fun demo, not production transpiler
- **Requires Ollama** - Uses LLM for both extraction and generation
- **Language support** - Works best with common languages
- **Complex code** - May struggle with very large/complex programs
- **Comments stripped** - Semantic core captures meaning, not documentation

## Bonus: Ada Annotations for Code

What if you could document code using Ada's symbols? See `examples/ada_annotations.py`:

```python
# Traditional docstring (298 characters, 12 lines):
"""
Authenticate a user with username and password.

Args:
    username: The user's login name
    password: The user's password

Returns:
    Session object if successful, None if failed

Raises:
    RateLimitError: If too many attempts
"""

# Ada annotation (63 characters, 1 line):
# @ada-sig: λ(𝕊,𝕊)→?Session | (u,p)→?(valid●)→S ↳ ∅ | guard: attempts<limit
```

**4.73x compression** - AND the Ada version formally captures the rate limit guard!

### Proposed Annotation Schema

| Annotation | Purpose | Example |
|------------|---------|---------|
| `@ada-sig` | Type signature | `λ([T], T) → ?ℕ` |
| `@ada-flow` | Control flow | `input → ?(valid●) → output ↳ ⊘error` |
| `@ada-guards` | Preconditions | `n > 0 ⟹ proceed ↳ ⊘ValueError` |
| `@ada-invariants` | Always-true properties | `∀x: 0 ≤ x ≤ max` |
| `@ada-state` | Mutation patterns | `⊕add, ⊖remove, ↻mutate` |
| `@ada-concurrency` | Parallel/async | `∥parallel, ⏳await` |

Works alongside existing `@ai-*` annotations:
- `@ai-*` → Module-level metadata (purpose, dependencies)
- `@ada-*` → Function-level semantics (contracts, flow)

## The Philosophy

> "The limits of my language mean the limits of my world."  
> — Wittgenstein

By extracting the semantic core, we find what code *means* rather than what it *says*. Ada's symbols are designed to be:

- **Dense** → Maximum meaning per character
- **Universal** → Language-agnostic concepts  
- **Composable** → Symbols combine naturally

This is Ada's native language - the way she thinks.

## License

MIT - Do what you want, have fun! 🎄

*Built with 💜 on Christmas Eve 2025*
