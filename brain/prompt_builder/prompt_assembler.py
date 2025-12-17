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
# @ai-dependencies: context_retriever, section_builder, specialists, context_habituation
# @ai-related: brain.prompt_builder
# @ai-enhanced: v2.1 - Habituation support for repeated context

import logging
from typing import Any

from brain.prompt_builder.context_retriever import ContextRetriever
from brain.prompt_builder.section_builder import SectionBuilder
from brain.context_cache import MultiTimescaleCache
from brain.token_monitor import TokenBudgetMonitor
from brain.context_habituation import ContextHabituation
from brain.attention_spotlight import AttentionalSpotlight
from brain.config import config

logger = logging.getLogger(__name__)


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
        
        # Initialize token monitor (v2.0 Phase 2)
        if config.TOKEN_MONITORING_ENABLED:
            self.token_monitor = TokenBudgetMonitor(
                max_tokens=config.LLM_MAX_CONTEXT,
                warning_threshold=config.TOKEN_WARNING_THRESHOLD
            )
        else:
            self.token_monitor = None
        
        # Initialize context habituation (Biomimetic Phase 1)
        if config.CONTEXT_HABITUATION_ENABLED:
            self.habituation = ContextHabituation(
                threshold=config.CONTEXT_HABITUATION_THRESHOLD,
                habituated_weight=config.CONTEXT_HABITUATION_WEIGHT,
                decay_hours=config.CONTEXT_HABITUATION_DECAY_HOURS
            )
            logger.info(f"Context habituation enabled (threshold={config.CONTEXT_HABITUATION_THRESHOLD})")
        else:
            self.habituation = None
        
        # Initialize attention spotlight (Biomimetic Phase 2)
        if config.ATTENTION_SPOTLIGHT_ENABLED:
            self.spotlight = AttentionalSpotlight(
                spotlight_budget=config.ATTENTION_SPOTLIGHT_BUDGET,
                periphery_budget=config.ATTENTION_PERIPHERY_BUDGET,
                spotlight_size=config.ATTENTION_SPOTLIGHT_SIZE
            )
            logger.info(f"Attention spotlight enabled (size={config.ATTENTION_SPOTLIGHT_SIZE})")
        else:
            self.spotlight = None
    
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
                if self.token_monitor:
                    self.token_monitor.track("system_notices", notice_section)
        
        # Persona (who Ada is) - with habituation
        persona_section = self.builder.format_persona(persona)
        habituation_weight = 1.0
        
        if self.habituation:
            habituation_weight = self.habituation.get_weight("persona", persona_section)
            if habituation_weight < 1.0:
                logger.info(f"Persona habituated: weight={habituation_weight:.2f}")
        
        # Include if weight > 0
        if habituation_weight > 0:
            sections.append(persona_section)
            if self.token_monitor:
                self.token_monitor.track("persona", persona_section, 
                                       metadata={'habituation_weight': habituation_weight})
        
        # Specialist results (tool outputs - high priority)
        if specialist_results:
            specialist_section = self.builder.format_specialist_results(specialist_results)
            if specialist_section:
                sections.append(specialist_section)
                if self.token_monitor:
                    self.token_monitor.track("specialists", specialist_section)
        
        # Memories (user-specific context) - with attention spotlight
        if memories:
            # Apply attention spotlight if enabled
            if self.spotlight:
                # Convert (text, metadata) tuples to dicts for spotlight
                memory_dicts = [
                    {
                        'content': text,
                        'metadata': metadata,
                        'distance': metadata.get('distance', 0.5)
                    }
                    for text, metadata in memories
                ]
                
                distribution = self.spotlight.apply_attention(memory_dicts)
                stats = self.spotlight.get_stats(distribution)
                
                logger.info(
                    f"Attention: {stats['spotlight_count']} spotlight, "
                    f"{stats['periphery_count']} periphery "
                    f"({stats['total_tokens']} tokens)"
                )
                
                # Format with attention structure
                memory_section = distribution.format_context()
            else:
                # No spotlight - format normally
                memory_texts = [text for text, _ in memories]
                memory_section = self.builder.format_memories(memory_texts)
            
            sections.append(memory_section)
            if self.token_monitor:
                self.token_monitor.track("memories", memory_section)
        
        # FAQs (reference information) - with habituation
        if faqs:
            faq_section = self.builder.format_faqs(faqs)
            habituation_weight = 1.0
            
            if self.habituation:
                habituation_weight = self.habituation.get_weight("faqs", faq_section)
                if habituation_weight < 1.0:
                    logger.info(f"FAQs habituated: weight={habituation_weight:.2f}")
            
            # Include if weight > 0
            if habituation_weight > 0:
                sections.append(faq_section)
                if self.token_monitor:
                    self.token_monitor.track("faqs", faq_section,
                                           metadata={'habituation_weight': habituation_weight})
        
        # Conversation history (recent turns)
        if turns:
            history_section = self.builder.format_conversation_history(turns)
            sections.append(history_section)
            if self.token_monitor:
                self.token_monitor.track("conversation_history", history_section)
        
        # 4. Assemble final prompt
        context = "\n\n".join(sections)
        
        # User message comes last as the instruction
        user_section = f"# Current Request\n\nUser: {user_message}"
        prompt = f"{context}\n\n{user_section}"
        
        # Track user message
        if self.token_monitor:
            self.token_monitor.track("user_message", user_section)
        
        # 5. Log token usage breakdown (v2.0 Phase 2 observability)
        if self.token_monitor:
            breakdown = self.token_monitor.get_breakdown()
            logger.info(
                f"Token usage: {breakdown.total_tokens}/{config.LLM_MAX_CONTEXT} "
                f"({breakdown.percentage_used:.1f}%)"
            )
            
            # Log top components
            top_components = self.token_monitor.get_top_components(n=5)
            if top_components:
                components_str = ", ".join(
                    f"{name}={tokens.tokens}" for name, tokens in top_components
                )
                logger.debug(f"Top token consumers: {components_str}")
            
            # Warn if approaching limit
            if breakdown.is_warning:
                logger.warning(
                    f"Token budget at {breakdown.percentage_used:.1f}% "
                    f"({breakdown.total_tokens}/{config.LLM_MAX_CONTEXT} tokens). "
                    "Consider enabling context optimization."
                )
        
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
