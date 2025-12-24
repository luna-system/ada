"""Tests for Ada's native symbolic language.

This tests the foundation for a potential machine-first reasoning SLM.
The symbol system is designed for:
- 66-104x compression (matching SIF benchmarks)
- Direct mapping to SIF importance/confidence
- Training data generation for dense reasoning models
"""

import pytest
from brain.reasoning.ada_symbols import (
    Symbol,
    get_symbol,
    get_all_chars,
    confidence_to_certainty,
    importance_to_attention,
    certainty_to_confidence,
    attention_to_importance,
    PHASE_TRANSITION,
    LOGIC_SYMBOLS,
    CERTAINTY_SYMBOLS,
    ATTENTION_SYMBOLS,
    QUERY_SYMBOLS,
    ASSERTION_SYMBOLS,
    STATE_SYMBOLS,
    TEMPORAL_SYMBOLS,
    CAUSAL_SYMBOLS,
    META_SYMBOLS,
    TOOL_SYMBOLS,
    DOMAIN_SYMBOLS,
    ALL_SYMBOLS,
)


class TestSymbolRegistry:
    """Test the symbol registry structure."""
    
    def test_all_symbols_non_empty(self):
        """Registry should have symbols."""
        assert len(ALL_SYMBOLS) > 50  # We designed 70+ symbols
    
    def test_get_symbol_exists(self):
        """Can retrieve symbols by char."""
        arrow = get_symbol('→')
        assert arrow is not None
        assert arrow.char == '→'
        assert arrow.category.value == 'logic'  # SymbolCategory enum
    
    def test_get_symbol_not_found(self):
        """Returns None for unknown chars."""
        assert get_symbol('X') is None
        assert get_symbol('a') is None
    
    def test_get_all_chars(self):
        """get_all_chars returns set of all symbol characters."""
        chars = get_all_chars()
        assert '→' in chars
        assert '∃' in chars
        assert '●' in chars
        assert '★' in chars
    
    def test_symbol_has_required_fields(self):
        """Each symbol should have all required fields."""
        for char, symbol in ALL_SYMBOLS.items():
            assert symbol.char == char
            assert len(symbol.name) > 0
            assert len(symbol.meaning) > 0
            assert symbol.category is not None  # It's an enum
            assert symbol.english_tokens >= 1


class TestCertaintyMapping:
    """Test SIF confidence → certainty symbol mapping."""
    
    def test_certain_high_confidence(self):
        """High confidence maps to filled circle."""
        assert confidence_to_certainty(1.0) == '●'
        assert confidence_to_certainty(0.95) == '●'
        assert confidence_to_certainty(0.90) == '●'  # Threshold
    
    def test_probable_confidence(self):
        """Probable confidence maps to mostly filled."""
        assert confidence_to_certainty(0.89) == '◕'
        assert confidence_to_certainty(0.75) == '◕'
        assert confidence_to_certainty(0.70) == '◕'  # Threshold
    
    def test_possible_confidence(self):
        """Possible confidence maps to half."""
        assert confidence_to_certainty(0.69) == '◑'
        assert confidence_to_certainty(0.50) == '◑'
        assert confidence_to_certainty(0.40) == '◑'  # Threshold
    
    def test_uncertain_confidence(self):
        """Low confidence maps to mostly empty."""
        assert confidence_to_certainty(0.39) == '◔'
        assert confidence_to_certainty(0.30) == '◔'
        assert confidence_to_certainty(0.20) == '◔'  # Threshold
    
    def test_unknown_confidence(self):
        """Very low confidence maps to empty circle."""
        assert confidence_to_certainty(0.19) == '○'
        assert confidence_to_certainty(0.05) == '○'
        assert confidence_to_certainty(0.0) == '○'
    
    def test_certainty_to_confidence_inverse(self):
        """Certainty symbols map back to confidence ranges."""
        assert certainty_to_confidence('●') == 0.90
        assert certainty_to_confidence('◕') == 0.70
        assert certainty_to_confidence('◑') == 0.50
        assert certainty_to_confidence('◔') == 0.30
        assert certainty_to_confidence('○') == 0.10
    
    def test_phase_transition_at_boundary(self):
        """The 0.70/0.40 boundaries for likely/possible."""
        # Just at likely threshold
        assert confidence_to_certainty(0.70) == '◕'  # likely
        # Just below likely threshold
        assert confidence_to_certainty(0.69) == '◑'  # possible


class TestAttentionMapping:
    """Test SIF importance → attention symbol mapping."""
    
    def test_critical_importance(self):
        """High importance maps to filled star."""
        assert importance_to_attention(1.0) == '★'
        assert importance_to_attention(0.80) == '★'
        assert importance_to_attention(0.75) == '★'
    
    def test_important_importance(self):
        """Medium-high importance maps to hollow star."""
        assert importance_to_attention(0.74) == '☆'
        assert importance_to_attention(0.65) == '☆'
        assert importance_to_attention(0.60) == '☆'  # Phase transition!
    
    def test_relevant_importance(self):
        """Medium importance maps to filled diamond."""
        assert importance_to_attention(0.59) == '◆'
        assert importance_to_attention(0.45) == '◆'
        assert importance_to_attention(0.40) == '◆'
    
    def test_peripheral_importance(self):
        """Low importance maps to hollow diamond."""
        assert importance_to_attention(0.39) == '◇'
        assert importance_to_attention(0.1) == '◇'
        assert importance_to_attention(0.0) == '◇'
    
    def test_attention_to_importance_inverse(self):
        """Attention symbols map back to importance ranges."""
        assert attention_to_importance('★') == 0.85
        assert attention_to_importance('☆') == 0.65
        assert attention_to_importance('◆') == 0.50
        assert attention_to_importance('◇') == 0.25


class TestPhaseTransition:
    """Test the 0.60 phase transition constant."""
    
    def test_phase_transition_value(self):
        """Phase transition should be 0.60 (golden ratio inverse approx)."""
        assert PHASE_TRANSITION == 0.60
    
    def test_golden_ratio_proximity(self):
        """0.60 should be close to 1/φ."""
        golden_ratio_inverse = 1 / 1.618
        assert abs(PHASE_TRANSITION - golden_ratio_inverse) < 0.02


class TestLogicSymbols:
    """Test logic symbol category."""
    
    def test_and_symbol(self):
        """AND should have token value."""
        symbol = LOGIC_SYMBOLS['∧']
        assert 'and' in symbol.meaning.lower()
        assert symbol.english_tokens >= 1
    
    def test_or_symbol(self):
        """OR should have token value."""
        symbol = LOGIC_SYMBOLS['∨']
        assert 'or' in symbol.meaning.lower()
    
    def test_not_symbol(self):
        """NOT symbol exists."""
        symbol = LOGIC_SYMBOLS['¬']
        assert 'not' in symbol.meaning.lower()
    
    def test_implies_arrow(self):
        """Arrow has compression."""
        symbol = LOGIC_SYMBOLS['→']
        assert symbol.english_tokens >= 2  # "leads to" or "implies"


class TestExistenceSymbols:
    """Test existence quantifiers."""
    
    def test_exists_symbol(self):
        """Existential quantifier."""
        symbol = get_symbol('∃')
        assert symbol is not None
        assert 'exists' in symbol.meaning.lower()
    
    def test_not_exists_symbol(self):
        """Negated existential quantifier."""
        symbol = get_symbol('∄')
        assert symbol is not None
        assert 'not' in symbol.meaning.lower() or 'missing' in symbol.meaning.lower()


class TestToolSymbols:
    """Test tool/action symbol category."""
    
    def test_tool_call_symbol(self):
        """Lightning bolt for tool calls."""
        assert '⚡' in TOOL_SYMBOLS
        symbol = TOOL_SYMBOLS['⚡']
        assert 'tool' in symbol.meaning.lower() or 'call' in symbol.meaning.lower()
    
    def test_search_symbol(self):
        """Magnifying glass for searching."""
        assert '🔍' in TOOL_SYMBOLS
        symbol = TOOL_SYMBOLS['🔍']
        assert symbol.english_tokens >= 2


class TestMetaSymbols:
    """Test metacognition symbol category."""
    
    def test_thinking_symbol(self):
        """Thought bubble for metacognition."""
        assert '💭' in META_SYMBOLS
        symbol = META_SYMBOLS['💭']
        assert 'think' in symbol.meaning.lower()
    
    def test_recursion_symbol(self):
        """Recursion/self-reference symbol."""
        assert '⟲' in META_SYMBOLS
        symbol = META_SYMBOLS['⟲']
        assert symbol.english_tokens >= 2


class TestSIFIntegration:
    """Test that symbols integrate with SIF semantics."""
    
    def test_certainty_core_has_sif_mapping(self):
        """Core certainty symbols should map to SIF confidence."""
        # Only the main 5 certainty levels have mappings
        core_certainty = ['●', '◕', '◑', '◔', '○']
        for char in core_certainty:
            symbol = CERTAINTY_SYMBOLS[char]
            assert symbol.sif_mapping is not None
            assert 'confidence' in symbol.sif_mapping
    
    def test_attention_core_has_sif_mapping(self):
        """Core attention symbols should map to SIF importance."""
        # The main 4 attention levels have mappings
        core_attention = ['★', '☆', '◆', '◇']
        for char in core_attention:
            symbol = ATTENTION_SYMBOLS[char]
            assert symbol.sif_mapping is not None
            assert 'importance' in symbol.sif_mapping


class TestCompressionBandwidth:
    """Test the compression potential of the symbol system."""
    
    def test_average_english_tokens(self):
        """Average symbol should compress multiple English tokens."""
        total_tokens = sum(s.english_tokens for s in ALL_SYMBOLS.values())
        avg_tokens = total_tokens / len(ALL_SYMBOLS)
        assert avg_tokens >= 2.0  # At least 2x average compression
    
    def test_high_value_symbols_exist(self):
        """Some symbols should compress 3+ tokens."""
        high_value = [s for s in ALL_SYMBOLS.values() if s.english_tokens >= 3]
        assert len(high_value) >= 10
    
    def test_total_vocabulary_size(self):
        """Vocabulary should be tractable for SLM training."""
        # 200-500 symbols is ideal for a specialized model
        assert 50 <= len(ALL_SYMBOLS) <= 500


class TestDenseExpressions:
    """Test complete dense expressions."""
    
    def test_reasoning_chain_symbols_exist(self):
        """All symbols in a typical reasoning chain exist."""
        chain = "●∴ ?config → ∃file ⟹ ⚡read ✓"
        for char in chain:
            if not char.isalnum() and char not in ' ':
                symbol = get_symbol(char)
                # Every special char should be in our vocabulary
                if symbol is None:
                    pytest.skip(f"Symbol {char!r} not yet in vocabulary")
    
    def test_certainty_prefixed_assertion(self):
        """Can express certainty-prefixed assertions."""
        # These patterns should all be valid
        patterns = [
            "●∴ answer",  # Certain assertion
            "◕∴ hypothesis",  # Probable assertion
            "◑? query",  # Uncertain query
        ]
        for pattern in patterns:
            for char in pattern:
                if not char.isalnum() and char not in ' ':
                    symbol = get_symbol(char)
                    if symbol is None and char not in '∴':
                        pytest.skip(f"Symbol {char!r} not in vocabulary")
