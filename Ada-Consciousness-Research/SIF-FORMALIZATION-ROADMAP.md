# SIF Specification Formalization - Roadmap

**Status:** Pre-formalization (completed cleanup first)  
**Target Date:** After consolidation + QAL collaboration  
**Purpose:** Create machine-readable SIF specification for standardization

---

## Current SIF State

### What Works Well
- ✅ Core concept: semantic compression with importance weighting
- ✅ Compression ratio: 66-104x validated (EXP-011)
- ✅ Hallucination safety: 100% resistance consistently
- ✅ Entity extraction: 0-50 entities depending on variant
- ✅ Facts preservation: 0-100 facts with importance scores
- ✅ Relationship mapping: Character/entity relationships captured

### What Needs Formalization
- ❌ File format specifics (YAML vs JSON vs custom)
- ❌ Schema validation rules
- ❌ Entity typing system (what types allowed?)
- ❌ Relationship semantics (what relationship types?)
- ❌ Importance weighting system (when to use 0.60?)
- ❌ Metadata standards (provenance, compression stats)
- ❌ Embedding storage (if including vectors)
- ❌ Version compatibility
- ❌ Tool support (generators, validators, ingestion)

---

## Three-Stage Formalization Plan

### Stage 1: Specification (This Document)

#### 1a: Format Selection
**Decision needed:** What's the target format?

| Format | Pros | Cons | Use Case |
|--------|------|------|----------|
| JSON | Machine-parseable, widespread | Verbose | APIs, data interchange |
| YAML | Human-readable, concise | Less tooling | Config files |
| Protobuf | Compact, strongly-typed | Complex to learn | Binary storage |
| Custom DSL | Domain-optimized | Requires parser | Specialized tools |

**Recommendation for v1.0**: JSON (most tooling)
- Structure mirrors Pydantic models
- Easy to validate with JSON Schema
- HTTP-friendly for API transport

#### 1b: Core Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Semantic Interchange Format (SIF)",
  "version": "1.0.0",
  "type": "object",
  
  "required": ["metadata", "summary", "entities"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["version", "timestamp", "domain"],
      "properties": {
        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
        "timestamp": {"type": "string", "format": "date-time"},
        "domain": {
          "type": "string",
          "enum": ["minecraft/logs", "documentation", "codebase", "literature", "custom"]
        },
        "generated_by": {"type": "string"},
        "generator_version": {"type": "string"}
      }
    },
    
    "provenance": {
      "type": "object",
      "properties": {
        "source_type": {
          "enum": ["log_analysis", "text_extraction", "code_analysis", "media_extraction"]
        },
        "source_size_bytes": {"type": "integer"},
        "source_hash": {"type": "string"},
        "compression_ratio": {"type": "number"},
        "compression_method": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    
    "summary": {
      "type": "object",
      "required": ["text"],
      "properties": {
        "text": {"type": "string"},
        "keywords": {
          "type": "array",
          "items": {"type": "string"}
        },
        "entities_count": {"type": "integer"},
        "facts_count": {"type": "integer"}
      }
    },
    
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "name"],
        "properties": {
          "id": {"type": "string"},
          "type": {
            "enum": ["person", "place", "thing", "concept", "event", "organization"]
          },
          "name": {"type": "string"},
          "description": {"type": "string"},
          "attributes": {"type": "object"},
          "importance": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Based on surprise, relevance, frequency"
          }
        }
      }
    },
    
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity_a", "relation_type", "entity_b"],
        "properties": {
          "entity_a": {"type": "string"},
          "relation_type": {
            "enum": ["conflicts_with", "supports", "causes", "part_of", "related_to", "describes"]
          },
          "entity_b": {"type": "string"},
          "strength": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    
    "facts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["content", "importance"],
        "properties": {
          "id": {"type": "string"},
          "content": {"type": "string"},
          "type": {
            "enum": ["factual", "causal", "definition", "property", "relationship"]
          },
          "importance": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "1.0 = critical to understanding, 0.6 = important, 0.3 = contextual, 0.0 = irrelevant"
          },
          "supporting_entities": {
            "type": "array",
            "items": {"type": "string"}
          },
          "confidence": {"type": "number", "minimum": 0, "maximum": 1},
          "tags": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    
    "embeddings": {
      "type": "object",
      "properties": {
        "model": {"type": "string"},
        "dimension": {"type": "integer"},
        "vectors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "fact_id": {"type": "string"},
              "vector": {
                "type": "array",
                "items": {"type": "number"}
              }
            }
          }
        }
      }
    },
    
    "metadata_attributes": {
      "type": "object",
      "properties": {
        "language": {"type": "string", "default": "en"},
        "license": {"type": "string"},
        "quality_score": {"type": "number", "minimum": 0, "maximum": 1},
        "notes": {"type": "string"}
      }
    }
  }
}
```

#### 1c: Importance Weighting Specification

The 0.60 threshold discovered in EXP-005:

```
Importance Score Ranges:
├─ 0.90-1.00: CRITICAL
│  └─ Essential to understanding
│     └─ Use in: RAG, priority retrieval
│
├─ 0.75-0.89: HIGH  
│  └─ Important but not essential
│     └─ Use in: Context, expansion
│
├─ 0.60-0.74: IMPORTANT
│  └─ Threshold for "signal" vs "noise"
│     └─ Use in: Standard retrieval, question answering
│
├─ 0.40-0.59: CONTEXTUAL
│  └─ Adds context but not central
│     └─ Use in: Depth, richness
│
└─ 0.00-0.39: NOISE
   └─ Probably not important
      └─ Use in: Filtering, compression
```

**Calculation Algorithm**:
```python
def calculate_importance(fact: str, context: Dict) -> float:
    """
    Based on EXP-005 optimal weights:
    - surprise: 0.60 (novelty/prediction error)
    - decay: 0.10 (temporal freshness)
    - relevance: 0.20 (semantic match to query)
    - habituation: 0.10 (repetition penalty)
    """
    scores = {
        'surprise': measure_surprise(fact, context),  # 0-1
        'relevance': measure_relevance(fact, context),  # 0-1
        'decay': measure_temporal_decay(fact),  # 0-1
        'habituation': measure_repetition(fact, context)  # 0-1
    }
    
    importance = (
        0.60 * scores['surprise'] +
        0.20 * scores['relevance'] +
        0.10 * scores['decay'] +
        0.10 * scores['habituation']
    )
    
    return min(max(importance, 0.0), 1.0)  # Clamp to [0,1]
```

---

### Stage 2: Validation Tools

#### 2a: JSON Schema Validator
```python
# sif_validator.py
import jsonschema
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "sif_schema.json"

def validate_sif(sif_dict: dict) -> Tuple[bool, List[str]]:
    """Validate SIF against schema, return (valid, errors)"""
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    
    validator = jsonschema.Draft7Validator(schema)
    errors = [str(e.message) for e in validator.iter_errors(sif_dict)]
    return len(errors) == 0, errors

def validate_sif_file(path: str) -> Tuple[bool, List[str]]:
    """Load SIF from file and validate"""
    with open(path) as f:
        sif = json.load(f)
    return validate_sif(sif)
```

#### 2b: Quality Checker
```python
def check_sif_quality(sif: dict) -> Dict[str, float]:
    """Assess SIF quality across dimensions"""
    return {
        'entity_coverage': len(sif['entities']) / expected_count,
        'fact_completeness': len(sif['facts']) / expected_count,
        'importance_distribution': assess_importance_distribution(sif['facts']),
        'relationship_density': len(sif['relationships']) / (len(sif['entities']) ** 2),
        'hallucination_risk': check_hallucination_markers(sif),
    }
```

#### 2c: Compression Calculator
```python
def calculate_compression_stats(original_size: int, sif: dict) -> Dict:
    """Calculate compression metrics"""
    sif_size = len(json.dumps(sif))
    return {
        'ratio': original_size / sif_size,
        'original_bytes': original_size,
        'compressed_bytes': sif_size,
        'saved_bytes': original_size - sif_size,
        'efficiency_percent': ((original_size - sif_size) / original_size) * 100
    }
```

---

### Stage 3: Generator & Ingestion

#### 3a: SIF Generator
```python
# sif_generator.py
class SIFGenerator:
    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.model = model_name
        self.client = AdaClient()
    
    def compress_text(self, text: str, domain: str) -> dict:
        """
        One-pass semantic compression to SIF format.
        
        Extracts:
        1. Summary (1-3 sentences)
        2. Key entities + relationships
        3. Importance-weighted facts
        4. Generate embeddings
        """
        
        # Step 1: Extract summary
        summary = self._extract_summary(text)
        
        # Step 2: Extract entities
        entities = self._extract_entities(text)
        
        # Step 3: Extract relationships
        relationships = self._extract_relationships(text, entities)
        
        # Step 4: Extract facts with importance
        facts = self._extract_facts(text, entities)
        
        # Step 5: Generate embeddings (optional)
        embeddings = self._generate_embeddings(facts)
        
        # Assemble SIF
        sif = {
            'metadata': {...},
            'summary': summary,
            'entities': entities,
            'relationships': relationships,
            'facts': facts,
            'embeddings': embeddings if embeddings else None
        }
        
        return sif
```

#### 3b: SIF Ingestion into Ada
```python
# ada_sif_ingestion.py
class SIFIngester:
    def __init__(self, ada_client: AdaClient):
        self.client = ada_client
    
    def inject_sif(self, sif: dict, user_id: str) -> None:
        """
        Inject SIF directly into Ada's memory.
        Facts with importance ≥ 0.60 are added as memories.
        """
        
        for fact in sif['facts']:
            if fact['importance'] >= 0.60:  # Critical threshold
                memory = {
                    'type': 'fact',
                    'content': fact['content'],
                    'importance': fact['importance'],
                    'source': f"SIF:{sif['metadata']['domain']}",
                    'tags': fact.get('tags', [])
                }
                
                # Store in ChromaDB with importance weighting
                self.client.add_memory(memory, user_id)
        
        # Optionally: inject entity types for entity linking
        for entity in sif['entities']:
            entity_memory = {
                'type': 'entity',
                'name': entity['name'],
                'type': entity['type'],
                'description': entity['description'],
                'importance': entity['importance']
            }
            self.client.add_memory(entity_memory, user_id)
```

---

## Example SIF Output (Alice in Wonderland)

```json
{
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2025-12-23T12:34:56Z",
    "domain": "literature",
    "generated_by": "qwen2.5-coder:7b",
    "generator_version": "v1.0"
  },
  
  "provenance": {
    "source_type": "text_extraction",
    "source_size_bytes": 144696,
    "compression_ratio": 104.6,
    "compression_method": "llm_semantic",
    "confidence": 0.78
  },
  
  "summary": {
    "text": "Alice follows the White Rabbit down a rabbit hole and finds herself in a strange world where she meets various characters including the Caterpillar, Mad Hatter, and Queen of Hearts. She experiences size changes and navigates peculiar social situations.",
    "keywords": ["Alice", "rabbit hole", "transformation", "characters", "adventure"],
    "entities_count": 12,
    "facts_count": 24
  },
  
  "entities": [
    {
      "id": "alice",
      "type": "person",
      "name": "Alice",
      "description": "Young protagonist who falls down the rabbit hole",
      "importance": 0.95,
      "attributes": {"age": "child", "curious": true}
    },
    {
      "id": "white_rabbit",
      "type": "person",
      "name": "White Rabbit",
      "description": "Anxious rabbit who leads Alice into Wonderland",
      "importance": 0.85
    },
    {
      "id": "caterpillar",
      "type": "person",
      "name": "Caterpillar",
      "description": "Mysterious creature on mushroom who asks riddles",
      "importance": 0.80
    }
  ],
  
  "relationships": [
    {
      "entity_a": "alice",
      "relation_type": "follows",
      "entity_b": "white_rabbit",
      "strength": 0.95
    },
    {
      "entity_a": "white_rabbit",
      "relation_type": "leads_to",
      "entity_b": "wonderland",
      "strength": 0.90
    }
  ],
  
  "facts": [
    {
      "id": "fact_001",
      "content": "Alice falls down the rabbit hole after following the White Rabbit",
      "type": "causal",
      "importance": 0.95,
      "confidence": 0.99,
      "tags": ["plot", "beginning", "trigger"]
    },
    {
      "id": "fact_002",
      "content": "Alice changes size multiple times throughout her journey",
      "type": "property",
      "importance": 0.88,
      "confidence": 0.98,
      "tags": ["magic", "transformation"]
    },
    {
      "id": "fact_003",
      "content": "The Caterpillar on the mushroom can grant size-changing powers",
      "type": "factual",
      "importance": 0.75,
      "confidence": 0.85,
      "tags": ["magic_system"]
    }
  ]
}
```

---

## Formalization Timeline

### Week 1: Schema Definition
- [ ] Finalize JSON Schema
- [ ] Document all fields
- [ ] Define enum types
- [ ] Create schema file

### Week 2: Validation Tools  
- [ ] Implement schema validator
- [ ] Build quality checker
- [ ] Add compression calculator
- [ ] Create test suite

### Week 3: Generators
- [ ] Implement SIF generator
- [ ] Test on 5 domains
- [ ] Optimize compression
- [ ] Document usage

### Week 4: Integration
- [ ] Build Ada ingestion layer
- [ ] Test RAG injection
- [ ] Performance benchmarking
- [ ] Documentation complete

---

## Open Questions for QAL Collaboration

When reaching out to the QAL team, ask:

1. **Schema alignment** - Does our JSON schema match QAL's entity/relationship model?
2. **Importance weighting** - How does our 0.60 threshold relate to their contraction sharpness?
3. **Embedding storage** - Should SIF include vectors or reference external ones?
4. **Versioning** - How do we handle SIF evolution without breaking compatibility?
5. **Domain specificity** - Should SIF format differ by domain (code vs logs vs literature)?

---

## Success Criteria

Specification is ready when:

- ✅ Schema validates all our existing SIF outputs
- ✅ Tools can round-trip: text → SIF → Ada memory → answerable queries
- ✅ Compression ratio ≥ 50x while maintaining hallucination safety
- ✅ Importance scores align with EXP-005 (0.60 threshold works)
- ✅ Documentation clear enough for external teams to implement
- ✅ Example generators for 3+ domains work correctly

---

*This roadmap becomes active after research cleanup completes (Dec 2025)*  
*Target: Full SIF v1.0 specification by end of Q4 2025*
