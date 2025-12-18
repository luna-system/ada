"""Phase 4: Weight Space Exploration 🔬

Scientific questions:
1. What are the optimal weights for ground truth correlation?
2. How does the weight space look? (smooth? peaks and valleys?)
3. Is there a Pareto frontier between recency and importance?
4. How sensitive is performance to weight changes?

Methodology:
- Grid search across decay/surprise weight combinations
- Measure correlation with ground truth for each
- Identify optimal configurations
- Visualize weight space as heatmap
- Compare to production defaults
"""

import json
import pytest
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from dataclasses import dataclass

from brain.prompt_builder.context_retriever import ContextRetriever


@dataclass
class WeightConfig:
    """Configuration for weight testing."""
    decay_weight: float
    surprise_weight: float
    relevance_weight: float = 0.20  # Keep constant
    habituation_weight: float = 0.10  # Keep constant
    
    def __post_init__(self):
        """Ensure weights sum to 1.0."""
        total = self.decay_weight + self.surprise_weight + self.relevance_weight + self.habituation_weight
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def to_dict(self) -> dict:
        return {
            "decay": self.decay_weight,
            "surprise": self.surprise_weight,
            "relevance": self.relevance_weight,
            "habituation": self.habituation_weight
        }


@dataclass
class WeightResult:
    """Result from testing a weight configuration."""
    config: WeightConfig
    correlation: float
    mean_importance: float
    std_importance: float
    gradient_distribution: Dict[str, int]


def load_synthetic_dataset(dataset_name: str = "realistic_100"):
    """Load a synthetic dataset."""
    fixture_path = Path(__file__).parent / "fixtures" / f"synthetic_{dataset_name}.json"
    with open(fixture_path) as f:
        return json.load(f)


def score_with_weights(
    turns: List[dict],
    weights: WeightConfig,
    retriever: ContextRetriever
) -> List[Tuple[float, float]]:
    """Score turns with given weights, return (importance, ground_truth) pairs.
    
    Returns:
        List of (calculated_importance, ground_truth_importance) tuples
    """
    results = []
    
    # Temporarily override retriever's weights
    original_weights = retriever.signal_weights.copy()
    retriever.set_signal_weights(weights.to_dict())
    
    try:
        for turn in turns:
            # Calculate importance (retriever handles all signals internally)
            importance = retriever.calculate_importance(turn, query="")
            ground_truth = turn['ground_truth']['true_importance']
            results.append((importance, ground_truth))
    finally:
        # Restore original weights
        retriever.set_signal_weights(original_weights)
    
    return results


def calculate_correlation(scores: List[Tuple[float, float]]) -> float:
    """Calculate Pearson correlation between calculated and ground truth."""
    calculated = [s[0] for s in scores]
    ground_truth = [s[1] for s in scores]
    return float(np.corrcoef(calculated, ground_truth)[0, 1])


class TestWeightSpaceExploration:
    """Explore the weight space to find optimal configurations."""
    
    def test_grid_search_coarse(self):
        """Coarse grid search: 5x5 grid of decay/surprise weights.
        
        This gives us a broad view of the weight space.
        """
        print("\n🔍 COARSE GRID SEARCH (5x5)")
        print("=" * 60)
        
        dataset = load_synthetic_dataset("realistic_100")
        retriever = ContextRetriever()
        
        results = []
        
        # Coarse grid: 0.1 to 0.7 in steps of 0.15
        decay_weights = np.arange(0.1, 0.75, 0.15)
        
        for decay_w in decay_weights:
            # Surprise weight is what's left after relevance (0.2) and habituation (0.1)
            surprise_w = 0.7 - decay_w  # 0.7 because 0.2 + 0.1 = 0.3 is fixed
            
            if surprise_w < 0.05:  # Skip invalid configurations
                continue
            
            weights = WeightConfig(
                decay_weight=decay_w,
                surprise_weight=surprise_w,
                relevance_weight=0.20,
                habituation_weight=0.10
            )
            
            scores = score_with_weights(dataset['turns'], weights, retriever)
            correlation = calculate_correlation(scores)
            
            calculated = [s[0] for s in scores]
            result = WeightResult(
                config=weights,
                correlation=correlation,
                mean_importance=float(np.mean(calculated)),
                std_importance=float(np.std(calculated)),
                gradient_distribution={}  # Not needed for grid search
            )
            results.append(result)
            
            print(f"decay={decay_w:.2f}, surprise={surprise_w:.2f} → r={correlation:.3f}")
        
        # Find best configuration
        best = max(results, key=lambda r: r.correlation)
        print(f"\n🏆 BEST CONFIGURATION:")
        print(f"   Decay: {best.config.decay_weight:.2f}")
        print(f"   Surprise: {best.config.surprise_weight:.2f}")
        print(f"   Correlation: {best.correlation:.3f}")
        
        # Compare to production default (0.4 decay, 0.3 surprise)
        prod_config = WeightConfig(decay_weight=0.4, surprise_weight=0.3)
        prod_scores = score_with_weights(dataset['turns'], prod_config, retriever)
        prod_correlation = calculate_correlation(prod_scores)
        
        print(f"\n📊 PRODUCTION DEFAULT:")
        print(f"   Decay: 0.40, Surprise: 0.30")
        print(f"   Correlation: {prod_correlation:.3f}")
        print(f"   Improvement: {(best.correlation - prod_correlation) * 100:.1f}%")
        
        # Verify we found something better
        assert best.correlation > 0.70, "Should find config with >0.70 correlation"
        assert len(results) >= 3, "Should test at least 3 configurations"
    
    def test_fine_grid_search(self):
        """Fine grid search around optimal region.
        
        Once we know the rough optimum, zoom in with finer resolution.
        """
        print("\n🔬 FINE GRID SEARCH (around optimum)")
        print("=" * 60)
        
        dataset = load_synthetic_dataset("realistic_100")
        retriever = ContextRetriever()
        
        results = []
        
        # Based on ablation: surprise-only was best (0.876)
        # So search around low decay, high surprise
        decay_weights = np.arange(0.05, 0.25, 0.05)  # Low decay region
        
        for decay_w in decay_weights:
            surprise_w = 0.7 - decay_w
            
            if surprise_w < 0.45 or surprise_w > 0.65:  # Stay in high-surprise region
                continue
            
            weights = WeightConfig(
                decay_weight=decay_w,
                surprise_weight=surprise_w,
                relevance_weight=0.20,
                habituation_weight=0.10
            )
            
            scores = score_with_weights(dataset['turns'], weights, retriever)
            correlation = calculate_correlation(scores)
            
            calculated = [s[0] for s in scores]
            result = WeightResult(
                config=weights,
                correlation=correlation,
                mean_importance=float(np.mean(calculated)),
                std_importance=float(np.std(calculated)),
                gradient_distribution={}
            )
            results.append(result)
            
            print(f"decay={decay_w:.2f}, surprise={surprise_w:.2f} → r={correlation:.3f}")
        
        best = max(results, key=lambda r: r.correlation)
        print(f"\n🎯 FINE-TUNED OPTIMUM:")
        print(f"   Decay: {best.config.decay_weight:.2f}")
        print(f"   Surprise: {best.config.surprise_weight:.2f}")
        print(f"   Correlation: {best.correlation:.3f}")
        
        # Should beat production
        prod_config = WeightConfig(decay_weight=0.4, surprise_weight=0.3)
        prod_scores = score_with_weights(dataset['turns'], prod_config, retriever)
        prod_correlation = calculate_correlation(prod_scores)
        
        improvement = (best.correlation - prod_correlation) / prod_correlation
        print(f"   Improvement over prod: {improvement * 100:.1f}%")
        
        assert best.correlation > prod_correlation, "Fine-tuned should beat production"
    
    def test_pareto_frontier(self):
        """Find Pareto frontier: trade-off between recency and importance.
        
        Some applications want recent context (high decay).
        Some want important context (high surprise).
        What's the Pareto frontier?
        """
        print("\n⚖️  PARETO FRONTIER ANALYSIS")
        print("=" * 60)
        
        dataset = load_synthetic_dataset("realistic_100")
        retriever = ContextRetriever()
        
        configurations = []
        
        # Test wide range
        for decay_w in np.arange(0.1, 0.7, 0.1):
            surprise_w = 0.7 - decay_w
            
            if surprise_w < 0.05:
                continue
            
            weights = WeightConfig(
                decay_weight=decay_w,
                surprise_weight=surprise_w,
                relevance_weight=0.20,
                habituation_weight=0.10
            )
            
            scores = score_with_weights(dataset['turns'], weights, retriever)
            correlation = calculate_correlation(scores)
            
            # Measure "recency bias" as correlation with 1/age
            # Calculate ages from timestamps
            most_recent = max(datetime.fromisoformat(t['timestamp']) for t in dataset['turns'])
            ages = [(most_recent - datetime.fromisoformat(t['timestamp'])).total_seconds() / 3600 
                    for t in dataset['turns']]
            calculated = [s[0] for s in scores]
            recency_correlation = abs(float(np.corrcoef(calculated, [1/max(a, 0.1) for a in ages])[0, 1]))
            
            configurations.append({
                'decay': decay_w,
                'surprise': surprise_w,
                'importance_correlation': correlation,
                'recency_correlation': recency_correlation
            })
            
            print(f"decay={decay_w:.1f}: importance_r={correlation:.3f}, recency_r={recency_correlation:.3f}")
        
        # Find Pareto frontier (maximize both objectives)
        print(f"\n📈 PARETO FRONTIER:")
        pareto_points = []
        
        for config in configurations:
            dominated = False
            for other in configurations:
                if (other['importance_correlation'] >= config['importance_correlation'] and
                    other['recency_correlation'] >= config['recency_correlation'] and
                    (other['importance_correlation'] > config['importance_correlation'] or
                     other['recency_correlation'] > config['recency_correlation'])):
                    dominated = True
                    break
            
            if not dominated:
                pareto_points.append(config)
                print(f"   decay={config['decay']:.1f}: imp_r={config['importance_correlation']:.3f}, rec_r={config['recency_correlation']:.3f}")
        
        # Show trade-off
        print(f"\n💡 TRADE-OFF INSIGHT:")
        high_decay = max(pareto_points, key=lambda c: c['decay'])
        low_decay = min(pareto_points, key=lambda c: c['decay'])
        
        print(f"   High decay ({high_decay['decay']:.1f}): Recency-focused")
        print(f"      → importance_r={high_decay['importance_correlation']:.3f}")
        print(f"      → recency_r={high_decay['recency_correlation']:.3f}")
        print(f"   Low decay ({low_decay['decay']:.1f}): Importance-focused")
        print(f"      → importance_r={low_decay['importance_correlation']:.3f}")
        print(f"      → recency_r={low_decay['recency_correlation']:.3f}")
        
        assert len(pareto_points) >= 2, "Should find multiple Pareto-optimal points"
    
    def test_weight_stability_landscape(self):
        """How stable is performance across the weight space?
        
        Are there sharp peaks (sensitive) or broad plateaus (stable)?
        """
        print("\n🗻 WEIGHT LANDSCAPE STABILITY")
        print("=" * 60)
        
        dataset = load_synthetic_dataset("realistic_100")
        retriever = ContextRetriever()
        
        # Dense grid
        decay_weights = np.arange(0.1, 0.7, 0.05)
        correlations = []
        
        for decay_w in decay_weights:
            surprise_w = 0.7 - decay_w
            
            if surprise_w < 0.05:
                continue
            
            weights = WeightConfig(
                decay_weight=decay_w,
                surprise_weight=surprise_w,
                relevance_weight=0.20,
                habituation_weight=0.10
            )
            
            scores = score_with_weights(dataset['turns'], weights, retriever)
            correlation = calculate_correlation(scores)
            correlations.append(correlation)
        
        # Analyze landscape
        gradients = np.diff(correlations)
        max_gradient = float(np.max(np.abs(gradients)))
        mean_gradient = float(np.mean(np.abs(gradients)))
        
        print(f"Correlation range: {min(correlations):.3f} to {max(correlations):.3f}")
        print(f"Max gradient: {max_gradient:.3f} per 0.05 weight change")
        print(f"Mean gradient: {mean_gradient:.3f} per 0.05 weight change")
        
        if max_gradient < 0.1:
            print("\n✅ STABLE LANDSCAPE: Performance changes gradually")
        else:
            print("\n⚠️  SHARP PEAKS: Performance sensitive to weight changes")
        
        # Test: landscape should not have extreme sensitivity
        assert max_gradient < 0.5, "Weight space should not have cliff-like drops"


class TestOptimalWeightsValidation:
    """Validate optimal weights on different datasets."""
    
    def test_optimal_on_realistic_dataset(self):
        """Test optimal weights on realistic_100 dataset."""
        print("\n✅ OPTIMAL WEIGHTS: realistic_100")
        
        dataset = load_synthetic_dataset("realistic_100")
        retriever = ContextRetriever()
        
        # From coarse search, expect low decay, high surprise
        optimal = WeightConfig(decay_weight=0.10, surprise_weight=0.60)
        prod = WeightConfig(decay_weight=0.40, surprise_weight=0.30)
        
        optimal_scores = score_with_weights(dataset['turns'], optimal, retriever)
        prod_scores = score_with_weights(dataset['turns'], prod, retriever)
        
        optimal_corr = calculate_correlation(optimal_scores)
        prod_corr = calculate_correlation(prod_scores)
        
        print(f"Optimal config: r={optimal_corr:.3f}")
        print(f"Production config: r={prod_corr:.3f}")
        print(f"Improvement: {(optimal_corr - prod_corr) * 100:.1f}%")
        
        assert optimal_corr > prod_corr, "Optimal should beat production"
    
    def test_optimal_on_recency_bias_dataset(self):
        """Test optimal weights on recency_bias_75 dataset.
        
        This dataset has exponential decay in ground truth.
        Does our optimal still work?
        """
        print("\n✅ OPTIMAL WEIGHTS: recency_bias_75")
        
        dataset = load_synthetic_dataset("recency_bias_75")
        retriever = ContextRetriever()
        
        # Same optimal from realistic dataset
        optimal = WeightConfig(decay_weight=0.10, surprise_weight=0.60)
        prod = WeightConfig(decay_weight=0.40, surprise_weight=0.30)
        
        optimal_scores = score_with_weights(dataset['turns'], optimal, retriever)
        prod_scores = score_with_weights(dataset['turns'], prod, retriever)
        
        optimal_corr = calculate_correlation(optimal_scores)
        prod_corr = calculate_correlation(prod_scores)
        
        print(f"Optimal config: r={optimal_corr:.3f}")
        print(f"Production config: r={prod_corr:.3f}")
        
        # On recency dataset, production might do better!
        if prod_corr > optimal_corr:
            print("💡 Production wins on recency-biased data!")
            print("   → Decay weight is important when ground truth has recency bias")
        else:
            print(f"Improvement: {(optimal_corr - prod_corr) * 100:.1f}%")
    
    def test_optimal_on_uniform_dataset(self):
        """Test optimal weights on uniform_50 dataset.
        
        This dataset has no temporal structure - pure importance.
        """
        print("\n✅ OPTIMAL WEIGHTS: uniform_50")
        
        dataset = load_synthetic_dataset("uniform_50")
        retriever = ContextRetriever()
        
        optimal = WeightConfig(decay_weight=0.10, surprise_weight=0.60)
        prod = WeightConfig(decay_weight=0.40, surprise_weight=0.30)
        
        optimal_scores = score_with_weights(dataset['turns'], optimal, retriever)
        prod_scores = score_with_weights(dataset['turns'], prod, retriever)
        
        optimal_corr = calculate_correlation(optimal_scores)
        prod_corr = calculate_correlation(prod_scores)
        
        print(f"Optimal config: r={optimal_corr:.3f}")
        print(f"Production config: r={prod_corr:.3f}")
        print(f"Improvement: {(optimal_corr - prod_corr) * 100:.1f}%")
        
        # On uniform data, optimal should dominate
        assert optimal_corr > prod_corr, "Optimal should beat production on uniform data"


if __name__ == "__main__":
    # Quick exploration
    print("🔬 Weight Space Exploration")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])
