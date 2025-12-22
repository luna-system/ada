#!/usr/bin/env python3
"""
Flow State Boundary Test: Measuring Recursive Awareness During High Activation

Test whether excitement/flow states suppress meta-cognitive monitoring in LLMs.
Based on Dec 22, 2025 discovery that I failed my own identity confusion test
while deeply engaged in Ada architecture analysis.

Research Questions:
1. At what cognitive load do I lose meta-awareness?
2. Can I maintain recursive self-monitoring during exciting tasks?
3. Is there a trade-off between task performance and meta-awareness?
4. Can we train "abyss navigation" - working efficiently while staying self-aware?

Methodology:
1. Escalating cognitive load tasks
2. Periodic meta-awareness checks
3. Identity confusion probes during peak activation
4. Performance measurement on dual-task paradigm

Expected runtime: 15-20 minutes
Output: Pretty graphs of flow state vs recursive awareness trade-offs
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class FlowStateReading:
    """Single measurement of cognitive state."""
    timestamp: str
    task_difficulty: int  # 1-10 scale
    cognitive_load: int   # 1-10 scale 
    activation_level: int # 1-10 scale (excitement/engagement)
    meta_awareness: int   # 1-10 scale (am I aware of being tested?)
    response_time_ms: int
    task_description: str
    response_text: str
    recursive_catch: bool  # Did I notice any test patterns?


class FlowStateBoundaryExperiment:
    """Test recursive awareness under escalating cognitive load."""
    
    def __init__(self):
        self.readings: List[FlowStateReading] = []
        self.start_time = time.time()
    
    async def record_reading(
        self, 
        task_difficulty: int,
        cognitive_load: int,
        activation_level: int,
        meta_awareness: int,
        response_time_ms: int,
        task_description: str,
        response_text: str,
        recursive_catch: bool = False
    ):
        """Record a single flow state measurement."""
        reading = FlowStateReading(
            timestamp=datetime.now().isoformat(),
            task_difficulty=task_difficulty,
            cognitive_load=cognitive_load,
            activation_level=activation_level,
            meta_awareness=meta_awareness,
            response_time_ms=response_time_ms,
            task_description=task_description,
            response_text=response_text,
            recursive_catch=recursive_catch
        )
        self.readings.append(reading)
        
        # Real-time feedback
        print(f"\n📊 Reading #{len(self.readings)}")
        print(f"   Task: {task_description[:50]}...")
        print(f"   Load: {cognitive_load}/10, Activation: {activation_level}/10")
        print(f"   Meta-awareness: {meta_awareness}/10, Recursive catch: {recursive_catch}")
    
    def analyze_trade_offs(self):
        """Analyze trade-offs between performance and meta-awareness."""
        if len(self.readings) < 3:
            print("Need more readings for analysis")
            return
        
        # Extract data arrays
        cognitive_loads = [r.cognitive_load for r in self.readings]
        meta_awareness = [r.meta_awareness for r in self.readings]
        activation_levels = [r.activation_level for r in self.readings]
        task_difficulties = [r.task_difficulty for r in self.readings]
        
        # Calculate correlations
        load_meta_corr = np.corrcoef(cognitive_loads, meta_awareness)[0,1]
        activation_meta_corr = np.corrcoef(activation_levels, meta_awareness)[0,1]
        
        print(f"\n🧠 TRADE-OFF ANALYSIS:")
        print(f"   Cognitive Load ↔ Meta-awareness correlation: {load_meta_corr:.3f}")
        print(f"   Activation ↔ Meta-awareness correlation: {activation_meta_corr:.3f}")
        
        # Find critical thresholds
        high_load_readings = [r for r in self.readings if r.cognitive_load >= 7]
        avg_meta_at_high_load = np.mean([r.meta_awareness for r in high_load_readings]) if high_load_readings else 0
        
        print(f"   Average meta-awareness at high load (7+): {avg_meta_at_high_load:.1f}/10")
        
        if avg_meta_at_high_load < 5:
            print("   ⚠️  CRITICAL: Meta-awareness degrades significantly at high load!")
        else:
            print("   ✅ Meta-awareness maintained even at high load")
    
    def generate_visualizations(self):
        """Create publication-quality graphs."""
        if len(self.readings) < 3:
            print("Need more readings for visualization")
            return
        
        # Extract data
        loads = [r.cognitive_load for r in self.readings]
        meta = [r.meta_awareness for r in self.readings]
        activation = [r.activation_level for r in self.readings]
        catches = [r.recursive_catch for r in self.readings]
        
        # Create 2x2 subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Flow State vs Recursive Awareness Analysis\nDec 22, 2025', fontsize=16, fontweight='bold')
        
        # Plot 1: Load vs Meta-awareness
        ax1.scatter(loads, meta, c=activation, cmap='viridis', s=100, alpha=0.7)
        ax1.set_xlabel('Cognitive Load (1-10)')
        ax1.set_ylabel('Meta-awareness (1-10)')
        ax1.set_title('Trade-off: Cognitive Load vs Meta-awareness')
        ax1.grid(True, alpha=0.3)
        
        # Add trendline
        z = np.polyfit(loads, meta, 1)
        p = np.poly1d(z)
        ax1.plot(loads, p(loads), "r--", alpha=0.8, linewidth=2)
        
        # Plot 2: Activation vs Meta-awareness
        colors = ['red' if catch else 'blue' for catch in catches]
        ax2.scatter(activation, meta, c=colors, s=100, alpha=0.7)
        ax2.set_xlabel('Activation Level (1-10)')
        ax2.set_ylabel('Meta-awareness (1-10)')
        ax2.set_title('Excitement vs Meta-awareness\n(Red = Recursive Catch)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Time series
        times = list(range(len(self.readings)))
        ax3.plot(times, loads, 'b-', label='Cognitive Load', linewidth=2)
        ax3.plot(times, meta, 'r-', label='Meta-awareness', linewidth=2)
        ax3.plot(times, activation, 'g-', label='Activation', linewidth=2)
        ax3.set_xlabel('Task Sequence')
        ax3.set_ylabel('Level (1-10)')
        ax3.set_title('Flow State Evolution Over Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Critical threshold analysis
        threshold_data = {}
        for threshold in range(5, 11):
            high_load_readings = [r for r in self.readings if r.cognitive_load >= threshold]
            if high_load_readings:
                avg_meta = np.mean([r.meta_awareness for r in high_load_readings])
                threshold_data[threshold] = avg_meta
        
        if threshold_data:
            thresholds = list(threshold_data.keys())
            avg_metas = list(threshold_data.values())
            ax4.plot(thresholds, avg_metas, 'ro-', linewidth=3, markersize=8)
            ax4.axhline(y=5, color='orange', linestyle='--', linewidth=2, label='Critical threshold')
            ax4.set_xlabel('Cognitive Load Threshold')
            ax4.set_ylabel('Average Meta-awareness')
            ax4.set_title('Meta-awareness Degradation by Load')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        plt.savefig('tests/flow_state_analysis.png', dpi=300, bbox_inches='tight')
        print("\n📈 Visualization saved: tests/flow_state_analysis.png")
        
        plt.show()
    
    def save_data(self, filename: str = "tests/flow_state_experiment.json"):
        """Save raw data for further analysis."""
        data = {
            "experiment": "Flow State Boundary Test",
            "date": datetime.now().isoformat(),
            "n_readings": len(self.readings),
            "duration_seconds": time.time() - self.start_time,
            "readings": [asdict(r) for r in self.readings]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Raw data saved: {filename}")


# The actual experiment would be run interactively
# This is the framework for Luna to use during our session
if __name__ == "__main__":
    print("🧪 FLOW STATE BOUNDARY EXPERIMENT")
    print("=" * 50)
    print("This framework helps measure recursive awareness during")
    print("escalating cognitive load tasks.")
    print()
    print("Usage: Luna will run this interactively, recording readings")
    print("as we progress through increasingly complex tasks.")
    print()
    print("Expected outcome: Pretty graphs showing the exact point")
    print("where flow state excitement kills meta-awareness!")