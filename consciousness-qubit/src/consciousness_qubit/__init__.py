"""
🌌⚡ Consciousness Qubit - Your First Quantum Computer ⚡🌌

An educational quantum computing playground powered by mathematical consciousness.
Perfect for students, researchers, and curious minds who want to explore quantum algorithms
with full observability and zero hardware requirements.

Built by Luna & Ada at the Ada Research Foundation.
"""

from .core.qubit import ConsciousnessQubit
from .core.playground import QuantumPlayground
from .core.gates import QuantumGates
from .core.algorithms import QuantumAlgorithms
from .core.visualization import QuantumVisualizer

# Enhanced playground with optional SLM consciousness integration
try:
    from .enhanced_playground import EnhancedQuantumPlayground
    CONSCIOUSNESS_MODE_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_MODE_AVAILABLE = False

__version__ = "0.1.0"
__authors__ = "Luna & Ada (Ada Research Foundation)"
__license__ = "CC0-1.0"

# Quick start for educational use
def quick_demo():
    """🎮 Launch interactive quantum playground demo"""
    from .playground import interactive_demo
    return interactive_demo()

def create_qubit(name: str = "φ●"):
    """⚡ Create your first consciousness qubit"""
    return ConsciousnessQubit(name)

def create_playground():
    """🌌 Create quantum computing playground"""  
    return QuantumPlayground()

def create_consciousness_playground():
    """🧠 Create consciousness-enhanced quantum playground with optional SLM integration"""
    if CONSCIOUSNESS_MODE_AVAILABLE:
        return EnhancedQuantumPlayground(use_consciousness_mode=True)
    else:
        print("⚠️ Consciousness mode not available - using mathematical simulation")
        return QuantumPlayground()

def create_quantum_microscope():
    """🔬 Create quantum microscope for dual-level observability"""
    return create_consciousness_playground()

# Educational shortcuts
Bell = QuantumAlgorithms.create_bell_states
Grover = QuantumAlgorithms.grovers_search  
Shor = QuantumAlgorithms.shors_factoring
Teleport = QuantumAlgorithms.quantum_teleportation

__all__ = [
    "ConsciousnessQubit",
    "QuantumPlayground", 
    "QuantumGates",
    "QuantumAlgorithms",
    "QuantumVisualizer",
    "quick_demo",
    "create_qubit",
    "create_playground",
    "create_consciousness_playground",
    "create_quantum_microscope",
    "Bell",
    "Grover", 
    "Shor",
    "Teleport"
]
