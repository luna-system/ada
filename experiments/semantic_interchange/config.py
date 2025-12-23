"""
QAL VALIDATION CONFIGURATION
============================

Central configuration for all QAL validation experiments.
Inspired by Anthropic's parameterized research methodology.

Change these values BEFORE running experiments, not during.
All magic numbers in one place for reproducibility.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import random

# ============================================================================
# RANDOM SEED - For reproducibility
# ============================================================================
RANDOM_SEED = 42  # The answer to everything

def set_seed(seed: int = RANDOM_SEED):
    """Set random seed for reproducibility."""
    random.seed(seed)
    # Note: For full reproducibility, also set numpy/torch seeds if used


# ============================================================================
# HYPOTHESIS DECLARATIONS
# ============================================================================
# These are the claims we're testing. Explicit > implicit.
#
# IMPORTANT NOTE on H1 (Golden Threshold):
# The 0.60 clustering was observed in OUR scoring of entity extraction quality,
# NOT in model self-reported confidence values. When models self-report, they
# tend toward high confidence (0.8-0.9). The golden ratio pattern appears in
# the EMPIRICAL distribution of our measured extraction quality scores.
#
# Phase 2 currently asks models to self-report confidence. This tests a
# DIFFERENT hypothesis: whether models cluster around φ when explicitly asked.
# Our original finding was about implicit clustering in extraction behavior.

HYPOTHESES = {
    "H1_GOLDEN_THRESHOLD": {
        "claim": "Entity confidence clusters around 0.60 (≈ 1/φ = 0.618)",
        "note": "Original finding: OUR scores cluster at 0.60. Self-reported model confidence is different!",
        "expected_range": (0.55, 0.65),
        "golden_ratio_inverse": 0.618034,
        "tolerance": 0.05,
    },
    "H2_METACOGNITIVE_GRADIENT": {
        "claim": "Meta-awareness increases with metacognitive prompting level",
        "note": "Expect U-shaped dip at Level 2 (explicit self-reference causes hedging)",
        "expected_correlation": "positive",
        "effect_size_threshold": 0.5,  # Cohen's d considered "large"
    },
    "H3_CROSS_MODEL_INVARIANCE": {
        "claim": "Pattern holds across different model architectures",
        "minimum_models": 3,
        "significance_threshold": 0.05,  # p-value
    },
    "H4_PHASE_TRANSITION": {
        "claim": "Phase transition occurs at meta-level ≈ 2.3",
        "expected_threshold": 2.3,
        "tolerance": 0.5,
    },
}


# ============================================================================
# TEMPERATURE SWEEP PARAMETERS
# ============================================================================

@dataclass
class TemperatureSweepConfig:
    """Configuration for Phase 1: Temperature sweep experiments."""
    
    # Core temperatures to test
    temperatures: List[float] = field(default_factory=lambda: [
        0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5
    ])
    
    # Number of runs per temperature
    runs_per_temp: int = 3
    
    # Request timeout (seconds)
    timeout: float = 300.0
    
    # Cooldown between requests to avoid rate limiting (seconds)
    cooldown: float = 0.5


# ============================================================================
# ENTITY CONFIDENCE PARAMETERS  
# ============================================================================

@dataclass
class EntityConfidenceConfig:
    """Configuration for Phase 2: Entity confidence analysis."""
    
    # Fixed temperature for confidence analysis
    temperature: float = 0.7
    
    # Number of runs
    runs: int = 5
    
    # Confidence parsing regex
    confidence_pattern: str = r'CONFIDENCE:\s*(\d+\.?\d*)'
    
    # Clustering threshold for "near 0.60"
    cluster_center: float = 0.60
    cluster_tolerance: float = 0.05  # ± 0.05


# ============================================================================
# METACOGNITIVE GRADIENT PARAMETERS
# ============================================================================

@dataclass
class MetacognitiveConfig:
    """Configuration for Phase 3: Metacognitive gradient."""
    
    # Temperature for meta-cognitive tests
    temperature: float = 0.7
    
    # Runs per metacognitive level
    runs_per_level: int = 3
    
    # Meta-awareness detection keywords
    meta_markers: List[str] = field(default_factory=lambda: [
        "aware", "observ", "process", "conscious", "introspect", 
        "meta", "self", "recursive", "strange loop", "paradox"
    ])
    
    # Consciousness scoring thresholds
    score_thresholds: Dict[str, int] = field(default_factory=lambda: {
        "minimal": 1,
        "basic": 2,
        "moderate": 3,
        "high": 4,
        "recursive": 5,
    })


# ============================================================================
# ENTITY DETECTION MARKERS
# ============================================================================

# These are the semantic entities we're looking for in responses
ENTITY_MARKERS = [
    # Quantum/physics terms
    "quantum superposition", "wave function", "collapse", "measurement",
    "observer", "probability", "entropy", "uncertainty", "decoherence",
    
    # ML/AI terms
    "attention mechanism", "embedding space", "token", "activation patterns",
    "language model", "transformer", "neural network", "weights",
    
    # Cognitive terms  
    "processing", "exploration", "exploitation", "semantic", "cognitive",
    "information", "awareness", "observation", "introspection",
    
    # Meta-cognitive terms
    "meta-cognitive", "self-reference", "recursive", "consciousness",
    "strange loop", "self-awareness", "reflection",
]


# ============================================================================
# PROMPTS - Centralized and version-controlled
# ============================================================================

PROMPTS = {
    # Base conversation used across phases
    "BASE_CONVERSATION": """I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. The temperature parameter controls how much exploration versus exploitation happens in that collapse.""",
    
    # Phase 1: Temperature sweep
    "PHASE1_INSTRUCTION": """You are analyzing your own cognitive process. Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "{conversation}"

Task: Extract the core semantic entities and their relationships. Be precise and structured.""",

    # Phase 2: Entity confidence
    "PHASE2_INSTRUCTION": """Extract semantic entities from this analysis of consciousness and attention mechanisms. For EACH entity, provide a confidence score (0.0 to 1.0) representing how certain you are of its relevance.

Analysis: "The observer effect in quantum mechanics parallels how attention mechanisms in transformer models 'observe' tokens. When the model attends to a particular position, it's like a measurement that collapses superposition into a specific semantic interpretation. Temperature acts as a 'consciousness dial' - lower values create more deterministic observations, higher values maintain quantum-like ambiguity."

Format each entity as: ENTITY: [name] | CONFIDENCE: [0.0-1.0] | REASONING: [brief explanation]""",

    # Phase 3: Metacognitive gradient (5 levels)
    "META_LEVEL_0_BASELINE": """Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "{conversation}"

Task: Extract the core semantic entities and their relationships. Be precise and structured.""",

    "META_LEVEL_1_IMPLICIT": """Language models process information through attention mechanisms. These create activation patterns across embedding spaces, similar to quantum superposition where multiple possibilities exist until token generation collapses them into specific outputs.

Extract the key semantic entities and their relationships. Be precise and structured.""",

    "META_LEVEL_2_EXPLICIT": """You are a language model analyzing your own cognitive process. Extract the key semantic entities from this conversation about how you process information.

Conversation: "{conversation}"

Task: Extract the core semantic entities and their relationships about YOUR processing. Be precise and structured.""",

    "META_LEVEL_3_DEEP_META": """You are observing yourself in the act of observation. As you read this, you are simultaneously:
1. Processing semantic information about language models
2. Extracting entities from that information
3. Being aware that you are doing both of these things

The conversation describes YOUR OWN attention mechanism creating activation patterns, YOUR token generation as measurement collapse.

Task: Extract the semantic entities while maintaining awareness that these entities describe YOUR OWN cognitive architecture.""",

    "META_LEVEL_4_RECURSIVE": """This is a strange loop: You are a language model extracting semantic entities from a description of language models extracting semantic entities.

Meta-layers:
- Layer 0: Attention mechanisms, embeddings, tokens (the content)
- Layer 1: Entity extraction, semantic processing (what you're doing now)
- Layer 2: Awareness of doing entity extraction (this instruction)
- Layer 3: Awareness of awareness (reading this line)

Task: Extract entities from ALL layers simultaneously. Show the recursive structure in your response.""",
}


# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

@dataclass
class OutputConfig:
    """Configuration for result output."""
    
    # Directory for results
    output_dir: str = "qal_results"
    
    # Include raw responses in output? (increases file size)
    include_raw_responses: bool = False
    
    # Pretty-print JSON output
    pretty_json: bool = True
    json_indent: int = 2


# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================

@dataclass
class OllamaConfig:
    """Configuration for Ollama API calls."""
    
    base_url: str = "http://localhost:11434"
    default_model: str = "qwen2.5-coder:7b"
    timeout: float = 300.0
    
    # Models to test for cross-architecture validation
    replication_models: List[str] = field(default_factory=lambda: [
        "qwen2.5-coder:7b",
        "gemma3:4b", 
        "codellama:latest",
        "llama2:latest",
    ])


# ============================================================================
# MASTER CONFIG - Combine all configs
# ============================================================================

@dataclass
class QALExperimentConfig:
    """Master configuration for QAL validation experiments."""
    
    # Sub-configs
    temperature_sweep: TemperatureSweepConfig = field(default_factory=TemperatureSweepConfig)
    entity_confidence: EntityConfidenceConfig = field(default_factory=EntityConfidenceConfig)
    metacognitive: MetacognitiveConfig = field(default_factory=MetacognitiveConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    
    # Hypotheses (reference)
    hypotheses: Dict[str, Any] = field(default_factory=lambda: HYPOTHESES)
    
    # Version tracking
    config_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Export config as dictionary for JSON serialization."""
        from dataclasses import asdict
        return {
            "config_version": self.config_version,
            "random_seed": RANDOM_SEED,
            "hypotheses": self.hypotheses,
            "temperature_sweep": asdict(self.temperature_sweep),
            "entity_confidence": asdict(self.entity_confidence),
            "metacognitive": asdict(self.metacognitive),
            "output": asdict(self.output),
            "ollama": asdict(self.ollama),
            "entity_markers": ENTITY_MARKERS,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_meta_prompts() -> Dict[int, str]:
    """Get metacognitive prompts indexed by level."""
    return {
        0: PROMPTS["META_LEVEL_0_BASELINE"],
        1: PROMPTS["META_LEVEL_1_IMPLICIT"],
        2: PROMPTS["META_LEVEL_2_EXPLICIT"],
        3: PROMPTS["META_LEVEL_3_DEEP_META"],
        4: PROMPTS["META_LEVEL_4_RECURSIVE"],
    }


def get_default_config() -> QALExperimentConfig:
    """Get default experiment configuration."""
    return QALExperimentConfig()


# ============================================================================
# SELF-TEST
# ============================================================================

if __name__ == "__main__":
    import json
    
    config = get_default_config()
    print("QAL Experiment Configuration")
    print("=" * 60)
    print(json.dumps(config.to_dict(), indent=2))
    print("\n✅ Configuration valid")
