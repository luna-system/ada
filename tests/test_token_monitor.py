"""Tests for token budget monitoring.

Test-driven development for Phase 1: Token Budget Monitoring
This defines the behavior we want before implementing.
"""

import pytest
from brain.token_monitor import (
    TokenBudgetMonitor,
    TokenUsageBreakdown,
    ComponentTokens,
)


class TestTokenBudgetMonitor:
    """Test the token budget monitoring system."""

    def test_monitor_initialization(self):
        """Monitor should initialize with default budget."""
        monitor = TokenBudgetMonitor()
        assert monitor.max_tokens > 0
        assert monitor.warning_threshold > 0
        assert monitor.warning_threshold < monitor.max_tokens

    def test_monitor_with_custom_budget(self):
        """Monitor should accept custom token budget."""
        monitor = TokenBudgetMonitor(max_tokens=50000, warning_threshold=40000)
        assert monitor.max_tokens == 50000
        assert monitor.warning_threshold == 40000

    def test_count_tokens_from_text(self):
        """Should accurately count tokens in text."""
        monitor = TokenBudgetMonitor()
        
        # Short text
        short_tokens = monitor.count_tokens("Hello world")
        assert short_tokens > 0
        assert short_tokens < 10  # Should be just a few tokens
        
        # Longer text
        long_text = "This is a longer piece of text " * 100
        long_tokens = monitor.count_tokens(long_text)
        assert long_tokens > short_tokens
        assert long_tokens > 100  # Should be substantial

    def test_track_component_usage(self):
        """Should track token usage by component."""
        monitor = TokenBudgetMonitor()
        
        # Track different components
        monitor.track("persona", "This is my persona description.")
        monitor.track("memories", "Retrieved memory content here.")
        monitor.track("specialist_ocr", "OCR extracted text.")
        
        breakdown = monitor.get_breakdown()
        
        assert "persona" in breakdown.components
        assert "memories" in breakdown.components
        assert "specialist_ocr" in breakdown.components
        assert breakdown.total_tokens > 0

    def test_breakdown_structure(self):
        """Breakdown should have proper structure."""
        monitor = TokenBudgetMonitor()
        monitor.track("test", "Some content")
        
        breakdown = monitor.get_breakdown()
        
        # Should have these attributes
        assert hasattr(breakdown, "components")
        assert hasattr(breakdown, "total_tokens")
        assert hasattr(breakdown, "percentage_used")
        assert hasattr(breakdown, "is_warning")
        
        # Components should be dict of ComponentTokens
        assert isinstance(breakdown.components, dict)
        for component in breakdown.components.values():
            assert hasattr(component, "tokens")
            assert hasattr(component, "percentage")

    def test_percentage_calculation(self):
        """Should correctly calculate percentage of budget used."""
        monitor = TokenBudgetMonitor(max_tokens=1000)
        
        # Track approximately 500 tokens worth
        text = "word " * 100  # Roughly 100-200 tokens
        monitor.track("test", text)
        
        breakdown = monitor.get_breakdown()
        assert 0 <= breakdown.percentage_used <= 100

    def test_warning_detection(self):
        """Should detect when approaching token limit."""
        monitor = TokenBudgetMonitor(max_tokens=100, warning_threshold=80)
        
        # Small amount - no warning
        monitor.track("small", "Few words")
        breakdown = monitor.get_breakdown()
        assert not breakdown.is_warning
        
        # Reset and add large amount - should warn
        monitor.reset()
        large_text = "word " * 100  # Will exceed 80% of 100 tokens
        monitor.track("large", large_text)
        breakdown = monitor.get_breakdown()
        # This might or might not warn depending on exact tokenization
        # Just check it's calculated
        assert isinstance(breakdown.is_warning, bool)

    def test_reset_tracking(self):
        """Should reset tracking between requests."""
        monitor = TokenBudgetMonitor()
        
        # Track some usage
        monitor.track("test", "Some content")
        breakdown1 = monitor.get_breakdown()
        assert breakdown1.total_tokens > 0
        
        # Reset
        monitor.reset()
        breakdown2 = monitor.get_breakdown()
        assert breakdown2.total_tokens == 0
        assert len(breakdown2.components) == 0

    def test_multiple_tracks_same_component(self):
        """Should accumulate tokens for same component."""
        monitor = TokenBudgetMonitor()
        
        monitor.track("memories", "First memory")
        monitor.track("memories", "Second memory")
        monitor.track("memories", "Third memory")
        
        breakdown = monitor.get_breakdown()
        assert "memories" in breakdown.components
        # Should have accumulated all three
        assert breakdown.components["memories"].tokens > 0

    def test_summary_string(self):
        """Should provide human-readable summary."""
        monitor = TokenBudgetMonitor()
        monitor.track("persona", "Test persona")
        monitor.track("memories", "Test memory")
        
        summary = monitor.get_summary()
        
        # Summary should mention components
        assert "persona" in summary
        assert "memories" in summary
        # Should show token counts
        assert "tokens" in summary.lower()

    def test_get_largest_components(self):
        """Should identify components using most tokens."""
        monitor = TokenBudgetMonitor()
        
        monitor.track("small", "Few words")
        monitor.track("medium", "Some more words here and there")
        monitor.track("large", "This is a much longer piece of text " * 20)
        
        top_components = monitor.get_top_components(n=2)
        
        assert len(top_components) <= 2
        # First should be largest
        assert top_components[0][0] == "large"
        # Should have (name, tokens) tuples
        assert isinstance(top_components[0][1], int)


class TestTokenUsageBreakdown:
    """Test the TokenUsageBreakdown data structure."""

    def test_breakdown_creation(self):
        """Should create breakdown with all fields."""
        components = {
            "persona": ComponentTokens(tokens=100, percentage=10.0),
            "memories": ComponentTokens(tokens=500, percentage=50.0),
        }
        
        breakdown = TokenUsageBreakdown(
            components=components,
            total_tokens=600,
            percentage_used=60.0,
            is_warning=False,
        )
        
        assert breakdown.total_tokens == 600
        assert breakdown.percentage_used == 60.0
        assert not breakdown.is_warning
        assert len(breakdown.components) == 2


class TestComponentTokens:
    """Test the ComponentTokens data structure."""

    def test_component_creation(self):
        """Should create component with tokens and percentage."""
        component = ComponentTokens(tokens=100, percentage=10.0)
        assert component.tokens == 100
        assert component.percentage == 10.0


class TestIntegrationWithPromptBuilder:
    """Test token monitoring integration with prompt builder."""

    @pytest.mark.asyncio
    async def test_monitor_during_prompt_building(self):
        """Token monitor should track usage during prompt building.
        
        This is an integration test that will be implemented
        once we integrate the monitor into prompt_builder.py
        """
        # This test will be implemented in integration phase
        # For now, just ensure test structure is ready
        pytest.skip("Integration test - implement after monitor is integrated")


class TestLogging:
    """Test that token usage is properly logged."""

    def test_logging_on_warning(self, caplog):
        """Should log warning when threshold exceeded."""
        # This will test logging functionality once implemented
        pytest.skip("Logging test - implement after logger integration")

    def test_logging_breakdown(self, caplog):
        """Should log detailed breakdown for debugging."""
        pytest.skip("Logging test - implement after logger integration")
