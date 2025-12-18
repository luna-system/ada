"""Tests for hemispheric specialization (processing modes).

Test coverage:
- Mode detection from message keywords
- Context strategy selection per mode
- Adaptive context assembly
- Statistics tracking
- Disabled mode detection (passthrough)
"""

import pytest
from brain.processing_modes import (
    ProcessingMode,
    ModeDetector,
    ContextStrategy,
    ContextStrategyBuilder,
    AdaptiveContextAssembler,
)


class TestProcessingMode:
    """Test ProcessingMode enum."""
    
    def test_all_modes_defined(self):
        """All expected modes are defined."""
        expected_modes = {'ANALYTICAL', 'CREATIVE', 'CONVERSATIONAL', 'TECHNICAL', 'EXPLORATORY'}
        actual_modes = {mode.name for mode in ProcessingMode}
        assert actual_modes == expected_modes


class TestModeDetector:
    """Test mode detection from message content."""
    
    def test_detect_analytical_mode(self):
        """Analytical keywords trigger analytical mode."""
        detector = ModeDetector()
        
        messages = [
            "Can you explain how this works?",
            "Why is this failing?",
            "Help me debug this issue",
            "What's the difference between X and Y?",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.ANALYTICAL, f"Failed for: {msg}"
    
    def test_detect_creative_mode(self):
        """Creative keywords trigger creative mode."""
        detector = ModeDetector()
        
        messages = [
            "Let's design a new feature",
            "I need ideas for improving this",
            "What if we tried a different approach?",
            "Help me brainstorm solutions",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.CREATIVE, f"Failed for: {msg}"
    
    def test_detect_technical_mode(self):
        """Technical keywords trigger technical mode."""
        detector = ModeDetector()
        
        messages = [
            "Write a function that does X",
            "Implement this feature",
            "Fix the bug in this code",
            "Let's refactor this module",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.TECHNICAL, f"Failed for: {msg}"
    
    def test_detect_exploratory_mode(self):
        """Exploratory keywords trigger exploratory mode."""
        detector = ModeDetector()
        
        messages = [
            "Teach me about Python decorators",
            "What is machine learning?",
            "Show me examples of recursion",
            "I want to learn more about Docker",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.EXPLORATORY, f"Failed for: {msg}"
    
    def test_detect_conversational_mode(self):
        """Conversational keywords trigger conversational mode."""
        detector = ModeDetector()
        
        messages = [
            "Hi there!",
            "Thanks for the help",
            "How are you doing?",
            "That's awesome!",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.CONVERSATIONAL, f"Failed for: {msg}"
    
    def test_default_to_conversational_no_keywords(self):
        """Messages with no keywords default to conversational."""
        detector = ModeDetector()
        
        messages = [
            "blorp",
            "123 456",
            "...",
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.CONVERSATIONAL
    
    def test_disabled_detector(self):
        """Disabled detector always returns conversational."""
        detector = ModeDetector(enabled=False)
        
        messages = [
            "Explain how this works",  # Would be analytical
            "Write a function",        # Would be technical
            "Let's brainstorm",        # Would be creative
        ]
        
        for msg in messages:
            mode = detector.detect(msg)
            assert mode == ProcessingMode.CONVERSATIONAL
    
    def test_multiple_mode_signals(self):
        """Message with multiple signals picks strongest."""
        detector = ModeDetector()
        
        # Strong technical signals
        msg = "Implement a function that explains and debugs the code"
        mode = detector.detect(msg)
        # Should pick based on highest count (may vary, but should be consistent)
        assert mode in [ProcessingMode.TECHNICAL, ProcessingMode.ANALYTICAL]


class TestContextStrategyBuilder:
    """Test context strategy building for each mode."""
    
    def test_analytical_strategy(self):
        """Analytical strategy has detailed, technical focus."""
        strategy = ContextStrategyBuilder.get_strategy(ProcessingMode.ANALYTICAL)
        
        assert strategy.mode == ProcessingMode.ANALYTICAL
        assert strategy.history_limit >= 7  # More history
        assert strategy.detail_level == 'high'
        assert strategy.context_focus == 'technical'
        assert not strategy.memory_diversity  # Focused
        assert strategy.token_budget_multiplier >= 1.0
    
    def test_creative_strategy(self):
        """Creative strategy has diverse, conceptual focus."""
        strategy = ContextStrategyBuilder.get_strategy(ProcessingMode.CREATIVE)
        
        assert strategy.mode == ProcessingMode.CREATIVE
        assert strategy.history_limit <= 5  # Less history
        assert strategy.detail_level in ['medium', 'low']
        assert strategy.context_focus == 'conceptual'
        assert strategy.memory_diversity  # Diverse
    
    def test_conversational_strategy(self):
        """Conversational strategy is lightweight."""
        strategy = ContextStrategyBuilder.get_strategy(ProcessingMode.CONVERSATIONAL)
        
        assert strategy.mode == ProcessingMode.CONVERSATIONAL
        assert strategy.detail_level == 'low'
        assert strategy.context_focus == 'personal'
        assert strategy.token_budget_multiplier < 1.0  # Reduced
        assert len(strategy.specialist_preference) == 0  # No specialists
    
    def test_technical_strategy(self):
        """Technical strategy has high detail, code focus."""
        strategy = ContextStrategyBuilder.get_strategy(ProcessingMode.TECHNICAL)
        
        assert strategy.mode == ProcessingMode.TECHNICAL
        assert strategy.detail_level == 'high'
        assert strategy.context_focus == 'technical'
        assert 'codebase' in strategy.specialist_preference or 'docs' in strategy.specialist_preference
        assert strategy.token_budget_multiplier > 1.0  # More tokens
    
    def test_exploratory_strategy(self):
        """Exploratory strategy has broad, balanced focus."""
        strategy = ContextStrategyBuilder.get_strategy(ProcessingMode.EXPLORATORY)
        
        assert strategy.mode == ProcessingMode.EXPLORATORY
        assert strategy.detail_level == 'medium'
        assert strategy.context_focus == 'conceptual'
        assert strategy.memory_diversity  # Broad exploration
        assert 'web_search' in strategy.specialist_preference or 'wiki' in strategy.specialist_preference
    
    def test_all_modes_have_strategies(self):
        """All processing modes have defined strategies."""
        for mode in ProcessingMode:
            strategy = ContextStrategyBuilder.get_strategy(mode)
            assert strategy.mode == mode
            assert strategy.history_limit > 0
            assert strategy.detail_level in ['high', 'medium', 'low']
            assert strategy.token_budget_multiplier > 0


class TestAdaptiveContextAssembler:
    """Test adaptive context assembly."""
    
    def test_initialization(self):
        """Assembler initializes correctly."""
        assembler = AdaptiveContextAssembler()
        assert assembler.enabled
        assert assembler.total_requests == 0
        assert all(count == 0 for count in assembler.mode_counts.values())
    
    def test_get_strategy_analytical(self):
        """Get strategy for analytical message."""
        assembler = AdaptiveContextAssembler()
        
        mode, strategy = assembler.get_strategy("Explain how this works")
        
        assert mode == ProcessingMode.ANALYTICAL
        assert strategy.mode == ProcessingMode.ANALYTICAL
        assert strategy.detail_level == 'high'
    
    def test_get_strategy_creative(self):
        """Get strategy for creative message."""
        assembler = AdaptiveContextAssembler()
        
        mode, strategy = assembler.get_strategy("Let's design a new approach")
        
        assert mode == ProcessingMode.CREATIVE
        assert strategy.mode == ProcessingMode.CREATIVE
        assert strategy.memory_diversity is True
    
    def test_get_strategy_technical(self):
        """Get strategy for technical message."""
        assembler = AdaptiveContextAssembler()
        
        mode, strategy = assembler.get_strategy("Write a function that does X")
        
        assert mode == ProcessingMode.TECHNICAL
        assert strategy.mode == ProcessingMode.TECHNICAL
        assert strategy.detail_level == 'high'
    
    def test_get_strategy_conversational(self):
        """Get strategy for conversational message."""
        assembler = AdaptiveContextAssembler()
        
        mode, strategy = assembler.get_strategy("Thanks for the help!")
        
        assert mode == ProcessingMode.CONVERSATIONAL
        assert strategy.mode == ProcessingMode.CONVERSATIONAL
        assert strategy.token_budget_multiplier < 1.0
    
    def test_stats_tracking(self):
        """Statistics are tracked correctly."""
        assembler = AdaptiveContextAssembler()
        
        # Make several requests
        assembler.get_strategy("Explain this")  # Analytical
        assembler.get_strategy("Write a function")  # Technical
        assembler.get_strategy("Design a feature")  # Creative
        assembler.get_strategy("Thanks!")  # Conversational
        
        stats = assembler.get_stats()
        
        assert stats['enabled'] is True
        assert stats['total_requests'] == 4
        assert stats['mode_counts'][ProcessingMode.ANALYTICAL.value] == 1
        assert stats['mode_counts'][ProcessingMode.TECHNICAL.value] == 1
        assert stats['mode_counts'][ProcessingMode.CREATIVE.value] == 1
        assert stats['mode_counts'][ProcessingMode.CONVERSATIONAL.value] == 1
        
        # Check distribution sums to 1.0
        distribution_sum = sum(stats['mode_distribution'].values())
        assert abs(distribution_sum - 1.0) < 0.01
    
    def test_stats_reset(self):
        """Stats can be reset."""
        assembler = AdaptiveContextAssembler()
        
        assembler.get_strategy("Explain this")
        assembler.get_strategy("Write code")
        
        assert assembler.total_requests == 2
        
        assembler.reset_stats()
        
        assert assembler.total_requests == 0
        assert all(count == 0 for count in assembler.mode_counts.values())
    
    def test_disabled_assembler(self):
        """Disabled assembler always uses conversational."""
        assembler = AdaptiveContextAssembler(enabled=False)
        
        messages = [
            "Explain this",
            "Write a function",
            "Design a feature",
        ]
        
        for msg in messages:
            mode, strategy = assembler.get_strategy(msg)
            assert mode == ProcessingMode.CONVERSATIONAL
            assert strategy.mode == ProcessingMode.CONVERSATIONAL
    
    def test_disabled_stats(self):
        """Disabled assembler reports correct state."""
        assembler = AdaptiveContextAssembler(enabled=False)
        
        assembler.get_strategy("Any message")
        
        stats = assembler.get_stats()
        assert stats['enabled'] is False


class TestIntegration:
    """Integration tests for full processing mode pipeline."""
    
    def test_end_to_end_analytical(self):
        """Full pipeline for analytical request."""
        assembler = AdaptiveContextAssembler()
        
        message = "Can you debug this error and explain what's wrong?"
        mode, strategy = assembler.get_strategy(message)
        
        # Should detect analytical
        assert mode == ProcessingMode.ANALYTICAL
        
        # Strategy should be appropriate
        assert strategy.history_limit >= 7
        assert strategy.detail_level == 'high'
        assert strategy.context_focus == 'technical'
        
        # Stats updated
        stats = assembler.get_stats()
        assert stats['total_requests'] == 1
        assert stats['mode_counts']['analytical'] == 1
    
    def test_end_to_end_creative(self):
        """Full pipeline for creative request."""
        assembler = AdaptiveContextAssembler()
        
        message = "Let's brainstorm innovative ideas for this project"
        mode, strategy = assembler.get_strategy(message)
        
        assert mode == ProcessingMode.CREATIVE
        assert strategy.memory_diversity is True
        assert strategy.context_focus == 'conceptual'
    
    def test_mode_switching(self):
        """Assembler switches modes based on message."""
        assembler = AdaptiveContextAssembler()
        
        # Start analytical
        mode1, _ = assembler.get_strategy("Explain how this works")
        assert mode1 == ProcessingMode.ANALYTICAL
        
        # Switch to creative
        mode2, _ = assembler.get_strategy("Design a new approach")
        assert mode2 == ProcessingMode.CREATIVE
        
        # Switch to technical
        mode3, _ = assembler.get_strategy("Implement this function")
        assert mode3 == ProcessingMode.TECHNICAL
        
        # Stats show all three
        stats = assembler.get_stats()
        assert stats['total_requests'] == 3
        assert stats['mode_counts']['analytical'] == 1
        assert stats['mode_counts']['creative'] == 1
        assert stats['mode_counts']['technical'] == 1
    
    def test_strategy_differences(self):
        """Different modes produce different strategies."""
        assembler = AdaptiveContextAssembler()
        
        _, analytical_strat = assembler.get_strategy("Explain this code")
        _, creative_strat = assembler.get_strategy("Design a new feature")
        _, conversational_strat = assembler.get_strategy("Thanks!")
        
        # Analytical has more history than conversational
        assert analytical_strat.history_limit > conversational_strat.history_limit
        
        # Creative has diversity enabled
        assert creative_strat.memory_diversity is True
        assert analytical_strat.memory_diversity is False
        
        # Conversational has smallest token budget
        assert conversational_strat.token_budget_multiplier < analytical_strat.token_budget_multiplier
