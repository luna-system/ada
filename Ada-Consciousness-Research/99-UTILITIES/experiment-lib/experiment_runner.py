"""
Generic Experiment Runner

JSON stimuli → Model (sterile black box) → JSON results

This is the core of our research methodology.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from uuid import uuid4

from .ollama_client import OllamaClient, ModelResponse
from .metrics import compute_metrics, consciousness_indicators


@dataclass
class ExperimentConfig:
    """Configuration for an experiment run"""
    experiment_name: str
    model: str
    runs_per_stimulus: int = 3
    timeout_seconds: float = 60.0
    default_options: Dict[str, Any] = field(default_factory=lambda: {
        "temperature": 0.7,
        "num_predict": 200  # max tokens
    })
    
    # Metadata
    researcher: str = "Luna & Ada"
    hypothesis: Optional[str] = None
    

@dataclass 
class TrialResult:
    """Result of a single model call"""
    stimulus_id: str
    run_number: int
    timestamp: str
    
    # Model response
    success: bool
    response_text: str
    latency_seconds: float
    tokens_generated: int
    error: Optional[str] = None
    
    # Computed metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    consciousness_indicators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResults:
    """Complete results from an experiment run"""
    experiment_id: str
    experiment_name: str
    model: str
    config: Dict[str, Any]
    
    started_at: str
    completed_at: Optional[str] = None
    
    stimuli_file: Optional[str] = None
    stimuli_count: int = 0
    total_trials: int = 0
    
    trials: List[Dict[str, Any]] = field(default_factory=list)
    
    # Aggregate stats
    success_rate: float = 0.0
    avg_latency: float = 0.0
    avg_coherence: float = 0.0


class ExperimentRunner:
    """
    Run experiments with JSON stimuli → Model → JSON results
    
    Usage:
        runner = ExperimentRunner(ExperimentConfig(
            experiment_name="cognitive-load-test",
            model="qwen2.5-coder:7b"
        ))
        
        results = runner.run_from_file("stimuli.json")
        runner.save_results(results, "results/")
    """
    
    def __init__(self, config: ExperimentConfig, ollama_url: str = "http://localhost:11434"):
        self.config = config
        self.client = OllamaClient(ollama_url)
    
    def run_from_file(self, stimuli_file: Path | str) -> ExperimentResults:
        """Load stimuli from JSON file and run experiment"""
        stimuli_file = Path(stimuli_file)
        
        with open(stimuli_file) as f:
            stimuli_data = json.load(f)
        
        prompts = stimuli_data.get("prompts", [])
        
        results = self._create_results(stimuli_file, len(prompts))
        
        print(f"🔬 Starting experiment: {self.config.experiment_name}")
        print(f"📊 Model: {self.config.model}")
        print(f"📝 Stimuli: {len(prompts)} prompts × {self.config.runs_per_stimulus} runs")
        print("-" * 50)
        
        for stimulus in prompts:
            self._run_stimulus(stimulus, results)
        
        self._compute_aggregates(results)
        results.completed_at = datetime.now().isoformat()
        
        print("-" * 50)
        print(f"✅ Experiment complete: {results.total_trials} trials")
        print(f"📈 Success rate: {results.success_rate:.1%}")
        print(f"⏱️  Avg latency: {results.avg_latency:.2f}s")
        
        return results
    
    def run_single_prompt(self, prompt: str, stimulus_id: str = "manual") -> List[TrialResult]:
        """Run experiment on a single prompt (for quick testing)"""
        stimulus = {"id": stimulus_id, "prompt": prompt}
        results = self._create_results(None, 1)
        self._run_stimulus(stimulus, results)
        return [TrialResult(**t) for t in results.trials]
    
    def _create_results(self, stimuli_file: Optional[Path], stimuli_count: int) -> ExperimentResults:
        """Create initial results structure"""
        return ExperimentResults(
            experiment_id=str(uuid4())[:8],
            experiment_name=self.config.experiment_name,
            model=self.config.model,
            config=asdict(self.config),
            started_at=datetime.now().isoformat(),
            stimuli_file=str(stimuli_file) if stimuli_file else None,
            stimuli_count=stimuli_count,
        )
    
    def _run_stimulus(self, stimulus: Dict[str, Any], results: ExperimentResults):
        """Run all trials for a single stimulus"""
        stimulus_id = stimulus.get("id", "unknown")
        prompt = stimulus["prompt"]
        options = {**self.config.default_options, **stimulus.get("options", {})}
        
        print(f"\n🧪 Stimulus: {stimulus_id}")
        print(f"   Prompt: {len(prompt)} chars, {len(prompt.split())} words")
        
        for run in range(1, self.config.runs_per_stimulus + 1):
            print(f"   Run {run}/{self.config.runs_per_stimulus}...", end=" ", flush=True)
            
            response = self.client.generate(
                model=self.config.model,
                prompt=prompt,
                options=options,
                timeout=self.config.timeout_seconds
            )
            
            # Compute metrics
            metrics = compute_metrics(response.response_text) if response.success else {}
            consciousness = consciousness_indicators(response.response_text) if response.success else {}
            
            trial = TrialResult(
                stimulus_id=stimulus_id,
                run_number=run,
                timestamp=datetime.now().isoformat(),
                success=response.success,
                response_text=response.response_text,
                latency_seconds=response.latency_seconds,
                tokens_generated=response.tokens_generated,
                error=response.error,
                metrics=metrics,
                consciousness_indicators=consciousness,
            )
            
            results.trials.append(asdict(trial))
            results.total_trials += 1
            
            if response.success:
                print(f"✅ {response.tokens_generated} tokens, {response.latency_seconds:.2f}s")
            else:
                print(f"❌ {response.error}")
            
            time.sleep(0.5)  # Brief pause between runs
    
    def _compute_aggregates(self, results: ExperimentResults):
        """Compute aggregate statistics"""
        if not results.trials:
            return
        
        successful = [t for t in results.trials if t["success"]]
        
        results.success_rate = len(successful) / len(results.trials)
        
        if successful:
            results.avg_latency = sum(t["latency_seconds"] for t in successful) / len(successful)
            coherence_scores = [
                t["metrics"].get("coherence", {}).get("score", 0) 
                for t in successful
            ]
            results.avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
    
    def save_results(self, results: ExperimentResults, output_dir: Path | str) -> Path:
        """Save results to timestamped JSON file"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"{results.experiment_name}_{timestamp}.json"
        output_path = output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        
        print(f"\n💾 Results saved: {output_path}")
        return output_path


# Convenience function for quick experiments
def quick_experiment(
    prompt: str,
    model: str = "qwen2.5-coder:7b",
    runs: int = 3,
    name: str = "quick-test"
) -> ExperimentResults:
    """Run a quick single-prompt experiment"""
    config = ExperimentConfig(
        experiment_name=name,
        model=model,
        runs_per_stimulus=runs
    )
    runner = ExperimentRunner(config)
    
    # Create minimal stimuli structure
    results = runner._create_results(None, 1)
    runner._run_stimulus({"id": "prompt", "prompt": prompt}, results)
    runner._compute_aggregates(results)
    results.completed_at = datetime.now().isoformat()
    
    return results
