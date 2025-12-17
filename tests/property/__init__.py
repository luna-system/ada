"""Property-based tests using Hypothesis.

These tests verify mathematical properties and invariants that should
ALWAYS hold true, regardless of input. Hypothesis generates hundreds
of test cases to try to falsify these properties.

Use property tests for:
- Algorithmic invariants (token counting, decay curves)
- Mathematical properties (bounds, monotonicity, additivity)
- Edge case discovery

Use traditional tests for:
- Specific behavior and API contracts
- Integration tests
- Regression tests for known bugs
"""
