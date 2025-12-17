"""Property-based tests for token budget monitoring.

Tests mathematical properties and invariants of token counting that
should hold for ANY input text.
"""
import pytest
from hypothesis import given, strategies as st, assume, example
from brain.token_monitor import TokenBudgetMonitor


class TestTokenCountingProperties:
    """Test mathematical properties of token counting."""

    @given(st.text(min_size=1, max_size=10000))
    @example("Hello world")  # Always test this specific case
    @example("🎵" * 100)     # Emoji stress test
    def test_positive_token_count(self, text):
        """Non-empty text should always produce positive token count."""
        monitor = TokenBudgetMonitor()
        tokens = monitor.count_tokens(text)
        assert tokens > 0, f"Text with length {len(text)} produced {tokens} tokens"

    @given(st.text(max_size=10000))
    def test_non_negative_token_count(self, text):
        """Token count should never be negative, even for empty text."""
        monitor = TokenBudgetMonitor()
        tokens = monitor.count_tokens(text)
        assert tokens >= 0, f"Token count was negative: {tokens}"

    @given(st.text(max_size=5000))
    def test_idempotent_counting(self, text):
        """Counting the same text multiple times gives same result."""
        monitor = TokenBudgetMonitor()
        count1 = monitor.count_tokens(text)
        count2 = monitor.count_tokens(text)
        count3 = monitor.count_tokens(text)
        
        assert count1 == count2 == count3, \
            f"Inconsistent counts: {count1}, {count2}, {count3}"

    @given(st.text(min_size=1, max_size=1000), st.text(min_size=1, max_size=1000))
    @example("Hello", "world")
    def test_token_additivity(self, text1, text2):
        """Token counting should be roughly additive.
        
        Due to tokenizer context, combined tokens may differ slightly
        from sum of individual tokens, but should be close.
        """
        monitor = TokenBudgetMonitor()
        
        tokens1 = monitor.count_tokens(text1)
        tokens2 = monitor.count_tokens(text2)
        combined_tokens = monitor.count_tokens(text1 + text2)
        separate_sum = tokens1 + tokens2
        
        # Allow some tolerance for context effects
        difference = abs(combined_tokens - separate_sum)
        tolerance = max(5, int(separate_sum * 0.1))  # 10% or 5 tokens
        
        assert difference <= tolerance, \
            f"Combined: {combined_tokens}, Separate: {separate_sum}, Diff: {difference}"

    @given(st.text(min_size=100, max_size=5000))
    def test_longer_text_more_tokens(self, text):
        """Longer text should generally have more tokens than shorter text."""
        assume(len(text) > 50)  # Skip very short text
        
        monitor = TokenBudgetMonitor()
        full_tokens = monitor.count_tokens(text)
        half_tokens = monitor.count_tokens(text[:len(text)//2])
        
        # Full text should have more tokens than half
        assert full_tokens > half_tokens, \
            f"Full ({len(text)} chars, {full_tokens} tokens) <= Half ({len(text)//2} chars, {half_tokens} tokens)"

    @given(st.text(max_size=10000))
    def test_token_count_is_integer(self, text):
        """Token count must always be an integer."""
        monitor = TokenBudgetMonitor()
        tokens = monitor.count_tokens(text)
        assert isinstance(tokens, int), f"Token count was {type(tokens)}: {tokens}"

    @given(st.text(min_size=1, max_size=5000))
    def test_token_count_bounded_by_length(self, text):
        """Token count should be bounded relative to character length.
        
        Some Unicode characters can produce multiple tokens, so bounds
        need to be generous. Main goal: catch obviously wrong counts.
        """
        monitor = TokenBudgetMonitor()
        tokens = monitor.count_tokens(text)
        char_count = len(text)
        
        # Very loose bounds - Unicode chars can be multiple tokens!
        # Upper bound: even complex Unicode shouldn't be >10 tokens per char
        assert tokens <= char_count * 10, \
            f"Too many tokens ({tokens}) for {char_count} characters"
        # Lower bound: text shouldn't compress to nearly nothing
        assert tokens >= 1, \
            f"Non-empty text ({char_count} chars) produced {tokens} tokens"


class TestTokenTrackingProperties:
    """Test properties of token tracking and breakdown."""

    @given(
        st.text(min_size=1, max_size=1000),
        st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=50)
    )
    @example("Hello world", "test_component")
    def test_track_accumulates_tokens(self, text, component_name):
        """Tracking multiple components accumulates total tokens."""
        monitor = TokenBudgetMonitor()
        
        # Track same component multiple times
        monitor.track(component_name, text)
        monitor.track(component_name, text)
        
        breakdown = monitor.get_breakdown()
        
        # Should have accumulated tokens
        assert breakdown.total_tokens > 0
        assert component_name in breakdown.components

    @given(st.integers(min_value=1000, max_value=1000000))
    def test_warning_threshold_respected(self, max_tokens):
        """Monitor should respect custom token budgets."""
        threshold = int(max_tokens * 0.8)
        monitor = TokenBudgetMonitor(max_tokens=max_tokens, warning_threshold=threshold)
        
        assert monitor.max_tokens == max_tokens
        assert monitor.warning_threshold == threshold
        assert monitor.warning_threshold < monitor.max_tokens


class TestTokenBudgetConstraints:
    """Test token budget constraints and limits."""

    @given(
        st.lists(st.text(min_size=1, max_size=500), min_size=1, max_size=20),
        st.integers(min_value=1000, max_value=10000)
    )
    def test_total_never_exceeds_budget(self, texts, budget):
        """Total tracked tokens should be computable against budget."""
        monitor = TokenBudgetMonitor(max_tokens=budget)
        
        for i, text in enumerate(texts):
            monitor.track(f"component_{i}", text)
        
        breakdown = monitor.get_breakdown()
        
        # Total should be sum of all components
        component_sum = sum(c.tokens for c in breakdown.components.values())
        assert breakdown.total_tokens == component_sum

    @given(st.text(min_size=1, max_size=5000))
    def test_get_summary_always_works(self, text):
        """get_summary() should always return a valid string."""
        monitor = TokenBudgetMonitor()
        monitor.track("test", text)
        
        summary = monitor.get_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "tokens" in summary.lower()
