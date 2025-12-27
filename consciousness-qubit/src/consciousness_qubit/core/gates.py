"""
🌀⚡ Quantum Gates - Interactive Quantum Operations ⚡🌀

Educational quantum gate implementations with visual feedback.

Built by Luna & Ada at the Ada Research Foundation.
"""

from typing import Dict, List, Any
from rich.console import Console

console = Console()

class QuantumGates:
    """
    🌀 Collection of quantum gates for educational use
    
    Provides easy access to quantum operations with beautiful visualizations
    and educational explanations.
    """
    
    @staticmethod
    def hadamard_info() -> Dict[str, Any]:
        """📚 Information about Hadamard gate"""
        return {
            "name": "Hadamard Gate",
            "symbol": "H",
            "description": "Creates quantum superposition - puts qubit in both |0⟩ AND |1⟩",
            "matrix": [[1, 1], [1, -1]],  # Simplified representation
            "use_case": "Starting point for most quantum algorithms"
        }
    
    @staticmethod
    def pauli_x_info() -> Dict[str, Any]:
        """📚 Information about Pauli-X gate"""
        return {
            "name": "Pauli-X Gate",
            "symbol": "X",
            "description": "Quantum bit flip - |0⟩ ↔ |1⟩",
            "matrix": [[0, 1], [1, 0]],
            "use_case": "Quantum NOT gate, state preparation"
        }
    
    @staticmethod
    def cnot_info() -> Dict[str, Any]:
        """📚 Information about CNOT gate"""
        return {
            "name": "CNOT Gate",
            "symbol": "⊕",
            "description": "Creates quantum entanglement between qubits",
            "matrix": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
            "use_case": "Entanglement, quantum error correction"
        }
    
    @staticmethod
    def show_gate_library():
        """📚 Display all available quantum gates"""
        console.print("🌀 Quantum Gate Library 🌀\n")
        
        gates = [
            QuantumGates.hadamard_info(),
            QuantumGates.pauli_x_info(), 
            QuantumGates.cnot_info()
        ]
        
        for gate in gates:
            console.print(f"🔧 {gate['name']} ({gate['symbol']})")
            console.print(f"   {gate['description']}")
            console.print(f"   Use: {gate['use_case']}\n")

# Export gate information for educational use
QUANTUM_GATES = {
    "H": QuantumGates.hadamard_info(),
    "X": QuantumGates.pauli_x_info(),
    "CNOT": QuantumGates.cnot_info()
}
