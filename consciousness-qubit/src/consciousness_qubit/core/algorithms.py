"""
🧪⚡ Quantum Algorithms - Famous Quantum Computing Breakthroughs ⚡🧪

Educational implementations of the most important quantum algorithms.

Built by Luna & Ada at the Ada Research Foundation.
"""

from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel

console = Console()

class QuantumAlgorithms:
    """
    🧪 Collection of famous quantum algorithms for education
    
    Provides easy-to-use implementations of breakthrough quantum algorithms
    with educational explanations and visualizations.
    """
    
    @staticmethod
    def create_bell_states(playground) -> Dict[str, Any]:
        """
        🔔 Create Bell states - Prove quantum entanglement exists!
        
        This experiment fundamentally changed our understanding of reality.
        Einstein called it "spooky action at a distance" because he couldn't
        believe that measuring one particle could instantly affect another.
        
        Args:
            playground: QuantumPlayground instance
            
        Returns:
            Results of Bell state creation and measurement
        """
        console.print(Panel(
            "🔔 CREATING BELL STATES 🔔\n"
            "Proving Einstein wrong about 'spooky action at a distance'!\n"
            "This experiment shows quantum entanglement is real.",
            title="Bell States Experiment",
            border_style="magenta"
        ))
        
        return playground.bell_experiment()
    
    @staticmethod  
    def grovers_search(playground, search_list: List[str], target: str) -> Dict[str, Any]:
        """
        🔍 Grover's quantum search - Find items faster than any classical computer!
        
        Classical computers need to check every item one by one: O(N) time.
        Quantum computers can find items in O(√N) time - quadratic speedup!
        
        This proves quantum computers can be fundamentally faster.
        
        Args:
            playground: QuantumPlayground instance
            search_list: Items to search through
            target: Item to find
            
        Returns:
            Search results showing quantum speedup
        """
        console.print(Panel(
            f"🔍 GROVER'S QUANTUM SEARCH 🔍\n"
            f"Searching for '{target}' in {len(search_list)} items\n"
            f"Classical time: {len(search_list)} steps\n"
            f"Quantum time: {int(len(search_list)**0.5)} steps!\n"
            f"Quantum advantage: {len(search_list) / int(len(search_list)**0.5):.1f}x faster!",
            title="Quantum Speedup Demonstration",
            border_style="cyan"
        ))
        
        return playground.grovers_search(search_list, target)
    
    @staticmethod
    def shors_factoring(playground, number: int = 15) -> Dict[str, Any]:
        """
        🔢 Shor's algorithm - Break encryption using quantum period finding!
        
        This is the algorithm that threatens all current internet security.
        RSA encryption relies on the fact that factoring large numbers is hard
        for classical computers. Shor's algorithm makes it easy for quantum computers!
        
        Args:
            playground: QuantumPlayground instance  
            number: Number to factor
            
        Returns:
            Factoring results (demonstrates cryptographic threat)
        """
        console.print(Panel(
            f"🔢 SHOR'S FACTORING ALGORITHM 🔢\n"
            f"Factoring {number} using quantum period finding\n"
            f"This algorithm threatens RSA encryption!\n"
            f"If we can factor large numbers, we can break internet security.",
            title="Quantum Cryptography Threat",
            border_style="red"
        ))
        
        return playground.simple_shor_demo(number)
    
    @staticmethod
    def quantum_teleportation(playground, qubit_name: str) -> Dict[str, Any]:
        """
        🚀 Quantum teleportation - Send quantum states instantly across space!
        
        This doesn't teleport matter (sorry Star Trek fans), but it does
        teleport quantum information instantly using entanglement.
        The original quantum state is destroyed, but appears elsewhere!
        
        Args:
            playground: QuantumPlayground instance
            qubit_name: Name of qubit to teleport
            
        Returns:
            Teleportation results
        """
        console.print(Panel(
            f"🚀 QUANTUM TELEPORTATION 🚀\n"
            f"Teleporting quantum state of '{qubit_name}'\n"
            f"Using quantum entanglement for instant transmission!\n"
            f"The original state is destroyed, but appears elsewhere.",
            title="Quantum Information Transfer",
            border_style="magenta"
        ))
        
        return playground.quantum_teleportation(qubit_name)

# Educational information about quantum algorithms
ALGORITHM_INFO = {
    "bell_states": {
        "name": "Bell States & Quantum Entanglement",
        "year": 1964,
        "inventor": "John Stewart Bell",
        "importance": "Proved quantum entanglement is real, not just theory",
        "applications": ["Quantum communication", "Quantum cryptography", "Quantum computing foundations"]
    },
    "grovers_search": {
        "name": "Grover's Quantum Search Algorithm", 
        "year": 1996,
        "inventor": "Lov Grover",
        "importance": "First practical quantum algorithm showing clear speedup",
        "applications": ["Database search", "Optimization", "Machine learning"]
    },
    "shors_factoring": {
        "name": "Shor's Factoring Algorithm",
        "year": 1994, 
        "inventor": "Peter Shor",
        "importance": "Threatens all current public-key cryptography",
        "applications": ["Breaking RSA", "Cryptanalysis", "Number theory"]
    },
    "quantum_teleportation": {
        "name": "Quantum Teleportation Protocol",
        "year": 1993,
        "inventor": "Charles Bennett et al.",
        "importance": "Enables quantum communication and distributed quantum computing",
        "applications": ["Quantum internet", "Quantum networks", "Quantum error correction"]
    }
}

def show_algorithm_history():
    """📚 Display the history of quantum algorithm breakthroughs"""
    console.print("📚 History of Quantum Algorithm Breakthroughs 📚\n")
    
    for alg_id, info in ALGORITHM_INFO.items():
        console.print(f"🧪 {info['name']} ({info['year']})")
        console.print(f"   Inventor: {info['inventor']}")
        console.print(f"   Impact: {info['importance']}")
        console.print(f"   Uses: {', '.join(info['applications'])}\n")

def get_algorithm_explanation(algorithm_name: str) -> Optional[str]:
    """📖 Get detailed explanation of a quantum algorithm"""
    explanations = {
        "bell": "Bell states demonstrate quantum entanglement - when two qubits become quantumly connected so that measuring one instantly affects the other, no matter how far apart they are. This 'spooky action at a distance' proves quantum mechanics is fundamentally different from classical physics.",
        
        "grover": "Grover's algorithm provides quadratic speedup for searching unsorted databases. While classical computers must check items one by one (O(N) time), quantum computers can find items in O(√N) time by using quantum superposition to check many possibilities simultaneously.",
        
        "shor": "Shor's algorithm efficiently factors large numbers by finding the period of modular exponentiation using quantum Fourier transform. This breaks RSA encryption, which relies on the assumption that factoring large numbers is computationally difficult.",
        
        "teleportation": "Quantum teleportation transmits quantum states using entanglement and classical communication. The original state is destroyed during measurement, but its exact quantum information appears in another location instantaneously."
    }
    
    return explanations.get(algorithm_name.lower())
