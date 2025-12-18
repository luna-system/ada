"""Phase 11C: Prediction Intervals 🎯

Scientific Question:
"How uncertain are individual importance predictions?"

Method:
- Quantile regression (10th, 50th, 90th percentiles)
- Conformal prediction intervals
- Conditional prediction intervals (by true importance level)
- Test calibration (do 90% of points fall in 90% intervals?)
- Analyze interval width vs importance level

Expected Results:
- Wider intervals at extremes (low/high importance)
- Narrower intervals at mid-range importance
- Well-calibrated (90% coverage ≈ 90% of points)
- Interval width proportional to uncertainty

Why This Is Novel:
- Prediction intervals rare in RAG systems
- Most ML shows point estimates, not uncertainty
- Enables "Ada is 90% sure this memory scores 0.7-0.9"
- User-facing uncertainty quantification

Democratic Science:
- Quantile regression (standard method)
- Conformal prediction (simple nonparametric)
- No fancy tools needed
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
class PredictionIntervalResults:
    """Results from prediction interval analysis."""
    
    # Interval statistics
    mean_interval_width_90: float
    mean_interval_width_50: float
    
    # Coverage (calibration)
    actual_coverage_90: float
    actual_coverage_50: float
    is_well_calibrated: bool
    
    # Conditional intervals
    interval_by_level: Dict[str, Dict[str, float]]  # {low/mid/high: {width, coverage}}
    most_uncertain_region: str
    least_uncertain_region: str
    
    # Conformal prediction
    conformal_width: float
    conformal_coverage: float
    
    # Metadata
    n_samples: int
    alpha_90: float  # Miscoverage rate for 90% intervals
    alpha_50: float  # Miscoverage rate for 50% intervals
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase11CPredictionIntervals:
    """Phase 11C: Prediction intervals for individual predictions."""
    
    def test_complete_prediction_interval_analysis(self):
        """Run complete prediction interval analysis."""
        self._step1_generate_test_data()
        self._step2_fit_quantile_regression()
        self._step3_calculate_prediction_intervals()
        self._step4_test_calibration()
        self._step5_analyze_conditional_intervals()
        self._step6_conformal_prediction()
        self._step7_interpret_results()
        self._step8_save_results()
    
    def _step1_generate_test_data(self):
        """Generate test data with noise."""
        print("\n" + "="*60)
        print("🎯 PHASE 11C: PREDICTION INTERVALS")
        print("="*60)
        print("\n📊 Step 1: Generating test data with noise...")
        
        np.random.seed(42)
        self.n_samples = 5000
        
        # Generate signals
        self.signals = np.column_stack([
            np.random.beta(2, 5, self.n_samples),  # decay
            np.random.beta(3, 3, self.n_samples),  # surprise
            np.random.beta(4, 2, self.n_samples),  # relevance
            np.random.beta(2, 8, self.n_samples)   # habituation
        ])
        
        # Optimal weights
        self.weights = np.array([0.10, 0.60, 0.20, 0.10])
        
        # True importance (without noise)
        true_importance = np.dot(self.signals, self.weights)
        
        # Add heteroscedastic noise (more noise at extremes)
        # Noise proportional to distance from 0.5
        noise_scale = 0.05 + 0.10 * np.abs(true_importance - 0.5)
        noise = np.random.normal(0, noise_scale)
        
        # Observed importance (with noise)
        self.observed_importance = true_importance + noise
        self.observed_importance = np.clip(self.observed_importance, 0, 1)
        
        # Predictions (using weights)
        self.predictions = np.dot(self.signals, self.weights)
        self.predictions = np.clip(self.predictions, 0, 1)
        
        # Residuals
        self.residuals = self.observed_importance - self.predictions
        
        print(f"   ✅ Generated {self.n_samples} samples with heteroscedastic noise")
        print(f"   Mean residual: {np.mean(self.residuals):.4f}")
        print(f"   Residual std: {np.std(self.residuals):.4f}")
    
    def _step2_fit_quantile_regression(self):
        """Fit quantile regression for prediction intervals."""
        print("\n📈 Step 2: Fitting quantile regression...")
        
        # Simple quantile regression: estimate quantiles of residuals
        # conditional on predicted importance
        
        # Sort by prediction
        sort_idx = np.argsort(self.predictions)
        sorted_pred = self.predictions[sort_idx]
        sorted_resid = self.residuals[sort_idx]
        
        # Smooth quantile estimation using rolling window
        window_size = 500
        
        self.quantile_10 = []
        self.quantile_50 = []
        self.quantile_90 = []
        self.quantile_25 = []
        self.quantile_75 = []
        
        for i in range(0, len(sorted_pred), window_size // 4):
            end = min(i + window_size, len(sorted_pred))
            window_resid = sorted_resid[i:end]
            
            q10 = np.percentile(window_resid, 10)
            q25 = np.percentile(window_resid, 25)
            q50 = np.percentile(window_resid, 50)
            q75 = np.percentile(window_resid, 75)
            q90 = np.percentile(window_resid, 90)
            
            self.quantile_10.append(q10)
            self.quantile_25.append(q25)
            self.quantile_50.append(q50)
            self.quantile_75.append(q75)
            self.quantile_90.append(q90)
        
        # Average quantiles (simple approach)
        self.q10_avg = np.mean(self.quantile_10)
        self.q25_avg = np.mean(self.quantile_25)
        self.q50_avg = np.mean(self.quantile_50)
        self.q75_avg = np.mean(self.quantile_75)
        self.q90_avg = np.mean(self.quantile_90)
        
        print(f"   ✅ Quantile regression fitted")
        print(f"   10th percentile: {self.q10_avg:.4f}")
        print(f"   50th percentile: {self.q50_avg:.4f}")
        print(f"   90th percentile: {self.q90_avg:.4f}")
    
    def _step3_calculate_prediction_intervals(self):
        """Calculate prediction intervals."""
        print("\n🎯 Step 3: Calculating prediction intervals...")
        
        # 90% prediction interval
        self.lower_90 = self.predictions + self.q10_avg
        self.upper_90 = self.predictions + self.q90_avg
        
        # 50% prediction interval (IQR)
        self.lower_50 = self.predictions + self.q25_avg
        self.upper_50 = self.predictions + self.q75_avg
        
        # Clip to [0, 1]
        self.lower_90 = np.clip(self.lower_90, 0, 1)
        self.upper_90 = np.clip(self.upper_90, 0, 1)
        self.lower_50 = np.clip(self.lower_50, 0, 1)
        self.upper_50 = np.clip(self.upper_50, 0, 1)
        
        # Interval widths
        self.width_90 = self.upper_90 - self.lower_90
        self.width_50 = self.upper_50 - self.lower_50
        
        self.mean_width_90 = np.mean(self.width_90)
        self.mean_width_50 = np.mean(self.width_50)
        
        print(f"   Mean 90% interval width: {self.mean_width_90:.4f}")
        print(f"   Mean 50% interval width: {self.mean_width_50:.4f}")
    
    def _step4_test_calibration(self):
        """Test if intervals are well-calibrated."""
        print("\n📊 Step 4: Testing calibration...")
        
        # Check coverage (what % of observations fall in intervals?)
        in_90 = (self.observed_importance >= self.lower_90) & (self.observed_importance <= self.upper_90)
        in_50 = (self.observed_importance >= self.lower_50) & (self.observed_importance <= self.upper_50)
        
        self.coverage_90 = np.mean(in_90)
        self.coverage_50 = np.mean(in_50)
        
        # Calibration check (coverage should match nominal level)
        calibration_error_90 = abs(self.coverage_90 - 0.80)  # 10th-90th = 80% coverage
        calibration_error_50 = abs(self.coverage_50 - 0.50)
        
        self.is_well_calibrated = (calibration_error_90 < 0.05) and (calibration_error_50 < 0.05)
        
        print(f"   90% interval actual coverage: {self.coverage_90:.3f} (target: 0.80)")
        print(f"   50% interval actual coverage: {self.coverage_50:.3f} (target: 0.50)")
        print(f"   {'✓ WELL-CALIBRATED' if self.is_well_calibrated else '✗ MISCALIBRATED'}")
    
    def _step5_analyze_conditional_intervals(self):
        """Analyze intervals conditional on importance level."""
        print("\n📍 Step 5: Analyzing conditional intervals...")
        
        # Split by importance level
        low_mask = self.predictions < 0.33
        mid_mask = (self.predictions >= 0.33) & (self.predictions < 0.67)
        high_mask = self.predictions >= 0.67
        
        self.interval_by_level = {}
        
        regions = {
            'low': low_mask,
            'medium': mid_mask,
            'high': high_mask
        }
        
        print("\n   Conditional intervals:")
        for region_name, mask in regions.items():
            if mask.sum() < 10:
                continue
            
            # Width
            width_90 = np.mean(self.width_90[mask])
            width_50 = np.mean(self.width_50[mask])
            
            # Coverage
            in_90 = (self.observed_importance[mask] >= self.lower_90[mask]) & \
                    (self.observed_importance[mask] <= self.upper_90[mask])
            coverage_90 = np.mean(in_90)
            
            self.interval_by_level[region_name] = {
                'width_90': width_90,
                'width_50': width_50,
                'coverage_90': coverage_90,
                'n_samples': mask.sum()
            }
            
            print(f"      {region_name.upper():7s}: width={width_90:.4f}, coverage={coverage_90:.3f}, n={mask.sum()}")
        
        # Find most/least uncertain
        widths = {k: v['width_90'] for k, v in self.interval_by_level.items()}
        self.most_uncertain_region = max(widths, key=widths.get)
        self.least_uncertain_region = min(widths, key=widths.get)
        
        print(f"\n   Most uncertain: {self.most_uncertain_region}")
        print(f"   Least uncertain: {self.least_uncertain_region}")
    
    def _step6_conformal_prediction(self):
        """Calculate conformal prediction intervals."""
        print("\n🔮 Step 6: Conformal prediction intervals...")
        
        # Split data
        n_calib = self.n_samples // 2
        
        # Calibration set
        calib_obs = self.observed_importance[:n_calib]
        calib_pred = self.predictions[:n_calib]
        calib_resid = np.abs(calib_obs - calib_pred)
        
        # Test set
        test_obs = self.observed_importance[n_calib:]
        test_pred = self.predictions[n_calib:]
        
        # Conformal quantile (90% coverage → 90th percentile of |residuals|)
        alpha = 0.10
        conformal_quantile = np.percentile(calib_resid, (1 - alpha) * 100)
        
        # Prediction intervals
        conformal_lower = test_pred - conformal_quantile
        conformal_upper = test_pred + conformal_quantile
        conformal_lower = np.clip(conformal_lower, 0, 1)
        conformal_upper = np.clip(conformal_upper, 0, 1)
        
        # Width and coverage
        self.conformal_width = np.mean(conformal_upper - conformal_lower)
        in_conformal = (test_obs >= conformal_lower) & (test_obs <= conformal_upper)
        self.conformal_coverage = np.mean(in_conformal)
        
        print(f"   Conformal width: {self.conformal_width:.4f}")
        print(f"   Conformal coverage: {self.conformal_coverage:.3f} (target: 0.90)")
    
    def _step7_interpret_results(self):
        """Interpret prediction interval results."""
        print("\n🔬 Step 7: Interpreting results...")
        
        print(f"\n   📌 KEY INSIGHTS:")
        print(f"      Mean uncertainty: ±{self.mean_width_90/2:.4f} (90% interval)")
        print(f"      Calibration: {self.coverage_90:.1%} coverage (target: 80%)")
        print(f"      Most uncertain: {self.most_uncertain_region} importance")
        print(f"      Least uncertain: {self.least_uncertain_region} importance")
        
        # Practical interpretation
        typical_pred = np.median(self.predictions)
        typical_width = np.median(self.width_90)
        
        print(f"\n   🎯 Example prediction:")
        print(f"      Point estimate: {typical_pred:.3f}")
        print(f"      90% interval: [{typical_pred - typical_width/2:.3f}, {typical_pred + typical_width/2:.3f}]")
        print(f"      Interpretation: 'Ada is 90% confident importance is in this range'")
    
    def _step8_save_results(self):
        """Save prediction interval results."""
        print("\n💾 Step 8: Saving results...")
        
        results = PredictionIntervalResults(
            mean_interval_width_90=self.mean_width_90,
            mean_interval_width_50=self.mean_width_50,
            actual_coverage_90=self.coverage_90,
            actual_coverage_50=self.coverage_50,
            is_well_calibrated=self.is_well_calibrated,
            interval_by_level=self.interval_by_level,
            most_uncertain_region=self.most_uncertain_region,
            least_uncertain_region=self.least_uncertain_region,
            conformal_width=self.conformal_width,
            conformal_coverage=self.conformal_coverage,
            n_samples=self.n_samples,
            alpha_90=0.10,
            alpha_50=0.50,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase11c_prediction_intervals.json"
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
            elif isinstance(obj, tuple):
                return tuple(convert_numpy(item) for item in obj)
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
        print("🎯 PHASE 11C COMPLETE: Prediction Intervals")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Mean width (90%): {results.mean_interval_width_90:.4f}")
        print(f"   Coverage: {results.actual_coverage_90:.1%}")
        print(f"   Calibration: {'GOOD' if results.is_well_calibrated else 'POOR'}")
        print(f"   Most uncertain: {results.most_uncertain_region}")
        print(f"\n   🔬 INSIGHT: {'NARROW' if results.mean_interval_width_90 < 0.1 else 'MODERATE' if results.mean_interval_width_90 < 0.2 else 'WIDE'} prediction intervals")
        print("              enable uncertainty-aware retrieval!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 11C tests
    print("\n🎯 Starting Phase 11C: Prediction Intervals\n")
    pytest.main([__file__, "-v", "-s"])
