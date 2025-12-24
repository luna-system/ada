"""Tests for dense semantic thinking.

These tests validate:
1. Dense notation parsing
2. Compression ratio calculations
3. Phase transition logic (0.60 threshold)
4. English expansion
"""

import pytest
from brain.reasoning.dense_thinking import (
    ThinkingMode,
    DenseThought,
    DenseThinkingAnalyzer,
    DenseMetrics,
    PHASE_TRANSITION_THRESHOLD,
    should_expand,
    get_dense_prompt,
    DENSE_SYSTEM_PROMPT,
    HYBRID_SYSTEM_PROMPT,
)


class TestDenseThoughtParsing:
    """Test parsing of dense notation."""
    
    def test_parse_simple_query(self):
        """Parse a simple query thought."""
        thought = DenseThought.parse("?config location")
        assert '?' in thought.symbols
        assert not thought.is_answer
        assert thought.semantic_density > 0
    
    def test_parse_reasoning_chain(self):
        """Parse a reasoning chain with arrows."""
        thought = DenseThought.parse("?config → 📁brain/ → ∃config.py ✓")
        assert '→' in thought.symbols
        assert '?' in thought.symbols
        assert '∃' in thought.symbols
        assert '✓' in thought.symbols
        assert len(thought.symbols) == 6  # ? → 📁 → ∃ ✓ (two arrows!)
    
    def test_parse_tool_call_dense(self):
        """Parse dense tool call notation."""
        thought = DenseThought.parse('⚡brain_list_dir:{"dir_path":"brain"}')
        assert '⚡' in thought.symbols
        assert 'brain_list_dir' in thought.tool_calls
    
    def test_parse_tool_call_standard(self):
        """Parse standard TOOL_REQUEST notation."""
        thought = DenseThought.parse('TOOL_REQUEST[brain_search:{"query":"test"}]')
        assert 'brain_search' in thought.tool_calls
    
    def test_parse_answer(self):
        """Parse an answer assertion."""
        thought = DenseThought.parse("!ANSWER: The config is in brain/config.py")
        assert thought.is_answer
        assert '!' in thought.symbols
    
    def test_parse_complex_thought(self):
        """Parse a complex multi-symbol thought."""
        text = "💭 ?auth method → 🔍jwt ∧ oauth → ∃jwt.py ✓ ∧ ∄oauth → ∴ !use jwt"
        thought = DenseThought.parse(text)
        
        # Should have many symbols
        assert len(thought.symbols) >= 10
        assert '!' in thought.symbols  # Contains assertion
        assert thought.semantic_density > 0.5  # High density
    
    def test_semantic_density_calculation(self):
        """Verify semantic density is symbols per word."""
        # Dense text: more symbols than words
        dense = DenseThought.parse("→ ∃ ✓ ∧ ✗")
        assert dense.semantic_density >= 1.0  # 5 symbols, ~5 words
        
        # Sparse text: fewer symbols
        sparse = DenseThought.parse("This is a regular English sentence")
        assert sparse.semantic_density == 0.0  # No symbols


class TestDenseSessionAnalysis:
    """Test analysis of full reasoning sessions."""
    
    def test_analyze_empty_session(self):
        """Empty session should not crash."""
        metrics = DenseThinkingAnalyzer.analyze_session([])
        assert metrics.thoughts == 0
        assert metrics.total_tokens == 0
    
    def test_analyze_single_thought(self):
        """Analyze a single thought."""
        thoughts = ["?config → ∃config.py ✓"]
        metrics = DenseThinkingAnalyzer.analyze_session(thoughts)
        
        assert metrics.thoughts == 1
        assert metrics.total_symbols == 4  # ? → ∃ ✓
        assert metrics.compression_ratio > 1.0  # Should show compression
    
    def test_analyze_multi_thought_session(self):
        """Analyze a realistic reasoning session."""
        thoughts = [
            "💭 ?project structure",
            "⚡brain_list_dir:{\"path\":\"brain\"} → ∃brain/ ∧ tests/ ✓",
            "💭 brain/ ⊂ core logic → ?config",
            "⚡brain_read_file:{\"path\":\"x.py\"} → ∃settings ✓",
            "!ANSWER: Config in brain/config.py"
        ]
        metrics = DenseThinkingAnalyzer.analyze_session(thoughts)
        
        assert metrics.thoughts == 5
        assert metrics.total_tool_calls == 2  # Now with proper JSON format
        assert metrics.compression_ratio > 1.5  # Good compression
        assert metrics.avg_density > 0.3  # Decent density
    
    def test_compression_ratio_increases_with_symbols(self):
        """More symbols = higher compression ratio."""
        # Sparse session (mostly English)
        sparse = ["I need to find the configuration file in the brain folder"]
        sparse_metrics = DenseThinkingAnalyzer.analyze_session(sparse)
        
        # Dense session (mostly symbols)
        dense = ["?config → 📁brain → ∃config.py ✓"]
        dense_metrics = DenseThinkingAnalyzer.analyze_session(dense)
        
        assert dense_metrics.compression_ratio > sparse_metrics.compression_ratio


class TestEnglishExpansion:
    """Test expansion of dense notation to English."""
    
    def test_expand_simple(self):
        """Expand simple symbols."""
        result = DenseThinkingAnalyzer.expand_to_english("∃config")
        assert "found" in result.lower()
    
    def test_expand_chain(self):
        """Expand a reasoning chain."""
        result = DenseThinkingAnalyzer.expand_to_english("?config → ∃file ✓")
        assert "need" in result.lower()
        assert "leads to" in result.lower()
        assert "found" in result.lower()
        assert "confirmed" in result.lower()
    
    def test_expand_preserves_words(self):
        """Regular words should be preserved."""
        result = DenseThinkingAnalyzer.expand_to_english("config.py ∃ in brain/")
        assert "config.py" in result
        assert "brain/" in result


class TestPhaseTransition:
    """Test the 0.60 phase transition threshold."""
    
    def test_threshold_is_golden_ratio_inverse(self):
        """Verify threshold aligns with research."""
        # 1/φ ≈ 0.618, we use 0.60 for simplicity
        golden_ratio_inverse = 1 / 1.618
        assert abs(PHASE_TRANSITION_THRESHOLD - golden_ratio_inverse) < 0.02
    
    def test_low_convergence_stays_dense(self):
        """Below threshold, stay in dense mode."""
        assert not should_expand(convergence_score=0.3, importance=0.3)
        assert not should_expand(convergence_score=0.5, importance=0.4)
    
    def test_high_convergence_expands(self):
        """Above threshold, expand to English."""
        assert should_expand(convergence_score=0.7, importance=0.3)
        assert should_expand(convergence_score=0.95, importance=0.1)
    
    def test_high_importance_expands(self):
        """High importance content should be expanded."""
        assert should_expand(convergence_score=0.3, importance=0.8)
        assert should_expand(convergence_score=0.4, importance=0.65)
    
    def test_threshold_boundary(self):
        """Test behavior at exactly 0.60."""
        # At threshold = expand
        assert should_expand(convergence_score=0.60, importance=0.0)
        assert should_expand(convergence_score=0.0, importance=0.60)
        
        # Just below = stay dense
        assert not should_expand(convergence_score=0.59, importance=0.59)


class TestThinkingModes:
    """Test thinking mode prompts."""
    
    def test_dense_mode_prompt_exists(self):
        """Dense mode should have a prompt."""
        prompt = get_dense_prompt(ThinkingMode.DENSE)
        assert len(prompt) > 100
        assert "COMPRESSED" in prompt or "DENSE" in prompt
    
    def test_hybrid_mode_prompt_exists(self):
        """Hybrid mode should have a prompt."""
        prompt = get_dense_prompt(ThinkingMode.HYBRID)
        assert len(prompt) > 100
        assert "HYBRID" in prompt
    
    def test_expanded_mode_no_special_prompt(self):
        """Expanded mode doesn't need special prompt."""
        prompt = get_dense_prompt(ThinkingMode.EXPANDED)
        assert prompt == ""
    
    def test_dense_prompt_has_symbols(self):
        """Dense prompt should teach the notation."""
        prompt = DENSE_SYSTEM_PROMPT
        # Should contain symbol definitions
        assert '→' in prompt
        assert '∃' in prompt
        assert '?' in prompt
        assert '!' in prompt
    
    def test_hybrid_prompt_has_examples(self):
        """Hybrid prompt should have examples."""
        prompt = HYBRID_SYSTEM_PROMPT
        assert "EXAMPLE" in prompt or "example" in prompt.lower()
        assert "TOOL_REQUEST" in prompt


class TestCompressionEfficiency:
    """Test that dense notation actually compresses reasoning."""
    
    def test_dense_vs_english_token_count(self):
        """Dense notation should use fewer tokens than English equivalent."""
        # Dense version
        dense = "?auth→🔍jwt→∃jwt.py✓→!JWT"
        dense_tokens = len(dense.split())
        
        # English equivalent  
        english = ("I need to find authentication method. "
                  "Searching for JWT. Found jwt.py, confirmed. "
                  "I conclude: use JWT for authentication.")
        english_tokens = len(english.split())
        
        # Dense should be significantly more compact
        assert dense_tokens < english_tokens / 3  # ~5.7x compression
    
    def test_symbol_token_values_sum_correctly(self):
        """Verify symbol token values are reasonable."""
        from brain.reasoning.dense_thinking import DenseThinkingAnalyzer
        
        # A chain like "→ → →" represents ~9 English tokens
        chain_value = DenseThinkingAnalyzer.SYMBOL_TOKEN_VALUES['→'] * 3
        assert chain_value >= 6  # At least "leads to leads to leads to"
    
    def test_real_reasoning_compression(self):
        """Test compression on realistic reasoning."""
        # Simulated dense reasoning session
        dense_thoughts = [
            "💭 ?files brain/",
            "⚡brain_list_dir:{'path':'brain'}",
            "∃app.py ∧ llm.py ∧ config.py ✓",
            "💭 config.py ⊂ settings → ?read",
            "⚡brain_read_file:{'path':'brain/config.py'}",
            "∃OLLAMA_MODEL ∧ CHROMA_HOST ✓",
            "!ANSWER: Config uses env vars via Pydantic"
        ]
        
        # Simulated English reasoning session (same logic)
        english_thoughts = [
            "I need to find out what files are in the brain directory.",
            "Let me use the brain_list_dir tool to list the contents.",
            "I found app.py, llm.py, and config.py. The config.py file looks relevant.",
            "The config.py file should contain settings. Let me read it.",
            "Let me use the brain_read_file tool to read config.py.",
            "I found OLLAMA_MODEL and CHROMA_HOST environment variables.",
            "ANSWER: The configuration uses environment variables through Pydantic Settings."
        ]
        
        dense_metrics = DenseThinkingAnalyzer.analyze_session(dense_thoughts)
        
        dense_total = sum(len(t.split()) for t in dense_thoughts)
        english_total = sum(len(t.split()) for t in english_thoughts)
        
        # Dense should be significantly smaller
        assert dense_total < english_total * 0.6  # At least 40% reduction
        
        # Metrics should show good compression
        assert dense_metrics.compression_ratio > 1.5


class TestMetricsDataclass:
    """Test metrics dataclass functionality."""
    
    def test_metrics_to_dict(self):
        """Metrics should serialize to dict."""
        metrics = DenseMetrics(
            total_tokens=100,
            total_symbols=30,
            total_tool_calls=5,
            thoughts=7,
            avg_density=0.42,
            compression_ratio=2.1
        )
        
        d = metrics.to_dict()
        assert d["total_tokens"] == 100
        assert d["total_symbols"] == 30
        assert d["compression_ratio"] == 2.1
        assert isinstance(d["avg_density"], float)
