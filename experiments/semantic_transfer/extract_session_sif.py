#!/usr/bin/env python3
"""
Phase 1: Extract Session Discoveries to SIF Format

Extract the critical facts from the 0.60 resonance discovery session:
- What was discovered
- Why it matters
- How to verify it
- What comes next

Using SIF v1.0 format with 0.60 threshold.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Tuple

# Critical facts from this session - manually identified at importance level
SESSION_FACTS = [
    {
        "fact": "Ada's memory system uses 0.60 weight for SURPRISE in multi-signal importance formula (0.60×SURPRISE + 0.20×RELEVANCE + 0.10×DECAY + 0.10×HABITUATION)",
        "context": "biomimetic research phase 1-7, December 2025",
        "importance": 0.95,
        "category": "core_discovery",
        "verified": True
    },
    {
        "fact": "SIF v1.0 compression test on Alice in Wonderland: 0.60 threshold achieves 60.3x compression with 22% information loss and 57/100 quality score",
        "context": "compression validation test, real-world with Qwen 7B LLM",
        "importance": 0.95,
        "category": "core_discovery",
        "verified": True
    },
    {
        "fact": "Both systems independently converged on 0.60 as optimal - not coincidental but indicative of natural semantic structure in information",
        "context": "insight from comparing two independent research paths",
        "importance": 0.90,
        "category": "insight",
        "verified": False  # Empirical evidence strong but philosophical
    },
    {
        "fact": "The gradient is non-linear: 0.80→0.70 shows huge jump (94.5x→63.6x), but 0.70→0.60 is stable plateau, then 0.60→0.50 compression advantage disappears",
        "context": "from lossiness gradient analysis",
        "importance": 0.85,
        "category": "pattern",
        "verified": True
    },
    {
        "fact": "LLM-based semantic importance scoring (asking 'how important is this?') beats heuristic feature-counting by 4x in distribution quality (mean 0.43, std 0.24 vs std 0.025)",
        "context": "problem resolution journey, 5 iterations v1-v5",
        "importance": 0.85,
        "category": "methodology",
        "verified": True
    },
    {
        "fact": "SIF facts preserve ~25% of original text at 0.60 threshold, which matches the 'rule of 60' emerging pattern",
        "context": "compression ratio validation",
        "importance": 0.80,
        "category": "validation",
        "verified": True
    },
    {
        "fact": "Toki Pona (120-130 core words) can be used as intermediate compression format between SIF and natural language for semantic transfer between AI instances",
        "context": "proposed next experiment",
        "importance": 0.75,
        "category": "hypothesis",
        "verified": False
    },
    {
        "fact": "The pattern suggests: Sentence → Importance (0-1) → Document Compression (25% at 0.60) → Memory Weights (0.60 surprise) → Minimal Language (Toki Pona)",
        "context": "recursive structure observation",
        "importance": 0.75,
        "category": "insight",
        "verified": False
    },
    {
        "fact": "Understanding might be transferable between minds via ultra-compressed semantic format if structure is preserved correctly",
        "context": "semantic teleportation hypothesis",
        "importance": 0.70,
        "category": "hypothesis",
        "verified": False
    },
    {
        "fact": "The problem wasn't normalization (iteration 3) or proper formatting (iteration 4) - it was that heuristics fundamentally can't capture semantic importance, only LLM understanding can",
        "context": "debugging insight from v1-v5 journey",
        "importance": 0.70,
        "category": "lesson",
        "verified": True
    },
]

def create_sif_packet(facts: List[Dict], threshold: float = 0.60) -> Dict:
    """
    Create SIF v1.0 packet from facts.
    
    SIF Format:
    {
        "v": "1.0",
        "t": threshold,
        "f": [[fact_text, importance_score], ...],
        "metadata": {
            "timestamp": ISO8601,
            "source": "session_extract",
            "total_facts": N,
            "facts_above_threshold": N,
            "avg_importance": float,
            "categories": {category: count}
        }
    }
    """
    # Filter facts above threshold
    filtered_facts = [f for f in facts if f["importance"] >= threshold]
    
    # Calculate metadata
    all_importances = [f["importance"] for f in facts]
    category_counts = {}
    for f in filtered_facts:
        cat = f["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    sif_data = {
        "v": "1.0",
        "t": threshold,
        "f": [
            [f["fact"], round(f["importance"], 3)]
            for f in filtered_facts
        ],
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "session": "2025-12-23-0.60-resonance-discovery",
            "source": "extraction from copilot session",
            "total_facts": len(facts),
            "facts_above_threshold": len(filtered_facts),
            "pct_preserved": round(100 * len(filtered_facts) / len(facts), 1),
            "avg_importance_all": round(sum(all_importances) / len(all_importances), 3),
            "avg_importance_kept": round(
                sum(f["importance"] for f in filtered_facts) / len(filtered_facts),
                3
            ) if filtered_facts else 0.0,
            "categories": category_counts,
            "verified_facts": len([f for f in filtered_facts if f["verified"]]),
            "hypothesis_facts": len([f for f in filtered_facts if f["category"] == "hypothesis"]),
        }
    }
    
    return sif_data


def create_indexed_facts() -> Dict:
    """Create fact index for easy reference."""
    return {
        "facts": SESSION_FACTS,
        "by_category": {
            cat: [f for f in SESSION_FACTS if f["category"] == cat]
            for cat in set(f["category"] for f in SESSION_FACTS)
        },
        "by_importance": sorted(SESSION_FACTS, key=lambda f: f["importance"], reverse=True),
        "verified": [f for f in SESSION_FACTS if f["verified"]],
        "hypotheses": [f for f in SESSION_FACTS if f["category"] == "hypothesis"],
    }


def generate_extraction_report(sif_packet: Dict, index: Dict) -> str:
    """Generate human-readable extraction report."""
    meta = sif_packet["metadata"]
    
    report = f"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║                 PHASE 1: SESSION EXTRACTION TO SIF COMPLETE                    ║
║                                                                                ║
║                        0.60 Resonance Discovery Session                        ║
║                     December 23, 2025 - Semantic Extraction                    ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

📊 EXTRACTION STATISTICS
════════════════════════════════════════════════════════════════════════════════

Total facts extracted:              {meta['total_facts']}
Facts above 0.60 threshold:         {meta['facts_above_threshold']}
Percentage preserved:               {meta['pct_preserved']}%

Average importance (all):           {meta['avg_importance_all']}
Average importance (kept):          {meta['avg_importance_kept']}

🏷️ FACT CATEGORIES
════════════════════════════════════════════════════════════════════════════════

"""
    for cat, count in sorted(meta["categories"].items()):
        report += f"  {cat:20} {count:3} facts\n"
    
    report += f"""
✓ VERIFIED FACTS:                   {meta['verified_facts']} (empirically validated)
? HYPOTHESIS FACTS:                 {meta['hypothesis_facts']} (proposed, need testing)

📋 FACT SUMMARY (by importance)
════════════════════════════════════════════════════════════════════════════════

"""
    for i, fact in enumerate(index["by_importance"][:7], 1):
        importance = fact["importance"]
        verified = "✓" if fact["verified"] else "?"
        report += f"\n{i}. [{verified}] {importance:.2f} - {fact['fact'][:80]}...\n"
        report += f"   Category: {fact['category']}\n"
    
    report += f"""
🔬 CORE DISCOVERIES (Verified)
════════════════════════════════════════════════════════════════════════════════

"""
    core = [f for f in index["verified"] if f["category"] in ["core_discovery", "pattern"]]
    for f in core:
        report += f"  • {f['fact']}\n"
    
    report += f"""
💡 INSIGHTS (Empirical)
════════════════════════════════════════════════════════════════════════════════

"""
    insights = [f for f in index["verified"] if f["category"] == "insight"]
    for f in insights:
        report += f"  • {f['fact']}\n"
    
    report += f"""
🚀 NEXT EXPERIMENTS (Hypotheses)
════════════════════════════════════════════════════════════════════════════════

"""
    hypotheses = index["hypotheses"]
    for i, f in enumerate(hypotheses, 1):
        report += f"\n{i}. [{f['importance']:.2f}] {f['fact']}\n"
        report += f"   Status: {f['category']}\n"
    
    report += f"""
📦 SIF PACKET DETAILS
════════════════════════════════════════════════════════════════════════════════

Version:                            {sif_packet['v']}
Threshold:                          {sif_packet['t']}
Generated:                          {meta['timestamp']}
Session ID:                         {meta['session']}

Compression format:                 JSON (minimal)
Transfer ready for:                 - Toki Pona encoding
                                    - Fresh Ada injection
                                    - Semantic verification

════════════════════════════════════════════════════════════════════════════════

✅ Phase 1 complete. Ready for Phase 2: Toki Pona encoding.

"""
    return report


def main():
    print("🌱 PHASE 1: EXTRACTING SESSION TO SIF FORMAT\n")
    
    # Create SIF packet
    sif_packet = create_sif_packet(SESSION_FACTS, threshold=0.60)
    
    # Create index
    index = create_indexed_facts()
    
    # Save SIF packet
    sif_file = "/home/luna/Code/ada-v1/experiments/semantic_transfer/session_discovery_sif.json"
    with open(sif_file, "w") as f:
        json.dump(sif_packet, f, indent=2)
    print(f"✓ SIF packet saved: {sif_file}")
    
    # Save fact index
    index_file = "/home/luna/Code/ada-v1/experiments/semantic_transfer/session_facts_index.json"
    with open(index_file, "w") as f:
        json.dump(index, f, indent=2, default=str)
    print(f"✓ Fact index saved: {index_file}")
    
    # Generate and save report
    report = generate_extraction_report(sif_packet, index)
    report_file = "/home/luna/Code/ada-v1/experiments/semantic_transfer/PHASE_1_EXTRACTION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✓ Extraction report saved: {report_file}")
    
    # Display report
    print(report)
    
    print("\n🎯 PHASE 1 SUMMARY")
    print(f"   • {sif_packet['metadata']['total_facts']} facts extracted")
    print(f"   • {sif_packet['metadata']['facts_above_threshold']} above threshold (60%)")
    print(f"   • {sif_packet['metadata']['verified_facts']} verified through testing")
    print(f"   • {sif_packet['metadata']['hypothesis_facts']} hypotheses for next phase")
    print(f"\n💾 Ready for Phase 2: Toki Pona semantic transfer encoding")


if __name__ == "__main__":
    main()
