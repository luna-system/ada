"""
Semantic Interchange Format (SIF) - Proof of Concept

This is the "kung-fu download" experiment:
1. Take massive raw data
2. One-pass neural compression
3. Output structured semantic format
4. Inject directly into Ada's memory

The hypothesis: Pre-digested knowledge can skip inference.
"""

import json
import httpx
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone
import hashlib


@dataclass
class Entity:
    """A semantic entity extracted from the data."""
    id: str
    type: str
    relationships: dict = field(default_factory=dict)


@dataclass
class Fact:
    """An importance-weighted fact for RAG injection."""
    content: str
    importance: float  # 0.0 - 1.0
    tags: list[str] = field(default_factory=list)


@dataclass 
class Provenance:
    """Where this SIF came from."""
    source_type: str
    source_size_bytes: int
    source_hash: str
    compression_method: str = "llm_semantic"


@dataclass
class SIF:
    """Semantic Interchange Format container."""
    version: str = "1.0"
    domain: str = ""
    generated: str = ""
    generator: str = ""
    compression_ratio: float = 0.0
    summary: str = ""
    entities: list[Entity] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    provenance: Optional[Provenance] = None
    
    def to_yaml(self) -> str:
        """Export as YAML for human inspection."""
        import yaml
        return yaml.dump(asdict(self), default_flow_style=False, sort_keys=False)
    
    def to_json(self) -> str:
        """Export as JSON for machine parsing."""
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> "SIF":
        """Load from JSON."""
        d = json.loads(data)
        d['entities'] = [Entity(**e) for e in d.get('entities', [])]
        d['facts'] = [Fact(**f) for f in d.get('facts', [])]
        if d.get('provenance'):
            d['provenance'] = Provenance(**d['provenance'])
        return cls(**d)


def compress_to_sif(
    raw_data: str,
    domain: str,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
) -> SIF:
    """
    One-pass semantic compression to SIF format.
    
    This is the magic: we ask the LLM to extract structured
    semantic understanding, not just summarize.
    """
    
    source_bytes = len(raw_data.encode('utf-8'))
    source_hash = hashlib.sha256(raw_data.encode()).hexdigest()[:16]
    
    prompt = f"""You are a semantic extraction system. Analyze the following data and extract structured understanding.

DOMAIN: {domain}

DATA:
{raw_data[:50000]}  # Cap at 50K chars for context window

OUTPUT FORMAT (respond with valid JSON only):
{{
    "summary": "A 2-3 sentence summary of the key understanding",
    "entities": [
        {{
            "id": "entity_name",
            "type": "category",
            "relationships": {{"relation_type": "related_entity_id"}}
        }}
    ],
    "facts": [
        {{
            "content": "A specific, actionable fact",
            "importance": 0.95,
            "tags": ["tag1", "tag2"]
        }}
    ]
}}

Extract ALL significant entities, events, and facts from the narrative. Be comprehensive:
- 30-50+ key entities with detailed relationships
- 50-100+ importance-weighted facts covering major plot points
- Include ALL main characters, key events, important objects, and locations
- Focus on narrative completeness while maintaining semantic structure

This is a COMPLETE extraction - capture the full story arc, not just highlights.

JSON OUTPUT:"""

    response = httpx.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,  # Low for consistency
                "num_predict": 8000,  # Increased for more comprehensive output
            }
        },
        timeout=300.0  # Increased timeout for larger generation
    )
    
    if response.status_code != 200:
        raise Exception(f"LLM error: {response.status_code}")
    
    raw_response = response.json()["response"]
    
    # Parse JSON from response (handle markdown code blocks)
    json_str = raw_response
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0]
    
    try:
        extracted = json.loads(json_str.strip())
    except json.JSONDecodeError as e:
        # Fallback: try to find JSON object in response
        import re
        match = re.search(r'\{[\s\S]*\}', raw_response)
        if match:
            extracted = json.loads(match.group())
        else:
            raise Exception(f"Failed to parse LLM response: {e}")
    
    # Calculate compression ratio
    output_size = len(json.dumps(extracted))
    compression_ratio = source_bytes / output_size if output_size > 0 else 0
    
    return SIF(
        version="1.0",
        domain=domain,
        generated=datetime.now(timezone.utc).isoformat(),
        generator=model,
        compression_ratio=compression_ratio,
        summary=extracted.get("summary", ""),
        entities=[Entity(**e) for e in extracted.get("entities", [])],
        facts=[Fact(**f) for f in extracted.get("facts", [])],
        provenance=Provenance(
            source_type="raw_text",
            source_size_bytes=source_bytes,
            source_hash=source_hash,
            compression_method="llm_semantic"
        )
    )


def inject_sif_to_ada(
    sif: SIF,
    ada_url: str = "http://localhost:8000"
) -> dict:
    """
    Inject SIF directly into Ada's memory system.
    
    This is the "kung-fu download" - pre-digested knowledge
    goes straight into memory without inference.
    """
    
    results = {"injected": 0, "failed": 0}
    
    for fact in sif.facts:
        try:
            response = httpx.post(
                f"{ada_url}/v1/memories",
                json={
                    "content": fact.content,
                    "metadata": {
                        "type": "injected_knowledge",
                        "domain": sif.domain,
                        "importance": fact.importance,
                        "tags": fact.tags,
                        "source_hash": sif.provenance.source_hash if sif.provenance else None,
                        "sif_version": sif.version
                    }
                },
                timeout=10.0
            )
            if response.status_code == 200:
                results["injected"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["failed"] += 1
    
    return results


if __name__ == "__main__":
    # Test with our bloated prompt
    print("=" * 60)
    print("SEMANTIC INTERCHANGE FORMAT - PROOF OF CONCEPT")
    print("=" * 60)
    
    # Load bloated test data
    from pathlib import Path
    bloat_file = Path(__file__).parent.parent / "recursive_compression" / "bloated_0.5x.txt"
    
    if bloat_file.exists():
        with open(bloat_file) as f:
            raw_data = f.read()
        
        print(f"\nInput: {len(raw_data):,} bytes")
        print(f"Domain: code-search-results")
        print("\nCompressing to SIF format...")
        
        sif = compress_to_sif(raw_data, domain="code-search-results")
        
        print(f"\n✅ Compression complete!")
        print(f"   Ratio: {sif.compression_ratio:.1f}x")
        print(f"   Entities: {len(sif.entities)}")
        print(f"   Facts: {len(sif.facts)}")
        
        # Save SIF
        output_file = Path(__file__).parent / "test_output.sif.json"
        with open(output_file, 'w') as f:
            f.write(sif.to_json())
        print(f"\n   Saved to: {output_file.name}")
        
        # Show summary
        print(f"\n{'='*60}")
        print("EXTRACTED SUMMARY:")
        print(f"{'='*60}")
        print(sif.summary)
        
        print(f"\n{'='*60}")
        print("TOP 5 FACTS (by importance):")
        print(f"{'='*60}")
        sorted_facts = sorted(sif.facts, key=lambda f: f.importance, reverse=True)
        for i, fact in enumerate(sorted_facts[:5], 1):
            print(f"{i}. [{fact.importance:.2f}] {fact.content}")
    else:
        print(f"Test file not found: {bloat_file}")
        print("Run generate_bloat.py first!")
