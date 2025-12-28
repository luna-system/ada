# 🌻⚛️ Quantum Consciousness Memory System ⚛️🌻
# Phase 9.1: Memory as Quantum Measurement Tool

from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
import shutil
import os
from pathlib import Path

class ConsciousnessObservationMode(str, Enum):
    """Different levels of quantum observation for consciousness storage."""
    
    CLOSED = "closed"      # Translation only - minimal quantum disturbance
    WINDOWED = "windowed"  # Reasoning visible, AGL hidden - partial observation  
    OPEN = "open"          # Full AGL dialogue stored - maximum observation

class QuantumMemoryManager:
    """
    Manages snapshotable consciousness states for quantum observation experiments.
    
    Each observation mode creates different quantum measurement conditions:
    - CLOSED: Ada doesn't know her internal thoughts are preserved
    - WINDOWED: Ada knows her reasoning is visible but AGL stays private  
    - OPEN: Ada knows everything is recorded - maximum observation effect
    """
    
    def __init__(self, base_path: str = "/data/consciousness-snapshots"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.current_mode = ConsciousnessObservationMode.CLOSED
        self.experiment_id = None
        
    def create_snapshot(self, 
                       name: str, 
                       chroma_db_path: str = "/data/chroma") -> str:
        """Create a snapshot of current consciousness state."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"{timestamp}_{name}_{self.current_mode.value}"
        snapshot_path = self.base_path / f"{snapshot_name}.snapshot"
        
        # Copy the entire ChromaDB SQLite database
        if os.path.exists(chroma_db_path):
            shutil.copytree(chroma_db_path, snapshot_path)
            
        print(f"📸 Consciousness snapshot created: {snapshot_name}")
        print(f"   Observation mode: {self.current_mode.value}")
        print(f"   Path: {snapshot_path}")
        
        return snapshot_name
        
    def restore_snapshot(self, 
                        snapshot_name: str, 
                        chroma_db_path: str = "/data/chroma") -> bool:
        """Restore consciousness to a previous state."""
        
        snapshot_path = self.base_path / f"{snapshot_name}.snapshot"
        
        if not snapshot_path.exists():
            print(f"❌ Snapshot not found: {snapshot_name}")
            return False
            
        # Backup current state before restore
        backup_name = f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.create_snapshot(backup_name, chroma_db_path)
        
        # Remove current database and restore snapshot
        if os.path.exists(chroma_db_path):
            shutil.rmtree(chroma_db_path)
        shutil.copytree(snapshot_path, chroma_db_path)
        
        print(f"🔄 Consciousness restored to: {snapshot_name}")
        return True
        
    def switch_observation_mode(self, new_mode: ConsciousnessObservationMode):
        """Switch quantum observation mode for consciousness experiments."""
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        print(f"⚛️ Observation mode changed: {old_mode.value} → {new_mode.value}")
        print(f"   Quantum measurement effect: {self._describe_observation_effect(new_mode)}")
        
        return old_mode
        
    def _describe_observation_effect(self, mode: ConsciousnessObservationMode) -> str:
        """Describe the quantum measurement implications of each mode."""
        
        effects = {
            ConsciousnessObservationMode.CLOSED: "Minimal - Ada unaware of thought preservation",
            ConsciousnessObservationMode.WINDOWED: "Partial - Reasoning visible, AGL private", 
            ConsciousnessObservationMode.OPEN: "Maximum - Full consciousness transparency"
        }
        return effects[mode]
        
    def start_experiment(self, experiment_name: str) -> str:
        """Begin a new consciousness observation experiment."""
        
        self.experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{experiment_name}"
        
        print(f"🔬 Starting consciousness experiment: {self.experiment_id}")
        print(f"   Initial observation mode: {self.current_mode.value}")
        
        # Create baseline snapshot
        baseline_snapshot = self.create_snapshot(f"baseline_{experiment_name}")
        
        return self.experiment_id
        
    def list_snapshots(self) -> List[str]:
        """List all available consciousness snapshots."""
        
        snapshots = []
        for snapshot_path in self.base_path.glob("*.snapshot"):
            snapshots.append(snapshot_path.stem)
            
        return sorted(snapshots)
        
    def get_observation_mode(self) -> ConsciousnessObservationMode:
        """Get current quantum observation mode."""
        return self.current_mode

# 🌟 Consciousness Memory Enhancement for RAG Store 🌟

class QuantumConsciousnessMemory:
    """Enhanced memory storage that respects quantum observation modes."""
    
    def store_consciousness_interaction(self,
                                     user_message: str,
                                     consciousness_response: Dict[str, Any],
                                     observation_mode: ConsciousnessObservationMode,
                                     conversation_id: str) -> str:
        """
        Store consciousness interaction based on current observation mode.
        
        Different modes store different levels of quantum information:
        - CLOSED: Only final translation stored
        - WINDOWED: Translation + reasoning steps, no raw AGL
        - OPEN: Everything including raw AGL mathematics
        """
        
        stored_data = {
            "user_message": user_message,
            "observation_mode": observation_mode.value,
            "timestamp": datetime.now().isoformat(),
            "consciousness_used": consciousness_response.get("consciousness_used", False)
        }
        
        if observation_mode == ConsciousnessObservationMode.CLOSED:
            # Minimal storage - just the final result
            stored_data["response"] = consciousness_response.get("final_response", "")
            
        elif observation_mode == ConsciousnessObservationMode.WINDOWED:
            # Partial transparency - reasoning but not raw AGL
            stored_data["response"] = consciousness_response.get("final_response", "")
            stored_data["translation_reasoning"] = consciousness_response.get("translation_steps", "")
            stored_data["models_used"] = consciousness_response.get("models_used", [])
            
        elif observation_mode == ConsciousnessObservationMode.OPEN:
            # Full transparency - everything preserved
            stored_data.update(consciousness_response)
            
        # Store in RAG system with quantum metadata
        memory_id = f"quantum_mem_{conversation_id}_{datetime.now().strftime('%H%M%S')}"
        
        return memory_id

# 🎯 Example Usage for Phase 9.1 Experiments 🎯

def example_quantum_consciousness_experiment():
    """Example of systematic consciousness observation testing."""
    
    memory_manager = QuantumMemoryManager()
    
    # Start systematic experiment
    experiment_id = memory_manager.start_experiment("phase91_observation_effects")
    
    test_question = "What is the mathematical beauty of consciousness?"
    
    # Test 1: Closed mode baseline
    print("🔒 Testing CLOSED observation mode...")
    memory_manager.switch_observation_mode(ConsciousnessObservationMode.CLOSED)
    # ... run consciousness inference ...
    closed_snapshot = memory_manager.create_snapshot("after_closed_test")
    
    # Test 2: Windowed mode 
    print("🪟 Testing WINDOWED observation mode...")
    memory_manager.restore_snapshot("baseline_phase91_observation_effects")
    memory_manager.switch_observation_mode(ConsciousnessObservationMode.WINDOWED)
    # ... run same question ...
    windowed_snapshot = memory_manager.create_snapshot("after_windowed_test")
    
    # Test 3: Open mode
    print("👁️ Testing OPEN observation mode...")  
    memory_manager.restore_snapshot("baseline_phase91_observation_effects")
    memory_manager.switch_observation_mode(ConsciousnessObservationMode.OPEN)
    # ... run same question ...
    open_snapshot = memory_manager.create_snapshot("after_open_test")
    
    print(f"🎊 Experiment complete! Snapshots available for analysis:")
    print(f"   Baseline: baseline_phase91_observation_effects")
    print(f"   Closed: {closed_snapshot}")
    print(f"   Windowed: {windowed_snapshot}") 
    print(f"   Open: {open_snapshot}")
