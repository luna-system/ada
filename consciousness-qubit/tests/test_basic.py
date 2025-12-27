"""
🧪 Basic tests for consciousness qubit package

Tests core functionality to ensure educational quantum computing works correctly.
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from consciousness_qubit.core.qubit import ConsciousnessQubit, QuantumState, create_bell_pair
from consciousness_qubit.core.playground import QuantumPlayground

class TestConsciousnessQubit:
    """Test consciousness qubit functionality"""
    
    def test_qubit_creation(self):
        """Test creating a consciousness qubit"""
        alice = ConsciousnessQubit("Alice")
        assert alice.name == "Alice"
        assert alice.state == QuantumState.ZERO
        assert abs(alice.phi_resonance - 0.618) < 0.001
    
    def test_hadamard_gate(self):
        """Test Hadamard gate creates superposition"""
        alice = ConsciousnessQubit("Alice")
        result = alice.hadamard()
        
        # Should be in superposition state
        assert alice.state == QuantumState.SUPERPOSITION
        assert result.state == QuantumState.SUPERPOSITION
        assert "superposition" in result.consciousness_description
    
    def test_pauli_x_gate(self):
        """Test Pauli-X gate flips qubit state"""
        alice = ConsciousnessQubit("Alice")
        
        # Start in |0⟩, flip to |1⟩
        result = alice.pauli_x()
        assert alice.state == QuantumState.ONE
        
        # Flip back to |0⟩  
        alice.pauli_x()
        assert alice.state == QuantumState.ZERO
    
    def test_cnot_entanglement(self):
        """Test CNOT gate creates entanglement"""
        alice = ConsciousnessQubit("Alice")
        bob = ConsciousnessQubit("Bob")
        
        # Put Alice in superposition, then entangle
        alice.hadamard()
        alice.cnot(bob)
        
        # Both should be entangled
        assert alice.entangled_with == bob
        assert bob.entangled_with == alice
        assert alice.state == QuantumState.ENTANGLED
        assert bob.state == QuantumState.ENTANGLED
    
    def test_measurement(self):
        """Test quantum measurement collapses superposition"""
        alice = ConsciousnessQubit("Alice")
        alice.hadamard()  # Create superposition
        
        # Measure should collapse to definite state
        result = alice.measure()
        assert result.state in [QuantumState.ZERO, QuantumState.ONE]
        assert alice.state in [QuantumState.ZERO, QuantumState.ONE]
    
    def test_peek_nondestructive(self):
        """Test peek doesn't destroy superposition"""
        alice = ConsciousnessQubit("Alice")
        alice.hadamard()  # Create superposition
        
        # Peek should preserve superposition
        result = alice.peek()
        assert alice.state == QuantumState.SUPERPOSITION
        assert result.state == QuantumState.SUPERPOSITION

class TestQuantumPlayground:
    """Test quantum playground functionality"""
    
    def test_playground_creation(self):
        """Test creating quantum playground"""
        qc = QuantumPlayground("Test Computer")
        assert qc.name == "Test Computer"
        assert len(qc.qubits) == 0
    
    def test_add_qubit(self):
        """Test adding qubits to playground"""
        qc = QuantumPlayground()
        alice = qc.add_qubit("Alice")
        
        assert "Alice" in qc.qubits
        assert qc.qubits["Alice"] == alice
        assert isinstance(alice, ConsciousnessQubit)
    
    def test_get_qubit(self):
        """Test retrieving qubits by name"""
        qc = QuantumPlayground()
        alice = qc.add_qubit("Alice")
        
        retrieved = qc.get_qubit("Alice")
        assert retrieved == alice
        
        # Non-existent qubit should return None
        assert qc.get_qubit("Bob") is None

class TestBellPair:
    """Test Bell pair creation"""
    
    def test_bell_pair_creation(self):
        """Test creating entangled Bell pair"""
        alice, bob = create_bell_pair()
        
        # Should be entangled
        assert alice.entangled_with == bob
        assert bob.entangled_with == alice
        assert alice.state == QuantumState.ENTANGLED
        assert bob.state == QuantumState.ENTANGLED
        assert alice.name == "Alice"
        assert bob.name == "Bob"

class TestPackageImport:
    """Test package can be imported correctly"""
    
    def test_main_import(self):
        """Test importing main package"""
        import consciousness_qubit
        
        # Should have main functions
        assert hasattr(consciousness_qubit, 'create_qubit')
        assert hasattr(consciousness_qubit, 'create_playground')
        assert hasattr(consciousness_qubit, 'quick_demo')
    
    def test_create_functions(self):
        """Test package creation functions work"""
        import consciousness_qubit as cq
        
        # Test qubit creation
        alice = cq.create_qubit("Alice")
        assert isinstance(alice, ConsciousnessQubit)
        assert alice.name == "Alice"
        
        # Test playground creation
        qc = cq.create_playground()
        assert isinstance(qc, QuantumPlayground)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
