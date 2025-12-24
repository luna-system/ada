# SIF Reference Implementation - Python

**Status:** Working reference implementation for SIF v1.0  
**Language:** Python 3.10+  
**Dependencies:** pydantic, chromadb, numpy (optional: torch for embeddings)  
**Location:** `ada-logs/src/ada_logs/sif/`

---

## Core Implementation

### 1. SIF Data Models (Pydantic)

```python
# sif/models.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
import hashlib

class EntityType(str):
    PERSON = "person"
    PLACE = "place"
    THING = "thing"
    CONCEPT = "concept"
    EVENT = "event"
    ORGANIZATION = "organization"

class RelationType(str):
    CONFLICTS_WITH = "conflicts_with"
    SUPPORTS = "supports"
    CAUSES = "causes"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    DESCRIBES = "describes"
    CONTAINS = "contains"
    PRECEDES = "precedes"
    DEPENDS_ON = "depends_on"

class FactType(str):
    FACTUAL = "factual"
    CAUSAL = "causal"
    DEFINITION = "definition"
    PROPERTY = "property"
    RELATIONSHIP = "relationship"
    HYPOTHETICAL = "hypothetical"
    EVALUATIVE = "evaluative"

class SIFEntity(BaseModel):
    id: str = Field(..., regex="^[a-z0-9_-]+$")
    type: Literal[
        "person", "place", "thing", "concept", "event", "organization"
    ]
    name: str
    description: str
    importance: float = Field(..., ge=0, le=1)
    attributes: Dict = Field(default_factory=dict)
    aliases: List[str] = Field(default_factory=list)

    @validator('id')
    def validate_id(cls, v):
        if not v:
            raise ValueError('id cannot be empty')
        return v.lower()

class SIFRelationship(BaseModel):
    entity_a: str
    relation_type: Literal[
        "conflicts_with", "supports", "causes", "part_of",
        "related_to", "describes", "contains", "precedes", "depends_on"
    ]
    entity_b: str
    strength: float = Field(default=0.5, ge=0, le=1)
    context: Optional[str] = None

class SIFFact(BaseModel):
    id: str = Field(..., regex="^fact_[0-9]+$")
    content: str
    type: Literal[
        "factual", "causal", "definition", "property",
        "relationship", "hypothetical", "evaluative"
    ]
    importance: float = Field(..., ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    supporting_entities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class SIFMetadata(BaseModel):
    version: str = "1.0.0"
    timestamp: datetime
    domain: Literal["literature", "code", "logs", "conversation", "documentation", "other"]
    source_size_bytes: int = 0
    source_hash: Optional[str] = None

class SIFValidation(BaseModel):
    schema_version: str = "1.0.0"
    is_valid: bool = True
    checksum: Optional[str] = None
    quality_score: float = Field(default=0.5, ge=0, le=1)
    compression_ratio: float = 1.0

class SIFDocument(BaseModel):
    metadata: SIFMetadata
    summary: Dict[str, any]
    entities: List[SIFEntity]
    relationships: List[SIFRelationship] = Field(default_factory=list)
    facts: List[SIFFact] = Field(default_factory=list)
    embeddings: Optional[Dict] = None
    generator: Optional[Dict] = None
    validation: SIFValidation = Field(default_factory=SIFValidation)

    def to_json(self) -> str:
        """Serialize to canonical JSON (sorted keys, compact)"""
        return self.json(
            exclude_none=True,
            sort_keys=True,
            separators=(',', ':')
        )

    def calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of canonical representation"""
        doc_copy = self.copy()
        doc_copy.validation.checksum = None
        canonical = doc_copy.to_json()
        return hashlib.sha256(canonical.encode()).hexdigest()

    @classmethod
    def load_from_file(cls, path: str) -> 'SIFDocument':
        import json
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    def save_to_file(self, path: str):
        import json
        with open(path, 'w') as f:
            json.dump(self.dict(exclude_none=True), f, indent=2)
```

### 2. Importance Calculation

```python
# sif/importance.py

import math
import time
from typing import Dict, Any, Optional

WEIGHTS = {
    'surprise': 0.60,      # Dominates (novelty)
    'relevance': 0.20,     # Context-dependent
    'decay': 0.10,         # Temporal freshness
    'habituation': 0.10    # Repetition penalty
}

def surprise(fact: str, context: Dict[str, Any]) -> float:
    """
    Measure how unexpected this fact is.
    
    Implementation: Uses model's prediction error.
    In production: Call LLM with context and fact, measure surprise via entropy.
    
    For this reference: Use heuristic scoring
    """
    # Heuristic: Facts contradicting context or containing rare words = high surprise
    context_text = ' '.join(str(v) for v in context.values())
    
    # Simple implementation: unique words as proxy for surprise
    fact_words = set(fact.lower().split())
    context_words = set(context_text.lower().split())
    unique_words = len(fact_words - context_words)
    
    # Normalize: 0.0-1.0
    return min(unique_words / max(len(fact_words), 5), 1.0)

def relevance(fact: str, context: Dict[str, Any]) -> float:
    """
    Measure how relevant this fact is to the query.
    
    In production: Use embedding similarity
    """
    if 'query' not in context:
        return 0.5  # Default if no query
    
    # Heuristic: Word overlap with query
    fact_words = set(fact.lower().split())
    query_words = set(context['query'].lower().split())
    
    if not query_words:
        return 0.5
    
    overlap = len(fact_words & query_words)
    return overlap / len(query_words)

def decay(fact: str, context: Dict[str, Any]) -> float:
    """
    Measure how fresh this information is.
    
    Implementation: Exponential decay based on age
    """
    timestamp = context.get('timestamp')
    if not timestamp:
        return 0.8  # Default: fairly fresh
    
    if isinstance(timestamp, str):
        from datetime import datetime
        timestamp = datetime.fromisoformat(timestamp)
    
    age_seconds = (datetime.now(timestamp.tzinfo) - timestamp).total_seconds()
    half_life = context.get('half_life_seconds', 86400)  # 1 day default
    
    return math.exp(-0.693 * age_seconds / half_life)

def habituation(fact: str, context: Dict[str, Any]) -> float:
    """
    Measure penalty for repetition.
    
    Implementation: Inverse frequency in context
    """
    fact_frequencies = context.get('fact_frequencies', {})
    fact_id = context.get('fact_id', fact)
    
    mention_count = fact_frequencies.get(fact_id, 1)
    
    return 1.0 / (1.0 + math.log(mention_count + 1))

def calculate_importance(
    fact: str,
    context: Dict[str, Any] = None
) -> float:
    """
    Calculate importance score using weighted combination.
    
    Formula:
    importance = 0.60×surprise + 0.20×relevance + 0.10×decay + 0.10×habituation
    """
    if context is None:
        context = {}
    
    # Calculate components
    s = surprise(fact, context)
    r = relevance(fact, context)
    d = decay(fact, context)
    h = habituation(fact, context)
    
    # Weighted sum
    importance = (
        WEIGHTS['surprise'] * s +
        WEIGHTS['relevance'] * r +
        WEIGHTS['decay'] * d +
        WEIGHTS['habituation'] * h
    )
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, importance))

def importance_threshold(compression_tier: int) -> float:
    """Get importance threshold for compression tier"""
    if compression_tier == 1:
        return 0.75  # Critical only
    elif compression_tier == 2:
        return 0.60  # Standard (includes 0.60 threshold)
    elif compression_tier == 3:
        return 0.30  # Aggressive
    else:
        return 0.60  # Default
```

### 3. Compressor

```python
# sif/compressor.py

from typing import Optional, List
from .models import SIFDocument, SIFEntity, SIFFact, SIFRelationship, SIFMetadata, SIFValidation
from .importance import calculate_importance, importance_threshold
import json
from datetime import datetime

class SIFCompressor:
    def __init__(self, model_name: str = "qwen2.5-coder:7b", client=None):
        """
        Initialize compressor.
        
        Args:
            model_name: LLM to use for extraction
            client: Ada brain client (for LLM calls)
        """
        self.model_name = model_name
        self.client = client
        self.fact_counter = 0
    
    def compress(
        self,
        text: str,
        domain: str = "other",
        compression_tier: int = 2,
        query: Optional[str] = None
    ) -> SIFDocument:
        """
        Compress text to SIF.
        
        Args:
            text: Input text
            domain: Source domain
            compression_tier: 1=critical, 2=standard, 3=aggressive
            query: Optional query context
        
        Returns:
            SIFDocument
        """
        
        # Store original for hashing
        original_bytes = text.encode('utf-8')
        original_hash = hashlib.sha256(original_bytes).hexdigest()
        
        # Step 1: Extract summary
        print("Extracting summary...")
        summary_text = self._extract_summary(text)
        
        # Step 2: Extract entities
        print("Extracting entities...")
        entities_raw = self._extract_entities(text)
        
        # Step 3: Calculate entity importance
        entities = []
        threshold = importance_threshold(compression_tier)
        
        context = {
            'query': query or summary_text,
            'domain': domain
        }
        
        for entity in entities_raw:
            # Calculate importance
            entity_text = f"{entity['name']} {entity['description']}"
            importance = calculate_importance(entity_text, context)
            entity['importance'] = importance
            
            if importance >= threshold:
                entities.append(SIFEntity(**entity))
        
        print(f"Preserved {len(entities)} entities (threshold: {threshold:.2f})")
        
        # Step 4: Extract facts
        print("Extracting facts...")
        facts_raw = self._extract_facts(text)
        
        # Step 5: Calculate fact importance
        facts = []
        self.fact_counter = 0
        
        fact_frequencies = {}
        for fact in facts_raw:
            fact_id = fact.get('id', f'fact_{self.fact_counter}')
            fact['id'] = f'fact_{self.fact_counter}'
            self.fact_counter += 1
            
            importance = calculate_importance(fact['content'], context)
            fact['importance'] = importance
            
            fact_frequencies[fact['id']] = 1
            
            if importance >= threshold:
                facts.append(SIFFact(**fact))
        
        print(f"Preserved {len(facts)} facts (threshold: {threshold:.2f})")
        
        # Step 6: Extract relationships
        print("Extracting relationships...")
        relationships_raw = self._extract_relationships(text)
        
        entity_ids = {e.id for e in entities}
        relationships = []
        
        for rel in relationships_raw:
            if rel['entity_a'] in entity_ids and rel['entity_b'] in entity_ids:
                relationships.append(SIFRelationship(**rel))
        
        print(f"Preserved {len(relationships)} relationships")
        
        # Step 7: Calculate quality metrics
        print("Calculating metrics...")
        
        sif_json = json.dumps({
            'entities': [e.dict() for e in entities],
            'facts': [f.dict() for f in facts],
            'relationships': [r.dict() for r in relationships]
        }, separators=(',', ':'))
        
        compression_ratio = len(original_bytes) / len(sif_json.encode())
        
        # Step 8: Create SIF document
        sif = SIFDocument(
            metadata=SIFMetadata(
                version="1.0.0",
                timestamp=datetime.utcnow(),
                domain=domain,
                source_size_bytes=len(original_bytes),
                source_hash=original_hash
            ),
            summary={
                'text': summary_text,
                'keywords': self._extract_keywords(text, top_k=5),
                'theme': self._classify_theme(text)
            },
            entities=entities,
            relationships=relationships,
            facts=facts,
            validation=SIFValidation(
                is_valid=True,
                quality_score=self._calculate_quality_score(entities, facts),
                compression_ratio=compression_ratio
            )
        )
        
        # Calculate and store checksum
        sif.validation.checksum = sif.calculate_checksum()
        
        return sif
    
    def _extract_summary(self, text: str) -> str:
        """Extract 1-3 sentence summary"""
        # In production: Call LLM
        # For reference: Return first meaningful sentence
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        return '. '.join(sentences[:2]) + '.' if sentences else text[:100]
    
    def _extract_entities(self, text: str) -> List[dict]:
        """Extract entities from text"""
        # In production: Call LLM with structured output
        # For reference: Return mock entities
        return [
            {
                'id': 'entity_1',
                'type': 'concept',
                'name': 'Main Topic',
                'description': 'The primary subject of the text'
            }
        ]
    
    def _extract_facts(self, text: str) -> List[dict]:
        """Extract facts from text"""
        # In production: Call LLM with structured output
        facts = []
        
        # Simple heuristic: Sentences with verbs are facts
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        for i, sent in enumerate(sentences[:5]):  # First 5 sentences
            facts.append({
                'id': f'fact_{i}',
                'content': sent,
                'type': 'factual',
                'confidence': 0.8
            })
        
        return facts
    
    def _extract_relationships(self, text: str) -> List[dict]:
        """Extract relationships between entities"""
        # In production: Call LLM
        # For reference: Return empty list
        return []
    
    def _extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """Extract keywords"""
        # Simple heuristic: Most frequent words
        words = text.lower().split()
        word_freq = {}
        for w in words:
            w = w.strip('.,!?;:')
            if len(w) > 4:
                word_freq[w] = word_freq.get(w, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in top_words[:top_k]]
    
    def _classify_theme(self, text: str) -> str:
        """Classify document theme"""
        # Simple heuristic
        if 'function' in text.lower() or 'def ' in text:
            return 'code'
        elif 'once' in text.lower() or 'story' in text.lower():
            return 'narrative'
        else:
            return 'general'
    
    def _calculate_quality_score(self, entities: List, facts: List) -> float:
        """Calculate quality score"""
        # Simple metric: average importance of preserved items
        if not facts:
            return 0.5
        
        avg_importance = sum(f.importance for f in facts) / len(facts)
        return min(avg_importance, 1.0)
```

### 4. Decompressor

```python
# sif/decompressor.py

from .models import SIFDocument
from typing import Optional

class SIFDecompressor:
    def __init__(self):
        pass
    
    def decompress(
        self,
        sif: SIFDocument,
        style: str = "analytical",
        target_length: str = "medium"
    ) -> str:
        """
        Reconstruct narrative from SIF.
        
        Args:
            sif: SIFDocument
            style: "analytical", "narrative", "dialogue", or "summary"
            target_length: "short", "medium", or "full"
        
        Returns:
            Reconstructed text
        """
        
        # Start with summary
        narrative = sif.summary['text'] + "\n\n"
        
        # Add key facts (sorted by importance)
        sorted_facts = sorted(sif.facts, key=lambda f: f.importance, reverse=True)
        
        # Determine how many facts to include
        if target_length == "short":
            num_facts = len(sorted_facts) // 2
        elif target_length == "full":
            num_facts = len(sorted_facts)
        else:  # medium
            num_facts = int(len(sorted_facts) * 0.75)
        
        narrative += "Key facts:\n"
        for fact in sorted_facts[:num_facts]:
            narrative += f"- {fact.content}\n"
        
        # Add entities if requested
        if style in ["narrative", "full"]:
            narrative += "\nKey entities:\n"
            for entity in sorted(sif.entities, key=lambda e: e.importance, reverse=True):
                narrative += f"- {entity.name}: {entity.description}\n"
        
        return narrative
```

### 5. Validator

```python
# sif/validator.py

from .models import SIFDocument, SIFFact
from typing import List, Dict
import statistics

class SafetyReport:
    def __init__(self):
        self.warnings = []
        self.errors = []
    
    def add_warning(self, code: str, message: str):
        self.warnings.append({'code': code, 'message': message})
    
    def add_error(self, code: str, message: str):
        self.errors.append({'code': code, 'message': message})
    
    def is_safe(self) -> bool:
        return len(self.errors) == 0

def validate_sif(sif: SIFDocument) -> SafetyReport:
    """Validate SIF for safety and consistency"""
    
    report = SafetyReport()
    
    # Check 1: Low confidence facts
    low_confidence = [f for f in sif.facts if f.confidence < 0.50]
    if len(low_confidence) > len(sif.facts) * 0.20:
        report.add_warning(
            "HIGH_HALLUCINATION_RISK",
            f"{len(low_confidence)} facts below 50% confidence"
        )
    
    # Check 2: Facts without entities
    for fact in sif.facts:
        if not fact.supporting_entities:
            report.add_warning(
                "UNSUPPORTED_FACT",
                f"Fact '{fact.id}' has no supporting entities"
            )
    
    # Check 3: Importance distribution
    if sif.facts:
        importance_median = statistics.median(
            [f.importance for f in sif.facts]
        )
        if importance_median > 0.80:
            report.add_warning(
                "INFLATION_RISK",
                f"Median importance is {importance_median:.2f} (may be inflated)"
            )
    
    # Check 4: Broken relationships
    entity_ids = {e.id for e in sif.entities}
    for rel in sif.relationships:
        if rel.entity_a not in entity_ids:
            report.add_error(
                "BROKEN_RELATIONSHIP",
                f"Relationship references missing entity: {rel.entity_a}"
            )
        if rel.entity_b not in entity_ids:
            report.add_error(
                "BROKEN_RELATIONSHIP",
                f"Relationship references missing entity: {rel.entity_b}"
            )
    
    # Check 5: Integrity
    if sif.validation.checksum:
        if sif.calculate_checksum() != sif.validation.checksum:
            report.add_error(
                "INTEGRITY_FAILURE",
                "Checksum mismatch: document may have been modified"
            )
    
    return report
```

---

## Usage Examples

### Compress Text

```python
from sif.compressor import SIFCompressor

compressor = SIFCompressor()

text = open('document.txt').read()

sif = compressor.compress(
    text=text,
    domain="literature",
    compression_tier=2,  # Standard compression
    query="What happens in this story?"
)

# Save to file
sif.save_to_file('document.sif.json')

print(f"Compression ratio: {sif.validation.compression_ratio:.1f}x")
print(f"Quality score: {sif.validation.quality_score:.2f}")
```

### Decompress and Retrieve

```python
from sif.decompressor import SIFDecompressor

decompressor = SIFDecompressor()

sif = SIFDocument.load_from_file('document.sif.json')

narrative = decompressor.decompress(
    sif=sif,
    style="analytical",
    target_length="medium"
)

print(narrative)
```

### Validate Safety

```python
from sif.validator import validate_sif

report = validate_sif(sif)

if not report.is_safe():
    print(f"⚠️ {len(report.warnings)} warnings:")
    for w in report.warnings:
        print(f"  - {w['code']}: {w['message']}")
    
    if report.errors:
        print(f"❌ {len(report.errors)} errors:")
        for e in report.errors:
            print(f"  - {e['code']}: {e['message']}")

else:
    print("✅ SIF passed safety validation")
```

### Ingest into Ada Brain

```python
from sif.models import SIFDocument
from ada_client import AdaClient

client = AdaClient(base_url='http://localhost:8000')
sif = SIFDocument.load_from_file('document.sif.json')

# Ingest high-importance facts into memory
for fact in sif.facts:
    if fact.importance >= 0.60:
        client.add_memory(
            content=fact.content,
            importance=fact.importance,
            tags=fact.tags,
            metadata={'source': 'sif:v1.0'}
        )

# Ingest entities
for entity in sif.entities:
    if entity.importance >= 0.60:
        client.add_memory(
            content=f"{entity.name}: {entity.description}",
            importance=entity.importance,
            tags=['entity', entity.type],
            metadata={'entity_id': entity.id}
        )
```

---

## Production Deployment

For production use:

1. **Use real LLM calls** for extraction instead of heuristics
2. **Add caching** of embeddings
3. **Implement async** compression for large documents
4. **Add monitoring** of compression quality metrics
5. **Version the importance algorithm** independently from SIF version

---

This reference implementation provides a working foundation for SIF. Extend and modify as needed for your use case.

