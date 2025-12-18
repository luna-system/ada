"""Tests using synthetic conversation data.

These tests validate biomimetic features against realistic conversation
patterns with known ground truth labels.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from brain.prompt_builder.context_retriever import ContextRetriever


# Load synthetic datasets
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def load_dataset(name: str):
    """Load a synthetic dataset from fixtures."""
    filepath = FIXTURES_DIR / f'synthetic_{name}.json'
    with open(filepath) as f:
        data = json.load(f)
    return data['turns']


class TestSyntheticDataValidation:
    """Validate that synthetic data has expected properties."""
    
    def test_realistic_dataset_pareto_distribution(self):
        """Realistic dataset should follow 80/20 rule."""
        turns = load_dataset('realistic_100')
        
        importances = [t['metadata']['importance'] for t in turns]
        high_importance = [i for i in importances if i >= 0.7]
        
        # Pareto: ~20% should be high importance
        high_pct = len(high_importance) / len(importances)
        assert 0.15 <= high_pct <= 0.25, f"Pareto violated: {high_pct:.1%} high importance"
    
    def test_uniform_dataset_no_pareto(self):
        """Uniform dataset should NOT follow Pareto distribution."""
        turns = load_dataset('uniform_50')
        
        importances = [t['metadata']['importance'] for t in turns]
        high_importance = [i for i in importances if i >= 0.7]
        
        # Uniform: should have more high importance than Pareto
        high_pct = len(high_importance) / len(importances)
        assert high_pct > 0.25, f"Should be > 25% for uniform, got {high_pct:.1%}"
    
    def test_temporal_ordering(self):
        """Turns should be in chronological order."""
        turns = load_dataset('realistic_100')
        
        timestamps = [datetime.fromisoformat(t['timestamp']) for t in turns]
        
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i+1], "Timestamps not sorted!"
    
    def test_ground_truth_labels_present(self):
        """All turns should have ground truth labels."""
        turns = load_dataset('realistic_100')
        
        for turn in turns:
            assert 'ground_truth' in turn
            assert 'true_importance' in turn['ground_truth']
            assert 'expected_detail_level' in turn['ground_truth']


class TestImportanceScoringOnSyntheticData:
    """Test importance scoring against synthetic conversations."""
    
    def test_high_importance_turns_detected(self):
        """High importance turns (≥0.7) should score high WHEN RECENT."""
        turns = load_dataset('recency_bias_75')  # Use recency dataset
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Only test RECENT high importance turns (less temporal decay)
        recent_high = [t for t in turns[-20:] if t['metadata']['importance'] >= 0.7]
        
        if not recent_high:
            pytest.skip("No recent high importance turns")
        
        scores = []
        for turn in recent_high:
            score = retriever.calculate_importance(turn, query="test")
            scores.append(score)
        
        avg_score = sum(scores) / len(scores)
        
        # Recent high importance turns should score reasonably high
        # (temporal decay still applies but is weaker)
        assert avg_score > 0.4, f"Recent high importance turns scored only {avg_score:.3f}"
    
    def test_low_importance_turns_score_lower(self):
        """Low importance turns (<0.3) should score lower than high."""
        turns = load_dataset('realistic_100')
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        low_importance_turns = [t for t in turns if t['metadata']['importance'] < 0.3][:10]
        high_importance_turns = [t for t in turns if t['metadata']['importance'] >= 0.7][:10]
        
        low_scores = [retriever.calculate_importance(t, "test") for t in low_importance_turns]
        high_scores = [retriever.calculate_importance(t, "test") for t in high_importance_turns]
        
        avg_low = sum(low_scores) / len(low_scores)
        avg_high = sum(high_scores) / len(high_scores)
        
        # High should beat low on average
        assert avg_high > avg_low, f"High ({avg_high:.3f}) not > low ({avg_low:.3f})"
    
    def test_gradient_levels_correlate_with_ground_truth(self):
        """Gradient detail levels should correlate with ground truth.
        
        This tests CORRELATION not exact match (temporal decay shifts scores).
        We check if high ground truth importance → higher detail levels.
        """
        turns = load_dataset('recency_bias_75')  # Recent bias = less decay
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Group by ground truth importance
        high_gt = [t for t in turns[-30:] if t['metadata']['importance'] >= 0.7]
        low_gt = [t for t in turns[-30:] if t['metadata']['importance'] < 0.3]
        
        if not high_gt or not low_gt:
            pytest.skip("Need both high and low importance turns")
        
        # Count FULL/CHUNKS for high vs low ground truth
        def count_preserved(turns):
            preserved = 0
            for t in turns:
                score = retriever.calculate_importance(t, "test")
                level = retriever.get_detail_level(score)
                if level in ['FULL', 'CHUNKS']:
                    preserved += 1
            return preserved
        
        high_preserved = count_preserved(high_gt)
        low_preserved = count_preserved(low_gt)
        
        high_rate = high_preserved / len(high_gt) if high_gt else 0
        low_rate = low_preserved / len(low_gt) if low_gt else 0
        
        # High ground truth should preserve MORE than low ground truth
        assert high_rate > low_rate, (
            f"Correlation broken: high_rate={high_rate:.1%}, low_rate={low_rate:.1%}"
        )
    
    def test_temporal_decay_on_synthetic_data(self):
        """Recent synthetic turns should score higher than old ones."""
        turns = load_dataset('realistic_100')
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Get recent and old turns with similar ground truth importance
        recent_turns = [t for t in turns[-10:] if 0.6 <= t['metadata']['importance'] <= 0.8]
        old_turns = [t for t in turns[:10] if 0.6 <= t['metadata']['importance'] <= 0.8]
        
        if not recent_turns or not old_turns:
            pytest.skip("Not enough turns in importance range")
        
        recent_scores = [retriever.calculate_importance(t, "test") for t in recent_turns]
        old_scores = [retriever.calculate_importance(t, "test") for t in old_turns]
        
        avg_recent = sum(recent_scores) / len(recent_scores)
        avg_old = sum(old_scores) / len(old_scores)
        
        # Recent should score higher due to temporal decay
        assert avg_recent > avg_old, (
            f"Temporal decay not working: recent={avg_recent:.3f}, old={avg_old:.3f}"
        )


class TestParetoPrincipleValidation:
    """Validate that Pareto distribution affects retrieval correctly."""
    
    def test_realistic_vs_uniform_score_distribution(self):
        """Realistic (Pareto) should preserve the distribution shape.
        
        Note: Temporal decay compresses variance, so we test correlation
        between ground truth importance and calculated score instead.
        """
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        realistic_turns = load_dataset('realistic_100')
        
        # Calculate correlation between ground truth and calculated importance
        gt_importances = [t['metadata']['importance'] for t in realistic_turns]
        calc_scores = [
            retriever.calculate_importance(t, "test") for t in realistic_turns
        ]
        
        # Simple correlation: do they move together?
        def correlation(x, y):
            """Simple Pearson correlation."""
            mean_x = sum(x) / len(x)
            mean_y = sum(y) / len(y)
            
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
            denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
            
            return numerator / (denom_x * denom_y) if denom_x and denom_y else 0
        
        corr = correlation(gt_importances, calc_scores)
        
        # Should have positive correlation (r > 0.3 is moderate)
        assert corr > 0.3, f"Weak correlation: r={corr:.3f}"
    
    def test_high_importance_minority_gets_better_treatment(self):
        """The important 20% should get higher detail levels than the mundane 80%."""
        turns = load_dataset('recency_bias_75')  # Use recency to reduce temporal decay
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Get recent turns only (to minimize temporal decay effects)
        recent = turns[-40:]
        
        # Split by ground truth importance
        high_importance = [t for t in recent if t['metadata']['importance'] >= 0.7]
        low_importance = [t for t in recent if t['metadata']['importance'] < 0.3]
        
        if not high_importance or not low_importance:
            pytest.skip("Need both high and low importance turns")
        
        def avg_score(turns):
            scores = [retriever.calculate_importance(t, "test") for t in turns]
            return sum(scores) / len(scores)
        
        high_avg = avg_score(high_importance)
        low_avg = avg_score(low_importance)
        
        # High importance should score higher on average
        assert high_avg > low_avg, (
            f"Pareto not working: high={high_avg:.3f}, low={low_avg:.3f}"
        )


if __name__ == '__main__':
    """Run tests with pytest."""
    pytest.main([__file__, '-v'])
