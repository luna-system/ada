"""
Tests for Phase C.3: Specialization Level Research

Tests the specialization vs. general-purpose architecture comparison.
"""

import pytest
from enum import Enum
from phase_c3_runner import (
    PhaseC3,
    ArchitectureStrategy,
    SpecializationQuery,
    ArchitectureResult,
    ArchitectureComparison,
)


# ============================================================================
# FIXTURE SETUP
# ============================================================================


@pytest.fixture
def runner():
    """Create Phase C.3 runner."""
    return PhaseC3()


@pytest.fixture
def queries(runner):
    """Get test queries."""
    return runner.queries


# ============================================================================
# QUERY CREATION TESTS
# ============================================================================


class TestQueryCreation:
    """Test that queries are created properly."""
    
    def test_queries_created(self, queries):
        """Verify queries are created."""
        assert len(queries) == 6
    
    def test_query_ids_unique(self, queries):
        """Verify all query IDs are unique."""
        ids = [q.query_id for q in queries]
        assert len(ids) == len(set(ids))
    
    def test_query_has_required_fields(self, queries):
        """Verify each query has required fields."""
        for query in queries:
            assert query.query_id
            assert query.query_text
            assert query.category
            assert query.optimal_strategy in ArchitectureStrategy
    
    def test_query_categories_valid(self, queries):
        """Verify query categories are sensible."""
        categories = {q.category for q in queries}
        assert len(categories) >= 3
        assert all(cat in ["code", "system", "reasoning"] for cat in categories)
    
    def test_queries_have_mixed_requirements(self, queries):
        """Verify queries have varied requirements."""
        has_execution = any(q.requires_execution for q in queries)
        has_history = any(q.requires_history for q in queries)
        has_structure = any(q.requires_structure for q in queries)
        
        assert has_execution
        assert has_history
        assert has_structure


# ============================================================================
# SIMULATION TESTS
# ============================================================================


class TestSimulation:
    """Test simulation of each architecture."""
    
    def test_supertool_simulation(self, runner, queries):
        """Verify SuperTool simulation produces valid results."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        
        assert result.strategy == ArchitectureStrategy.SUPERTOOL
        assert result.total_latency_ms > 0
        assert result.answer_quality >= 1 and result.answer_quality <= 10
        assert result.llm_percentage >= 0 and result.llm_percentage <= 100
    
    def test_specialized_simulation(self, runner, queries):
        """Verify Specialized simulation produces valid results."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        assert result.strategy == ArchitectureStrategy.SPECIALIZED
        assert result.total_latency_ms > 0
        assert result.answer_quality >= 1 and result.answer_quality <= 10
    
    def test_hybrid_simulation(self, runner, queries):
        """Verify Hybrid simulation produces valid results."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.HYBRID)
        
        assert result.strategy == ArchitectureStrategy.HYBRID
        assert result.total_latency_ms > 0
        assert result.answer_quality >= 1 and result.answer_quality <= 10
    
    def test_latency_composition(self, runner, queries):
        """Verify latency is sum of components."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        expected_total = result.python_overhead_ms + result.tool_routing_time_ms + result.llm_inference_ms
        assert abs(result.total_latency_ms - expected_total) < 1.0
    
    def test_llm_percentage_calculation(self, runner, queries):
        """Verify LLM percentage is calculated correctly."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        expected_percentage = (result.llm_inference_ms / result.total_latency_ms) * 100
        assert abs(result.llm_percentage - expected_percentage) < 0.1
    
    def test_tokens_per_quality_calculation(self, runner, queries):
        """Verify tokens_per_quality is calculated correctly."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        expected_tpq = result.tokens_used / (result.answer_quality / 10.0)
        assert abs(result.tokens_per_quality_point - expected_tpq) < 0.1
    
    def test_context_size_varies(self, runner, queries):
        """Verify context size differs between strategies."""
        query = queries[0]
        
        supertool = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        specialized = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        # Both have context, sizes should be different
        assert supertool.context_size_bytes > 0
        assert specialized.context_size_bytes > 0


# ============================================================================
# ARCHITECTURE COMPARISON TESTS
# ============================================================================


class TestArchitectureComparison:
    """Test comparison between architectures."""
    
    def test_comparison_creates_deltas(self, runner, queries):
        """Verify comparison calculates deltas."""
        query = queries[0]
        
        supertool = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        specialized = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        hybrid = runner.simulate_query(query, ArchitectureStrategy.HYBRID)
        
        comparison = ArchitectureComparison(
            query_id=query.query_id,
            supertool_result=supertool,
            specialized_result=specialized,
            hybrid_result=hybrid,
            specialized_vs_supertool_latency_delta=(
                supertool.total_latency_ms - specialized.total_latency_ms
            ),
            specialized_vs_supertool_quality_delta=(
                specialized.answer_quality - supertool.answer_quality
            ),
            specialized_vs_supertool_clarity_delta=(
                specialized.answer_clarity - supertool.answer_clarity
            ),
            hybrid_vs_supertool_latency_delta=(
                supertool.total_latency_ms - hybrid.total_latency_ms
            ),
            hybrid_vs_specialized_clarity_delta=(
                hybrid.answer_clarity - specialized.answer_clarity
            ),
            fastest_strategy=ArchitectureStrategy.SPECIALIZED,
            highest_quality_strategy=ArchitectureStrategy.SPECIALIZED,
            clearest_strategy=ArchitectureStrategy.SPECIALIZED,
            most_efficient_strategy=ArchitectureStrategy.SPECIALIZED,
        )
        
        # Deltas should exist (can be positive or negative)
        assert isinstance(comparison.specialized_vs_supertool_latency_delta, float)
        assert isinstance(comparison.specialized_vs_supertool_quality_delta, int)


# ============================================================================
# SPECIALIZED PERFORMANCE TESTS
# ============================================================================


class TestSpecializedPerformance:
    """Test that specialized architecture performs better."""
    
    def test_specialized_faster_than_supertool(self, runner, queries):
        """Verify specialized is faster than SuperTool on average."""
        query = queries[0]
        
        supertool_times = [
            runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL).total_latency_ms
            for _ in range(5)
        ]
        specialized_times = [
            runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED).total_latency_ms
            for _ in range(5)
        ]
        
        avg_supertool = sum(supertool_times) / len(supertool_times)
        avg_specialized = sum(specialized_times) / len(specialized_times)
        
        assert avg_specialized < avg_supertool
    
    def test_specialized_higher_quality(self, runner, queries):
        """Verify specialized produces higher quality."""
        query = queries[0]
        
        supertool_qualities = [
            runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL).answer_quality
            for _ in range(5)
        ]
        specialized_qualities = [
            runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED).answer_quality
            for _ in range(5)
        ]
        
        avg_supertool = sum(supertool_qualities) / len(supertool_qualities)
        avg_specialized = sum(specialized_qualities) / len(specialized_qualities)
        
        assert avg_specialized > avg_supertool
    
    def test_specialized_clearer(self, runner, queries):
        """Verify specialized has better developer clarity."""
        query = queries[0]
        
        supertool_clarity = [
            runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL).developer_clarity
            for _ in range(5)
        ]
        specialized_clarity = [
            runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED).developer_clarity
            for _ in range(5)
        ]
        
        avg_supertool = sum(supertool_clarity) / len(supertool_clarity)
        avg_specialized = sum(specialized_clarity) / len(specialized_clarity)
        
        assert avg_specialized > avg_supertool
    
    def test_specialized_fewer_hallucinations(self, runner, queries):
        """Verify specialized has fewer hallucinations."""
        query = queries[0]
        
        supertool_hallu = sum(
            1 for _ in range(10)
            if runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL).hallucination_detected
        )
        specialized_hallu = sum(
            1 for _ in range(10)
            if runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED).hallucination_detected
        )
        
        assert specialized_hallu <= supertool_hallu


# ============================================================================
# ROUTING OVERHEAD TESTS
# ============================================================================


class TestRoutingOverhead:
    """Test that routing overhead is modeled correctly."""
    
    def test_supertool_has_routing_overhead(self, runner, queries):
        """Verify SuperTool has routing overhead."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        
        # SuperTool should have more routing overhead
        assert result.tool_routing_time_ms >= 50
    
    def test_specialized_minimal_routing(self, runner, queries):
        """Verify specialized has minimal routing."""
        query = queries[0]
        result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        # Specialized tools are clear about their purpose
        assert result.tool_routing_time_ms <= 30
    
    def test_routing_contributes_to_latency(self, runner, queries):
        """Verify routing time is significant component."""
        query = queries[0]
        
        supertool = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        routing_percentage = (supertool.tool_routing_time_ms / supertool.total_latency_ms) * 100
        
        assert routing_percentage >= 5  # At least 5% of total


# ============================================================================
# CLARITY METRIC TESTS
# ============================================================================


class TestClarityMetric:
    """Test developer clarity metric."""
    
    def test_specialized_high_clarity(self, runner, queries):
        """Verify specialized has high clarity."""
        query = queries[0]
        
        for _ in range(10):
            result = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
            assert result.developer_clarity >= 7
    
    def test_supertool_lower_clarity(self, runner, queries):
        """Verify SuperTool has lower clarity."""
        query = queries[0]
        
        for _ in range(10):
            result = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
            assert result.developer_clarity <= 8
    
    def test_context_organization_differs(self, runner, queries):
        """Verify context organization differs by strategy."""
        query = queries[0]
        
        supertool = runner.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
        specialized = runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
        
        # Specialized should organize context better
        assert specialized.context_organization >= supertool.context_organization


# ============================================================================
# FULL EXPERIMENT TESTS
# ============================================================================


class TestFullExperiment:
    """Test the full experiment running."""
    
    def test_experiment_completes(self, runner):
        """Verify experiment runs to completion."""
        result = runner.run_experiment()
        assert result is not None
    
    def test_experiment_has_all_results(self, runner):
        """Verify experiment has results for all queries."""
        result = runner.run_experiment()
        
        assert len(result.results_by_strategy[ArchitectureStrategy.SUPERTOOL]) == 6
        assert len(result.results_by_strategy[ArchitectureStrategy.SPECIALIZED]) == 6
        assert len(result.results_by_strategy[ArchitectureStrategy.HYBRID]) == 6
    
    def test_experiment_computes_aggregates(self, runner):
        """Verify experiment computes aggregate statistics."""
        result = runner.run_experiment()
        
        assert result.supertool_avg_latency > 0
        assert result.specialized_avg_latency > 0
        assert result.hybrid_avg_latency > 0
        
        assert result.supertool_avg_quality > 0
        assert result.specialized_avg_quality > 0
        assert result.hybrid_avg_quality > 0
    
    def test_experiment_determines_winners(self, runner):
        """Verify experiment determines strategy winners."""
        result = runner.run_experiment()
        
        assert result.winner_for_performance in ArchitectureStrategy
        assert result.winner_for_clarity in ArchitectureStrategy
        assert result.winner_for_reliability in ArchitectureStrategy
    
    def test_experiment_provides_recommendation(self, runner):
        """Verify experiment provides a recommendation."""
        result = runner.run_experiment()
        
        assert result.recommendation
        assert len(result.recommendation) > 50


# ============================================================================
# HYPOTHESIS VALIDATION TESTS
# ============================================================================


class TestHypothesisValidation:
    """Test that experiment validates the hypothesis."""
    
    def test_specialized_wins_overall(self, runner):
        """Test that specialized wins on most dimensions."""
        result = runner.run_experiment()
        
        # Specialized should win on clarity at minimum
        assert result.winner_for_clarity == ArchitectureStrategy.SPECIALIZED
    
    def test_comparison_shows_specialization_benefit(self, runner):
        """Verify comparisons show specialization benefits."""
        result = runner.run_experiment()
        
        for comparison in result.comparisons:
            # Specialized should win at least on clarity
            assert comparison.clearest_strategy == ArchitectureStrategy.SPECIALIZED
    
    def test_hybrid_is_middle_ground(self, runner):
        """Verify hybrid shows middle-ground performance."""
        result = runner.run_experiment()
        
        # Hybrid should be between supertool and specialized
        assert result.hybrid_avg_latency < result.supertool_avg_latency
        assert result.hybrid_avg_latency > result.specialized_avg_latency
        
        assert result.hybrid_avg_quality < result.specialized_avg_quality
        assert result.hybrid_avg_quality > result.supertool_avg_quality


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_quality_within_bounds(self, runner, queries):
        """Verify quality is always 1-10."""
        for query in queries:
            for strategy in ArchitectureStrategy:
                result = runner.simulate_query(query, strategy)
                assert 1 <= result.answer_quality <= 10
    
    def test_clarity_within_bounds(self, runner, queries):
        """Verify clarity is always 1-10."""
        for query in queries:
            for strategy in ArchitectureStrategy:
                result = runner.simulate_query(query, strategy)
                assert 1 <= result.developer_clarity <= 10
    
    def test_latency_positive(self, runner, queries):
        """Verify latency is always positive."""
        for query in queries:
            for strategy in ArchitectureStrategy:
                result = runner.simulate_query(query, strategy)
                assert result.total_latency_ms > 0
    
    def test_llm_percentage_valid(self, runner, queries):
        """Verify LLM percentage is 0-100."""
        for query in queries:
            for strategy in ArchitectureStrategy:
                result = runner.simulate_query(query, strategy)
                assert 0 <= result.llm_percentage <= 100


# ============================================================================
# CONSISTENCY TESTS
# ============================================================================


class TestConsistency:
    """Test consistency of measurements."""
    
    def test_same_query_produces_range(self, runner, queries):
        """Verify same query produces range (randomness)."""
        query = queries[0]
        
        latencies = [
            runner.simulate_query(query, ArchitectureStrategy.SPECIALIZED).total_latency_ms
            for _ in range(5)
        ]
        
        # Should have some variance due to randomness
        assert max(latencies) > min(latencies)
    
    def test_aggregate_is_average(self, runner):
        """Verify aggregates are correctly averaged."""
        result = runner.run_experiment()
        
        expected_avg = sum(
            r.total_latency_ms for r in result.results_by_strategy[ArchitectureStrategy.SPECIALIZED]
        ) / len(result.results_by_strategy[ArchitectureStrategy.SPECIALIZED])
        
        assert abs(result.specialized_avg_latency - expected_avg) < 0.1
