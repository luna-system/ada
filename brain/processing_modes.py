"""Hemispheric specialization - adaptive processing modes for different tasks.

Based on biological hemispheric specialization: left hemisphere handles
detail-focused, sequential, analytical tasks while right hemisphere handles
big picture, parallel, holistic tasks. The brain switches between modes
based on the task at hand.

For Ada: Detect task type from user message and adapt context assembly
strategy accordingly. Analytical tasks get more detail and history,
creative tasks get diverse exploration, conversational tasks stay lightweight.

@ai-indexable: biomimetic-phase4
@ai-purpose: Adaptive context assembly based on task type detection
@ai-dependencies: None (pure Python)
@ai-related: brain/prompt_builder/prompt_assembler.py
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Different cognitive processing modes for different task types."""
    
    ANALYTICAL = "analytical"  # Detail-focused: explain, debug, analyze
    CREATIVE = "creative"      # Big picture: design, brainstorm, imagine
    CONVERSATIONAL = "conversational"  # Social: chat, casual interaction
    TECHNICAL = "technical"    # Implementation: write code, configure, build
    EXPLORATORY = "exploratory"  # Research: learn, discover, investigate


@dataclass
class ContextStrategy:
    """Strategy for assembling context in a specific processing mode."""
    
    mode: ProcessingMode
    """The processing mode this strategy applies to"""
    
    history_limit: int
    """Maximum conversation turns to include"""
    
    memory_diversity: bool
    """Whether to prioritize diverse memories over similar ones"""
    
    detail_level: str
    """Level of detail: 'high', 'medium', 'low'"""
    
    specialist_preference: List[str] = field(default_factory=list)
    """Preferred specialist types for this mode"""
    
    context_focus: str = "balanced"
    """Context focus: 'technical', 'personal', 'conceptual', 'balanced'"""
    
    token_budget_multiplier: float = 1.0
    """Multiplier for token budget (e.g., 1.5 = 50% more tokens)"""


class ModeDetector:
    """Detect processing mode from user message content.
    
    Uses keyword matching and pattern recognition to infer what type
    of cognitive processing the user's request requires.
    """
    
    # Keyword patterns for each mode
    ANALYTICAL_KEYWORDS = [
        r'\b(?:explain|why|debug|troubleshoot|diagnose|analyze|investigate)\b',
        r'\bhow (?:does|do|can|should|would|to|is)\b',  # "how X" but not "how are you"
        r'\bhow (?:this|that|it)\b',  # "how this works" etc
        r'\b(?:what(?:\'s| is) (?:wrong|the (?:issue|problem|error)))\b',
        r'\b(?:understand|clarify|break down|walk (?:me )?through)\b',
        r'\b(?:compare|contrast|difference between)\b',
    ]
    
    CREATIVE_KEYWORDS = [
        r'\b(?:design|create|build|make|generate|brainstorm|imagine)\b',
        r'\b(?:idea[s]?|concept|approach|strategy|solution)\b',
        r'\b(?:what if|suppose|consider|alternative)\b',
        r'\b(?:innovative|creative|novel|unique|improving)\b',
    ]
    
    TECHNICAL_KEYWORDS = [
        r'\b(?:implement|code|write|program|script|function|class)\b',
        r'\b(?:fix|patch|update|modify|refactor|optimize)\b',
        r'\b(?:configure|setup|install|deploy)\b',
        r'\b(?:test|pytest|unittest|assert)\b',
    ]
    
    EXPLORATORY_KEYWORDS = [
        r'\b(?:learn|teach|show|demonstrate|example)\b',
        r'\b(?:research|investigate|explore|discover)\b',
        r'\b(?:overview|introduction|basics|fundamentals)\b',
        r'\b(?:what (?:are|is)|tell me about)\b',
    ]
    
    CONVERSATIONAL_KEYWORDS = [
        r'\b(?:hi|hello|hey|greetings)\b',
        r'\b(?:thanks|thank you|appreciate)\b',
        r'\b(?:how are you|what\'s up|how\'s it going|how are you doing)\b',
        r'\b(?:cool|nice|awesome|great)\b',
    ]
    
    def __init__(self, enabled: bool = True):
        """Initialize mode detector.
        
        Args:
            enabled: Whether mode detection is enabled
        """
        self.enabled = enabled
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.analytical_patterns = [re.compile(p, re.IGNORECASE) for p in self.ANALYTICAL_KEYWORDS]
        self.creative_patterns = [re.compile(p, re.IGNORECASE) for p in self.CREATIVE_KEYWORDS]
        self.technical_patterns = [re.compile(p, re.IGNORECASE) for p in self.TECHNICAL_KEYWORDS]
        self.exploratory_patterns = [re.compile(p, re.IGNORECASE) for p in self.EXPLORATORY_KEYWORDS]
        self.conversational_patterns = [re.compile(p, re.IGNORECASE) for p in self.CONVERSATIONAL_KEYWORDS]
    
    def detect(self, message: str, conversation_history: Optional[List] = None) -> ProcessingMode:
        """Detect processing mode from message.
        
        Args:
            message: User's message text
            conversation_history: Optional conversation history for context
        
        Returns:
            Detected ProcessingMode
        """
        if not self.enabled:
            return ProcessingMode.CONVERSATIONAL  # Default
        
        # Count pattern matches for each mode
        scores = {
            ProcessingMode.ANALYTICAL: self._count_matches(message, self.analytical_patterns),
            ProcessingMode.CREATIVE: self._count_matches(message, self.creative_patterns),
            ProcessingMode.TECHNICAL: self._count_matches(message, self.technical_patterns),
            ProcessingMode.EXPLORATORY: self._count_matches(message, self.exploratory_patterns),
            ProcessingMode.CONVERSATIONAL: self._count_matches(message, self.conversational_patterns),
        }
        
        # Get mode with highest score
        detected_mode = max(scores.keys(), key=lambda m: scores[m])
        max_score = scores[detected_mode]
        
        # If no strong signal, default to conversational
        if max_score == 0:
            detected_mode = ProcessingMode.CONVERSATIONAL
        
        logger.info(f"Detected mode: {detected_mode.value} (scores: {scores})")
        return detected_mode
    
    def _count_matches(self, text: str, patterns: List[re.Pattern]) -> int:
        """Count how many patterns match in text."""
        count = 0
        for pattern in patterns:
            if pattern.search(text):
                count += 1
        return count


class ContextStrategyBuilder:
    """Build context assembly strategies for different processing modes.
    
    Defines how context should be assembled for each cognitive mode,
    inspired by how human brains adapt processing strategies to task demands.
    """
    
    @staticmethod
    def get_strategy(mode: ProcessingMode) -> ContextStrategy:
        """Get context assembly strategy for a processing mode.
        
        Args:
            mode: The processing mode
        
        Returns:
            ContextStrategy for that mode
        """
        strategies = {
            ProcessingMode.ANALYTICAL: ContextStrategy(
                mode=ProcessingMode.ANALYTICAL,
                history_limit=10,  # More history for understanding context
                memory_diversity=False,  # Similar memories (deep knowledge)
                detail_level='high',  # Full detail
                specialist_preference=['docs', 'codebase'],
                context_focus='technical',
                token_budget_multiplier=1.2  # 20% more tokens
            ),
            
            ProcessingMode.CREATIVE: ContextStrategy(
                mode=ProcessingMode.CREATIVE,
                history_limit=3,  # Less history (more freedom)
                memory_diversity=True,  # Diverse memories (broad inspiration)
                detail_level='medium',  # Balanced detail
                specialist_preference=['web_search', 'docs'],
                context_focus='conceptual',
                token_budget_multiplier=1.0  # Standard budget
            ),
            
            ProcessingMode.CONVERSATIONAL: ContextStrategy(
                mode=ProcessingMode.CONVERSATIONAL,
                history_limit=5,  # Recent context
                memory_diversity=False,  # Relevant memories
                detail_level='low',  # Lightweight
                specialist_preference=[],  # No specialists by default
                context_focus='personal',
                token_budget_multiplier=0.8  # Reduced budget
            ),
            
            ProcessingMode.TECHNICAL: ContextStrategy(
                mode=ProcessingMode.TECHNICAL,
                history_limit=7,  # Some context
                memory_diversity=False,  # Focused technical memories
                detail_level='high',  # Precise detail
                specialist_preference=['codebase', 'docs'],
                context_focus='technical',
                token_budget_multiplier=1.3  # More tokens for code
            ),
            
            ProcessingMode.EXPLORATORY: ContextStrategy(
                mode=ProcessingMode.EXPLORATORY,
                history_limit=5,  # Moderate history
                memory_diversity=True,  # Broad exploration
                detail_level='medium',  # Balanced
                specialist_preference=['web_search', 'docs', 'wiki'],
                context_focus='conceptual',
                token_budget_multiplier=1.1  # Slightly more
            ),
        }
        
        return strategies[mode]


class AdaptiveContextAssembler:
    """Assemble context adaptively based on detected processing mode.
    
    This is the main integration point - detects mode and applies
    appropriate context assembly strategy.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize adaptive assembler.
        
        Args:
            enabled: Whether adaptive assembly is enabled
        """
        self.enabled = enabled
        self.detector = ModeDetector(enabled=enabled)
        self.strategy_builder = ContextStrategyBuilder()
        
        # Statistics
        self.mode_counts: Dict[ProcessingMode, int] = {mode: 0 for mode in ProcessingMode}
        self.total_requests = 0
    
    def get_strategy(
        self,
        message: str,
        conversation_history: Optional[List] = None
    ) -> Tuple[ProcessingMode, ContextStrategy]:
        """Get processing mode and context strategy for a message.
        
        Args:
            message: User's message
            conversation_history: Optional conversation history
        
        Returns:
            Tuple of (detected_mode, context_strategy)
        """
        if not self.enabled:
            # Default strategy when disabled
            mode = ProcessingMode.CONVERSATIONAL
            strategy = self.strategy_builder.get_strategy(mode)
            return mode, strategy
        
        # Detect mode
        mode = self.detector.detect(message, conversation_history)
        
        # Get strategy
        strategy = self.strategy_builder.get_strategy(mode)
        
        # Update stats
        self.mode_counts[mode] += 1
        self.total_requests += 1
        
        logger.info(
            f"Adaptive context: mode={mode.value}, "
            f"history_limit={strategy.history_limit}, "
            f"detail={strategy.detail_level}"
        )
        
        return mode, strategy
    
    def get_stats(self) -> Dict:
        """Get processing mode statistics.
        
        Returns:
            Dictionary with mode distribution and counts
        """
        if self.total_requests == 0:
            distribution = {mode.value: 0.0 for mode in ProcessingMode}
        else:
            distribution = {
                mode.value: count / self.total_requests
                for mode, count in self.mode_counts.items()
            }
        
        return {
            'enabled': self.enabled,
            'total_requests': self.total_requests,
            'mode_counts': {mode.value: count for mode, count in self.mode_counts.items()},
            'mode_distribution': distribution
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.mode_counts = {mode: 0 for mode in ProcessingMode}
        self.total_requests = 0
