"""
Tests for Phase C.1 Function-Level Granularity Research

Validates the experiment framework and research methodology.
"""

import pytest
from phase_c1_runner import (
    Granularity,
    QueryGranularity,
    GranularityMetric,
    GranularityAnalysis,
    PhaseC1Result,
    PhaseC1,
)


class TestPhaseC1Setup:
    """Test Phase C.1 experiment initialization."""
    
    def test_experiment_creates_queries(self):
        """Verify experiment creates all test queries."""
        exp = PhaseC1()
        assert len(exp.queries) == 6
        assert len([q for q in exp.queries if q.granularity == Granularity.FUNCTION]) == 2
        assert len([q for q in exp.queries if q.granularity == Granularity.CLASS]) == 2
        assert len([q for q in exp.queries if q.granularity == Granularity.MODULE]) == 2
    
    def test_queries_have_all_fields(self):
        """Verify all queries are properly defined."""
        exp = PhaseC1()
        for query in exp.queries:
            assert query.query_id
            assert query.granularity in [Granularity.FUNCTION, Granularity.CLASS, Granularity.MODULE]
            assert query.target
            assert query.description
            assert query.expected_lines > 0
            assert query.category


class TestQuerySimulation:
    """Test query simulation at different granularities."""
    
    def test_narrow_query_simulation(self):
        """Test function-level query simulation."""
        exp = PhaseC1()
        query = QueryGranularity(
            query_id="test-func",
            granularity=Granularity.FUNCTION,
            target="test",
            description="test",
            expected_lines=15,
            category="code",
        )
        metric = exp.simulate_query(query)
        
        assert metric.query_id == "test-func"
        assert metric.granularity == Granularity.FUNCTION
        assert 500 <= metric.context_bytes <= 1500
        assert 5 <= metric.context_lines <= 25
        assert 50 <= metric.python_overhead_ms <= 100
        assert 300 <= metric.llm_inference_ms <= 600
        assert metric.answer_quality >= 5
    
    def test_medium_query_simulation(self):
        """Test class-level query simulation."""
        exp = PhaseC1()
        query = QueryGranularity(
            query_id="test-class",
            granularity=Granularity.CLASS,
            target="test",
            description="test",
            expected_lines=100,
            category="code",
        )
        metric = exp.simulate_query(query)
        
        assert metric.granularity == Granularity.CLASS
        assert 3000 <= metric.context_bytes <= 6000
        assert 80 <= metric.context_lines <= 150
        assert 100 <= metric.python_overhead_ms <= 200
        assert 150 <= metric.llm_inference_ms <= 350
        assert metric.answer_quality >= 7
    
    def test_broad_query_simulation(self):
        """Test module-level query simulation."""
        exp = PhaseC1()
        query = QueryGranularity(
            query_id="test-module",
            granularity=Granularity.MODULE,
            target="test",
            description="test",
            expected_lines=300,
            category="code",
        )
        metric = exp.simulate_query(query)
        
        assert metric.granularity == Granularity.MODULE
        assert 8000 <= metric.context_bytes <= 15000
        assert 250 <= metric.context_lines <= 350
        assert 200 <= metric.python_overhead_ms <= 400
        assert 100 <= metric.llm_inference_ms <= 250
        assert metric.answer_quality >= 8
    
    def test_latency_pattern_narrow_vs_broad(self):
        """Verify LLM time decreases with broader context (grounding effect)."""
        exp = PhaseC1()
        
        narrow_query = QueryGranularity(
            query_id="narrow",
            granularity=Granularity.FUNCTION,
            target="test",
            description="test",
            expected_lines=15,
            category="code",
        )
        
        broad_query = QueryGranularity(
            query_id="broad",
            granularity=Granularity.MODULE,
            target="test",
            description="test",
            expected_lines=300,
            category="code",
        )
        
        # Run multiple times to check trend
        narrow_times = [exp.simulate_query(narrow_query).llm_inference_ms for _ in range(5)]
        broad_times = [exp.simulate_query(broad_query).llm_inference_ms for _ in range(5)]
        
        avg_narrow = sum(narrow_times) / len(narrow_times)
        avg_broad = sum(broad_times) / len(broad_times)
        
        # Broad should be faster on average (Phase B grounding effect)
        assert avg_broad < avg_narrow, f"Expected broad ({avg_broad}ms) < narrow ({avg_narrow}ms)"
    
    def test_quality_pattern_narrow_vs_broad(self):
        """Verify quality improves with broader context."""
        exp = PhaseC1()
        
        narrow_query = QueryGranularity(
            query_id="narrow",
            granularity=Granularity.FUNCTION,
            target="test",
            description="test",
            expected_lines=15,
            category="code",
        )
        
        broad_query = QueryGranularity(
            query_id="broad",
            granularity=Granularity.MODULE,
            target="test",
            description="test",
            expected_lines=300,
            category="code",
        )
        
        # Run multiple times
        narrow_qualities = [exp.simulate_query(narrow_query).answer_quality for _ in range(5)]
        broad_qualities = [exp.simulate_query(broad_query).answer_quality for _ in range(5)]
        
        avg_narrow = sum(narrow_qualities) / len(narrow_qualities)
        avg_broad = sum(broad_qualities) / len(broad_qualities)
        
        # Broad should be higher quality
        assert avg_broad > avg_narrow, f"Expected broad ({avg_broad}) > narrow ({avg_narrow})"


class TestGranularityAnalysis:
    """Test granularity-level analysis aggregation."""
    
    def test_analysis_calculation(self):
        """Verify analysis calculations work correctly."""
        metrics = [
            GranularityMetric(
                query_id="q1",
                granularity=Granularity.FUNCTION,
                context_bytes=100,
                context_lines=10,
                llm_inference_ms=100.0,
                python_overhead_ms=50.0,
                total_ms=150.0,
                llm_percentage=66.7,
                answer_quality=5,
                answer_complete=True,
                hallucination_detected=False,
                tokens_per_quality_point=10.0,
                tokens_used=50,
                relevance_score=0.9,
                overhead_ratio=2.0,
            ),
            GranularityMetric(
                query_id="q2",
                granularity=Granularity.FUNCTION,
                context_bytes=150,
                context_lines=15,
                llm_inference_ms=120.0,
                python_overhead_ms=60.0,
                total_ms=180.0,
                llm_percentage=66.7,
                answer_quality=6,
                answer_complete=True,
                hallucination_detected=False,
                tokens_per_quality_point=12.0,
                tokens_used=72,
                relevance_score=0.85,
                overhead_ratio=2.5,
            ),
        ]
        
        analysis = GranularityAnalysis(
            granularity=Granularity.FUNCTION,
            queries=[],
            metrics=metrics,
        )
        analysis.calculate()
        
        assert analysis.avg_llm_ms == 110.0
        assert analysis.avg_quality == 5.5
        assert analysis.avg_hallucination_rate == 0.0
        assert analysis.avg_efficiency == 11.0


class TestComparisonLogic:
    """Test comparison logic between granularities."""
    
    def test_comparison_metrics(self):
        """Verify comparison calculation."""
        exp = PhaseC1()
        
        # Create two analyses
        narrow_metrics = [
            GranularityMetric(
                query_id="n1",
                granularity=Granularity.FUNCTION,
                context_bytes=100,
                context_lines=10,
                llm_inference_ms=400.0,
                python_overhead_ms=50.0,
                total_ms=450.0,
                llm_percentage=88.9,
                answer_quality=5,
                answer_complete=True,
                hallucination_detected=True,
                tokens_per_quality_point=100.0,
                tokens_used=500,
                relevance_score=0.8,
                overhead_ratio=1.0,
            ),
        ]
        
        broad_metrics = [
            GranularityMetric(
                query_id="b1",
                granularity=Granularity.MODULE,
                context_bytes=1000,
                context_lines=300,
                llm_inference_ms=200.0,
                python_overhead_ms=200.0,
                total_ms=400.0,
                llm_percentage=50.0,
                answer_quality=10,
                answer_complete=True,
                hallucination_detected=False,
                tokens_per_quality_point=50.0,
                tokens_used=500,
                relevance_score=0.99,
                overhead_ratio=2.0,
            ),
        ]
        
        narrow = GranularityAnalysis(Granularity.FUNCTION, [], narrow_metrics)
        broad = GranularityAnalysis(Granularity.MODULE, [], broad_metrics)
        narrow.calculate()
        broad.calculate()
        
        comparison = exp._compare_granularities(narrow, broad)
        
        # Broad should be faster
        assert comparison['llm_improvement'] > 0
        # Broad should have better quality
        assert comparison['quality_improvement'] > 0


class TestOptimalGranularitySelection:
    """Test optimal granularity determination."""
    
    def test_optimal_selection_logic(self):
        """Verify optimal granularity is selected correctly."""
        exp = PhaseC1()
        result = exp.run_experiment()
        
        # Should always select CLASS as optimal for this data pattern
        assert result.optimal_granularity == Granularity.CLASS
        assert result.optimal_explanation
        assert "CLASS-LEVEL" in result.optimal_explanation.upper() or "class-level" in result.optimal_explanation


class TestExperimentIntegration:
    """Test full experiment execution."""
    
    def test_full_experiment_runs(self):
        """Verify full Phase C.1 experiment completes."""
        exp = PhaseC1()
        result = exp.run_experiment()
        
        assert result.query_set
        assert result.narrow_analysis
        assert result.medium_analysis
        assert result.broad_analysis
        assert result.narrow_vs_medium_improvement
        assert result.medium_vs_broad_improvement
        assert result.optimal_granularity
    
    def test_experiment_metrics_consistency(self):
        """Verify metrics are consistent across the experiment."""
        exp = PhaseC1()
        result = exp.run_experiment()
        
        # Check that each analysis has the right number of queries
        assert len(result.narrow_analysis.metrics) == 2
        assert len(result.medium_analysis.metrics) == 2
        assert len(result.broad_analysis.metrics) == 2
        
        # Check that metrics match query count
        for analysis in [result.narrow_analysis, result.medium_analysis, result.broad_analysis]:
            assert len(analysis.metrics) == len(analysis.queries)


class TestResearchHypothesis:
    """Test the Phase C.1 research hypothesis."""
    
    def test_phase_b_effect_still_holds(self):
        """Verify Phase B grounding effect is replicated in C.1."""
        exp = PhaseC1()
        result = exp.run_experiment()
        
        # Phase B: More tools → faster LLM
        # C.1: More context (broader granularity) → faster LLM
        
        # Function-level should be slowest
        assert result.narrow_analysis.avg_llm_ms > result.medium_analysis.avg_llm_ms
        # Module-level should be fastest
        assert result.broad_analysis.avg_llm_ms <= result.medium_analysis.avg_llm_ms
    
    def test_quality_improves_with_granularity(self):
        """Verify broader granularity produces better quality."""
        exp = PhaseC1()
        result = exp.run_experiment()
        
        assert result.narrow_analysis.avg_quality <= result.medium_analysis.avg_quality
        assert result.medium_analysis.avg_quality <= result.broad_analysis.avg_quality


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
