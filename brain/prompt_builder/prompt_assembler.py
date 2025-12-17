"""PromptAssembler - orchestrates complete prompt building.

This is the top-level coordinator that ties together:
- ContextRetriever (fetch RAG data)
- SectionBuilder (format sections)
- Specialist coordination
- Final prompt assembly

The assembler ensures correct ordering, handles optional sections,
and produces the final prompt string ready for the LLM.
"""
# @ai-indexable: core-component
# @ai-purpose: Orchestrate prompt building from all components
# @ai-dependencies: context_retriever, section_builder, specialists
# @ai-related: brain.prompt_builder

from typing import Any

from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.section_builder import SectionBuilder
from brain.context_cache import MultiTimescaleCache
from brain.config import config


class PromptAssembler:
    """Orchestrates prompt building from all components.
    
    This is the main entry point for prompt construction. It:
    1. Retrieves context via ContextRetriever
    2. Formats sections via SectionBuilder
    3. Coordinates specialist activation
    4. Assembles final prompt in priority order
    
    Section Priority (high to low):
    1. System notices (urgent information)
    2. Persona (who Ada is)
    3. Specialist results (tool outputs)
    4. Memories (user context)
    5. FAQs (reference information)
    6. Conversation history (recent turns)
    7. User message (current instruction)
    """
    
    def __init__(
        self,
        retriever: ContextRetriever | None = None,
        builder: SectionBuilder | None = None,
        cache: MultiTimescaleCache | None = None
    ):
        """Initialize with dependencies.
        
        Args:
            retriever: ContextRetriever instance (creates default if None)
            builder: SectionBuilder instance (creates default if None)
            cache: Cache instance (creates default if None)
        """
        # Initialize cache first
        self.cache = cache or MultiTimescaleCache(config)
        
        # Pass cache to retriever
        self.retriever = retriever or ContextRetriever(cache=self.cache)
        self.builder = builder or SectionBuilder()
    
    def build_prompt(
        self,
        user_message: str,
        conversation_id: str,
        specialists: list[Any] | None = None,
        notices: list[dict[str, Any]] | None = None,
        request_context: dict[str, Any] | None = None
    ) -> str:
        """Build complete prompt from all components.
        
        Args:
            user_message: Current user message/query
            conversation_id: Conversation identifier for history retrieval
            specialists: List of specialist instances to check for activation
            notices: System notices to include
            request_context: Additional context for specialist activation
            
        Returns:
            Complete formatted prompt string
        """
        specialists = specialists or []
        notices = notices or []
        request_context = request_context or {}
        
        # 1. Retrieve RAG context
        persona = self.retriever.get_persona()
        memories = self.retriever.get_memories(query=user_message, k=5)
        faqs = self.retriever.get_faqs(query=user_message, k=3)
        turns = self.retriever.get_turns(conversation_id=conversation_id, k=10)
        
        # 2. Activate specialists
        specialist_results = self._activate_specialists(
            specialists,
            user_message,
            request_context
        )
        
        # 3. Format sections
        sections = []
        
        # System notices (highest priority - urgent info)
        if notices:
            notice_section = self.builder.format_notices(notices)
            if notice_section:
                sections.append(notice_section)
        
        # Persona (who Ada is)
        sections.append(self.builder.format_persona(persona))
        
        # Specialist results (tool outputs - high priority)
        if specialist_results:
            specialist_section = self.builder.format_specialist_results(specialist_results)
            if specialist_section:
                sections.append(specialist_section)
        
        # Memories (user-specific context)
        if memories:
            sections.append(self.builder.format_memories(memories))
        
        # FAQs (reference information)
        if faqs:
            sections.append(self.builder.format_faqs(faqs))
        
        # Conversation history (recent turns)
        if turns:
            sections.append(self.builder.format_conversation_history(turns))
        
        # 4. Assemble final prompt
        context = "\n\n".join(sections)
        
        # User message comes last as the instruction
        prompt = f"{context}\n\n# Current Request\n\nUser: {user_message}"
        
        return prompt
    
    def _activate_specialists(
        self,
        specialists: list[Any],
        user_message: str,
        request_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Activate applicable specialists and collect results.
        
        Args:
            specialists: List of specialist instances
            user_message: User's message
            request_context: Additional context
            
        Returns:
            List of specialist results (dicts with specialist name and result)
        """
        results = []
        
        for specialist in specialists:
            # Build context for specialist decision
            context = {
                "user_message": user_message,
                **request_context
            }
            
            # Check if specialist should activate
            if specialist.should_activate(context):
                try:
                    # Process and collect result
                    result = specialist.process(context)
                    if result:
                        results.append({
                            "specialist": specialist.capability.name,
                            "result": result
                        })
                except Exception as e:
                    # Log error but don't crash prompt building
                    print(f"Specialist {specialist.capability.name} failed: {e}")
        
        return results
