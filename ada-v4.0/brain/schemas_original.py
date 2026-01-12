"""
Data model schemas for Ada's vector database (Chroma).

All documents stored in Chroma follow these schemas. Each document has:
- An ID (UUID)
- Text content (the actual document)
- Embeddings (768-dim vector from nomic-embed-text)
- Metadata (structured data about the document)

Document Types:
- persona: Identity and behavior guidelines
- faq: Knowledge base entries and tool documentation
- memory: Long-term facts and context
- turn: Conversation history (user/assistant pairs)
- summary: Conversation summaries

This module provides:
1. Pydantic models for each metadata schema
2. Validation functions
3. Schema export for documentation
4. Type hints for the codebase
"""

from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import time


# ============= Latency & Performance =============

class LatencyBreakdown(BaseModel):
    """Detailed timing breakdown for a chat request (milliseconds)."""
    
    python_overhead_ms: float = Field(
        description="Time spent in Python code (context retrieval, prompt building, tool activation)"
    )
    llm_inference_ms: float = Field(
        description="Time spent waiting for LLM to generate response (the neural net)"
    )
    total_ms: float = Field(
        description="Total request time (sum of all components)"
    )
    llm_percentage: float = Field(
        description="Percentage of total time spent in LLM inference (0-100)"
    )
    
    tools_activated: int = Field(
        default=0,
        description="Number of tools invoked during this request"
    )
    
    context_retrieved: bool = Field(
        default=False,
        description="Whether RAG context was retrieved"
    )
    
    cache_hit_rate: Optional[float] = Field(
        default=None,
        description="Hit rate for context cache (0-1) if caching is enabled"
    )


# ============= Document Types =============

class DocumentType(str, Enum):
    """All valid document types in the vector database."""
    PERSONA = "persona"
    FAQ = "faq"
    MEMORY = "memory"
    TURN = "turn"
    SUMMARY = "summary"


class ScopeType(str, Enum):
    """Scope types for document access control."""
    GLOBAL = "global"  # Available to all conversations
    ENTITY = "entity"  # Scoped to specific entity (format: "entity:project-name")


# ============= Base Metadata Schema =============

class BaseMetadata(BaseModel):
    """
    Base metadata fields present in all documents.
    
    All documents in Chroma have at minimum these fields.
    """
    
    type: DocumentType = Field(
        description="Document type (persona, faq, memory, turn, summary)"
    )
    
    timestamp: str = Field(
        description="ISO 8601 UTC timestamp when document was created/updated",
        examples=["2025-12-16T06:00:00+00:00"]
    )
    
    source: str = Field(
        default="system",
        description="Origin of the document",
        examples=["chat", "kb", "system", "import"]
    )
    
    scope: str = Field(
        default="global",
        description="Access scope (global or entity:name)",
        examples=["global", "entity:project-alpha"]
    )


# ============= Persona Metadata =============

class PersonaMetadata(BaseMetadata):
    """
    Metadata for persona documents (identity and behavior).
    
    Persona documents define Ada's identity, tone, and behavioral guidelines.
    Usually loaded from persona.md on startup.
    
    Example Query: "What is my tone?" retrieves persona context
    """
    
    type: Literal[DocumentType.PERSONA] = DocumentType.PERSONA
    
    version: str = Field(
        description="Version timestamp for persona updates",
        examples=["2025-12-14T20:12:53.986582Z"]
    )
    
    topic: Optional[str] = Field(
        default=None,
        description="Topic or section of persona (if chunked)",
        examples=["tone", "safety", "reasoning"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "persona",
                "timestamp": "2025-12-16T06:00:00+00:00",
                "source": "kb",
                "scope": "global",
                "version": "2025-12-14T20:12:53.986582Z",
                "topic": "tone"
            }
        }


# ============= FAQ Metadata =============

class FAQMetadata(BaseMetadata):
    """
    Metadata for FAQ documents (knowledge base entries).
    
    FAQ documents contain question-answer pairs, tool documentation,
    and general knowledge. Retrieved via semantic similarity for relevant context.
    
    Example Query: "How do I invoke a tool?" retrieves FAQ entries
    """
    
    type: Literal[DocumentType.FAQ] = DocumentType.FAQ
    
    topic: Optional[str] = Field(
        default=None,
        description="Topic or category for organization",
        examples=["tools", "api", "configuration", "troubleshooting"]
    )
    
    # Tool-specific fields (when FAQ is tool documentation)
    tool_name: Optional[str] = Field(
        default=None,
        description="Name of tool this doc describes",
        examples=["web_search", "ocr", "vision", "media"],
        json_schema_extra={"alias": "_tool_name"}
    )
    
    version: Optional[str] = Field(
        default="auto",
        description="Version of the FAQ entry",
        examples=["auto", "2025-12-16T06:00:00+00:00"],
        json_schema_extra={"alias": "_version"}
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "faq",
                    "timestamp": "2025-12-16T06:00:00+00:00",
                    "source": "system",
                    "scope": "global",
                    "topic": "tools",
                    "tool_name": "web_search",
                    "version": "auto"
                },
                {
                    "type": "faq",
                    "timestamp": "2025-12-16T06:00:00+00:00",
                    "source": "kb",
                    "scope": "global",
                    "topic": "api"
                }
            ]
        }


# ============= Memory Metadata =============

class MemoryMetadata(BaseMetadata):
    """
    Metadata for memory documents (long-term facts).
    
    Memories are persistent facts that span conversations. They can be scoped
    globally or to specific entities (projects, topics). Retrieved via semantic
    similarity weighted by importance and recency.
    
    Example: "Remember that luna prefers Python over JavaScript" creates a memory
    """
    
    type: Literal[DocumentType.MEMORY] = DocumentType.MEMORY
    
    conversation_id: Optional[str] = Field(
        default=None,
        description="Original conversation where memory was created",
        examples=["conv-123e4567-e89b-12d3-a456-426614174000"]
    )
    
    importance: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Importance level (1=low, 5=critical). Affects retrieval ranking."
    )
    
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags for categorization and filtering",
        examples=[["python", "preferences"], ["project-alpha", "deadline"]]
    )
    
    entity: Optional[str] = Field(
        default=None,
        description="Entity this memory pertains to (extracted from scope if present)",
        examples=["project-alpha", "team-beta"]
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "memory",
                    "timestamp": "2025-12-16T06:00:00+00:00",
                    "source": "chat",
                    "scope": "global",
                    "importance": 4,
                    "tags": ["preferences", "programming"]
                },
                {
                    "type": "memory",
                    "timestamp": "2025-12-16T06:00:00+00:00",
                    "source": "chat",
                    "scope": "entity:project-alpha",
                    "entity": "project-alpha",
                    "importance": 5,
                    "tags": ["deadline", "critical"],
                    "conversation_id": "conv-abc123"
                }
            ]
        }


# ============= Turn Metadata =============

class TurnMetadata(BaseMetadata):
    """
    Metadata for conversation turn documents.
    
    Each turn consists of two documents: user message and assistant response.
    Turns are scoped to conversations and retrieved for recent context.
    Includes recency-based ranking for temporal awareness.
    
    Example Query: Recent messages in conversation retrieve turns
    """
    
    type: Literal[DocumentType.TURN] = DocumentType.TURN
    
    conversation_id: str = Field(
        description="Conversation this turn belongs to",
        examples=["conv-123e4567-e89b-12d3-a456-426614174000"]
    )
    
    role: Literal["user", "assistant"] = Field(
        description="Speaker role (user or assistant)"
    )
    
    turn_index: Optional[int] = Field(
        default=None,
        description="Sequential turn number within conversation",
        examples=[1, 2, 3]
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "turn",
                    "timestamp": "2025-12-16T06:00:00+00:00",
                    "source": "chat",
                    "scope": "global",
                    "conversation_id": "conv-abc123",
                    "role": "user",
                    "turn_index": 1
                },
                {
                    "type": "turn",
                    "timestamp": "2025-12-16T06:00:01+00:00",
                    "source": "chat",
                    "scope": "global",
                    "conversation_id": "conv-abc123",
                    "role": "assistant",
                    "turn_index": 1
                }
            ]
        }


# ============= Summary Metadata =============

class SummaryMetadata(BaseMetadata):
    """
    Metadata for conversation summary documents.
    
    Summaries compress multiple conversation turns into key points.
    Generated periodically (every N turns) to maintain context efficiency.
    Retrieved for high-level conversation history.
    
    Example: After 8 turns, Ada generates a summary of the discussion
    """
    
    type: Literal[DocumentType.SUMMARY] = DocumentType.SUMMARY
    
    conversation_id: str = Field(
        description="Conversation this summary belongs to",
        examples=["conv-123e4567-e89b-12d3-a456-426614174000"]
    )
    
    turn_range: Optional[str] = Field(
        default=None,
        description="Range of turns covered by this summary",
        examples=["1-8", "9-16"]
    )
    
    summary_index: Optional[int] = Field(
        default=None,
        description="Sequential summary number within conversation",
        examples=[1, 2, 3]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "summary",
                "timestamp": "2025-12-16T06:00:00+00:00",
                "source": "system",
                "scope": "global",
                "conversation_id": "conv-abc123",
                "turn_range": "1-8",
                "summary_index": 1
            }
        }


# ============= Complete Document Schema =============

class ChromaDocument(BaseModel):
    """
    Complete document schema including ID, text, and metadata.
    
    This represents a full document as stored in Chroma, including
    the vector embedding (not shown here as it's computed automatically).
    """
    
    id: str = Field(
        description="Unique document ID (UUID)",
        examples=["doc-123e4567-e89b-12d3-a456-426614174000"]
    )
    
    document: str = Field(
        description="The actual text content of the document",
        examples=["Q: How do I use the web search tool?\nA: Use TOOL_USE[web_search:{\"query\":\"your search\"}]"]
    )
    
    metadata: BaseMetadata = Field(
        description="Structured metadata about the document"
    )
    
    # Note: embeddings are not included here as they're computed automatically
    # embeddings: List[float] = Field(description="768-dimensional vector from nomic-embed-text")


# ============= Schema Export Functions =============

def get_all_schemas() -> Dict[str, Dict[str, Any]]:
    """
    Export all metadata schemas as JSON Schema.
    
    Returns a dictionary mapping document types to their JSON Schema definitions.
    Useful for documentation generation and API schema endpoints.
    """
    return {
        "persona": PersonaMetadata.model_json_schema(),
        "faq": FAQMetadata.model_json_schema(),
        "memory": MemoryMetadata.model_json_schema(),
        "turn": TurnMetadata.model_json_schema(),
        "summary": SummaryMetadata.model_json_schema(),
    }


def get_schema_by_type(doc_type: str) -> Dict[str, Any]:
    """Get JSON Schema for a specific document type."""
    schemas = get_all_schemas()
    if doc_type not in schemas:
        raise ValueError(f"Unknown document type: {doc_type}. Valid types: {list(schemas.keys())}")
    return schemas[doc_type]


def validate_metadata(doc_type: str, metadata: Dict[str, Any]) -> BaseMetadata:
    """
    Validate metadata against the schema for the given document type.
    
    Args:
        doc_type: One of "persona", "faq", "memory", "turn", "summary"
        metadata: Dictionary of metadata fields
    
    Returns:
        Validated metadata model instance
    
    Raises:
        ValidationError: If metadata doesn't match schema
    
    Example:
        >>> meta = {"type": "memory", "timestamp": "2025-12-16T06:00:00+00:00", "importance": 4}
        >>> validated = validate_metadata("memory", meta)
    """
    type_to_model = {
        "persona": PersonaMetadata,
        "faq": FAQMetadata,
        "memory": MemoryMetadata,
        "turn": TurnMetadata,
        "summary": SummaryMetadata,
    }
    
    model_class = type_to_model.get(doc_type)
    if not model_class:
        raise ValueError(f"Unknown document type: {doc_type}")
    
    return model_class(**metadata)


# ============= Statistics and Introspection =============

def get_metadata_fields_by_type() -> Dict[str, List[str]]:
    """
    Get list of metadata fields for each document type.
    
    Useful for understanding what fields are available for filtering and querying.
    """
    return {
        "persona": list(PersonaMetadata.model_fields.keys()),
        "faq": list(FAQMetadata.model_fields.keys()),
        "memory": list(MemoryMetadata.model_fields.keys()),
        "turn": list(TurnMetadata.model_fields.keys()),
        "summary": list(SummaryMetadata.model_fields.keys()),
    }


def get_required_fields_by_type() -> Dict[str, List[str]]:
    """Get required (non-optional) fields for each document type."""
    result = {}
    for doc_type, model_class in [
        ("persona", PersonaMetadata),
        ("faq", FAQMetadata),
        ("memory", MemoryMetadata),
        ("turn", TurnMetadata),
        ("summary", SummaryMetadata),
    ]:
        required = [
            field_name
            for field_name, field_info in model_class.model_fields.items()
            if field_info.is_required()
        ]
        result[doc_type] = required
    
    return result
