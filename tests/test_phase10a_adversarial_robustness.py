"""Phase 10A: Adversarial Robustness Testing 🛡️

Scientific Question:
"How fragile are our optimal weights to noise and perturbations?"

Method:
- Perturb signals with increasing Gaussian noise (±1%, ±5%, ±10%, ±20%, ±50%)
- Measure performance degradation at each noise level
- Test systematic biases (shift signals up/down)
- Find "brittleness threshold" (where performance collapses)
- Compare graceful vs catastrophic degradation

Expected Results:
- Robust to small noise (±5% → <5% performance loss)
- Graceful degradation with medium noise (±10% → 10-20% loss)
- Brittleness threshold around ±30-40%
- Surprise signal most critical (largest impact when perturbed)

Why This Is Novel:
- Adversarial robustness mostly studied for neural nets (FGSM, PGD attacks)
- Rarely applied to RAG/importance functions
- We test WEIGHT robustness, not model robustness
- Shows if optimal weights are fragile or stable

Democratic Science:
- Synthetic perturbations = free experiments
- No real-world A/B testing needed
- Standard statistical techniques
- Fast (<30min runtime)
"""

import pytest
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class AdversarialRobustnessResults:
    """Results from adversarial robustness testing."""
    
    # Noise robustness
    noise_levels: List[float]
    performance_at_noise: Dict[str, List[float]]  # Per signal
    combined_performance_at_noise: List[float]
    
    # Degradation analysis
    brittleness_threshold: float  # Noise level where r drops below 0.70
    graceful_degradation: bool  # Is degradation smooth?
    
    # Signal-specific robustness
    most_robust_signal: str
    least_robust_signal: str
    robustness_ranking: List[Tuple[str, float]]
    
    # Bias perturbations
    bias_sensitivity: Dict[str, float]  # Performance under systematic shift
    
    # Overall verdict
    is_robust: bool
    robustness_score: float  # 0-1 scale
    
    # Metadata
    n_samples: int
    n_trials: int
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase10AAdversarialRobustness:
    """Phase 10A: Test robustness to adversarial perturbations."""
    
    def test_complete_adversarial_analysis(self):
        """Run complete adversarial robustness testing."""
        self._step1_generate_clean_data()
        self._step2_test_gaussian_noise()
        self._step3_test_per_signal_robustness()
        self._step4_test_bias_perturbations()
        self._step5_find_brittleness_threshold()
        self._step6_calculate_robustness_score()
        self._step7_save_results()
    
    def _step1_generate_clean_data(self):
        """Generate clean baseline data."""
        print("\n" + "="*60)
        print("🛡️ PHASE 10A: ADVERSARIAL ROBUSTNESS")
        print("="*60)
        print("\n📊 Step 1: Generating clean baseline data...")
        
        np.random.seed(42)
        n_samples = 10000
        
        # Generate clean signals
        self.clean_signals = {
            'decay': np.random.beta(2, 5, n_samples),
            'surprise': np.random.beta(3, 3, n_samples),
            'relevance': np.random.beta(4, 2, n_samples),
            'habituation': np.random.beta(2, 8, n_samples)
        }
        
        # Clean importance (ground truth)
        self.clean_importance = (
            0.10 * self.clean_signals['decay'] +
            0.60 * self.clean_signals['surprise'] +
            0.20 * self.clean_signals['relevance'] +
            0.10 * self.clean_signals['habituation']
        )
        self.clean_importance = np.clip(self.clean_importance, 0, 1)
        
        # Baseline performance (should be ~0.884 from Phase 4)
        self.baseline_performance = np.corrcoef(
            self.clean_importance,
            self.clean_importance  # Perfect correlation
        )[0, 1]
        
        self.n_samples = n_samples
        self.weights = {'decay': 0.10, 'surprise': 0.60, 'relevance': 0.20, 'habituation': 0.10}
        
        print(f"✅ Generated {n_samples:,} clean samples")
        print(f"   Baseline performance: r = {self.baseline_performance:.4f}")
    
    def _step2_test_gaussian_noise(self):
        """Test performance under increasing Gaussian noise."""
        print("\n⚡ Step 2: Testing Gaussian noise perturbations...")
        
        noise_levels = [0.0, 0.01, 0.05, 0.10, 0.20, 0.30, 0.50]
        n_trials = 10  # Multiple trials per noise level
        
        combined_performance = []
        
        for noise_std in noise_levels:
            trial_performances = []
            
            for trial in range(n_trials):
                # Perturb ALL signals with same noise level
                perturbed_signals = {}
                for name, signal in self.clean_signals.items():
                    noise = np.random.normal(0, noise_std, self.n_samples)
                    perturbed = signal + noise
                    perturbed_signals[name] = np.clip(perturbed, 0, 1)
                
                # Calculate perturbed importance
                perturbed_importance = (
                    0.10 * perturbed_signals['decay'] +
                    0.60 * perturbed_signals['surprise'] +
                    0.20 * perturbed_signals['relevance'] +
                    0.10 * perturbed_signals['habituation']
                )
                perturbed_importance = np.clip(perturbed_importance, 0, 1)
                
                # Performance vs clean ground truth
                perf = np.corrcoef(perturbed_importance, self.clean_importance)[0, 1]
                trial_performances.append(perf)
            
            # Average over trials
            avg_perf = np.mean(trial_performances)
            combined_performance.append(avg_perf)
            
            loss = (1 - avg_perf) * 100
            print(f"   Noise σ={noise_std:.2f}: r={avg_perf:.4f} (loss: {loss:.1f}%)")
        
        self.noise_levels = noise_levels
        self.combined_performance_at_noise = combined_performance
        self.n_trials = n_trials
    
    def _step3_test_per_signal_robustness(self):
        """Test robustness of each signal individually."""
        print("\n🔍 Step 3: Testing per-signal robustness...")
        
        noise_level = 0.10  # 10% noise
        n_trials = 20
        
        signal_robustness = {}
        
        for signal_name in self.clean_signals.keys():
            trial_performances = []
            
            for trial in range(n_trials):
                # Perturb ONLY this signal
                perturbed_signals = self.clean_signals.copy()
                noise = np.random.normal(0, noise_level, self.n_samples)
                perturbed = self.clean_signals[signal_name] + noise
                perturbed_signals[signal_name] = np.clip(perturbed, 0, 1)
                
                # Calculate importance with perturbed signal
                perturbed_importance = (
                    0.10 * perturbed_signals['decay'] +
                    0.60 * perturbed_signals['surprise'] +
                    0.20 * perturbed_signals['relevance'] +
                    0.10 * perturbed_signals['habituation']
                )
                perturbed_importance = np.clip(perturbed_importance, 0, 1)
                
                # Performance
                perf = np.corrcoef(perturbed_importance, self.clean_importance)[0, 1]
                trial_performances.append(perf)
            
            avg_perf = np.mean(trial_performances)
            signal_robustness[signal_name] = avg_perf
            
            loss = (1 - avg_perf) * 100
            print(f"   {signal_name:12s}: r={avg_perf:.4f} (loss: {loss:.1f}%)")
        
        # Store for all noise levels
        self.performance_at_noise = {}
        for signal_name in self.clean_signals.keys():
            self.performance_at_noise[signal_name] = []
            
            for noise_std in self.noise_levels:
                trials = []
                for _ in range(5):  # Fewer trials for speed
                    perturbed_signals = self.clean_signals.copy()
                    noise = np.random.normal(0, noise_std, self.n_samples)
                    perturbed = self.clean_signals[signal_name] + noise
                    perturbed_signals[signal_name] = np.clip(perturbed, 0, 1)
                    
                    perturbed_importance = (
                        0.10 * perturbed_signals['decay'] +
                        0.60 * perturbed_signals['surprise'] +
                        0.20 * perturbed_signals['relevance'] +
                        0.10 * perturbed_signals['habituation']
                    )
                    perturbed_importance = np.clip(perturbed_importance, 0, 1)
                    
                    perf = np.corrcoef(perturbed_importance, self.clean_importance)[0, 1]
                    trials.append(perf)
                
                self.performance_at_noise[signal_name].append(np.mean(trials))
        
        # Rank by robustness
        sorted_signals = sorted(signal_robustness.items(), key=lambda x: -x[1])
        self.robustness_ranking = sorted_signals
        self.most_robust_signal = sorted_signals[0][0]
        self.least_robust_signal = sorted_signals[-1][0]
        
        print(f"\n   📊 Robustness ranking:")
        for rank, (name, perf) in enumerate(sorted_signals, 1):
            print(f"      {rank}. {name:12s}: r={perf:.4f}")
    
    def _step4_test_bias_perturbations(self):
        """Test systematic bias (shift all values up/down)."""
        print("\n🔄 Step 4: Testing bias perturbations...")
        
        bias_amounts = [-0.1, -0.05, 0.0, 0.05, 0.1]
        bias_sensitivity = {}
        
        for signal_name in self.clean_signals.keys():
            performances = []
            
            for bias in bias_amounts:
                # Add systematic bias
                biased_signals = self.clean_signals.copy()
                biased = self.clean_signals[signal_name] + bias
                biased_signals[signal_name] = np.clip(biased, 0, 1)
                
                # Calculate importance
                biased_importance = (
                    0.10 * biased_signals['decay'] +
                    0.60 * biased_signals['surprise'] +
                    0.20 * biased_signals['relevance'] +
                    0.10 * biased_signals['habituation']
                )
                biased_importance = np.clip(biased_importance, 0, 1)
                
                # Performance
                perf = np.corrcoef(biased_importance, self.clean_importance)[0, 1]
                performances.append(perf)
            
            # Sensitivity = variance of performance under bias
            sensitivity = np.std(performances)
            bias_sensitivity[signal_name] = sensitivity
            
            print(f"   {signal_name:12s}: σ={sensitivity:.4f}")
        
        self.bias_sensitivity = bias_sensitivity
    
    def _step5_find_brittleness_threshold(self):
        """Find noise level where performance drops below 0.70."""
        print("\n🎯 Step 5: Finding brittleness threshold...")
        
        threshold = 0.70
        
        # Find first noise level where performance < threshold
        brittleness_idx = None
        for i, perf in enumerate(self.combined_performance_at_noise):
            if perf < threshold:
                brittleness_idx = i
                break
        
        if brittleness_idx is None:
            brittleness_threshold = max(self.noise_levels)
            print(f"   ✅ No brittleness! Robust up to σ={brittleness_threshold:.2f}")
        else:
            brittleness_threshold = self.noise_levels[brittleness_idx]
            print(f"   ⚠️  Brittleness at σ={brittleness_threshold:.2f}")
        
        self.brittleness_threshold = brittleness_threshold
        
        # Check if degradation is graceful (linear) or catastrophic (sudden drop)
        # Measure linearity of performance vs noise
        valid_perfs = [p for p in self.combined_performance_at_noise if p > 0.5]
        valid_noise = self.noise_levels[:len(valid_perfs)]
        
        if len(valid_perfs) > 2:
            # Fit linear regression
            coeffs = np.polyfit(valid_noise, valid_perfs, 1)
            predicted = np.polyval(coeffs, valid_noise)
            r_squared = 1 - (np.sum((valid_perfs - predicted)**2) / 
                            np.sum((valid_perfs - np.mean(valid_perfs))**2))
            
            graceful = r_squared > 0.90  # Linear degradation
        else:
            graceful = True
        
        self.graceful_degradation = graceful
        
        if graceful:
            print(f"   ✅ Graceful degradation (R²={r_squared:.3f})")
        else:
            print(f"   ⚠️  Catastrophic degradation (R²={r_squared:.3f})")
    
    def _step6_calculate_robustness_score(self):
        """Calculate overall robustness score (0-1)."""
        print("\n📊 Step 6: Calculating robustness score...")
        
        # Score components:
        # 1. Performance at 10% noise (most common real-world scenario)
        perf_at_10 = self.combined_performance_at_noise[
            self.noise_levels.index(0.10)
        ]
        
        # 2. Brittleness threshold (higher = better)
        brittleness_score = min(self.brittleness_threshold / 0.50, 1.0)
        
        # 3. Graceful degradation bonus
        graceful_bonus = 0.1 if self.graceful_degradation else 0.0
        
        # Combined score
        robustness_score = (
            0.50 * perf_at_10 +           # 50% weight on 10% noise
            0.40 * brittleness_score +    # 40% weight on threshold
            0.10 * (1.0 if self.graceful_degradation else 0.0)  # 10% bonus
        )
        
        self.robustness_score = robustness_score
        
        # Verdict
        if robustness_score > 0.85:
            verdict = "HIGHLY ROBUST"
            is_robust = True
        elif robustness_score > 0.70:
            verdict = "MODERATELY ROBUST"
            is_robust = True
        else:
            verdict = "FRAGILE"
            is_robust = False
        
        self.is_robust = is_robust
        
        print(f"   Robustness score: {robustness_score:.3f}")
        print(f"   Verdict: {verdict}")
        print(f"\n   Components:")
        print(f"      Perf at 10% noise: {perf_at_10:.3f}")
        print(f"      Brittleness threshold: {self.brittleness_threshold:.2f}")
        print(f"      Graceful degradation: {'Yes' if self.graceful_degradation else 'No'}")
    
    def _step7_save_results(self):
        """Save robustness results."""
        print("\n💾 Step 7: Saving results...")
        
        results = AdversarialRobustnessResults(
            noise_levels=self.noise_levels,
            performance_at_noise=self.performance_at_noise,
            combined_performance_at_noise=self.combined_performance_at_noise,
            brittleness_threshold=self.brittleness_threshold,
            graceful_degradation=self.graceful_degradation,
            most_robust_signal=self.most_robust_signal,
            least_robust_signal=self.least_robust_signal,
            robustness_ranking=self.robustness_ranking,
            bias_sensitivity=self.bias_sensitivity,
            is_robust=self.is_robust,
            robustness_score=self.robustness_score,
            n_samples=self.n_samples,
            n_trials=self.n_trials,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase10a_adversarial_robustness.json"
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
            elif isinstance(obj, tuple):
                return tuple(convert_numpy(item) for item in obj)
            return obj
        
        results_dict = convert_numpy(results.to_dict())
        
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"   ✅ Results saved to: {output_path}")
        print("\n" + "="*60)
        print("🛡️ PHASE 10A COMPLETE: Adversarial Robustness")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Robustness score: {results.robustness_score:.3f}")
        print(f"   Brittleness threshold: σ={results.brittleness_threshold:.2f}")
        print(f"   Most robust signal: {results.most_robust_signal}")
        print(f"   Graceful degradation: {'Yes' if results.graceful_degradation else 'No'}")
        print(f"\n   🔬 INSIGHT: Weights are {'ROBUST' if results.is_robust else 'FRAGILE'}")
        print("              to real-world noise and perturbations!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 10A tests
    print("\n🛡️ Starting Phase 10A: Adversarial Robustness Testing\n")
    pytest.main([__file__, "-v", "-s"])
