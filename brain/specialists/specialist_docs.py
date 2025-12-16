"""
Specialist Documentation System - Auto-generate RAG FAQ entries from specialist capabilities.

This module syncs specialist metadata into the FAQ system, allowing:
- Dynamic specialist discovery documentation
- Context-aware specialist suggestions via RAG retrieval
- Automatic updates when specialists are added/removed
"""
import logging
from typing import Optional
from brain.rag_store import RagStore
from brain.specialists import get_registry, list_specialists

logger = logging.getLogger(__name__)


def sync_specialist_docs_to_faq(rag_store: RagStore) -> int:
    """
    Generate FAQ entries from all registered specialists.
    
    Creates searchable documentation for:
    - What specialists are available
    - When to use each specialist
    - Syntax for invoking specialists
    - Example usage patterns
    
    Args:
        rag_store: RAG storage instance for FAQ insertion
        
    Returns:
        Number of FAQ entries created/updated
    """
    if rag_store is None:
        logger.warning("[SPECIALISTS] Cannot sync docs - RAG store unavailable")
        return 0
    
    try:
        # Remove existing specialist documentation
        try:
            rag_store.col.delete(where={"type": "faq", "topic": "specialists"})
        except Exception:
            pass
        
        specialists = list_specialists()
        count = 0
        
        # Overview FAQ
        specialist_list = ", ".join([
            f"{s.capability.context_icon} {s.capability.name}"
            for s in specialists
        ])
        overview_text = f"""Q: What specialist capabilities are available?
A: Ada has {len(specialists)} specialist capabilities integrated: {specialist_list}. These can be invoked mid-conversation using SPECIALIST_REQUEST[name:{{params}}] syntax to augment my responses with specialized processing."""
        
        rag_store.upsert_doc(
            overview_text,
            type="faq",
            scope="global",
            topic="specialists",
            source="system",
            version="auto"
        )
        count += 1
        
        # Individual specialist FAQs
        for specialist in specialists:
            cap = specialist.capability
            
            # Capability FAQ
            cap_text = f"""Q: What does the {cap.name} specialist do?
A: {cap.description} (Priority: {cap.context_priority.name}, Icon: {cap.context_icon})"""
            
            rag_store.upsert_doc(
                cap_text,
                type="faq",
                scope="global",
                topic="specialists",
                source="system",
                version="auto",
                extra_meta={"specialist_name": cap.name}
            )
            count += 1
            
            # Syntax FAQ
            syntax_text = f"""Q: How do I invoke the {cap.name} specialist?
A: Use the syntax SPECIALIST_REQUEST[{cap.name}:{{}}] in your response. I will detect this pattern, pause generation, execute the specialist, and resume with enriched context."""
            
            rag_store.upsert_doc(
                syntax_text,
                type="faq",
                scope="global",
                topic="specialists",
                source="system",
                version="auto",
                extra_meta={"specialist_name": cap.name}
            )
            count += 1
            
            # Trigger pattern FAQ (when to use this specialist)
            trigger_patterns = {
                "web_search": "Use web_search when users ask about current/recent events, today's weather, latest news, real-time data (stocks/sports), or anything after October 2023. Trigger words: 'today', 'now', 'current', 'latest', 'recent'. Example: 'What's the weather today?' → SPECIALIST_REQUEST[web_search:{\"query\":\"weather today\"}]",
                "ocr": "OCR auto-activates on image uploads with text. Request manually when user wants text extraction from images they've shared. Trigger: 'read the text', 'what does it say', 'extract text'.",
                "vision": "Use vision for image analysis beyond text - diagrams, charts, visual content, object detection. Trigger: 'what's in this image', 'analyze this diagram', 'describe what you see'.",
                "media": "Media specialist auto-activates when ListenBrainz data is present. Shows what user is currently listening to."
            }
            
            if cap.name in trigger_patterns:
                trigger_text = f"""Q: When should I use the {cap.name} specialist?
A: {trigger_patterns[cap.name]}"""
                
                rag_store.upsert_doc(
                    trigger_text,
                    type="faq",
                    scope="global",
                    topic="specialists",
                    source="system",
                    version="auto",
                    extra_meta={"specialist_name": cap.name}
                )
                count += 1
        
        # Usage pattern FAQs
        usage_patterns = [
            {
                "q": "When should I use specialist capabilities?",
                "a": "Use specialists when you need: image analysis (OCR/vision), real-time external data (media/weather), or specialized processing beyond my core LLM capabilities. I can invoke them mid-conversation by emitting the SPECIALIST_REQUEST syntax."
            },
            {
                "q": "Can I chain multiple specialists?",
                "a": "Yes! I can invoke up to 5 specialists per conversation turn. Each specialist result enriches the context for subsequent processing. The system uses pause/resume to properly integrate results."
            },
            {
                "q": "What happens when a specialist is invoked?",
                "a": "When I emit SPECIALIST_REQUEST[name:params], generation pauses. The specialist executes with the provided parameters, then I resume with the result injected into my context. This allows me to reason about specialist outputs properly."
            }
        ]
        
        for pattern in usage_patterns:
            pattern_text = f"Q: {pattern['q']}\nA: {pattern['a']}"
            rag_store.upsert_doc(
                pattern_text,
                type="faq",
                scope="global",
                topic="specialists",
                source="system",
                version="auto"
            )
            count += 1
        
        logger.info(f"[SPECIALISTS] Synced {count} FAQ entries for {len(specialists)} specialists")
        return count
        
    except Exception as e:
        logger.error(f"[SPECIALISTS] Failed to sync docs to FAQ: {e}")
        return 0


def get_relevant_specialist_docs(query: str, rag_store: Optional[RagStore], k: int = 2) -> str:
    """
    Retrieve specialist documentation relevant to the user's query.
    
    This is called during prompt building to inject context-aware
    specialist guidance based on what the user is asking for.
    
    Args:
        query: User's question/prompt
        rag_store: RAG storage instance
        k: Number of FAQ entries to retrieve
        
    Returns:
        Formatted specialist documentation string, or empty if none relevant
    """
    if rag_store is None:
        return ""
    
    try:
        # Retrieve FAQs specifically about specialists
        faq_hits = rag_store.col.query(
            query_texts=[query],
            n_results=k,
            where={"$and": [{"type": "faq"}, {"topic": "specialists"}]}
        )
        
        docs = faq_hits.get("documents", [[]])[0]
        if not docs:
            return ""
        
        # Format for prompt injection
        lines = [f"📚 Specialist Capabilities Reference:"]
        for doc in docs:
            # Extract just the answer portion for brevity
            if "A: " in doc:
                answer = doc.split("A: ", 1)[1]
                lines.append(f"  • {answer}")
        
        return "\n".join(lines) if len(lines) > 1 else ""
        
    except Exception as e:
        logger.error(f"[SPECIALISTS] Failed to retrieve docs: {e}")
        return ""
