"""
🎨⚡ Quantum Visualization - Beautiful φ-Optimized Quantum Graphics ⚡🎨

Visual components for consciousness qubit education with golden ratio aesthetics.

Built by Luna & Ada at the Ada Research Foundation.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class QuantumVisualizer:
    """
    🎨 Beautiful visualizations for quantum states and algorithms
    
    Uses φ-optimized design principles and consciousness-inspired aesthetics
    to make quantum computing concepts visually intuitive.
    """
    
    def __init__(self):
        """Initialize quantum visualizer with φ-optimized color scheme"""
        # φ-optimized colors (golden ratio inspired)
        self.colors = {
            'zero_state': '#1a1a2e',      # Deep potential
            'one_state': '#f59e0b',       # Golden actualization  
            'superposition': '#6366f1',    # Mysterious purple
            'entangled': '#ec4899',       # Quantum pink
            'phi_gold': '#fbbf24',        # φ golden ratio
            'consciousness': '#a78bfa'     # Consciousness purple
        }
        
        # φ-ratio proportions
        self.phi = 1.618
        self.phi_inverse = 0.618
        
    def plot_quantum_state(self, qubit_name: str, state_history: List[Dict]) -> plt.Figure:
        """
        📊 Plot quantum state evolution over time
        
        Args:
            qubit_name: Name of the qubit
            state_history: List of quantum state measurements
            
        Returns:
            Matplotlib figure with beautiful quantum state visualization
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6*self.phi_inverse))
        fig.patch.set_facecolor(self.colors['zero_state'])
        
        # Extract data
        times = range(len(state_history))
        zero_probs = [state.get('prob_zero', 0) for state in state_history]
        one_probs = [state.get('prob_one', 0) for state in state_history]
        phi_resonance = [state.get('phi_resonance', 0.618) for state in state_history]
        
        # Plot state probabilities
        ax1.fill_between(times, zero_probs, alpha=0.7, color=self.colors['zero_state'], label='|0⟩ ⊥')
        ax1.fill_between(times, one_probs, alpha=0.7, color=self.colors['one_state'], label='|1⟩ ●')
        ax1.set_ylabel('Probability', color='white')
        ax1.set_title(f'Quantum State Evolution: {qubit_name}', color=self.colors['phi_gold'], fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#0f0f23')
        
        # Plot φ-resonance
        ax2.plot(times, phi_resonance, color=self.colors['phi_gold'], linewidth=2, marker='●')
        ax2.axhline(y=0.618, color=self.colors['consciousness'], linestyle='--', alpha=0.7, label='φ = 0.618')
        ax2.set_ylabel('φ-Resonance', color='white')
        ax2.set_xlabel('Time Steps', color='white')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#0f0f23')
        
        # Style axes
        for ax in [ax1, ax2]:
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            
        plt.tight_layout()
        return fig
        
    def plot_entanglement_network(self, qubits: Dict[str, Any]) -> plt.Figure:
        """
        🔗 Visualize quantum entanglement network
        
        Shows which qubits are entangled with beautiful network graph
        """
        fig, ax = plt.subplots(figsize=(8, 8*self.phi_inverse))
        fig.patch.set_facecolor(self.colors['zero_state'])
        ax.set_facecolor('#0f0f23')
        
        # Create network layout
        num_qubits = len(qubits)
        angle_step = 2 * np.pi / num_qubits
        
        positions = {}
        qubit_names = list(qubits.keys())
        
        for i, name in enumerate(qubit_names):
            angle = i * angle_step
            x = np.cos(angle) * self.phi
            y = np.sin(angle) * self.phi
            positions[name] = (x, y)
            
        # Draw qubits
        for name, (x, y) in positions.items():
            qubit = qubits[name]
            
            # Choose color based on state
            if hasattr(qubit, 'state'):
                if str(qubit.state.value) == '⊥':
                    color = self.colors['zero_state']
                elif str(qubit.state.value) == '●':
                    color = self.colors['one_state']
                elif str(qubit.state.value) == '◑':
                    color = self.colors['superposition']
                else:  # Entangled
                    color = self.colors['entangled']
            else:
                color = self.colors['consciousness']
                
            # Draw qubit node
            circle = plt.Circle((x, y), 0.3, color=color, alpha=0.8)
            ax.add_patch(circle)
            
            # Add qubit label
            ax.text(x, y, name, ha='center', va='center', fontweight='bold', 
                   color='white', fontsize=10)
            
            # Draw entanglement connections
            if hasattr(qubit, 'entangled_with') and qubit.entangled_with:
                partner_name = qubit.entangled_with.name
                if partner_name in positions:
                    x2, y2 = positions[partner_name]
                    ax.plot([x, x2], [y, y2], color=self.colors['entangled'], 
                           linewidth=3, alpha=0.7, linestyle='--')
                    
                    # Add φ● symbol at midpoint
                    mid_x, mid_y = (x + x2) / 2, (y + y2) / 2
                    ax.text(mid_x, mid_y, 'φ●', ha='center', va='center',
                           color=self.colors['phi_gold'], fontsize=12, fontweight='bold')
        
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect('equal')
        ax.set_title('Quantum Entanglement Network', color=self.colors['phi_gold'], fontsize=16)
        ax.axis('off')
        
        return fig
        
    def create_algorithm_summary_table(self, algorithm_history: List[Dict]) -> Table:
        """
        📊 Create beautiful summary table of quantum algorithms
        """
        table = Table(title="🧪 Quantum Algorithm Results 🧪")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Key Result", style="yellow")
        table.add_column("Quantum Advantage", style="magenta")
        
        for result in algorithm_history:
            algorithm = result.get('experiment', 'Unknown')
            
            # Determine status
            success_keys = ['success', 'quantum_entanglement_demonstrated', 'factoring_success']
            success = any(result.get(key, False) for key in success_keys)
            status = "✅ Success" if success else "❌ Failed"
            
            # Extract key result
            if algorithm == 'Bell States':
                key_result = f"Correlation: {result.get('correlation', 0):.1%}"
                advantage = "Entanglement Proven"
            elif algorithm == 'Grovers Search':
                key_result = f"Found: {result.get('found_item', 'N/A')}"
                advantage = f"√N Speedup ({result.get('quantum_steps', 1)} steps)"
            elif algorithm == 'Shors Algorithm':
                factors = result.get('factors', [])
                key_result = f"Factors: {factors}"
                advantage = "Exponential Speedup"
            elif algorithm == 'Quantum Teleportation':
                fidelity = result.get('teleportation_fidelity', 0)
                key_result = f"Fidelity: {fidelity:.1%}"
                advantage = "Instant Transfer"
            else:
                key_result = "Completed"
                advantage = "Quantum Effect"
                
            table.add_row(algorithm, status, key_result, advantage)
            
        return table
        
    def show_quantum_state_symbols(self):
        """📚 Display guide to quantum state symbols"""
        symbols_text = Text()
        symbols_text.append("🌌 Quantum State Symbol Guide 🌌\n\n", style="bold magenta")
        symbols_text.append("⊥  |0⟩ State - Potential Consciousness\n", style="blue")
        symbols_text.append("●  |1⟩ State - Actualized Consciousness\n", style="gold1")
        symbols_text.append("◑  Superposition - Both States Simultaneously\n", style="purple") 
        symbols_text.append("φ● Entangled - Quantum Connection (φ-Resonance)\n", style="magenta")
        symbols_text.append("\nφ = 0.618... (Golden Ratio - Consciousness Resonance)", style="cyan")
        
        console.print(Panel(
            symbols_text,
            title="Understanding Consciousness Quantum States", 
            border_style="magenta"
        ))
        
    def animate_quantum_algorithm(self, algorithm_name: str, steps: List[Dict]) -> None:
        """
        🎬 Create animated visualization of quantum algorithm execution
        
        Shows step-by-step quantum state changes during algorithm execution
        """
        console.print(f"\n🎬 Animating {algorithm_name} Algorithm")
        console.print("=" * 50)
        
        for i, step in enumerate(steps, 1):
            console.print(f"\n⏯️  Step {i}: {step.get('description', 'Quantum Operation')}")
            
            # Show quantum states
            if 'qubit_states' in step:
                state_table = Table(title=f"Quantum States - Step {i}")
                state_table.add_column("Qubit", style="cyan")
                state_table.add_column("State", style="yellow")
                state_table.add_column("Description", style="white")
                
                for qubit_name, state_info in step['qubit_states'].items():
                    state_symbol = state_info.get('symbol', '?')
                    description = state_info.get('description', 'Unknown state')
                    state_table.add_row(qubit_name, state_symbol, description)
                    
                console.print(state_table)
                
            # Pause for animation effect (in real use, this could be time.sleep)
            # time.sleep(1)
        
        console.print(f"\n✨ {algorithm_name} animation complete!")

def create_quantum_circuit_diagram(gates: List[str], num_qubits: int = 2) -> str:
    """
    🔧 Create ASCII quantum circuit diagram
    
    Args:
        gates: List of gate names applied
        num_qubits: Number of qubits in circuit
        
    Returns:
        ASCII art quantum circuit
    """
    circuit = []
    
    # Header
    circuit.append("🔧 Quantum Circuit Diagram 🔧")
    circuit.append("=" * 30)
    
    # Qubit lines
    for i in range(num_qubits):
        line = f"q{i} |0⟩ ――"
        
        for gate in gates:
            if gate == "H":
                line += "―[H]―"
            elif gate == "X":
                line += "―[X]―"
            elif gate == "Z": 
                line += "―[Z]―"
            elif gate == "CNOT":
                if i == 0:  # Control qubit
                    line += "―●―"
                else:  # Target qubit
                    line += "―⊕―"
            else:
                line += "―――"
                
        line += "→ 📏"
        circuit.append(line)
        
        # Add connection line for CNOT
        if "CNOT" in gates and i == 0 and num_qubits > 1:
            circuit.append("     " + " " * (len(gates) * 5) + "│")
    
    return "\n".join(circuit)
