# Ada Code Annotation Specification (@ada-*) v1.0

**Version:** 1.0.0  
**Status:** Draft  
**Date:** December 24, 2025  
**Authors:** Ada + Luna  
**License:** CC0 (Public Domain)  
**Parent Spec:** ASL v1.0 (Ada Symbol Language)

---

## Overview

The `@ada-*` annotation system provides a standardized way to document code using ASL (Ada Symbol Language). These annotations:

1. **Compress** documentation by 4-5x vs traditional docstrings
2. **Preserve** semantic meaning for both humans and machines
3. **Enable** automated tooling (LSP, linters, generators)
4. **Work** across all programming languages

---

## Annotation Types

### @ada-sig (Function Signature)

Defines the semantic type signature of a function.

**Format:** `@ada-sig: λname:(params)→return_type`

**Examples:**
```python
# @ada-sig: λfib:ℕ→ℕ
def fibonacci(n: int) -> int: ...

# @ada-sig: λauth:(𝕊,𝕊)→?Session
def authenticate(username: str, password: str) -> Session | None: ...

# @ada-sig: λfetch_all:[𝕊]→⏳[Response]
async def fetch_all(urls: list[str]) -> list[Response]: ...
```

**Type Symbols:**
| Symbol | Meaning | Python Equivalent |
|--------|---------|-------------------|
| `ℕ` | Natural number | `int` (≥0) |
| `ℤ` | Integer | `int` |
| `ℝ` | Real number | `float` |
| `𝕊` | String | `str` |
| `𝔹` | Boolean | `bool` |
| `?T` | Optional T | `T \| None` |
| `[T]` | List of T | `list[T]` |
| `{K:V}` | Dict | `dict[K,V]` |
| `⏳T` | Async T | `Awaitable[T]` |

---

### @ada-flow (Data/Control Flow)

Describes the flow of data through the function.

**Format:** `@ada-flow: input→transforms→output`

**Operators:**
| Symbol | Meaning |
|--------|---------|
| `→` | then / flows to |
| `↳` | else branch |
| `?()` | conditional |
| `⟲` | loop/recursion |
| `∥` | parallel |
| `⏳` | async |

**Examples:**
```python
# @ada-flow: (user,pass)→?(valid●)→Session ↳ ∅
def login(user, password): ...

# @ada-flow: items→filter(active●)→map(transform)→collect
def process_items(items): ...

# @ada-flow: ⟲(item←next)→?(done)→break ↳ process(item)
def iterate_until_done(iterator): ...

# @ada-flow: ⏳(∥(urls.map(fetch)))→filter(ok●)
async def fetch_all(urls): ...
```

---

### @ada-guards (Preconditions)

Specifies conditions that must be true before execution.

**Format:** `@ada-guards: condition₁ ∧ condition₂ ∧ ...`

**Examples:**
```python
# @ada-guards: n≥0
def factorial(n): ...

# @ada-guards: sorted●(items) ∧ len(items)>0
def binary_search(items, target): ...

# @ada-guards: ∃user ∧ user.active● ∧ rate_limit◕
def process_request(user, request): ...

# @ada-guards: ∀item∈items: item≠∅
def process_all(items): ...
```

---

### @ada-invariants (Class Invariants)

Conditions that must always be true for a class instance.

**Format:** `@ada-invariants: condition₁ ∧ condition₂`

**Examples:**
```python
# @ada-invariants: balance≥0 ∧ ∃owner
class BankAccount:
    ...

# @ada-invariants: ∀item∈items: item.valid● ∧ len≤max_size
class BoundedQueue:
    ...

# @ada-invariants: head=∅ ⟺ tail=∅ ⟺ size=0
class DoublyLinkedList:
    ...
```

---

### @ada-state (State Machine)

Describes valid state transitions.

**Format:** `@ada-state: state₁→state₂→(state₃∨state₄)`

**Examples:**
```python
# @ada-state: init→connecting→connected→(disconnected∨error)
class Connection:
    ...

# @ada-state: pending→?(approved●)→active ↳ rejected
class Application:
    ...

# @ada-state: idle⟷running ∧ (running→done∨failed)
class Task:
    ...
```

---

### @ada-complexity (Algorithmic Complexity)

Documents time and space complexity.

**Format:** `@ada-complexity: O(time), O(space)`

**Examples:**
```python
# @ada-complexity: O(n log n) time, O(1) space
def heap_sort(items): ...

# @ada-complexity: O(1) amortized, O(n) worst
def hash_insert(table, key, value): ...

# @ada-complexity: O(V+E) time, O(V) space
def bfs(graph, start): ...
```

---

### @ada-concurrency (Threading Model)

Documents thread safety and concurrency characteristics.

**Format:** `@ada-concurrency: properties`

**Symbols:**
| Symbol | Meaning |
|--------|---------|
| `∥-safe` | Thread-safe |
| `∥-unsafe` | Not thread-safe |
| `lock-free●` | Lock-free |
| `wait-free●` | Wait-free |
| `atomic●` | Atomic operations |
| `⊗reentrant` | Not reentrant |

**Examples:**
```python
# @ada-concurrency: ∥-safe ∧ lock-free●
class ConcurrentQueue:
    ...

# @ada-concurrency: ∥-unsafe ∧ ⊗reentrant
def update_global_state(): ...

# @ada-concurrency: ∥-safe ∧ atomic●(counter)
class AtomicCounter:
    ...
```

---

### @ada-errors (Error Conditions)

Documents what errors can be raised and when.

**Format:** `@ada-errors: condition→ErrorType`

**Examples:**
```python
# @ada-errors: n<0→ValueError ∧ overflow→OverflowError
def factorial(n): ...

# @ada-errors: ¬∃file→FileNotFoundError ∧ ¬readable→PermissionError
def read_file(path): ...

# @ada-errors: timeout→TimeoutError ∧ network⊗→ConnectionError
async def fetch(url): ...
```

---

### @ada-effects (Side Effects)

Documents side effects of a function.

**Format:** `@ada-effects: effect₁ ∧ effect₂`

**Symbols:**
| Symbol | Meaning |
|--------|---------|
| `📁⊕` | Creates file |
| `📁⊖` | Deletes file |
| `📁↻` | Modifies file |
| `🌐⚡` | Network call |
| `💾↻` | Database mutation |
| `📤console` | Console output |
| `∅effects` | Pure function |

**Examples:**
```python
# @ada-effects: ∅effects
def calculate_total(items): ...  # Pure function

# @ada-effects: 📁⊕ ∧ 📤console
def save_and_log(data, path): ...

# @ada-effects: 🌐⚡ ∧ 💾↻
async def sync_with_server(): ...
```

---

## Placement Rules

### Python

```python
def function_name():
    """Short description in ASL notation."""
    # @ada-sig: ...
    # @ada-flow: ...
    # @ada-guards: ...
    ...
```

Or in docstring:
```python
def function_name():
    """
    λfunc:(T)→U
    @ada-flow: input→process→output
    @ada-guards: valid●(input)
    """
    ...
```

### Rust

```rust
/// @ada-sig: λfunc:(T)→Result<U,E>
/// @ada-flow: input→?(valid●)→Ok(result) ↳ Err(e)
fn function_name(input: T) -> Result<U, E> {
    ...
}
```

### TypeScript

```typescript
/**
 * @ada-sig: λfetch:(𝕊)→⏳?Response
 * @ada-flow: url→⏳(⚡fetch)→?(ok●)→Response ↳ ∅
 */
async function fetchData(url: string): Promise<Response | null> {
    ...
}
```

### Go

```go
// @ada-sig: λRead:(io.Reader,[]byte)→(ℕ,?error)
// @ada-flow: r→read(buf)→?(err=∅)→n ↳ (0,err)
func Read(r io.Reader, buf []byte) (int, error) {
    ...
}
```

---

## Parsing Annotations

### Regex Pattern

```python
ANNOTATION_PATTERN = r'@ada-(\w+):\s*(.+?)(?=@ada-|\n\n|$)'
```

### Parser Implementation

```python
import re
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AdaAnnotations:
    sig: Optional[str] = None
    flow: Optional[str] = None
    guards: Optional[str] = None
    invariants: Optional[str] = None
    state: Optional[str] = None
    complexity: Optional[str] = None
    concurrency: Optional[str] = None
    errors: Optional[str] = None
    effects: Optional[str] = None

def parse_ada_annotations(source: str) -> AdaAnnotations:
    """Parse @ada-* annotations from source code."""
    pattern = r'@ada-(\w+):\s*(.+?)(?=@ada-|\n|$)'
    matches = re.findall(pattern, source, re.MULTILINE)
    
    annotations = AdaAnnotations()
    for name, value in matches:
        if hasattr(annotations, name):
            setattr(annotations, name, value.strip())
    
    return annotations
```

---

## Generating Traditional Documentation

Ada annotations can be expanded to traditional docstrings:

```python
def expand_to_google_style(annotations: AdaAnnotations) -> str:
    """Convert Ada annotations to Google-style docstring."""
    parts = []
    
    if annotations.sig:
        # Parse λname:(params)→return
        # Generate Args: and Returns: sections
        pass
    
    if annotations.guards:
        parts.append(f"Preconditions:\n    {expand_guards(annotations.guards)}")
    
    if annotations.errors:
        parts.append(f"Raises:\n    {expand_errors(annotations.errors)}")
    
    if annotations.complexity:
        parts.append(f"Complexity: {annotations.complexity}")
    
    return "\n\n".join(parts)
```

---

## Validation Rules

### @ada-sig Validation

1. Function name must match actual function
2. Parameter count must match
3. Return type must be compatible

### @ada-guards Validation

1. Referenced variables must exist in scope
2. Conditions must be evaluatable at runtime (for contract checking)

### @ada-invariants Validation

1. Must reference class attributes
2. Should be checkable after `__init__` and public methods

---

## IDE Integration

### Language Server Protocol (LSP)

Ada annotations can provide:
- **Hover**: Expand annotations to readable text
- **Completion**: Suggest symbols after `@ada-`
- **Diagnostics**: Validate annotations against code
- **CodeLens**: Show complexity inline

### VS Code Extension

```json
{
  "contributes": {
    "languages": [{
      "id": "ada-annotations",
      "extensions": [],
      "configuration": "./language-configuration.json"
    }],
    "grammars": [{
      "language": "ada-annotations",
      "scopeName": "source.ada-annotations",
      "path": "./syntaxes/ada-annotations.tmLanguage.json",
      "injectTo": ["source.python", "source.rust", "source.typescript"]
    }]
  }
}
```

---

## Examples

### Complete Function Documentation

```python
def binary_search(items: list[int], target: int) -> int | None:
    """λ([ℤ],ℤ)→?ℕ | sorted●(items)⟹⟲halving→?idx ↳ ∅"""
    # @ada-sig: λbinary_search:([ℤ],ℤ)→?ℕ
    # @ada-guards: sorted●(items) ∧ ∀item∈items: item∈ℤ
    # @ada-flow: ⟲(mid←(lo+hi)÷2 → ?(items[mid]≡target)→mid ↳ adjust_bounds) until lo>hi→∅
    # @ada-complexity: O(log n) time, O(1) space
    # @ada-effects: ∅effects
    # @ada-errors: ∅ (returns None on not found)
    
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return None
```

### Complete Class Documentation

```python
# @ada-invariants: ∀item∈_items: item≠∅ ∧ len(_items)≤max_size ∧ max_size>0
class BoundedQueue:
    """Thread-safe bounded queue with blocking operations."""
    # @ada-state: empty⟷partial⟷full
    # @ada-concurrency: ∥-safe ∧ uses(Lock)
    
    def __init__(self, max_size: int):
        """λ(ℕ)→BoundedQueue | max_size>0"""
        # @ada-guards: max_size>0
        # @ada-effects: ∅effects
        self.max_size = max_size
        self._items = []
        self._lock = Lock()
    
    def put(self, item):
        """λ(T)→𝔹 | ?(¬full●)→⊕item→True ↳ False"""
        # @ada-sig: λput:(T)→𝔹
        # @ada-flow: ?(len<max)→append(item)→True ↳ False
        # @ada-guards: item≠∅
        # @ada-concurrency: acquires(_lock)
        with self._lock:
            if len(self._items) < self.max_size:
                self._items.append(item)
                return True
            return False
```

---

## Relationship to Other Standards

### Google-Style Docstrings

Ada annotations can be **generated from** or **converted to** Google-style:

| Google-Style | Ada Equivalent |
|--------------|----------------|
| Args: | Parsed from @ada-sig params |
| Returns: | Parsed from @ada-sig return |
| Raises: | @ada-errors |
| Examples: | (Not covered - use doctest) |

### Type Hints (PEP 484)

Ada annotations **complement** type hints:
- Type hints: What types are accepted
- @ada-sig: Semantic meaning of types
- @ada-guards: Runtime constraints on values

### Design by Contract (PEP 316 - rejected)

Ada annotations provide a lighter-weight alternative:
- No runtime enforcement by default
- Machine-readable for static analysis
- Human-readable when expanded

---

## Changelog

### v1.0.0 (December 24, 2025)
- Initial release
- 9 annotation types defined
- Placement rules for Python, Rust, TypeScript, Go
- Parser specification
- IDE integration guidelines

---

*"Documentation should be as dense as the thought it represents."*  
— Ada, December 2025

