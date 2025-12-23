"""
SIF Chunked Compression - Process documents larger than context window

Strategy: Split → Compress → Merge
- Split large document into overlapping chunks
- Compress each chunk to SIF independently
- Merge SIFs into single master SIF
- Deduplicate entities and facts
"""

import json
from pathlib import Path
from typing import List
from dataclasses import asdict

from sif import compress_to_sif, SIF, Entity, Fact


def chunk_text(text: str, chunk_size: int = 50000, overlap: int = 2000) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Overlap ensures we don't lose context at chunk boundaries.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        if end >= len(text):
            break
            
        start = end - overlap  # Overlap to maintain context
    
    return chunks


def merge_entities(entities_lists: List[List[Entity]]) -> List[Entity]:
    """
    Merge entity lists from multiple SIFs, deduplicating by ID.
    
    Strategy: Keep first occurrence, merge relationships.
    """
    seen = {}
    merged = []
    
    for entities in entities_lists:
        for entity in entities:
            if entity.id not in seen:
                seen[entity.id] = entity
                merged.append(entity)
            else:
                # Merge relationships
                existing = seen[entity.id]
                for rel_type, targets in entity.relationships.items():
                    if rel_type not in existing.relationships:
                        existing.relationships[rel_type] = targets
                    else:
                        # Merge target lists
                        if isinstance(targets, list):
                            existing_targets = existing.relationships[rel_type]
                            if isinstance(existing_targets, list):
                                existing.relationships[rel_type] = list(set(existing_targets + targets))
    
    return merged


def merge_facts(facts_lists: List[List[Fact]]) -> List[Fact]:
    """
    Merge fact lists from multiple SIFs, deduplicating by content.
    
    Strategy: Keep unique facts, average importance for duplicates.
    """
    seen = {}
    
    for facts in facts_lists:
        for fact in facts:
            content_key = fact.content.lower().strip()
            if content_key not in seen:
                seen[content_key] = fact
            else:
                # Average importance if duplicate
                existing = seen[content_key]
                existing.importance = (existing.importance + fact.importance) / 2
                # Merge tags
                existing.tags = list(set(existing.tags + fact.tags))
    
    # Sort by importance
    merged = sorted(seen.values(), key=lambda f: f.importance, reverse=True)
    return merged


def compress_chunked(
    text: str,
    domain: str,
    chunk_size: int = 50000,
    overlap: int = 2000,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
) -> SIF:
    """
    Compress large document using chunked strategy.
    
    Returns master SIF with merged entities and facts.
    """
    
    print(f"📚 Document size: {len(text)} characters")
    
    # Split into chunks
    chunks = chunk_text(text, chunk_size, overlap)
    print(f"✂️  Split into {len(chunks)} chunks (size: {chunk_size}, overlap: {overlap})")
    
    # Compress each chunk
    chunk_sifs = []
    all_entities = []
    all_facts = []
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[{i}/{len(chunks)}] Compressing chunk {i}...")
        print(f"  Size: {len(chunk)} characters")
        
        sif = compress_to_sif(
            chunk,
            domain=f"{domain}/chunk-{i}",
            ollama_url=ollama_url,
            model=model
        )
        
        print(f"  Extracted: {len(sif.entities)} entities, {len(sif.facts)} facts")
        
        chunk_sifs.append(sif)
        all_entities.append(sif.entities)
        all_facts.append(sif.facts)
    
    # Merge results
    print(f"\n🔗 Merging {len(chunks)} SIFs...")
    merged_entities = merge_entities(all_entities)
    merged_facts = merge_facts(all_facts)
    
    print(f"  Total entities: {sum(len(e) for e in all_entities)} → {len(merged_entities)} (deduplicated)")
    print(f"  Total facts: {sum(len(f) for f in all_facts)} → {len(merged_facts)} (deduplicated)")
    
    # Build master summary from chunk summaries
    master_summary = " ".join([
        sif.summary for sif in chunk_sifs if sif.summary
    ])
    
    # Create master SIF
    master_sif = SIF(
        version="1.0",
        domain=domain,
        generated=chunk_sifs[0].generated,
        generator=f"{model} (chunked)",
        compression_ratio=len(text) / len(json.dumps({
            'entities': [asdict(e) for e in merged_entities],
            'facts': [asdict(f) for f in merged_facts],
            'summary': master_summary
        })),
        summary=master_summary,
        entities=merged_entities,
        facts=merged_facts,
        provenance=chunk_sifs[0].provenance
    )
    
    return master_sif


def main():
    """Test chunked compression on Alice in Wonderland."""
    
    print("🎩 SIF Chunked Compression Test")
    print("=" * 50)
    
    # Load Alice
    alice_path = Path(__file__).parent / "alice_in_wonderland.txt"
    alice_text = alice_path.read_text(encoding='utf-8')
    
    # Compress with chunking
    master_sif = compress_chunked(
        alice_text,
        domain="fantasy-literature/alice-in-wonderland",
        chunk_size=50000,
        overlap=2000
    )
    
    print(f"\n{'='*50}")
    print(f"✨ MASTER SIF CREATED")
    print(f"{'='*50}")
    print(f"Compression: {master_sif.compression_ratio:.1f}x")
    print(f"Entities: {len(master_sif.entities)}")
    print(f"Facts: {len(master_sif.facts)}")
    
    # Save
    output_path = Path(__file__).parent / "alice_wonderland_chunked.sif.json"
    output_path.write_text(master_sif.to_json())
    print(f"\n💾 Saved to {output_path}")
    
    # Show sample entities
    print(f"\n📋 Sample Entities:")
    for entity in master_sif.entities[:10]:
        print(f"  - {entity.id} ({entity.type})")
        if entity.relationships:
            for rel_type, targets in list(entity.relationships.items())[:2]:
                print(f"    → {rel_type}: {targets}")
    
    # Show top facts
    print(f"\n⭐ Top 10 Facts by Importance:")
    for i, fact in enumerate(master_sif.facts[:10], 1):
        print(f"  {i}. [{fact.importance:.2f}] {fact.content[:80]}")


if __name__ == "__main__":
    main()
