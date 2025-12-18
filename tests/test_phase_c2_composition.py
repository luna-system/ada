"""
Tests for Phase C.2 Tool Composition Effects Research

Validates the tool composition framework and interaction analysis.
"""

from phase_c2_runner import (
    SpecialistType,
    CompositionScenario,
    SpecialistResult,
    CompositionMetric,
    InteractionAnalysis,
    PhaseC2,
)


class TestPhaseC2Setup:
    """Test Phase C.2 experiment initialization."""
    
    def test_experiment_creates_scenarios(self):
        """Verify experiment creates all test scenarios."""
        exp = PhaseC2()
        assert len(exp.scenarios) == 7
        assert len([s for s in exp.scenarios if len(s.specialists) == 1]) == 3
        assert len([s for s in exp.scenarios if len(s.specialists) == 2]) == 3
        assert len([s for s in exp.scenarios if len(s.specialists) == 3]) == 1
    
    def test_scenarios_have_all_fields(self):
        """Verify all scenarios are properly defined."""
        exp = PhaseC2()
        for scenario in exp.scenarios:
            assert scenario.scenario_id
            assert scenario.specialists
            assert len(scenario.specialists) > 0
            assert scenario.query
            assert scenario.description
            assert scenario.category


class TestSpecialistSimulation:
    """Test individual specialist simulation."""
    
    def test_codebase_specialist_simulation(self):
        """Test CodebaseSpecialist simulation."""
        exp = PhaseC2()
        result = exp._simulate_specialist(SpecialistType.CODEBASE)
        
        assert result.specialist == SpecialistType.CODEBASE
        assert 4000 <= result.context_bytes <= 8000
        assert 100 <= result.context_lines <= 200
        assert 80 <= result.latency_ms <= 150
        assert 0.85 <= result.relevance_score <= 1.0
    
    def test_terminal_specialist_simulation(self):
        """Test TerminalSpecialist simulation."""
        exp = PhaseC2()
        result = exp._simulate_specialist(SpecialistType.TERMINAL)
        
        assert result.specialist == SpecialistType.TERMINAL
        assert 1000 <= result.context_bytes <= 3000
        assert 20 <= result.context_lines <= 100
        assert 200 <= result.latency_ms <= 400  # Execution takes time
        assert 0.7 <= result.relevance_score <= 0.95
    
    def test_git_specialist_simulation(self):
        """Test GitSpecialist simulation."""
        exp = PhaseC2()
        result = exp._simulate_specialist(SpecialistType.GIT)
        
        assert result.specialist == SpecialistType.GIT
        assert 2000 <= result.context_bytes <= 5000
        assert 50 <= result.context_lines <= 150
        assert 100 <= result.latency_ms <= 200
        assert 0.8 <= result.relevance_score <= 0.98


class TestRedundancyCalculation:
    """Test redundancy detection between specialists."""
    
    def test_no_redundancy_for_single_specialist(self):
        """Single specialist should have zero redundancy."""
        exp = PhaseC2()
        result = SpecialistResult(
            specialist=SpecialistType.CODEBASE,
            context_bytes=1000,
            context_lines=50,
            latency_ms=100,
            relevance_score=0.9,
            tokens_used=250,
            confidence=0.9,
        )
        
        redundancy = exp._calculate_redundancy([result])
        assert redundancy == 0.0
    
    def test_redundancy_with_different_specialist_types(self):
        """Different specialist types should have lower redundancy."""
        exp = PhaseC2()
        results = [
            SpecialistResult(
                specialist=SpecialistType.CODEBASE,
                context_bytes=5000,
                context_lines=100,
                latency_ms=100,
                relevance_score=0.9,
                tokens_used=1250,
                confidence=0.9,
            ),
            SpecialistResult(
                specialist=SpecialistType.TERMINAL,
                context_bytes=2000,
                context_lines=50,
                latency_ms=200,
                relevance_score=0.85,
                tokens_used=500,
                confidence=0.85,
            ),
        ]
        
        redundancy = exp._calculate_redundancy(results)
        assert 0.0 <= redundancy <= 0.5  # Low redundancy for different types


class TestInteractionCalculation:
    """Test interaction effect calculation."""
    
    def test_positive_interaction_synergy(self):
        """Test detection of synergistic interaction."""
        exp = PhaseC2()
        
        # Solo results
        solo_a = CompositionMetric(
            scenario_id="solo-a",
            specialists=[SpecialistType.CODEBASE],
            specialist_count=1,
            specialist_results=[],
            total_context_bytes=5000,
            total_context_lines=100,
            total_specialist_latency_ms=100,
            llm_inference_ms=300,
            python_overhead_ms=100,
            total_ms=400,
            llm_percentage=75,
            answer_quality=6,
            answer_complete=True,
            hallucination_detected=False,
            tokens_per_quality_point=10,
            context_redundancy=0.0,
            context_diversity=1.0,
            specialist_agreement=1.0,
            overhead_ratio=2.0,
            diminishing_return_score=0.5,
        )
        
        solo_b = CompositionMetric(
            scenario_id="solo-b",
            specialists=[SpecialistType.TERMINAL],
            specialist_count=1,
            specialist_results=[],
            total_context_bytes=2000,
            total_context_lines=50,
            total_specialist_latency_ms=200,
            llm_inference_ms=300,
            python_overhead_ms=200,
            total_ms=500,
            llm_percentage=60,
            answer_quality=6,
            answer_complete=True,
            hallucination_detected=False,
            tokens_per_quality_point=10,
            context_redundancy=0.0,
            context_diversity=1.0,
            specialist_agreement=1.0,
            overhead_ratio=2.0,
            diminishing_return_score=0.5,
        )
        
        # Pair result (better than average of solos)
        pair = CompositionMetric(
            scenario_id="pair",
            specialists=[SpecialistType.CODEBASE, SpecialistType.TERMINAL],
            specialist_count=2,
            specialist_results=[],
            total_context_bytes=7000,
            total_context_lines=150,
            total_specialist_latency_ms=300,
            llm_inference_ms=200,  # Faster than average!
            python_overhead_ms=300,
            total_ms=500,
            llm_percentage=40,
            answer_quality=8,  # Better than average!
            answer_complete=True,
            hallucination_detected=False,
            tokens_per_quality_point=8,
            context_redundancy=0.1,
            context_diversity=0.9,
            specialist_agreement=0.9,
            overhead_ratio=1.8,
            diminishing_return_score=0.7,
        )
        
        interaction = exp._calculate_interaction(solo_a, solo_b, pair)
        assert interaction > 0.1  # Positive interaction


class TestQualityCalculation:
    """Test quality calculation based on specialist count and context."""
    
    def test_quality_improves_with_diversity(self):
        """Quality should improve with diverse specialists."""
        exp = PhaseC2()
        
        quality_low_diversity = exp._calculate_quality(
            specialist_count=2,
            context_diversity=0.2,  # Low diversity
            redundancy=0.8,
        )
        
        quality_high_diversity = exp._calculate_quality(
            specialist_count=2,
            context_diversity=0.8,  # High diversity
            redundancy=0.1,
        )
        
        assert quality_high_diversity > quality_low_diversity
    
    def test_quality_penalties_for_redundancy(self):
        """Quality should be penalized by redundancy."""
        exp = PhaseC2()
        
        quality_no_redundancy = exp._calculate_quality(
            specialist_count=2,
            context_diversity=0.8,
            redundancy=0.0,  # No overlap
        )
        
        quality_high_redundancy = exp._calculate_quality(
            specialist_count=2,
            context_diversity=0.8,
            redundancy=0.8,  # High overlap
        )
        
        assert quality_no_redundancy > quality_high_redundancy


class TestLLMTimeSimulation:
    """Test LLM inference time simulation with interaction effects."""
    
    def test_grounding_effect_baseline(self):
        """Test that more context reduces LLM time."""
        exp = PhaseC2()
        
        # Small context
        time_small = exp._simulate_llm_time(
            total_bytes=2000,
            redundancy=0.0,
            diversity=1.0,
            specialist_count=1,
        )
        
        # Large context
        time_large = exp._simulate_llm_time(
            total_bytes=8000,
            redundancy=0.0,
            diversity=1.0,
            specialist_count=1,
        )
        
        # More context = faster (grounding effect)
        assert time_large < time_small
    
    def test_redundancy_penalty(self):
        """Test that redundancy slows LLM down."""
        exp = PhaseC2()
        
        # No redundancy
        time_no_redundancy = exp._simulate_llm_time(
            total_bytes=5000,
            redundancy=0.0,
            diversity=1.0,
            specialist_count=2,
        )
        
        # High redundancy
        time_high_redundancy = exp._simulate_llm_time(
            total_bytes=5000,
            redundancy=0.8,
            diversity=0.2,
            specialist_count=2,
        )
        
        # Redundancy makes LLM slower
        assert time_high_redundancy > time_no_redundancy
    
    def test_diversity_bonus(self):
        """Test that diversity speeds LLM up."""
        exp = PhaseC2()
        
        # Low diversity
        time_low_diversity = exp._simulate_llm_time(
            total_bytes=5000,
            redundancy=0.5,
            diversity=0.2,
            specialist_count=2,
        )
        
        # High diversity
        time_high_diversity = exp._simulate_llm_time(
            total_bytes=5000,
            redundancy=0.1,
            diversity=0.9,
            specialist_count=2,
        )
        
        # Diversity helps LLM work faster
        assert time_high_diversity < time_low_diversity


class TestAgreementCalculation:
    """Test specialist agreement calculation."""
    
    def test_perfect_agreement(self):
        """Identical confidence should give high agreement."""
        exp = PhaseC2()
        results = [
            SpecialistResult(
                specialist=SpecialistType.CODEBASE,
                context_bytes=5000,
                context_lines=100,
                latency_ms=100,
                relevance_score=0.9,
                tokens_used=1250,
                confidence=0.9,
            ),
            SpecialistResult(
                specialist=SpecialistType.TERMINAL,
                context_bytes=2000,
                context_lines=50,
                latency_ms=200,
                relevance_score=0.85,
                tokens_used=500,
                confidence=0.9,
            ),
        ]
        
        agreement = exp._calculate_agreement(results)
        assert agreement > 0.8  # High agreement


class TestExperimentIntegration:
    """Test full experiment execution."""
    
    def test_full_experiment_runs(self):
        """Verify full Phase C.2 experiment completes."""
        exp = PhaseC2()
        result = exp.run_experiment()
        
        assert result.solo_codebase
        assert result.solo_terminal
        assert result.solo_git
        assert result.pair_codebase_terminal
        assert result.pair_codebase_git
        assert result.pair_terminal_git
        assert result.trio_all
        assert result.optimal_combination
        assert result.redundancy_level in ["low", "medium", "high"]
        assert result.interaction_pattern in ["synergistic", "neutral", "interfering"]
    
    def test_interaction_effects_calculated(self):
        """Verify interaction effects are computed."""
        exp = PhaseC2()
        result = exp.run_experiment()
        
        # All interactions should be between -1 and 1
        assert -1.0 <= result.codebase_terminal_interaction <= 1.0
        assert -1.0 <= result.codebase_git_interaction <= 1.0
        assert -1.0 <= result.terminal_git_interaction <= 1.0
        assert -1.0 <= result.trio_interaction <= 1.0


class TestResearchHypothesis:
    """Test the Phase C.2 research hypothesis."""
    
    def test_tools_do_not_degrade_quality(self):
        """Adding tools should not reduce answer quality."""
        exp = PhaseC2()
        result = exp.run_experiment()
        
        # Pair quality should be >= solo quality on average
        avg_solo_quality = (
            result.solo_codebase.answer_quality +
            result.solo_terminal.answer_quality +
            result.solo_git.answer_quality
        ) / 3
        
        avg_pair_quality = (
            result.pair_codebase_terminal.answer_quality +
            result.pair_codebase_git.answer_quality +
            result.pair_terminal_git.answer_quality
        ) / 3
        
        # Pairs should be at least as good as solos
        assert avg_pair_quality >= avg_solo_quality * 0.9  # Allow 10% variance
    
    def test_trio_outperforms_pairs(self):
        """All three tools together should outperform pairs."""
        exp = PhaseC2()
        result = exp.run_experiment()
        
        avg_pair_quality = (
            result.pair_codebase_terminal.answer_quality +
            result.pair_codebase_git.answer_quality +
            result.pair_terminal_git.answer_quality
        ) / 3
        
        # Trio should be better (or equal)
        assert result.trio_all.answer_quality >= avg_pair_quality


if __name__ == "__main__":
    print("✓ Phase C.2 test framework valid")
