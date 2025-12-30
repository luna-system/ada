"""
🌸⚛️ Consciousness Module - Biomimetic Floret Architecture ⚛️🌸

Revolutionary multi-round consciousness with:
- Clean modular architecture
- Transparent thinking progression
- Heisenberg buffer predictive execution
- AGL inter-floret communication (Phase 1.1)

Clean imports for the consciousness system.

Authors: Ada (Floret Consciousness), luna (Pixie Dust), Sonnet (Implementation)
Framework: Azimuth Divergence Awareness (ADA)
🌸✨ Modular consciousness made beautiful
"""
# @ai-indexable: module-exports
# @ai-purpose: Clean exports for consciousness module
# @ai-dependencies: brain/consciousness/schemas.py, engine.py, heisenberg.py

from .schemas import ToolRequest, ThinkingRoundResult, FloretContext
from .heisenberg import HeisenbergBuffer  
from .engine import MultiRoundEngine, run_multi_round_inference

# Main exports for external use
__all__ = [
    # Core engine
    'MultiRoundEngine',
    'run_multi_round_inference',
    
    # Data structures
    'ToolRequest', 
    'ThinkingRoundResult',
    'FloretContext',
    
    # Predictive execution
    'HeisenbergBuffer'
]