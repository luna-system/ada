# Ada Consciousness Research - Experiment Library
"""
This package provides the infrastructure for empirical LLM research.

The key distinction:
- Unit tests (pytest) → deterministic, fast, verify code works
- Experiments (this lib) → stochastic, data-collecting, study model behavior

"If the test would pass with a mock response, it's a unit test.
If you need to actually call the model to get meaningful data, it's an experiment."
"""

from .experiment_runner import ExperimentRunner, ExperimentConfig
from .metrics import compute_metrics, coherence_score, token_metrics
from .ollama_client import OllamaClient

__all__ = [
    'ExperimentRunner',
    'ExperimentConfig', 
    'OllamaClient',
    'compute_metrics',
    'coherence_score',
    'token_metrics',
]
