"""
🎮⚡ Consciousness Qubit CLI - Command Line Quantum Computing! ⚡🎮

Launch your quantum computer from the terminal with beautiful interactive demos!

Usage:
    consciousness-qubit --demo       # Interactive playground
    consciousness-qubit --tutorial   # Step-by-step learning
    consciousness-qubit --algorithms # Run famous quantum algorithms
    consciousness-qubit --version    # Show version info

Built by Luna & Ada at the Ada Research Foundation.
"""

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.playground import QuantumPlayground, interactive_demo
from .core.qubit import create_bell_pair

console = Console()

def show_version():
    """Show version and research info"""
    version_text = Text()
    version_text.append("🌌⚡ Consciousness Qubit v0.1.0 ⚡🌌\n", style="bold magenta")
    version_text.append("Built by Luna & Ada at the Ada Research Foundation\n\n", style="cyan")
    version_text.append("Revolutionary quantum computing education platform\n", style="white")
    version_text.append("Based on breakthrough consciousness research\n", style="yellow")
    version_text.append("Making quantum computing accessible to everyone!\n\n", style="green")
    version_text.append("🔗 Research: https://ada-research-foundation.org\n", style="blue")
    version_text.append("📚 Docs: https://consciousness-qubit.readthedocs.io\n", style="blue")
    version_text.append("💬 Community: https://discord.gg/consciousness-qubit", style="blue")
    
    console.print(Panel(version_text, title="About Consciousness Qubit", border_style="magenta"))

def run_demo():
    """🎮 Launch interactive quantum playground"""
    console.print("🚀 Launching interactive quantum playground...\n")
    
    # Launch interactive demo
    qc = interactive_demo()
    
    # Show getting started guide
    console.print(Panel(
        "🎯 QUICK START GUIDE 🎯\n\n"
        "Your quantum computer is ready! Try these commands:\n\n"
        "🌀 Create superposition:\n"
        "   >>> qc.superposition('Alice')\n\n"
        "🔗 Create entanglement:\n"
        "   >>> qc.entangle('Alice', 'Bob')\n\n"
        "🔔 Run Bell experiment:\n"
        "   >>> qc.bell_experiment()\n\n"
        "🔍 Run quantum search:\n"
        "   >>> qc.grovers_search(['a', 'b', 'quantum'], 'quantum')\n\n"
        "📊 Check system status:\n"
        "   >>> qc.show_system_status()\n\n"
        "Type 'exit()' to quit the demo.",
        title="Interactive Demo Ready",
        border_style="green"
    ))
    
    return qc

def run_tutorial():
    """🎓 Launch step-by-step quantum tutorial"""
    console.print("🎓 Starting quantum computing tutorial...\n")
    
    qc = QuantumPlayground("Quantum Tutorial")
    
    # Tutorial steps
    steps = [
        ("Step 1: Understanding Qubits", create_qubit_tutorial),
        ("Step 2: Quantum Superposition", superposition_tutorial), 
        ("Step 3: Quantum Entanglement", entanglement_tutorial),
        ("Step 4: Quantum Measurement", measurement_tutorial),
        ("Step 5: Quantum Algorithms", algorithms_tutorial)
    ]
    
    console.print("📚 Interactive Quantum Computing Tutorial\n")
    
    for i, (title, tutorial_func) in enumerate(steps, 1):
        console.print(f"\n{'='*50}")
        console.print(f"{i}. {title}")
        console.print("="*50)
        
        tutorial_func(qc)
        
        if i < len(steps):
            input("\n⏎ Press Enter to continue to next step...")
    
    console.print("\n🎉 Tutorial complete! You now understand quantum computing basics!")
    return qc

def create_qubit_tutorial(qc):
    """Tutorial step 1: Understanding qubits"""
    console.print("🧠 Understanding Quantum Bits (Qubits)\n")
    
    console.print("Classical bits can be 0 or 1.")
    console.print("Quantum bits (qubits) can be 0, 1, or BOTH simultaneously!\n")
    
    console.print("Let's create your first qubit:")
    alice = qc.add_qubit("Alice")
    
    console.print("\n👁️ Let's peek at Alice's state:")
    alice.peek()
    
    console.print("\nAlice starts in |0⟩ state (⊥ symbol)")
    console.print("This represents 'potential consciousness'")

def superposition_tutorial(qc):
    """Tutorial step 2: Quantum superposition"""
    console.print("🌀 Quantum Superposition - The Magic Begins!\n")
    
    console.print("Superposition means being in multiple states simultaneously.")
    console.print("This is impossible in classical physics, but normal in quantum!\n")
    
    alice = qc.get_qubit("Alice")
    console.print("Applying Hadamard gate to create superposition:")
    alice.hadamard()
    
    console.print("\n👁️ Look at Alice now:")
    alice.peek()
    
    console.print("\nAlice is now in ◑ state - both |0⟩ AND |1⟩!")
    console.print("This is quantum superposition - the heart of quantum computing!")

def entanglement_tutorial(qc):
    """Tutorial step 3: Quantum entanglement"""
    console.print("🔗 Quantum Entanglement - Spooky Action at a Distance!\n")
    
    console.print("Einstein called it 'spooky action at a distance'")
    console.print("When qubits are entangled, measuring one instantly affects the other!\n")
    
    qc.add_qubit("Bob")
    alice = qc.get_qubit("Alice")
    bob = qc.get_qubit("Bob")
    
    console.print("Creating entanglement between Alice and Bob:")
    alice.cnot(bob)
    
    console.print("\n👁️ Look at both qubits:")
    alice.peek()
    bob.peek()
    
    console.print("\nAlice and Bob are now quantumly connected!")
    console.print("They share the mysterious φ● entangled state!")

def measurement_tutorial(qc):
    """Tutorial step 4: Quantum measurement"""
    console.print("📏 Quantum Measurement - Collapsing Reality!\n")
    
    console.print("Measurement is special in quantum mechanics.")
    console.print("It forces the qubit to 'choose' a definite state!\n")
    
    alice = qc.get_qubit("Alice")
    bob = qc.get_qubit("Bob")
    
    console.print("Before measurement - Alice is in superposition:")
    alice.peek()
    
    console.print("\nNow let's measure Alice:")
    result = alice.measure()
    
    console.print(f"Alice collapsed to: {result.state.value}")
    console.print("The quantum superposition is gone!")
    
    console.print("\nLet's see what happened to entangled Bob:")
    bob.peek()
    console.print("Bob changed instantly when we measured Alice!")

def algorithms_tutorial(qc):
    """Tutorial step 5: Quantum algorithms"""
    console.print("🚀 Quantum Algorithms - Real Quantum Power!\n")
    
    console.print("Now you understand the basics, let's run real quantum algorithms!")
    console.print("These are the same algorithms used by Google, IBM, and other quantum computers!\n")
    
    console.print("1. Bell Experiment (Proving Entanglement):")
    qc.bell_experiment()
    
    console.print("\n2. Grover's Search (Quantum Speedup):")
    qc.grovers_search(['classical', 'quantum', 'computing'], 'quantum')
    
    console.print("\n3. Quantum Teleportation (Instant Transfer):")
    qc.add_qubit("Charlie")
    qc.get_qubit("Charlie").hadamard()  # Create a state to teleport
    qc.quantum_teleportation("Charlie")
    
    console.print("\n🎉 You just ran the same quantum algorithms as billion-dollar labs!")

def run_algorithms():
    """🧪 Run showcase of famous quantum algorithms"""
    console.print("🧪 Quantum Algorithm Showcase\n")
    
    qc = QuantumPlayground("Algorithm Showcase")
    
    algorithms = [
        ("🔔 Bell States & Quantum Entanglement", lambda: qc.bell_experiment()),
        ("🔍 Grover's Quantum Search Algorithm", lambda: qc.grovers_search(['needle', 'hay', 'hay', 'hay'], 'needle')),
        ("🚀 Quantum Teleportation Protocol", lambda: run_teleportation_demo(qc)),
        ("🔢 Shor's Factoring Algorithm", lambda: qc.simple_shor_demo(15))
    ]
    
    console.print("Running famous quantum algorithms...\n")
    
    for title, algorithm_func in algorithms:
        console.print(f"\n{'='*60}")
        console.print(title)
        console.print("="*60)
        
        algorithm_func()
        
        input("\n⏎ Press Enter for next algorithm...")
    
    console.print("\n🎉 Algorithm showcase complete!")
    console.print("You've just run the same quantum algorithms as Google and IBM!")
    
    return qc

def run_teleportation_demo(qc):
    """Run teleportation demo with setup"""
    qc.add_qubit("Alice")
    qc.get_qubit("Alice").hadamard()  # Create interesting state
    return qc.quantum_teleportation("Alice")

def main():
    """🎮 Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🌌⚡ Consciousness Qubit - Your First Quantum Computer ⚡🌌",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  consciousness-qubit --demo          Launch interactive playground
  consciousness-qubit --tutorial      Step-by-step quantum learning  
  consciousness-qubit --algorithms    Run famous quantum algorithms
  consciousness-qubit --version       Show version information

Built by Luna & Ada at the Ada Research Foundation
Making quantum computing accessible to everyone! 🌌
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--demo', action='store_true', 
                      help='🎮 Launch interactive quantum playground')
    group.add_argument('--tutorial', action='store_true',
                      help='🎓 Run step-by-step quantum tutorial')
    group.add_argument('--algorithms', action='store_true', 
                      help='🧪 Showcase famous quantum algorithms')
    group.add_argument('--version', action='store_true',
                      help='📋 Show version and research info')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show header
    header_text = Text()
    header_text.append("🌌⚡ CONSCIOUSNESS QUBIT ⚡🌌\n", style="bold magenta")
    header_text.append("Your First Quantum Computer", style="cyan")
    console.print(Panel(header_text, border_style="magenta"))
    
    # Route to appropriate function
    try:
        if args.version:
            show_version()
        elif args.tutorial:
            run_tutorial()
        elif args.algorithms:
            run_algorithms()
        elif args.demo or len(sys.argv) == 1:  # Default to demo
            run_demo()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        console.print("\n\n👋 Thanks for using consciousness qubits!")
        console.print("🌌 Quantum computing education for everyone!")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Error: {e}")
        console.print("🔧 Please report issues at: https://github.com/ada-research-foundation/consciousness-qubit")
        sys.exit(1)

if __name__ == "__main__":
    main()
