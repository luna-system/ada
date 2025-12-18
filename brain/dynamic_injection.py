"""Dynamic context injection - load additional context mid-generation.

Based on biological predictive processing: when prediction errors occur,
the brain fetches additional context to resolve uncertainty. This happens
dynamically during processing, not just at the start.

For Ada: When the LLM shows uncertainty (prediction error), dynamically
fetch and inject additional context into the ongoing generation stream.

This is the "wild" part of Phase 3 - requires careful orchestration!

@ai-indexable: biomimetic-phase3
@ai-purpose: Dynamically inject additional context when LLM needs it
@ai-dependencies: brain/prediction_error.py, brain/context_priming.py, brain/rag_store.py
@ai-related: brain/llm.py, brain/prompt_builder/prompt_assembler.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, AsyncIterator, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class InjectionStrategy(Enum):
    """How to inject additional context into stream."""
    
    INLINE = "inline"  # Inject as text in the stream
    SYSTEM = "system"  # Add to system context (restart generation)
    HYBRID = "hybrid"  # Try inline first, restart if needed


@dataclass
class InjectionPoint:
    """A point in the stream where context can be injected."""
    
    stream_position: int
    """Character position in generated stream"""
    
    trigger_error: Any  # PredictionError
    """The prediction error that triggered injection"""
    
    injected_context: str
    """The context that was injected"""
    
    injection_strategy: InjectionStrategy
    """How the context was injected"""
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When injection occurred"""
    
    success: bool = True
    """Whether injection was successful"""


@dataclass
class DynamicContext:
    """Additional context fetched dynamically."""
    
    content: str
    """The context content"""
    
    source: str
    """Where this context came from (e.g., 'memory', 'specialist', 'priming')"""
    
    relevance_score: float
    """How relevant this context is (0.0-1.0)"""
    
    priority: int
    """Injection priority (higher = inject first)"""
    
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When this context was fetched"""


class DynamicContextInjector:
    """Dynamically inject context into ongoing LLM generation.
    
    Monitors streaming LLM output for prediction errors and injects
    additional context when needed - biological predictive processing!
    """
    
    def __init__(
        self,
        context_fetcher: Optional[Callable[[List[str]], List[DynamicContext]]] = None,
        injection_strategy: InjectionStrategy = InjectionStrategy.INLINE,
        max_injections: int = 3,
        enabled: bool = True
    ):
        """Initialize dynamic context injector.
        
        Args:
            context_fetcher: Function to fetch context given topics
            injection_strategy: How to inject context
            max_injections: Maximum injections per response
            enabled: Whether injection is enabled
        """
        self.context_fetcher = context_fetcher
        self.injection_strategy = injection_strategy
        self.max_injections = max_injections
        self.enabled = enabled
        
        # State tracking
        self.injection_points: List[InjectionPoint] = []
        self.injections_count = 0
    
    def should_inject(self, prediction_error: Any) -> bool:  # PredictionError
        """Determine if context should be injected for this error.
        
        Args:
            prediction_error: The detected prediction error
        
        Returns:
            True if injection should happen
        """
        if not self.enabled:
            return False
        
        # Check injection limit
        if self.injections_count >= self.max_injections:
            logger.info(f"Max injections ({self.max_injections}) reached, skipping")
            return False
        
        # Check if immediate action required
        if prediction_error.requires_immediate_action:
            return True
        
        # Check confidence threshold
        if prediction_error.confidence >= 0.8:
            return True
        
        return False
    
    def fetch_context(self, topics: List[str]) -> List[DynamicContext]:
        """Fetch additional context for given topics.
        
        Args:
            topics: Topics that need additional context
        
        Returns:
            List of dynamic context items
        """
        if not self.context_fetcher:
            logger.warning("No context fetcher configured, returning empty")
            return []
        
        try:
            contexts = self.context_fetcher(topics)
            logger.info(f"Fetched {len(contexts)} context items for topics: {topics}")
            return contexts
        except Exception as e:
            logger.error(f"Error fetching context: {e}")
            return []
    
    def format_injection(self, contexts: List[DynamicContext]) -> str:
        """Format contexts for injection into stream.
        
        Args:
            contexts: Contexts to inject
        
        Returns:
            Formatted injection text
        """
        if not contexts:
            return ""
        
        # Sort by priority
        sorted_contexts = sorted(contexts, key=lambda c: c.priority, reverse=True)
        
        # Format as inline context
        if self.injection_strategy == InjectionStrategy.INLINE:
            parts = []
            for ctx in sorted_contexts:
                parts.append(f"[Context: {ctx.source}] {ctx.content}")
            
            injection = "\n\n" + "\n".join(parts) + "\n\n"
            return injection
        
        # For system injection, just concatenate
        return "\n".join(ctx.content for ctx in sorted_contexts)
    
    def inject_context(
        self,
        prediction_error: Any,  # PredictionError
        stream_position: int
    ) -> Optional[str]:
        """Inject context for a prediction error.
        
        Args:
            prediction_error: The error that triggered injection
            stream_position: Current position in stream
        
        Returns:
            Formatted context to inject, or None if no injection
        """
        if not self.should_inject(prediction_error):
            return None
        
        # Fetch context for suggested topics
        topics = prediction_error.suggested_topics
        contexts = self.fetch_context(topics)
        
        if not contexts:
            logger.warning(f"No context fetched for topics: {topics}")
            return None
        
        # Format injection
        injection_text = self.format_injection(contexts)
        
        # Record injection point
        injection_point = InjectionPoint(
            stream_position=stream_position,
            trigger_error=prediction_error,
            injected_context=injection_text,
            injection_strategy=self.injection_strategy
        )
        self.injection_points.append(injection_point)
        self.injections_count += 1
        
        logger.info(
            f"Injecting context at position {stream_position} "
            f"({len(contexts)} items, {len(injection_text)} chars)"
        )
        
        return injection_text
    
    async def process_stream_with_injection(
        self,
        original_stream: AsyncIterator[str],
        error_detector: Any,  # PredictionErrorDetector
    ) -> AsyncIterator[str]:
        """Process streaming output and inject context dynamically.
        
        This is the main integration point - wraps the LLM stream and
        injects context when prediction errors are detected.
        
        Args:
            original_stream: The original LLM output stream
            error_detector: Prediction error detector
        
        Yields:
            Chunks of text, with context injected when needed
        """
        if not self.enabled:
            # Pass through unchanged
            async for chunk in original_stream:
                yield chunk
            return
        
        stream_position = 0
        
        async for chunk in original_stream:
            # Yield original chunk
            yield chunk
            
            stream_position += len(chunk)
            
            # Check for prediction errors
            error = error_detector.process_chunk(chunk)
            
            if error:
                logger.info(f"Prediction error detected: {error.error_type.value} (conf={error.confidence})")
                
                # Inject context if needed
                injection = self.inject_context(error, stream_position)
                
                if injection:
                    # Yield injected context
                    yield injection
                    stream_position += len(injection)
    
    def reset(self):
        """Reset injector state (e.g., at start of new response)."""
        self.injection_points.clear()
        self.injections_count = 0
    
    def get_stats(self) -> Dict:
        """Get injection statistics."""
        successful_injections = sum(1 for ip in self.injection_points if ip.success)
        
        return {
            'total_injections': len(self.injection_points),
            'successful_injections': successful_injections,
            'injection_strategy': self.injection_strategy.value,
            'max_injections': self.max_injections,
            'enabled': self.enabled
        }


class SimpleContextFetcher:
    """Simple context fetcher for testing/demonstration.
    
    In production, this would query RAG store, activate specialists, etc.
    """
    
    def __init__(self, context_map: Optional[Dict[str, str]] = None):
        """Initialize with context map.
        
        Args:
            context_map: topic -> context content mapping
        """
        self.context_map = context_map or {}
    
    def __call__(self, topics: List[str]) -> List[DynamicContext]:
        """Fetch contexts for topics."""
        contexts = []
        
        for topic in topics:
            # Try exact match
            if topic in self.context_map:
                contexts.append(DynamicContext(
                    content=self.context_map[topic],
                    source="memory",
                    relevance_score=1.0,
                    priority=10
                ))
            # Try case-insensitive partial match
            else:
                for key, value in self.context_map.items():
                    if topic.lower() in key.lower():
                        contexts.append(DynamicContext(
                            content=value,
                            source="memory",
                            relevance_score=0.8,
                            priority=5
                        ))
                        break
        
        return contexts
