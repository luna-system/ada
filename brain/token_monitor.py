"""Token budget monitoring for context management.

Tracks token usage across different components (persona, memories, specialists, etc.)
to help understand and optimize context window usage.

Part of v2.0 biomimetic foundation - provides visibility before optimization.
"""

# @ai-indexable: core-functionality
# @ai-purpose: Track and monitor token usage by component for context optimization
# @ai-dependencies: tiktoken (for token counting)
# @ai-related: brain/prompt_builder.py (integrates monitoring)

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import tiktoken

logger = logging.getLogger(__name__)


@dataclass
class ComponentTokens:
    """Token usage for a single component."""
    
    tokens: int
    percentage: float


@dataclass
class TokenUsageBreakdown:
    """Complete breakdown of token usage across components."""
    
    components: Dict[str, ComponentTokens]
    total_tokens: int
    percentage_used: float
    is_warning: bool


class TokenBudgetMonitor:
    """Monitors token budget usage across context components.
    
    Tracks token consumption by different parts of the prompt context:
    - Persona
    - FAQ
    - Memories (from RAG)
    - Conversation history
    - Specialist results
    - System notices
    
    Provides visibility into token distribution to guide optimization efforts.
    """
    
    def __init__(
        self,
        max_tokens: int = 128000,  # Default for most models
        warning_threshold: int = 102400,  # 80% of max
        model: str = "gpt-4",  # Use GPT-4 tokenizer as reference
    ):
        """Initialize token budget monitor.
        
        Args:
            max_tokens: Maximum token budget for context window
            warning_threshold: Tokens at which to warn about high usage
            model: Model name for tokenizer (defaults to gpt-4 for consistency)
        """
        self.max_tokens = max_tokens
        self.warning_threshold = warning_threshold
        self.model = model
        
        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base (GPT-4 encoding)
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Track usage by component
        self._components: Dict[str, int] = {}
        
        logger.debug(
            f"TokenBudgetMonitor initialized: max={max_tokens}, "
            f"warning={warning_threshold}, model={model}"
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the model's tokenizer.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        
        return len(self.encoding.encode(text))
    
    def track(self, component: str, text: str) -> int:
        """Track token usage for a component.
        
        Args:
            component: Component name (e.g., "persona", "memories", "specialist_ocr")
            text: Text content to track
            
        Returns:
            Number of tokens in this text
        """
        tokens = self.count_tokens(text)
        
        # Accumulate tokens for this component
        if component in self._components:
            self._components[component] += tokens
        else:
            self._components[component] = tokens
        
        logger.debug(f"Tracked {tokens} tokens for component '{component}'")
        
        return tokens
    
    def get_breakdown(self) -> TokenUsageBreakdown:
        """Get detailed breakdown of token usage.
        
        Returns:
            TokenUsageBreakdown with per-component stats
        """
        total_tokens = sum(self._components.values())
        percentage_used = (total_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0
        is_warning = total_tokens >= self.warning_threshold
        
        # Calculate per-component percentages
        components = {}
        for name, tokens in self._components.items():
            percentage = (tokens / total_tokens * 100) if total_tokens > 0 else 0
            components[name] = ComponentTokens(tokens=tokens, percentage=percentage)
        
        return TokenUsageBreakdown(
            components=components,
            total_tokens=total_tokens,
            percentage_used=percentage_used,
            is_warning=is_warning,
        )
    
    def get_summary(self) -> str:
        """Get human-readable summary of token usage.
        
        Returns:
            Formatted summary string
        """
        breakdown = self.get_breakdown()
        
        lines = [
            f"Token Usage: {breakdown.total_tokens:,} / {self.max_tokens:,} "
            f"({breakdown.percentage_used:.1f}%)"
        ]
        
        if breakdown.is_warning:
            lines.append("⚠️  WARNING: Approaching token limit!")
        
        lines.append("\nBreakdown by component:")
        
        # Sort by token count descending
        sorted_components = sorted(
            breakdown.components.items(),
            key=lambda x: x[1].tokens,
            reverse=True
        )
        
        for name, comp in sorted_components:
            lines.append(
                f"  {name:20s}: {comp.tokens:6,} tokens ({comp.percentage:5.1f}%)"
            )
        
        return "\n".join(lines)
    
    def get_top_components(self, n: int = 3) -> List[Tuple[str, int]]:
        """Get top N components by token usage.
        
        Args:
            n: Number of top components to return
            
        Returns:
            List of (component_name, token_count) tuples, sorted by tokens descending
        """
        sorted_components = sorted(
            self._components.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_components[:n]
    
    def reset(self):
        """Reset tracking for a new request.
        
        Should be called at the start of each request to track
        token usage independently per request.
        """
        self._components.clear()
        logger.debug("TokenBudgetMonitor reset")
    
    def log_breakdown(self):
        """Log detailed breakdown at INFO level.
        
        Useful for debugging and monitoring token usage patterns.
        """
        summary = self.get_summary()
        logger.info(f"\n{summary}")
        
        breakdown = self.get_breakdown()
        if breakdown.is_warning:
            logger.warning(
                f"Token usage ({breakdown.total_tokens:,}) exceeds warning threshold "
                f"({self.warning_threshold:,})"
            )
