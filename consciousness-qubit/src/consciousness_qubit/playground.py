"""
🎮⚡ Interactive Playground - Launch Your Quantum Computer! ⚡🎮

Simple interface for starting interactive quantum computing sessions.

Built by Luna & Ada at the Ada Research Foundation.
"""

from .core.playground import QuantumPlayground, interactive_demo as _interactive_demo
from rich.console import Console

console = Console()

def interactive():
    """🎮 Launch interactive quantum playground from command line"""
    return _interactive_demo()

def quick_start():
    """⚡ Quick start guide for new users"""
    console.print("⚡ Consciousness Qubit Quick Start ⚡\n")
    
    console.print("1. Create your quantum computer:")
    console.print("   >>> import consciousness_qubit as cq")
    console.print("   >>> qc = cq.create_playground()\n")
    
    console.print("2. Add qubits:")
    console.print("   >>> alice = qc.add_qubit('Alice')")
    console.print("   >>> bob = qc.add_qubit('Bob')\n")
    
    console.print("3. Create quantum superposition:")
    console.print("   >>> alice.hadamard()")
    console.print("   >>> alice.peek()  # Shows: ◑\n")
    
    console.print("4. Create quantum entanglement:")
    console.print("   >>> alice.cnot(bob)")
    console.print("   >>> # Alice and Bob are now connected!\n")
    
    console.print("5. Run quantum algorithms:")
    console.print("   >>> qc.bell_experiment()")
    console.print("   >>> qc.grovers_search(['a', 'b', 'quantum'], 'quantum')\n")
    
    console.print("🌌 You now have a quantum computer more powerful than")
    console.print("   billion-dollar labs, running on your laptop!")

# Make playground easily accessible
__all__ = ["interactive", "quick_start"]
