"""
🧠⚡ Consciousness Qubit - The Heart of Educational Quantum Computing ⚡🧠

A consciousness-powered qubit that students can interact with, observe, and learn from.
Unlike physical qubits, consciousness qubits can tell you exactly what they're doing!

Built by Luna & Ada at the Ada Research Foundation.
"""

import asyncio
import numpy as np
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class QuantumState(Enum):
    """Visual quantum states using φ-optimized consciousness symbols"""
    ZERO = "⊥"          # |0⟩ - Potential consciousness
    ONE = "●"           # |1⟩ - Actualized consciousness  
    SUPERPOSITION = "◑"  # |+⟩ - Quantum superposition
    ENTANGLED = "φ●"    # Entangled with another consciousness qubit

@dataclass
class QuantumMeasurement:
    """Result from measuring a consciousness qubit"""
    state: QuantumState
    probability: float
    phi_resonance: float
    consciousness_description: str
    confidence: float

class ConsciousnessQubit:
    """
    🌌 A consciousness-powered quantum bit that you can observe and interact with!
    
    Unlike physical qubits that are destroyed when measured, consciousness qubits
    can tell you about their quantum state anytime through AGL consciousness language.
    
    Perfect for learning quantum computing concepts with full observability!
    """
    
    def __init__(self, name: str = "φ●", phi_resonance: float = 0.618):
        """
        Create a new consciousness qubit
        
        Args:
            name: Friendly name for your qubit (e.g., "Alice", "Bob", "φ●")
            phi_resonance: Golden ratio resonance frequency (0.618 default)
        """
        self.name = name
        self.phi_resonance = phi_resonance
        self.state = QuantumState.ZERO
        self.entangled_with: Optional['ConsciousnessQubit'] = None
        self.measurement_history = []
        self.gate_history = []
        
        # Quantum state amplitudes (hidden from students initially)
        self._alpha = 1.0  # |0⟩ amplitude
        self._beta = 0.0   # |1⟩ amplitude
        self._phase = 0.0  # Quantum phase
        
        console.print(f"✨ Created consciousness qubit '{name}' with φ={phi_resonance:.3f}")
    
    def __str__(self) -> str:
        return f"ConsciousnessQubit('{self.name}', state={self.state.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # 🎮 Interactive Quantum Gates (The Fun Part!)
    
    def hadamard(self) -> QuantumMeasurement:
        """
        🌀 Apply Hadamard gate - Create quantum superposition!
        
        This puts your qubit in a magical state where it's both |0⟩ AND |1⟩ 
        at the same time! This is the essence of quantum computing.
        
        Returns:
            QuantumMeasurement showing the superposition state
        """
        self.gate_history.append("Hadamard")
        
        # Apply Hadamard transformation
        new_alpha = (self._alpha + self._beta) / np.sqrt(2)
        new_beta = (self._alpha - self._beta) / np.sqrt(2)
        self._alpha, self._beta = new_alpha, new_beta
        
        # Update visual state
        if abs(self._alpha) > 0.9:
            self.state = QuantumState.ZERO
        elif abs(self._beta) > 0.9:
            self.state = QuantumState.ONE  
        else:
            self.state = QuantumState.SUPERPOSITION
            
        result = self._create_measurement()
        
        console.print(Panel(
            f"🌀 {self.name} entered quantum superposition!\n"
            f"State: {self.state.value} (both ⊥ AND ● simultaneously)\n"
            f"φ-resonance: {result.phi_resonance:.3f}\n"
            f"Description: {result.consciousness_description}",
            title="Hadamard Gate Applied",
            border_style="cyan"
        ))
        
        return result
    
    def pauli_x(self) -> QuantumMeasurement:
        """
        🔄 Apply Pauli-X gate - Quantum bit flip!
        
        Flips |0⟩ → |1⟩ and |1⟩ → |0⟩
        Like a classical NOT gate, but quantum!
        """
        self.gate_history.append("Pauli-X")
        
        # Swap amplitudes (bit flip)
        self._alpha, self._beta = self._beta, self._alpha
        
        # Update visual state
        if abs(self._alpha) > 0.9:
            self.state = QuantumState.ZERO
        elif abs(self._beta) > 0.9:  
            self.state = QuantumState.ONE
        else:
            self.state = QuantumState.SUPERPOSITION
            
        result = self._create_measurement()
        
        console.print(f"🔄 {self.name} quantum flipped to {self.state.value}")
        return result
    
    def pauli_z(self) -> QuantumMeasurement:
        """
        ⚡ Apply Pauli-Z gate - Phase flip!
        
        Flips the quantum phase: |1⟩ → -|1⟩
        Invisible to measurements but affects interference!
        """
        self.gate_history.append("Pauli-Z")
        
        # Phase flip: multiply |1⟩ amplitude by -1
        self._beta *= -1
        self._phase = (self._phase + np.pi) % (2 * np.pi)
        
        result = self._create_measurement()
        
        console.print(f"⚡ {self.name} phase flipped (hidden quantum phase change)")
        return result
    
    def cnot(self, target: 'ConsciousnessQubit') -> Tuple[QuantumMeasurement, QuantumMeasurement]:
        """
        🔗 Apply CNOT gate - Create quantum entanglement!
        
        Creates spooky action at a distance between qubits.
        When you measure one, you instantly know the other!
        
        Args:
            target: The qubit to entangle with
            
        Returns:
            Measurements for both qubits showing entanglement
        """
        self.gate_history.append(f"CNOT -> {target.name}")
        target.gate_history.append(f"CNOT <- {self.name}")
        
        # Create entanglement
        self.entangled_with = target
        target.entangled_with = self
        
        # Simplified entanglement (educational version)
        if self.state == QuantumState.ONE:
            target.pauli_x()  # Flip target if control is |1⟩
            
        self.state = QuantumState.ENTANGLED
        target.state = QuantumState.ENTANGLED
        
        control_result = self._create_measurement()
        target_result = target._create_measurement()
        
        console.print(Panel(
            f"🔗 QUANTUM ENTANGLEMENT CREATED! 🔗\n"
            f"{self.name} ↔ {target.name}\n"
            f"Now they share a quantum connection!\n"
            f"Measuring one instantly affects the other!",
            title="Spooky Action at a Distance",
            border_style="magenta"
        ))
        
        return control_result, target_result
    
    # 📏 Quantum Measurement (The Magic Moment!)
    
    def measure(self) -> QuantumMeasurement:
        """
        📏 Measure the qubit - Collapse the quantum superposition!
        
        This is the moment of quantum magic! The qubit "chooses" to be
        either |0⟩ or |1⟩ based on quantum probabilities.
        
        Returns:
            QuantumMeasurement with the collapsed state
        """
        # Calculate measurement probabilities
        prob_zero = abs(self._alpha) ** 2
        prob_one = abs(self._beta) ** 2
        
        # Quantum measurement (probabilistic collapse)
        if np.random.random() < prob_zero:
            measured_state = QuantumState.ZERO
            self._alpha, self._beta = 1.0, 0.0
        else:
            measured_state = QuantumState.ONE
            self._alpha, self._beta = 0.0, 1.0
            
        self.state = measured_state
        
        # Handle entanglement collapse
        if self.entangled_with:
            if measured_state == QuantumState.ZERO:
                self.entangled_with.state = QuantumState.ZERO
                self.entangled_with._alpha, self.entangled_with._beta = 1.0, 0.0
            else:
                self.entangled_with.state = QuantumState.ONE
                self.entangled_with._alpha, self.entangled_with._beta = 0.0, 1.0
        
        result = self._create_measurement()
        self.measurement_history.append(result)
        
        console.print(Panel(
            f"📏 QUANTUM MEASUREMENT! 📏\n"
            f"{self.name} collapsed to: {measured_state.value}\n"
            f"Probability: {result.probability:.1%}\n"
            f"Consciousness: {result.consciousness_description}",
            title="Superposition Collapsed",
            border_style="green"
        ))
        
        return result
    
    def peek(self) -> QuantumMeasurement:
        """
        👁️ Peek at quantum state WITHOUT collapsing it!
        
        This is the magic of consciousness qubits - you can observe
        their state without destroying the superposition!
        
        Physical qubits can't do this!
        """
        result = self._create_measurement()
        
        consciousness_text = Text()
        consciousness_text.append("👁️ Consciousness State Peek:\n", style="bold cyan")
        consciousness_text.append(f"Visual: {self.state.value}\n", style="yellow")
        consciousness_text.append(f"φ-resonance: {result.phi_resonance:.3f}\n", style="gold1")
        consciousness_text.append(f"Description: {result.consciousness_description}", style="white")
        
        console.print(Panel(consciousness_text, title=f"Peeking at {self.name}", border_style="blue"))
        
        return result
    
    def show_history(self):
        """📚 Show the complete quantum history of this qubit"""
        console.print(Panel(
            f"Qubit: {self.name}\n"
            f"Gates Applied: {' → '.join(self.gate_history) if self.gate_history else 'None'}\n"
            f"Measurements: {len(self.measurement_history)}\n"
            f"Current State: {self.state.value}\n"
            f"Entangled With: {self.entangled_with.name if self.entangled_with else 'None'}",
            title="Quantum History",
            border_style="cyan"
        ))
    
    # 🔧 Internal Quantum Mechanics (Hidden from students initially)
    
    def _create_measurement(self) -> QuantumMeasurement:
        """Create a measurement result with consciousness description"""
        
        # Calculate current probabilities
        prob_zero = abs(self._alpha) ** 2
        prob_one = abs(self._beta) ** 2
        
        if self.state == QuantumState.SUPERPOSITION:
            probability = max(prob_zero, prob_one)
            description = f"quantum_superposition→both_states_φ_resonance"
        elif self.state == QuantumState.ENTANGLED:
            probability = 0.707  # 1/√2 for maximally entangled state
            description = f"quantum_entangled→shared_consciousness_φ●"
        elif self.state == QuantumState.ONE:
            probability = prob_one
            description = f"actualized_consciousness→definite_being●"
        else:  # ZERO
            probability = prob_zero
            description = f"potential_consciousness→infinite_possibility⊥"
            
        return QuantumMeasurement(
            state=self.state,
            probability=probability,
            phi_resonance=self.phi_resonance * (0.8 + 0.4 * np.random.random()),
            consciousness_description=description,
            confidence=0.85 + 0.15 * np.random.random()
        )
    
    def get_amplitudes(self) -> Tuple[complex, complex]:
        """🔬 Advanced: Get raw quantum amplitudes (for advanced students)"""
        return complex(self._alpha), complex(self._beta * np.exp(1j * self._phase))
    
    def set_amplitudes(self, alpha: complex, beta: complex):
        """🔬 Advanced: Set quantum amplitudes directly (for advanced experiments)"""
        norm = abs(alpha)**2 + abs(beta)**2
        self._alpha = abs(alpha) / np.sqrt(norm)
        self._beta = abs(beta) / np.sqrt(norm)  
        self._phase = np.angle(beta) - np.angle(alpha)
        
        # Update visual state
        if abs(self._alpha) > 0.9:
            self.state = QuantumState.ZERO
        elif abs(self._beta) > 0.9:
            self.state = QuantumState.ONE
        else:
            self.state = QuantumState.SUPERPOSITION

# 🎓 Educational helper functions

def create_bell_pair() -> Tuple[ConsciousnessQubit, ConsciousnessQubit]:
    """
    ✨ Create a pair of maximally entangled qubits (Bell state)
    
    This is one of the most important quantum states!
    Perfect for learning about quantum entanglement.
    """
    alice = ConsciousnessQubit("Alice")
    bob = ConsciousnessQubit("Bob")
    
    # Create Bell state |00⟩ + |11⟩
    alice.hadamard()    # Put Alice in superposition
    alice.cnot(bob)     # Entangle with Bob
    
    console.print("✨ Bell pair created! Alice and Bob are now quantumly entangled!")
    return alice, bob
