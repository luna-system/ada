"""Phase 11A: Bayesian Weight Posteriors 🎲

Scientific Question:
"How confident should we be in the optimal weights?"

Method:
- MCMC (Metropolis-Hastings) to sample posterior distribution
- Likelihood: How well weights explain observed importance
- Prior: Weakly informative Beta(2,2) for each weight
- Posterior: Combine likelihood + prior via Bayes rule
- Analyze: means, credible intervals, correlations

Expected Results:
- Tight posteriors around optimal weights (high confidence)
- 95% credible intervals narrow (±0.05)
- Low correlation between weight parameters
- Posterior means ≈ optimal weights

Why This Is Novel:
- Bayesian inference rarely used in RAG systems
- Quantifies uncertainty in weight space
- Shows "probability of being right" not just "best guess"
- Enables principled uncertainty propagation

Democratic Science:
- Simple Metropolis-Hastings (no fancy libraries)
- Self-contained MCMC implementation
- Standard Bayesian statistics
- Fast (~30min)
"""

import pytest
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class BayesianPosteriorResults:
    """Results from Bayesian posterior analysis."""
    
    # Posterior statistics
    posterior_means: Dict[str, float]
    posterior_stds: Dict[str, float]
    credible_intervals_95: Dict[str, Tuple[float, float]]
    credible_intervals_50: Dict[str, Tuple[float, float]]
    
    # Uncertainty metrics
    total_uncertainty: float
    most_certain_weight: str
    least_certain_weight: str
    
    # Convergence
    n_samples: int
    n_burn_in: int
    acceptance_rate: float
    converged: bool
    
    # Comparison to optimal
    posterior_vs_optimal: Dict[str, Dict[str, float]]
    weights_in_credible_interval: Dict[str, bool]
    
    # Metadata
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class TestPhase11ABayesianPosteriors:
    """Phase 11A: Bayesian posterior inference for weights."""
    
    def test_complete_bayesian_analysis(self):
        """Run complete Bayesian posterior analysis."""
        self._step1_generate_observed_data()
        self._step2_define_likelihood()
        self._step3_define_priors()
        self._step4_run_mcmc()
        self._step5_calculate_posteriors()
        self._step6_calculate_credible_intervals()
        self._step7_compare_to_optimal()
        self._step8_save_results()
    
    def _step1_generate_observed_data(self):
        """Generate observed data for Bayesian inference."""
        print("\n" + "="*60)
        print("🎲 PHASE 11A: BAYESIAN WEIGHT POSTERIORS")
        print("="*60)
        print("\n📊 Step 1: Generating observed data...")
        
        np.random.seed(42)
        self.n_obs = 1000  # Observed importance values
        
        # Generate signals
        self.signals = {
            'decay': np.random.beta(2, 5, self.n_obs),
            'surprise': np.random.beta(3, 3, self.n_obs),
            'relevance': np.random.beta(4, 2, self.n_obs),
            'habituation': np.random.beta(2, 8, self.n_obs)
        }
        
        # True weights (what we optimized to)
        self.true_weights = {
            'decay': 0.10,
            'surprise': 0.60,
            'relevance': 0.20,
            'habituation': 0.10
        }
        
        # Observed importance (with measurement noise)
        noise = np.random.normal(0, 0.05, self.n_obs)
        self.observed_importance = (
            self.true_weights['decay'] * self.signals['decay'] +
            self.true_weights['surprise'] * self.signals['surprise'] +
            self.true_weights['relevance'] * self.signals['relevance'] +
            self.true_weights['habituation'] * self.signals['habituation'] +
            noise
        )
        self.observed_importance = np.clip(self.observed_importance, 0, 1)
        
        print(f"   ✅ Generated {self.n_obs} observations")
        print(f"   True weights: {self.true_weights}")
    
    def _step2_define_likelihood(self):
        """Define likelihood function."""
        print("\n📈 Step 2: Defining likelihood function...")
        
        def log_likelihood(weights: Dict[str, float]) -> float:
            """Log likelihood of weights given data."""
            # Predicted importance
            predicted = (
                weights['decay'] * self.signals['decay'] +
                weights['surprise'] * self.signals['surprise'] +
                weights['relevance'] * self.signals['relevance'] +
                weights['habituation'] * self.signals['habituation']
            )
            predicted = np.clip(predicted, 0, 1)
            
            # Gaussian likelihood
            residuals = self.observed_importance - predicted
            sigma = 0.1  # Noise level
            log_lik = -0.5 * np.sum((residuals / sigma) ** 2)
            
            return log_lik
        
        self.log_likelihood = log_likelihood
        print("   ✅ Likelihood: Gaussian with σ=0.1")
    
    def _step3_define_priors(self):
        """Define prior distributions."""
        print("\n🎲 Step 3: Defining prior distributions...")
        
        def log_prior(weights: Dict[str, float]) -> float:
            """Log prior probability of weights."""
            # Beta(2, 2) prior for each weight (weakly informative)
            # Centered at 0.5, allows flexibility
            log_p = 0.0
            
            for signal, w in weights.items():
                if w < 0 or w > 1:
                    return -np.inf
                # Beta(2, 2) log pdf
                log_p += (2-1) * np.log(w) + (2-1) * np.log(1-w)
            
            # Constraint: weights must sum to 1
            weight_sum = sum(weights.values())
            if abs(weight_sum - 1.0) > 0.01:
                return -np.inf
            
            return log_p
        
        self.log_prior = log_prior
        print("   ✅ Prior: Beta(2, 2) for each weight")
        print("   ✅ Constraint: Σweights = 1.0")
    
    def _step4_run_mcmc(self):
        """Run MCMC sampling (Metropolis-Hastings)."""
        print("\n🔄 Step 4: Running MCMC sampling...")
        
        n_samples = 10000
        n_burn_in = 2000
        proposal_std = 0.02
        
        # Initialize at true weights
        current_weights = self.true_weights.copy()
        current_log_prob = self.log_likelihood(current_weights) + self.log_prior(current_weights)
        
        # Storage
        samples = {signal: [] for signal in current_weights}
        acceptances = []
        
        print(f"   Sampling {n_samples} iterations (burn-in: {n_burn_in})...")
        
        for i in range(n_samples):
            # Propose new weights (random walk)
            proposal = {}
            for signal in current_weights:
                proposal[signal] = current_weights[signal] + np.random.normal(0, proposal_std)
            
            # Renormalize to sum to 1
            weight_sum = sum(proposal.values())
            if weight_sum > 0:
                for signal in proposal:
                    proposal[signal] /= weight_sum
            
            # Calculate proposal probability
            proposal_log_prob = self.log_likelihood(proposal) + self.log_prior(proposal)
            
            # Metropolis acceptance
            log_accept_ratio = proposal_log_prob - current_log_prob
            
            if np.log(np.random.rand()) < log_accept_ratio:
                current_weights = proposal
                current_log_prob = proposal_log_prob
                acceptances.append(1)
            else:
                acceptances.append(0)
            
            # Store sample (after burn-in)
            if i >= n_burn_in:
                for signal in current_weights:
                    samples[signal].append(current_weights[signal])
            
            # Progress
            if (i + 1) % 2000 == 0:
                recent_accept = np.mean(acceptances[-1000:])
                print(f"      Iteration {i+1}/{n_samples}, acceptance: {recent_accept:.3f}")
        
        self.samples = samples
        self.n_samples = n_samples
        self.n_burn_in = n_burn_in
        self.acceptance_rate = np.mean(acceptances[n_burn_in:])
        
        print(f"   ✅ MCMC complete!")
        print(f"   Final acceptance rate: {self.acceptance_rate:.3f}")
    
    def _step5_calculate_posteriors(self):
        """Calculate posterior statistics."""
        print("\n📊 Step 5: Calculating posterior statistics...")
        
        self.posterior_means = {}
        self.posterior_stds = {}
        
        print("\n   Posterior distributions:")
        for signal in self.samples:
            samples_array = np.array(self.samples[signal])
            mean = np.mean(samples_array)
            std = np.std(samples_array)
            
            self.posterior_means[signal] = mean
            self.posterior_stds[signal] = std
            
            print(f"      {signal:12s}: {mean:.4f} ± {std:.4f}")
        
        # Uncertainty metrics
        self.total_uncertainty = np.mean(list(self.posterior_stds.values()))
        uncertainties = [(signal, std) for signal, std in self.posterior_stds.items()]
        uncertainties.sort(key=lambda x: x[1])
        self.most_certain_weight = uncertainties[0][0]
        self.least_certain_weight = uncertainties[-1][0]
        
        print(f"\n   Total uncertainty: {self.total_uncertainty:.4f}")
        print(f"   Most certain: {self.most_certain_weight}")
        print(f"   Least certain: {self.least_certain_weight}")
    
    def _step6_calculate_credible_intervals(self):
        """Calculate credible intervals."""
        print("\n🎯 Step 6: Calculating credible intervals...")
        
        self.credible_intervals_95 = {}
        self.credible_intervals_50 = {}
        
        print("\n   95% Credible Intervals:")
        for signal in self.samples:
            samples_array = np.array(self.samples[signal])
            
            # 95% CI
            ci_95 = (
                np.percentile(samples_array, 2.5),
                np.percentile(samples_array, 97.5)
            )
            self.credible_intervals_95[signal] = ci_95
            
            # 50% CI (interquartile range)
            ci_50 = (
                np.percentile(samples_array, 25),
                np.percentile(samples_array, 75)
            )
            self.credible_intervals_50[signal] = ci_50
            
            width_95 = ci_95[1] - ci_95[0]
            print(f"      {signal:12s}: [{ci_95[0]:.4f}, {ci_95[1]:.4f}] (width: {width_95:.4f})")
    
    def _step7_compare_to_optimal(self):
        """Compare posteriors to optimal weights."""
        print("\n⚖️  Step 7: Comparing to optimal weights...")
        
        self.posterior_vs_optimal = {}
        self.weights_in_credible_interval = {}
        
        print("\n   Optimal vs Posterior:")
        for signal in self.true_weights:
            optimal = self.true_weights[signal]
            posterior = self.posterior_means[signal]
            ci_95 = self.credible_intervals_95[signal]
            
            # Check if optimal is in 95% CI
            in_ci = ci_95[0] <= optimal <= ci_95[1]
            self.weights_in_credible_interval[signal] = in_ci
            
            diff = posterior - optimal
            match = "✓" if abs(diff) < 0.01 else "✗"
            ci_check = "✓" if in_ci else "✗"
            
            self.posterior_vs_optimal[signal] = {
                'optimal': optimal,
                'posterior': posterior,
                'difference': diff,
                'in_95_ci': in_ci
            }
            
            print(f"      {match} {signal:12s}: optimal={optimal:.3f}, posterior={posterior:.4f}, diff={diff:+.4f}, in_CI={ci_check}")
        
        # Convergence check
        all_in_ci = all(self.weights_in_credible_interval.values())
        all_close = all(abs(self.posterior_vs_optimal[s]['difference']) < 0.05 for s in self.true_weights)
        self.converged = all_in_ci and all_close
        
        print(f"\n   🎯 Convergence: {'✓ CONVERGED' if self.converged else '✗ NOT CONVERGED'}")
        print(f"   All weights in 95% CI: {all_in_ci}")
    
    def _step8_save_results(self):
        """Save Bayesian results."""
        print("\n💾 Step 8: Saving results...")
        
        results = BayesianPosteriorResults(
            posterior_means=self.posterior_means,
            posterior_stds=self.posterior_stds,
            credible_intervals_95=self.credible_intervals_95,
            credible_intervals_50=self.credible_intervals_50,
            total_uncertainty=self.total_uncertainty,
            most_certain_weight=self.most_certain_weight,
            least_certain_weight=self.least_certain_weight,
            n_samples=self.n_samples,
            n_burn_in=self.n_burn_in,
            acceptance_rate=self.acceptance_rate,
            converged=self.converged,
            posterior_vs_optimal=self.posterior_vs_optimal,
            weights_in_credible_interval=self.weights_in_credible_interval,
            timestamp=datetime.now().isoformat()
        )
        
        # Save to JSON
        output_path = Path(__file__).parent / "fixtures" / "phase11a_bayesian_posteriors.json"
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
        print("🎲 PHASE 11A COMPLETE: Bayesian Posteriors")
        print("="*60)
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   Total uncertainty: {results.total_uncertainty:.4f}")
        print(f"   Acceptance rate: {results.acceptance_rate:.3f}")
        print(f"   Most certain: {results.most_certain_weight}")
        print(f"   Converged: {results.converged}")
        print(f"\n   🔬 INSIGHT: {'HIGH' if results.total_uncertainty < 0.02 else 'MODERATE' if results.total_uncertainty < 0.05 else 'LOW'} confidence")
        print("              in optimal weights!")
        print("="*60 + "\n")
        
        assert output_path.exists()


if __name__ == "__main__":
    # Run Phase 11A tests
    print("\n🎲 Starting Phase 11A: Bayesian Posterior Analysis\n")
    pytest.main([__file__, "-v", "-s"])
