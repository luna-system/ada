"""Importance scoring for tool results using biomimetic weights.

Applies validated research weights (v2.2) to tool results:
- Surprise/novelty: 60% (dominant signal)
- Relevance: 20% (semantic match)
- Temporal decay: 10% (recency)
- Habituation: 10% (repeated patterns)

Results are compressed using gradient detail levels:
- FULL (≥0.75): Complete results with full context
- CHUNKS (≥0.50): Key sections, trimmed details
- SUMMARY (≥0.20): Natural language summary
- DROPPED (<0.20): Filtered out entirely
"""
# @ai-indexable: reasoning-system
# @ai-purpose: Score and compress tool results using biomimetic importance
# @ai-dependencies: brain.config, brain.memory_decay, re, dataclasses

import re
import hashlib
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from brain.config import (
    IMPORTANCE_WEIGHT_SURPRISE,
    IMPORTANCE_WEIGHT_RELEVANCE,
    IMPORTANCE_WEIGHT_DECAY,
    IMPORTANCE_WEIGHT_HABITUATION,
)


class DetailLevel(Enum):
    """Gradient compression levels for tool results."""
    FULL = "full"           # ≥0.75: Complete results
    CHUNKS = "chunks"       # ≥0.50: Key sections only
    SUMMARY = "summary"     # ≥0.20: Natural language summary
    DROPPED = "dropped"     # <0.20: Filtered out


@dataclass
class ScoredResult:
    """Tool result with importance scoring."""
    content: str                    # Original or compressed content
    importance: float               # 0.0-1.0 importance score
    detail_level: DetailLevel       # Compression level applied
    signals: Dict[str, float]       # Individual signal contributions
    metadata: Dict[str, Any]        # Tool-specific metadata


class ToolResultScorer:
    """Score tool results using biomimetic importance signals.
    
    Example:
        scorer = ToolResultScorer(query="authentication logic")
        
        # Score a file read result
        result = scorer.score_file_content(
            content="import jwt\\n\\nclass AuthHandler:\\n...",
            tool_name="brain_read_file",
            params={"file_path": "auth.py"}
        )
        
        # Result has importance score and appropriate detail level
        print(f"Importance: {result.importance:.2f}")
        print(f"Detail: {result.detail_level}")
        # Importance: 0.87
        # Detail: DetailLevel.FULL
    """
    
    def __init__(
        self,
        query: str,
        seen_patterns: Optional[set] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """Initialize scorer with query context.
        
        Args:
            query: User's original query for relevance scoring
            seen_patterns: Set of content hashes seen before (for habituation)
            weights: Optional weight overrides (defaults to v2.2 research)
        """
        self.query = query.lower()
        self.query_keywords = set(re.findall(r'\w+', self.query))
        self.seen_patterns = seen_patterns or set()
        
        # Use validated research weights by default
        self.weights = weights or {
            'surprise': IMPORTANCE_WEIGHT_SURPRISE,      # 0.60
            'relevance': IMPORTANCE_WEIGHT_RELEVANCE,    # 0.20
            'decay': IMPORTANCE_WEIGHT_DECAY,            # 0.10
            'habituation': IMPORTANCE_WEIGHT_HABITUATION # 0.10
        }
    
    def calculate_surprise(self, content: str) -> float:
        """Calculate novelty/surprise score.
        
        Surprise is HIGH when content:
        - Contains unique patterns not seen before
        - Has high information density (code vs boilerplate)
        - Shows unexpected relationships
        
        Args:
            content: Tool result content
            
        Returns:
            Surprise score 0.0-1.0
        """
        # Hash content for pattern tracking
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # New pattern = high surprise
        if content_hash not in self.seen_patterns:
            self.seen_patterns.add(content_hash)
            novelty_score = 1.0
        else:
            novelty_score = 0.3  # Repeated pattern
        
        # Information density heuristics
        # More unique tokens = higher density
        tokens = set(re.findall(r'\w+', content.lower()))
        total_words = len(content.split())
        if total_words > 0:
            density = len(tokens) / total_words
        else:
            density = 0.0
        
        # Code patterns (def, class, async) boost surprise
        code_indicators = ['def ', 'class ', 'async ', 'import ', 'return ', 'if ']
        code_score = sum(1 for indicator in code_indicators if indicator in content)
        code_bonus = min(code_score / len(code_indicators), 1.0)
        
        # Combine signals
        surprise = (novelty_score * 0.5) + (density * 0.3) + (code_bonus * 0.2)
        return min(surprise, 1.0)
    
    def calculate_relevance(self, content: str) -> float:
        """Calculate semantic relevance to query.
        
        Relevance is HIGH when content:
        - Contains query keywords
        - Matches query intent (file names, function names)
        - Has contextual overlap
        
        Args:
            content: Tool result content
            
        Returns:
            Relevance score 0.0-1.0
        """
        content_lower = content.lower()
        content_tokens = set(re.findall(r'\w+', content_lower))
        
        # Direct keyword matches
        keyword_overlap = self.query_keywords & content_tokens
        if len(self.query_keywords) > 0:
            keyword_score = len(keyword_overlap) / len(self.query_keywords)
        else:
            keyword_score = 0.0
        
        # Substring matches (query in content)
        substring_score = 1.0 if self.query in content_lower else 0.0
        
        # Contextual signals
        # If query is "auth", boost if content has "authentication", "jwt", etc
        contextual_keywords = {
            'auth': ['authentication', 'jwt', 'token', 'login', 'password'],
            'data': ['database', 'model', 'schema', 'query'],
            'api': ['endpoint', 'route', 'request', 'response'],
            'test': ['unittest', 'pytest', 'assert', 'mock'],
        }
        
        context_score = 0.0
        for base_word, related_words in contextual_keywords.items():
            if base_word in self.query:
                context_matches = sum(1 for word in related_words if word in content_lower)
                context_score = max(context_score, context_matches / len(related_words))
        
        # Combine signals
        relevance = (keyword_score * 0.5) + (substring_score * 0.3) + (context_score * 0.2)
        return min(relevance, 1.0)
    
    def calculate_decay(self, tool_name: str, iteration: int) -> float:
        """Calculate temporal decay (recency).
        
        For tool results, "recency" is iteration-based:
        - Recent iterations (current) = high score
        - Older iterations = decay
        
        Args:
            tool_name: Name of the tool
            iteration: Current iteration number
            
        Returns:
            Decay score 0.0-1.0 (higher = more recent)
        """
        # For now, all tool results are "current" (iteration 0)
        # This will be enhanced when we track result age
        return 1.0
    
    def calculate_habituation(self, content: str) -> float:
        """Calculate habituation penalty for repeated patterns.
        
        Habituation is HIGH (penalty) when:
        - Content seen multiple times before
        - Boilerplate patterns (imports, config)
        - Low variety in structure
        
        Args:
            content: Tool result content
            
        Returns:
            Habituation score 0.0-1.0 (higher = less habituated)
        """
        # Hash for pattern detection
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Check if we've seen this before (BEFORE calculate_surprise adds it)
        was_seen_before = content_hash in self.seen_patterns
        
        # First time seeing this = no habituation
        if not was_seen_before:
            return 1.0
        
        # Repeated content = high habituation (lower score)
        # This applies penalty to boilerplate
        return 0.4
    
    def calculate_importance(
        self,
        content: str,
        tool_name: str,
        iteration: int = 0
    ) -> tuple[float, Dict[str, float]]:
        """Calculate multi-signal importance score.
        
        Uses validated v2.2 weights:
        - Surprise: 60% (dominant - what's new and interesting?)
        - Relevance: 20% (matches query intent)
        - Decay: 10% (temporal recency)
        - Habituation: 10% (penalty for repetition)
        
        Args:
            content: Tool result content
            tool_name: Name of tool that produced this
            iteration: Current reasoning iteration
            
        Returns:
            (importance_score, signal_breakdown)
        """
        # Calculate habituation FIRST (before surprise adds to seen_patterns)
        habituation = self.calculate_habituation(content)
        
        # Then calculate other signals
        surprise = self.calculate_surprise(content)
        relevance = self.calculate_relevance(content)
        decay = self.calculate_decay(tool_name, iteration)
        
        # Apply validated weights
        importance = (
            surprise * self.weights['surprise'] +
            relevance * self.weights['relevance'] +
            decay * self.weights['decay'] +
            habituation * self.weights['habituation']
        )
        
        # Return score and breakdown for transparency
        signals = {
            'surprise': surprise,
            'relevance': relevance,
            'decay': decay,
            'habituation': habituation,
            'final': importance
        }
        
        return importance, signals
    
    def get_detail_level(self, importance: float) -> DetailLevel:
        """Determine compression level based on importance.
        
        Gradient thresholds (research-validated):
        - ≥0.75: FULL (critical context)
        - ≥0.50: CHUNKS (important sections)
        - ≥0.20: SUMMARY (mentioned but compressed)
        - <0.20: DROPPED (filtered out)
        
        Args:
            importance: Importance score 0.0-1.0
            
        Returns:
            DetailLevel enum
        """
        if importance >= 0.75:
            return DetailLevel.FULL
        elif importance >= 0.50:
            return DetailLevel.CHUNKS
        elif importance >= 0.20:
            return DetailLevel.SUMMARY
        else:
            return DetailLevel.DROPPED
    
    def compress_content(
        self,
        content: str,
        detail_level: DetailLevel,
        metadata: Dict[str, Any]
    ) -> str:
        """Apply compression based on detail level.
        
        Args:
            content: Original content
            detail_level: Target compression level
            metadata: Tool-specific context
            
        Returns:
            Compressed content string
        """
        if detail_level == DetailLevel.FULL:
            return content
        
        elif detail_level == DetailLevel.CHUNKS:
            # Keep first 500 chars + last 200 chars
            if len(content) > 700:
                return (
                    content[:500] +
                    "\n... (middle section trimmed for brevity) ...\n" +
                    content[-200:]
                )
            return content
        
        elif detail_level == DetailLevel.SUMMARY:
            # Natural language summary
            lines = content.split('\n')
            tool_name = metadata.get('tool_name', 'tool')
            
            if tool_name == 'brain_read_file':
                file_path = metadata.get('file_path', 'file')
                return f"File {file_path}: {len(lines)} lines of code (importance below threshold, summary only)"
            
            elif tool_name == 'brain_list_dir':
                return f"Directory listing: {len(lines)} items (low importance, details omitted)"
            
            elif tool_name == 'brain_grep':
                return f"Search results: {len(lines)} matches (low relevance, skipped)"
            
            return f"Result from {tool_name} (compressed due to low importance)"
        
        else:  # DROPPED
            return ""
    
    def score_tool_result(
        self,
        content: str,
        tool_name: str,
        params: Dict[str, Any],
        iteration: int = 0
    ) -> ScoredResult:
        """Score and compress a tool result.
        
        Args:
            content: Raw tool result content
            tool_name: Name of the tool
            params: Parameters passed to tool
            iteration: Current reasoning iteration
            
        Returns:
            ScoredResult with importance and compression applied
        """
        # Calculate importance
        importance, signals = self.calculate_importance(content, tool_name, iteration)
        
        # Determine detail level
        detail_level = self.get_detail_level(importance)
        
        # Apply compression
        metadata = {
            'tool_name': tool_name,
            **params
        }
        compressed_content = self.compress_content(content, detail_level, metadata)
        
        return ScoredResult(
            content=compressed_content,
            importance=importance,
            detail_level=detail_level,
            signals=signals,
            metadata=metadata
        )
