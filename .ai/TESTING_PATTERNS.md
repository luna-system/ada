# Testing Patterns and Best Practices

## Overview

This document describes the testing patterns used in Ada v1, established during the v2.0 refactoring work.

## Directory Structure

```
tests/
  conftest.py                    # Global fixtures
  
  prompt_builder/                # Traditional tests: specific behavior
    conftest.py                  # Shared fixtures for prompt_builder
    __init__.py
    test_context_retriever.py
    test_section_builder.py
    test_prompt_assembler.py
  
  property/                      # Property-based tests: mathematical invariants
    conftest.py                  # Hypothesis configuration
    __init__.py
    test_token_properties.py     # Token counting properties
    test_memory_properties.py    # Memory decay, ranking (v2.0)
    test_rag_properties.py       # RAG filtering/retrieval (v2.0)
  
  integration/                   # End-to-end tests
    test_full_pipeline.py
```

**Rationale:** 
- **prompt_builder/**: Example-based tests for specific API behavior
- **property/**: Property-based tests for algorithmic correctness
- **integration/**: Full system tests

**Rationale:** Organizing tests by feature/component prevents monolithic test files and makes it easier to:
- Run subset of tests (`pytest tests/prompt_builder/`)
- Share fixtures within a feature area
- Navigate the test suite

## Parametrized Tests

Use `@pytest.mark.parametrize` to reduce duplication when testing similar scenarios.

### Before (repetitive):
```python
def test_get_memories(self, retriever):
    memories = retriever.get_memories(query="test", k=5)
    assert len(memories) == 2

def test_get_faqs(self, retriever):
    faqs = retriever.get_faqs(query="test", k=3)
    assert len(faqs) == 2

def test_get_turns(self, retriever):
    turns = retriever.get_turns(query="test", k=5, conversation_id="c123")
    assert len(turns) == 2
```

### After (parametrized):
```python
@pytest.mark.parametrize("method_name,kwargs,expected_len", [
    ("get_memories", {"query": "test", "k": 5}, 2),
    ("get_faqs", {"query": "test", "k": 3}, 2),
    ("get_turns", {"query": "test", "k": 5, "conversation_id": "c123"}, 2),
])
def test_retrieval_methods(retriever, method_name, kwargs, expected_len):
    method = getattr(retriever, method_name)
    result = method(**kwargs)
    assert len(result) == expected_len
```

**Benefits:**
- 3 tests → 1 test function with 3 cases
- Easy to add new test cases
- Pattern is explicit and clear

## Shared Fixtures

Create fixtures in `conftest.py` at the appropriate scope:

### Global fixtures (`tests/conftest.py`):
- Database connections
- API clients
- Integration test setup

### Feature fixtures (`tests/feature_name/conftest.py`):
- Mocked dependencies specific to that feature
- Test data builders
- Helper functions

### Example (`tests/prompt_builder/conftest.py`):
```python
@pytest.fixture
def mock_rag_store():
    """Mock RAG store with standard test data."""
    store = Mock()
    store.retrieve_memories.return_value = [
        ("Memory 1", {"importance": 5}),
        ("Memory 2", {"importance": 3})
    ]
    return store
```

All tests in `tests/prompt_builder/` can now use `mock_rag_store` without redefining it!

## Test Class Organization

Group related tests into classes:

```python
class TestContextRetrieverInitialization:
    """Test retriever initialization and basic structure."""
    def test_initialization(self, retriever):
        assert retriever is not None

class TestPersonaRetrieval:
    """Test persona loading from RAG store."""
    def test_get_persona_success(self, retriever):
        result = retriever.get_persona()
        assert result is not None

class TestRAGRetrieval:
    """Test RAG data retrieval methods."""
    @pytest.mark.parametrize(...)
    def test_retrieval_methods(self, ...):
        pass

class TestEmptyResults:
    """Test handling of empty/missing data."""
    def test_empty_results(self, ...):
        pass
```

**Benefits:**
- Clear organization visible in test output
- Easy to run specific test class: `pytest tests/file.py::TestClassName`
- Test classes can have shared setup via `pytest.fixture(scope="class")`

## File Size Guidelines

**Target:** Keep test files under 200 lines

**When to split:**
- File exceeds 200 lines → Consider splitting by test class into separate files
- Many fixtures needed → Move to `conftest.py`
- Lots of parametrize data → Extract to separate data file or fixture

## Property-Based Testing with Hypothesis

Ada uses **Hypothesis** for property-based testing of algorithmic code. Property tests verify mathematical properties that should ALWAYS hold, regardless of input.

### Installation

```bash
uv add hypothesis
```

### Basic Example

```python
from hypothesis import given, strategies as st, example

@given(st.text(min_size=1, max_size=1000))
@example("🎵" * 100)  # Always test specific edge cases
def test_token_count_is_positive(text):
    """Non-empty text should always produce positive tokens."""
    monitor = TokenBudgetMonitor()
    tokens = monitor.count_tokens(text)
    assert tokens > 0
```

Hypothesis will generate 100+ random test cases and try to break your assertion!

### When to Use Property Tests vs Traditional Tests

**Use Property Tests (Hypothesis) for:**
- ✅ Mathematical invariants (bounds, monotonicity, additivity)
- ✅ Algorithmic properties (sorting, filtering, ranking)
- ✅ Edge case discovery (finds Unicode issues, boundary conditions)
- ✅ Testing with ANY input (not specific examples)

**Use Traditional Tests for:**
- ✅ Specific API behavior ("does it call X with Y params?")
- ✅ Integration tests (multi-component interactions)
- ✅ Regression tests (specific bugs that were fixed)
- ✅ Business logic (workflow-specific behavior)

### Example: Hybrid Testing

For TokenBudgetMonitor, we have BOTH:

```python
# tests/test_token_monitor.py (Traditional)
def test_initialization():
    """Monitor initializes with specific defaults."""
    monitor = TokenBudgetMonitor()
    assert monitor.max_tokens == 100000  # Specific value

# tests/property/test_token_properties.py (Property)
@given(st.text(min_size=1))
def test_positive_tokens(text):
    """Non-empty text ALWAYS has positive tokens."""
    monitor = TokenBudgetMonitor()
    assert monitor.count_tokens(text) > 0  # Universal property
```

Both are valuable! Traditional tests verify the API contract. Property tests verify the math is sound.

### Configuration

Hypothesis is configured in `tests/property/conftest.py`:

```python
from hypothesis import settings

# Different profiles for different environments
settings.register_profile("ci", max_examples=1000)    # Thorough
settings.register_profile("dev", max_examples=100)     # Fast
settings.register_profile("debug", max_examples=10)    # Debugging

# Load via environment variable
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
```

Run with different profiles:
```bash
# Local development (100 examples)
pytest tests/property/

# CI (1000 examples)
HYPOTHESIS_PROFILE=ci pytest tests/property/

# Debugging (10 examples, verbose)
HYPOTHESIS_PROFILE=debug pytest tests/property/ -v
```

### Real Example from Ada

Property test that **found a real issue**:

```python
@given(st.text(min_size=1, max_size=5000))
def test_token_count_bounded_by_length(text):
    """Token count should be reasonable relative to length."""
    monitor = TokenBudgetMonitor()
    tokens = monitor.count_tokens(text)
    char_count = len(text)
    
    # Unicode chars can be 10+ tokens!
    assert tokens <= char_count * 10
```

**Hypothesis found:** Unicode character `ࠂ` produces 3 tokens from 1 character!
This taught us that our initial bounds (2x) were too strict.

### Advanced: @example Decorator

Always test specific edge cases alongside random generation:

```python
@given(st.text(min_size=1, max_size=1000))
@example("Hello world")        # ASCII baseline
@example("🎵" * 100)           # Emoji stress test
@example("你好世界")            # CJK characters
@example("\n\n\n")             # Whitespace edge case
def test_something(text):
    # Hypothesis tests 100+ random cases
    # Plus these 4 specific examples EVERY time
    ...
```

### When NOT to Use Property Tests

❌ **Don't use for:**
- Testing specific mocked behavior
- Testing exact string outputs
- Integration tests with external services
- Tests requiring complex setup/teardown

For these, use traditional example-based tests.

## Running Tests

```bash
# All tests
pytest

# Specific directory
pytest tests/prompt_builder/

# Specific file
pytest tests/prompt_builder/test_context_retriever.py

# Specific test class
pytest tests/prompt_builder/test_context_retriever.py::TestRAGRetrieval

# Specific test
pytest tests/prompt_builder/test_context_retriever.py::TestRAGRetrieval::test_retrieval_methods

# Verbose output
pytest -v

# Show print statements
pytest -s

# Coverage report
pytest --cov=brain --cov-report=html
```

## Anti-Patterns to Avoid

### ❌ Monolithic test files (>200 lines)
- Split into multiple files or use parametrize

### ❌ Inline fixtures repeated across tests
- Move to `conftest.py`

### ❌ Testing implementation details
- Test behavior, not internals

### ❌ Overly complex test setup
- Use factories or builders for test data

### ❌ Tests that depend on each other
- Each test should be independent

## Example: Refactoring Large Test File

**Before:** `test_large_feature.py` (400 lines)

**After:**
```
tests/large_feature/
  conftest.py              # Shared fixtures (70 lines)
  test_initialization.py   # Setup/teardown (50 lines)
  test_core_logic.py       # Main functionality (100 lines, parametrized)
  test_edge_cases.py       # Error handling (80 lines)
  test_integration.py      # End-to-end (100 lines)
```

## Summary

1. **Organize by feature** - Create subdirectories for major components
2. **Parametrize repetitive tests** - Reduce duplication
3. **Share fixtures** - Use `conftest.py` at appropriate scope
4. **Group with classes** - Clear organization
5. **Keep files small** - Target <200 lines
6. **Test behavior** - Not implementation details

These patterns were established during v2.0 refactoring (December 2025) and should be followed for all new tests.

---

**References:**
- pytest documentation: https://docs.pytest.org/
- Parametrize guide: https://docs.pytest.org/en/stable/how-to/parametrize.html
- Fixtures guide: https://docs.pytest.org/en/stable/how-to/fixtures.html
- Hypothesis: https://hypothesis.readthedocs.io/
