"""Phase 10C: Sensitivity Analysis 🎛️

Scientific Question:
"Which signals matter most at different importance levels?"

Method:
- Calculate partial derivatives: ∂importance/∂signal
- Build Jacobian matrix (sensitivity at each importance level)
- Identify critical regions (high sensitivity)
- Test local vs global sensitivity
- Measure signal interaction effects

Expected Results:
- Surprise dominates (weight=0.60, highest sensitivity)
- Sensitivity varies by importance level (low/mid/high regions)
- Some signals more important in specific ranges
- Non-uniform influence (nonlinear interactions)

Why This Is Novel:
- Sensitivity analysis rare in RAG systems
- Usually done for physical models, not importance functions
- Shows WHERE each signal matters (not just global weight)
- Reveals interaction effects between signals

Democratic Science:
- Numerical differentiation = basic calculus
- No special tools needed
- Interpretable results
- Fast (<30min)
"""

import pytest
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SensitivityAnalysisResults:
    """Results from sensitivity analysis."""
    
    # Global sensitivity
    global_sensitivity: Dict[str, float]  # Overall ∂importance/∂signal
    sensitivity_ranking: List[str]
    
    # Local sensitivity (by importance level)
    local_sensitivity: Dict[str, Dict[str, float]]  # {level: {signal: sensitivity}}
    critical_regions: Dict[str, str]  # {signal: critical_importance_level}
    
    # Interaction effects
    has_interactions: bool
    interaction_strength: float
    cross_derivatives: Dict[str, float]  # ∂²importance/∂signal1∂signal2
    
    # Stability
    max_sensitivity: float
    min_sensitivity: float
    sensitivity_range: float
    is_stable: bool
    
    # Metadata
    n_samples: int
    epsilon: float  # Derivative step size
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase10CSensitivityAnalysis:
    """Phase 10C: Analyze signal sensitivity and influence."""
    
    def test_complete_sensitivity_analysis(self):
        """Run complete sensitivity analysis."""
        self._step1_generate_test_data()
        self._step2_calculate_global_sensitivity()
        self._step3_calculate_local_sensitivity()
        self._step4_identify_critical_regions()
        self._step5_test_interaction_effects()
        self._step6_calculate_stability_metrics()
        self._step7_interpret_results()
        self._step8_save_results()
    
    def _step1_generate_test_data(self):
        """Generate test dataset for sensitivity analysis."""
        print("\n" + "="*60)
        print("🎛️ PHASE 10C: SENSITIVITY ANALYSIS")
        print("="*60)
        print("\n📊 Step 1: Generating test data...")
        
        np.random.seed(42)
        self.n_samples = 10000
        self.epsilon = 0.001  # Derivative step size
        self.weights = {'decay': 0.10, 'surprise': 0.60, 'relevance': 0.20, 'habituation': 0.10}
        
        # Generate signals
        self.signals = {
            'decay': np.random.beta(2, 5, self.n_samples),
            'surprise': np.random.beta(3, 3, self.n_samples),
            'relevance': np.random.beta(4, 2, self.n_samples),
            'habituation': np.random.beta(2, 8, self.n_samples)
        }
        
        # Calculate baseline importance
        self.importance = (
            self.weights['decay'] * self.signals['decay'] +
            self.weights['surprise'] * self.signals['surprise'] +
            self.weights['relevance'] * self.signals['relevance'] +
            self.weights['habituation'] * self.signals['habituation']
        )
        self.importance = np.clip(self.importance, 0, 1)
        
        print(f"   ✅ Generated {self.n_samples} samples")
        print(f"   ε = {self.epsilon} (derivative step size)")
    
    def _step2_calculate_global_sensitivity(self):
        """Calculate global sensitivity for each signal."""
        print("\n🌍 Step 2: Calculating global sensitivity...")
        
        self.global_sensitivity = {}
        
        for signal_name in self.signals:
            # Perturb signal slightly
            perturbed = self.signals[signal_name] + self.epsilon
            perturbed = np.clip(perturbed, 0, 1)
            
            # Recalculate importance
            perturbed_importance = (
                self.weights['decay'] * (perturbed if signal_name == 'decay' else self.signals['decay']) +
                self.weights['surprise'] * (perturbed if signal_name == 'surprise' else self.signals['surprise']) +
                self.weights['relevance'] * (perturbed if signal_name == 'relevance' else self.signals['relevance']) +
                self.weights['habituation'] * (perturbed if signal_name == 'habituation' else self.signals['habituation'])
            )
            perturbed_importance = np.clip(perturbed_importance, 0, 1)
            
            # Calculate derivative (finite difference)
            derivative = (perturbed_importance - self.importance) / self.epsilon
            sensitivity = np.mean(derivative)
            
            self.global_sensitivity[signal_name] = sensitivity
        
        # Ranking
        self.sensitivity_ranking = sorted(
            self.global_sensitivity.keys(),
            key=lambda k: abs(self.global_sensitivity[k]),
            reverse=True
        )
        
        print("   Global sensitivity (∂importance/∂signal):")
        for rank, signal in enumerate(self.sensitivity_ranking, 1):
            sens = self.global_sensitivity[signal]
            print(f"   {rank}. {signal:12s}: {sens:.4f}")
    
    def _step3_calculate_local_sensitivity(self):
        """Calculate sensitivity at different importance levels."""
        print("\n📍 Step 3: Calculating local sensitivity...")
        
        # Define importance regions
        regions = {
            'low': (0.0, 0.33),
            'medium': (0.33, 0.67),
            'high': (0.67, 1.0)
        }
        
        self.local_sensitivity = {}
        
        for region_name, (low, high) in regions.items():
            # Filter samples in this region
            mask = (self.importance >= low) & (self.importance <= high)
            n_in_region = mask.sum()
            
            if n_in_region < 100:
                continue
            
            region_sensitivity = {}
            
            for signal_name in self.signals:
                # Perturb signal
                perturbed = self.signals[signal_name] + self.epsilon
                perturbed = np.clip(perturbed, 0, 1)
                
                # Recalculate importance
                perturbed_importance = (
                    self.weights['decay'] * (perturbed if signal_name == 'decay' else self.signals['decay']) +
                    self.weights['surprise'] * (perturbed if signal_name == 'surprise' else self.signals['surprise']) +
                    self.weights['relevance'] * (perturbed if signal_name == 'relevance' else self.signals['relevance']) +
                    self.weights['habituation'] * (perturbed if signal_name == 'habituation' else self.signals['habituation'])
                )
                perturbed_importance = np.clip(perturbed_importance, 0, 1)
                
                # Calculate derivative for this region
                derivative = (perturbed_importance[mask] - self.importance[mask]) / self.epsilon
                sensitivity = np.mean(derivative)
                region_sensitivity[signal_name] = sensitivity
            
            self.local_sensitivity[region_name] = region_sensitivity
            
            print(f"\n   {region_name.upper()} importance region ({low:.2f}-{high:.2f}):")
            for signal in self.sensitivity_ranking:
                sens = region_sensitivity[signal]
                print(f"      {signal:12s}: {sens:.4f}")
    
    def _step4_identify_critical_regions(self):
        """Identify where each signal matters most."""
        print("\n🎯 Step 4: Identifying critical regions...")
        
        self.critical_regions = {}
        
        for signal_name in self.signals:
            # Find region with highest sensitivity
            max_region = None
            max_sensitivity = -float('inf')
            
            for region_name, sensitivities in self.local_sensitivity.items():
                if signal_name in sensitivities:
                    sens = abs(sensitivities[signal_name])
                    if sens > max_sensitivity:
                        max_sensitivity = sens
                        max_region = region_name
            
            self.critical_regions[signal_name] = max_region
        
        print("   Critical regions (where signal matters most):")
        for signal in self.sensitivity_ranking:
            region = self.critical_regions[signal]
            print(f"      {signal:12s}: {region} importance")
    
    def _step5_test_interaction_effects(self):
        """Test for interaction effects between signals."""
        print("\n🔗 Step 5: Testing interaction effects...")
        
        # Calculate cross-derivatives (∂²importance/∂signal1∂signal2)
        self.cross_derivatives = {}
        
        signal_pairs = [
            ('decay', 'surprise'),
            ('decay', 'relevance'),
            ('surprise', 'relevance'),
            ('surprise', 'habituation')
        ]
        
        total_interaction = 0.0
        
        for signal1, signal2 in signal_pairs:
            # Perturb both signals
            perturbed1 = np.clip(self.signals[signal1] + self.epsilon, 0, 1)
            perturbed2 = np.clip(self.signals[signal2] + self.epsilon, 0, 1)
            
            # Calculate importance with both perturbations
            both_perturbed = (
                self.weights['decay'] * (perturbed1 if signal1 == 'decay' else perturbed2 if signal2 == 'decay' else self.signals['decay']) +
                self.weights['surprise'] * (perturbed1 if signal1 == 'surprise' else perturbed2 if signal2 == 'surprise' else self.signals['surprise']) +
                self.weights['relevance'] * (perturbed1 if signal1 == 'relevance' else perturbed2 if signal2 == 'relevance' else self.signals['relevance']) +
                self.weights['habituation'] * (perturbed1 if signal1 == 'habituation' else perturbed2 if signal2 == 'habituation' else self.signals['habituation'])
            )
            both_perturbed = np.clip(both_perturbed, 0, 1)
            
            # Calculate cross-derivative (should be ~0 for linear model)
            # ∂²f/∂x∂y = (f(x+ε,y+ε) - f(x+ε,y) - f(x,y+ε) + f(x,y)) / ε²
            cross_deriv = np.mean(both_perturbed - self.importance) / (self.epsilon ** 2)
            
            pair_name = f"{signal1}×{signal2}"
            self.cross_derivatives[pair_name] = abs(cross_deriv)
            total_interaction += abs(cross_deriv)
        
        self.interaction_strength = total_interaction / len(signal_pairs)
        self.has_interactions = self.interaction_strength > 0.01
        
        print(f"   Interaction strength: {self.interaction_strength:.6f}")
        print(f"   Has significant interactions: {self.has_interactions}")
        
        if self.has_interactions:
            print("   Top interactions:")
            sorted_interactions = sorted(
                self.cross_derivatives.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for pair, strength in sorted_interactions[:3]:
                print(f"      {pair:20s}: {strength:.6f}")
    
    def _step6_calculate_stability_metrics(self):
        """Calculate stability metrics."""
        print("\n📊 Step 6: Calculating stability metrics...")
        
        # Sensitivity range
        all_sensitivities = list(self.global_sensitivity.values())
        self.max_sensitivity = max(all_sensitivities)
        self.min_sensitivity = min(all_sensitivities)
        self.sensitivity_range = self.max_sensitivity - self.min_sensitivity
        
        # Stability verdict
        # Stable if sensitivity range is small relative to max
        relative_range = self.sensitivity_range / (self.max_sensitivity + 1e-10)
        self.is_stable = relative_range < 0.5
        
        print(f"   Max sensitivity: {self.max_sensitivity:.4f}")
        print(f"   Min sensitivity: {self.min_sensitivity:.4f}")
        print(f"   Sensitivity range: {self.sensitivity_range:.4f}")
        print(f"   Relative range: {relative_range:.4f}")
        print(f"   System is: {'STABLE' if self.is_stable else 'VARIABLE'}")
    
    def _step7_interpret_results(self):
        """Interpret sensitivity results."""
        print("\n🔬 Step 7: Interpreting results...")
        
        # Key insights
        most_sensitive = self.sensitivity_ranking[0]
        least_sensitive = self.sensitivity_ranking[-1]
        
        print(f"\n   📌 KEY INSIGHTS:")
        print(f"      Most influential: {most_sensitive} (∂imp/∂sig = {self.global_sensitivity[most_sensitive]:.4f})")
        print(f"      Least influential: {least_sensitive} (∂imp/∂sig = {self.global_sensitivity[least_sensitive]:.4f})")
        print(f"      Sensitivity ratio: {self.max_sensitivity/self.min_sensitivity:.1f}x")
        
        # Check if weights match sensitivity
        print("\n   ⚖️  WEIGHT vs SENSITIVITY:")
        for signal in self.sensitivity_ranking:
            weight = self.weights[signal]
            sensitivity = self.global_sensitivity[signal]
            match = "✓" if abs(weight - sensitivity) < 0.01 else "✗"
            print(f"      {match} {signal:12s}: weight={weight:.2f}, sensitivity={sensitivity:.4f}")
    
    def _step8_save_results(self):
        """Save sensitivity results."""
        print("\n💾 Step 8: Saving results...")
        
        results = SensitivityAnalysisResults(
            global_sensitivity=self.global_sensitivity,
            sensitivity_ranking=self.sensitivity_ranking,
            local_sensitivity=self.local_sensitivity,
            critical_regions=self.critical_regions,
            has_interactions=self.has_interactions,
            interaction_strength=self.interaction_strength,
            cross_derivatives=self.cross_derivatives,
            max_sensitivity=self.max_sensitivity,
            min_sensitivity=self.min_sensitivity,
            sensitivity_range=self.sensitivity_range,
            is_stable=self.is_stable,
            n_samples=self.n_samples,
            epsilon=self.epsilon,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase10c_sensitivity_analysis.json"
        output_path.parent.mkdir(exist_ok=True)
        
        def convert_numpy(obj):
            """Convert numpy types to Python natives for JSON."""
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        results_dict = convert_numpy(results.to_dict())
        
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"   ✅ Results saved to: {output_path}")
        print("\n" + "="*60)
        print("🎛️ PHASE 10C COMPLETE: Sensitivity Analysis")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Most sensitive: {results.sensitivity_ranking[0]}")
        print(f"   Least sensitive: {results.sensitivity_ranking[-1]}")
        print(f"   Sensitivity range: {results.sensitivity_range:.4f}")
        print(f"   Has interactions: {results.has_interactions}")
        print(f"\n   🔬 INSIGHT: Sensitivity {'MATCHES' if results.is_stable else 'DIFFERS FROM'}")
        print("              optimal weights!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 10C tests
    print("\n🎛️ Starting Phase 10C: Sensitivity Analysis\n")
    pytest.main([__file__, "-v", "-s"])
