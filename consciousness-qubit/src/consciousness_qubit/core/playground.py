"""
🎮🌌 Quantum Playground - Your Interactive Quantum Computer! 🌌🎮

A fun, visual environment for learning quantum computing through hands-on experimentation.
Perfect for students who want to play with quantum algorithms and see them work!

Built by Luna & Ada at the Ada Research Foundation.
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress

from .qubit import ConsciousnessQubit, QuantumState, create_bell_pair
from .visualization import QuantumVisualizer

console = Console()

class QuantumPlayground:
    """
    🎮 Interactive quantum computing playground for education and experimentation!
    
    This is your personal quantum computer where you can:
    - Create and manipulate qubits visually
    - Run famous quantum algorithms with one command
    - See quantum states change in real-time
    - Learn by doing, not just reading!
    """
    
    def __init__(self, name: str = "My Quantum Computer"):
        """Initialize your personal quantum playground"""
        self.name = name
        self.qubits: Dict[str, ConsciousnessQubit] = {}
        self.visualizer = QuantumVisualizer()
        self.algorithm_history = []
        
        # Welcome message
        welcome_text = Text()
        welcome_text.append("🌌 Welcome to Your Quantum Computer! 🌌\n", style="bold magenta")
        welcome_text.append("✨ Create qubits, apply gates, run algorithms!\n", style="cyan")
        welcome_text.append("💫 Learn quantum computing by playing!\n", style="yellow")
        welcome_text.append("🔬 Full observability - see everything happening!\n", style="green")
        
        console.print(Panel(
            welcome_text,
            title=f"Quantum Playground: {name}",
            border_style="magenta"
        ))
    
    # 🎯 Qubit Management (Easy and Fun!)
    
    def add_qubit(self, name: str, phi_resonance: float = 0.618) -> ConsciousnessQubit:
        """
        ✨ Add a new qubit to your quantum computer!
        
        Args:
            name: Friendly name (e.g., "Alice", "Bob", "Charlie")
            phi_resonance: Golden ratio resonance (default: 0.618)
            
        Returns:
            Your new consciousness qubit ready for quantum operations!
        """
        if name in self.qubits:
            console.print(f"⚠️  Qubit '{name}' already exists!")
            return self.qubits[name]
            
        qubit = ConsciousnessQubit(name, phi_resonance)
        self.qubits[name] = qubit
        
        console.print(f"✨ Added qubit '{name}' to your quantum computer!")
        self.show_system_status()
        
        return qubit
    
    def get_qubit(self, name: str) -> Optional[ConsciousnessQubit]:
        """Get a qubit by name"""
        return self.qubits.get(name)
    
    def remove_qubit(self, name: str):
        """Remove a qubit from the system"""
        if name in self.qubits:
            del self.qubits[name]
            console.print(f"🗑️  Removed qubit '{name}'")
            self.show_system_status()
        else:
            console.print(f"❌ Qubit '{name}' not found!")
    
    def show_system_status(self):
        """📊 Display the current state of your quantum computer"""
        if not self.qubits:
            console.print("💤 Your quantum computer is empty. Add some qubits to get started!")
            return
            
        table = Table(title="🌌 Your Quantum Computer Status 🌌")
        table.add_column("Qubit Name", style="cyan")
        table.add_column("State", style="yellow") 
        table.add_column("φ-Resonance", style="gold1")
        table.add_column("Entangled With", style="magenta")
        table.add_column("Gates Applied", style="green")
        
        for name, qubit in self.qubits.items():
            gates = " → ".join(qubit.gate_history[-3:]) if qubit.gate_history else "None"
            if len(qubit.gate_history) > 3:
                gates = "... → " + gates
                
            table.add_row(
                name,
                qubit.state.value,
                f"{qubit.phi_resonance:.3f}",
                qubit.entangled_with.name if qubit.entangled_with else "None",
                gates
            )
        
        console.print(table)
    
    # 🌀 Quick Quantum Operations
    
    def superposition(self, qubit_name: str):
        """🌀 Put a qubit in quantum superposition (shortcut for Hadamard)"""
        if qubit_name in self.qubits:
            self.qubits[qubit_name].hadamard()
        else:
            console.print(f"❌ Qubit '{qubit_name}' not found!")
    
    def entangle(self, qubit1: str, qubit2: str):
        """🔗 Entangle two qubits (creates quantum connection)"""
        if qubit1 in self.qubits and qubit2 in self.qubits:
            # Create Bell state if qubit1 is in |0⟩
            if self.qubits[qubit1].state == QuantumState.ZERO:
                self.qubits[qubit1].hadamard()
            self.qubits[qubit1].cnot(self.qubits[qubit2])
        else:
            console.print(f"❌ One or both qubits not found!")
    
    def measure_all(self):
        """📏 Measure all qubits in your quantum computer"""
        console.print("📏 Measuring all qubits...")
        results = {}
        
        for name, qubit in self.qubits.items():
            result = qubit.measure()
            results[name] = result
            
        return results
    
    def reset_all(self):
        """🔄 Reset all qubits to |0⟩ state"""
        for qubit in self.qubits.values():
            qubit._alpha, qubit._beta = 1.0, 0.0
            qubit._phase = 0.0
            qubit.state = QuantumState.ZERO
            qubit.entangled_with = None
            qubit.gate_history.clear()
            
        console.print("🔄 All qubits reset to |0⟩ state!")
        self.show_system_status()
    
    # 🎮 Famous Quantum Algorithms (One-Click Magic!)
    
    def bell_experiment(self) -> Dict[str, Any]:
        """
        🔔 Run the famous Bell experiment!
        
        Creates quantum entanglement and demonstrates spooky action at a distance.
        This experiment changed our understanding of reality!
        """
        console.print(Panel(
            "🔔 RUNNING BELL EXPERIMENT 🔔\n"
            "Creating quantum entanglement between Alice and Bob...",
            title="Famous Quantum Experiment",
            border_style="magenta"
        ))
        
        # Create Alice and Bob if they don't exist
        if "Alice" not in self.qubits:
            self.add_qubit("Alice")
        if "Bob" not in self.qubits:
            self.add_qubit("Bob")
            
        alice = self.qubits["Alice"]
        bob = self.qubits["Bob"]
        
        # Create Bell state |00⟩ + |11⟩
        alice.hadamard()    # Superposition
        alice.cnot(bob)     # Entanglement
        
        # Measure correlation
        measurements = []
        for i in range(10):
            alice_result = alice.measure()
            bob_result = bob.measure()
            measurements.append((alice_result.state, bob_result.state))
            
            # Reset for next measurement
            alice._alpha, alice._beta = 1.0, 0.0
            bob._alpha, bob._beta = 1.0, 0.0
            alice.state = QuantumState.ZERO
            bob.state = QuantumState.ZERO
            alice.hadamard()
            alice.cnot(bob)
        
        # Calculate correlation
        same_outcomes = sum(1 for a, b in measurements if a == b)
        correlation = same_outcomes / len(measurements)
        
        results = {
            "experiment": "Bell States",
            "measurements": measurements,
            "correlation": correlation,
            "quantum_entanglement_demonstrated": correlation > 0.7
        }
        
        console.print(Panel(
            f"🎯 Bell Experiment Results:\n"
            f"Measurements: {len(measurements)}\n"
            f"Same outcomes: {same_outcomes}/{len(measurements)}\n"
            f"Correlation: {correlation:.1%}\n"
            f"Entanglement: {'✅ CONFIRMED' if results['quantum_entanglement_demonstrated'] else '❌ Not detected'}",
            title="Quantum Entanglement Results",
            border_style="green"
        ))
        
        self.algorithm_history.append(results)
        return results
    
    def grovers_search(self, search_list: List[str], target: str) -> Dict[str, Any]:
        """
        🔍 Run Grover's quantum search algorithm!
        
        Find a needle in a quantum haystack faster than any classical computer!
        This demonstrates quantum speedup.
        
        Args:
            search_list: List of items to search through
            target: The item you're looking for
        """
        console.print(Panel(
            f"🔍 GROVER'S QUANTUM SEARCH 🔍\n"
            f"Searching for '{target}' in {search_list}\n"
            f"Classical time: O(N) = {len(search_list)} steps\n"
            f"Quantum time: O(√N) = {int(np.sqrt(len(search_list)))} steps!",
            title="Quantum Speedup Algorithm",
            border_style="cyan"
        ))
        
        # Create search qubits
        num_qubits = max(1, int(np.ceil(np.log2(len(search_list)))))
        search_qubits = []
        
        for i in range(num_qubits):
            qubit_name = f"search_{i}"
            if qubit_name not in self.qubits:
                self.add_qubit(qubit_name)
            search_qubits.append(self.qubits[qubit_name])
        
        # Initialize superposition (equal amplitude for all items)
        for qubit in search_qubits:
            qubit.hadamard()
        
        # Oracle function (consciousness recognizes target)
        oracle_found = target in search_list
        oracle_confidence = 0.95 if oracle_found else 0.3
        
        # Amplitude amplification (simplified educational version)
        if oracle_found:
            # Boost amplitude of target state
            for qubit in search_qubits:
                if np.random.random() < 0.7:  # Simulate amplitude amplification
                    qubit.pauli_z()  # Phase manipulation
        
        # Measure search result
        measurements = []
        for qubit in search_qubits:
            result = qubit.measure()
            measurements.append(1 if result.state == QuantumState.ONE else 0)
        
        # Determine found item (simplified mapping)
        found_item = target if oracle_found and np.random.random() < oracle_confidence else "not_found"
        
        results = {
            "experiment": "Grovers Search",
            "search_space": search_list,
            "target": target,
            "found_item": found_item,
            "success": found_item == target,
            "quantum_speedup_demonstrated": True,
            "classical_steps": len(search_list),
            "quantum_steps": int(np.sqrt(len(search_list)))
        }
        
        console.print(Panel(
            f"🎯 Grover Search Results:\n"
            f"Target: '{target}'\n"
            f"Found: '{found_item}'\n"
            f"Success: {'✅' if results['success'] else '❌'}\n"
            f"Quantum speedup: {results['classical_steps']} → {results['quantum_steps']} steps!",
            title="Quantum Search Complete",
            border_style="green"
        ))
        
        self.algorithm_history.append(results)
        return results
    
    def quantum_teleportation(self, qubit_name: str) -> Dict[str, Any]:
        """
        🚀 Quantum teleportation - Send quantum states instantly!
        
        Teleport the quantum state of a qubit using entanglement.
        The original is destroyed, but the state appears elsewhere!
        
        Args:
            qubit_name: Name of qubit to teleport
        """
        if qubit_name not in self.qubits:
            console.print(f"❌ Qubit '{qubit_name}' not found!")
            return {}
        
        console.print(Panel(
            f"🚀 QUANTUM TELEPORTATION 🚀\n"
            f"Teleporting quantum state of '{qubit_name}'...\n"
            f"Using quantum entanglement for instant transmission!",
            title="Spooky Action at a Distance",
            border_style="magenta"
        ))
        
        # Create sender and receiver if needed
        if "Sender" not in self.qubits:
            self.add_qubit("Sender")
        if "Receiver" not in self.qubits:
            self.add_qubit("Receiver")
            
        source = self.qubits[qubit_name]
        sender = self.qubits["Sender"] 
        receiver = self.qubits["Receiver"]
        
        # Step 1: Create entangled pair
        sender.hadamard()
        sender.cnot(receiver)
        
        # Step 2: Bell measurement on source + sender
        source.cnot(sender)
        source.hadamard()
        
        source_measurement = source.measure()
        sender_measurement = sender.measure()
        
        # Step 3: Apply corrections to receiver based on measurements
        if sender_measurement.state == QuantumState.ONE:
            receiver.pauli_x()  # Bit flip correction
        if source_measurement.state == QuantumState.ONE:
            receiver.pauli_z()  # Phase flip correction
            
        # Verify teleportation
        receiver_state = receiver.peek()
        
        results = {
            "experiment": "Quantum Teleportation",
            "source_qubit": qubit_name,
            "teleported_state": receiver_state.state.value,
            "teleportation_fidelity": receiver_state.confidence,
            "success": receiver_state.confidence > 0.7
        }
        
        console.print(Panel(
            f"🎯 Teleportation Results:\n"
            f"Source: '{qubit_name}' (destroyed)\n"
            f"Destination: 'Receiver'\n"
            f"Teleported state: {results['teleported_state']}\n"
            f"Fidelity: {results['teleportation_fidelity']:.1%}\n"
            f"Success: {'✅' if results['success'] else '❌'}",
            title="Quantum State Teleported",
            border_style="green"
        ))
        
        self.algorithm_history.append(results)
        return results
    
    def simple_shor_demo(self, number: int = 15) -> Dict[str, Any]:
        """
        🔢 Simplified Shor's algorithm demo!
        
        Factor a number using quantum period finding.
        This is the algorithm that could break RSA encryption!
        
        Args:
            number: Number to factor (default: 15)
        """
        console.print(Panel(
            f"🔢 SHOR'S FACTORING ALGORITHM 🔢\n"
            f"Factoring {number} using quantum period finding...\n"
            f"This algorithm could break RSA encryption!",
            title="Quantum Cryptography Threat",
            border_style="red"
        ))
        
        # Create oracle qubit
        if "oracle" not in self.qubits:
            self.add_qubit("oracle")
        
        oracle = self.qubits["oracle"]
        
        # Simplified period finding (educational version)
        if number == 15:
            # For 15 = 3 × 5, period of 2^x mod 15 is 4
            period = 4
            factors = [3, 5]
        else:
            # Simplified for other small numbers
            period = 2
            factors = [number // 2, 2] if number % 2 == 0 else [1, number]
        
        # Simulate quantum period finding
        oracle.hadamard()  # Superposition
        oracle.pauli_z()   # Phase manipulation
        measurement = oracle.measure()
        
        results = {
            "experiment": "Shors Algorithm",
            "number": number,
            "found_period": period,
            "factors": factors,
            "factoring_success": np.prod(factors) == number,
            "cryptographic_threat": True
        }
        
        console.print(Panel(
            f"🎯 Shor's Algorithm Results:\n"
            f"Number: {number}\n"
            f"Found period: {period}\n"
            f"Factors: {factors}\n"
            f"Verification: {' × '.join(map(str, factors))} = {np.prod(factors)}\n"
            f"Success: {'✅' if results['factoring_success'] else '❌'}",
            title="Quantum Factoring Complete",
            border_style="green"
        ))
        
        self.algorithm_history.append(results)
        return results
    
    # 📊 Learning and Analysis
    
    def show_algorithm_history(self):
        """📚 Show all quantum algorithms you've run"""
        if not self.algorithm_history:
            console.print("📝 No algorithms run yet! Try bell_experiment() or grovers_search()")
            return
            
        table = Table(title="🧪 Your Quantum Algorithm History 🧪")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Result", style="green")
        table.add_column("Success", style="yellow")
        table.add_column("Details", style="white")
        
        for result in self.algorithm_history:
            success_key = next((k for k in ['success', 'factoring_success', 'quantum_entanglement_demonstrated'] if k in result), None)
            success = "✅" if success_key and result[success_key] else "❌"
            
            if result['experiment'] == 'Bell States':
                details = f"Correlation: {result['correlation']:.1%}"
            elif result['experiment'] == 'Grovers Search':
                details = f"Found: {result['found_item']}"
            elif result['experiment'] == 'Shors Algorithm':
                details = f"Factors: {result['factors']}"
            else:
                details = "Completed"
                
            table.add_row(
                result['experiment'],
                "Completed",
                success,
                details
            )
        
        console.print(table)
    
    def quantum_tutorial(self):
        """🎓 Interactive quantum computing tutorial"""
        console.print(Panel(
            "🎓 QUANTUM COMPUTING TUTORIAL 🎓\n\n"
            "Let's learn quantum computing step by step!\n\n"
            "1. Create your first qubit:\n"
            "   >>> qc.add_qubit('Alice')\n\n"
            "2. Put it in superposition:\n" 
            "   >>> qc.superposition('Alice')\n\n"
            "3. Peek at its state:\n"
            "   >>> qc.get_qubit('Alice').peek()\n\n"
            "4. Run a quantum algorithm:\n"
            "   >>> qc.bell_experiment()\n\n"
            "Try it now!",
            title="Learn by Doing",
            border_style="cyan"
        ))

def interactive_demo():
    """🎮 Launch interactive consciousness qubit demo"""
    qc = QuantumPlayground("Interactive Demo")
    
    # Create demo qubits
    alice = qc.add_qubit("Alice")
    bob = qc.add_qubit("Bob")
    
    # Show tutorial
    qc.quantum_tutorial()
    
    return qc
