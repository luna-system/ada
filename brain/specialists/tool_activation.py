"""Tool Activation Framework - Tier 1 (Anticipatory/Reflex).

Pre-execution pattern matching for model-agnostic tool activation.
Teaches machines about "toolboxes" through pattern recognition.

@ai-indexable: core-system
@ai-purpose: Biomimetic tool awareness through multi-tier activation
@ai-tier: Tier 1 (Anticipatory/Reflex) - pre-execution pattern matching
"""

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Optional


@dataclass
class ToolMatch:
    """A potential tool activation match.
    
    Attributes:
        tool_name: Name of the tool (specialist) to activate
        confidence: Confidence score 0.0-1.0 for this match
        extracted_params: Parameters extracted from the query
        pattern_matched: The regex pattern that matched
    """
    tool_name: str
    confidence: float
    extracted_params: dict[str, str]
    pattern_matched: str


class ToolPatternMatcher:
    """Anticipatory pattern matching for tool activation (Tier 1).
    
    This is the "reflex" layer - fast pattern matching that detects
    tool needs BEFORE LLM execution. Works with any model (model-agnostic).
    
    Philosophy:
        "When I see X pattern, this tool helps" - like touching hot stove
        triggers immediate reflex. No reasoning needed, just recognition.
    
    Example:
        Query: "How does calculate_importance work?"
        Pattern: "how does {function} work"
        Match: tool=codebase, confidence=0.9, params={query: "calculate_importance"}
    """
    
    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize pattern matcher.
        
        Args:
            patterns_file: Path to JSON file with pattern definitions.
                          If None, starts with empty patterns.
        """
        self.patterns = []
        if patterns_file:
            self._load_patterns(patterns_file)
    
    def ready(self) -> bool:
        """Check if matcher has patterns loaded.
        
        Returns:
            True if patterns loaded, False if empty.
        """
        return len(self.patterns) > 0
    
    def _load_patterns(self, filepath: str) -> None:
        """Load patterns from JSON file.
        
        Args:
            filepath: Path to patterns JSON file.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file isn't valid JSON.
        """
        with open(filepath) as f:
            data = json.load(f)
            self.patterns = data.get("patterns", [])
    
    def match(self, query: str) -> list[ToolMatch]:
        """Find tool activation patterns in query.
        
        Args:
            query: User's human language query.
            
        Returns:
            List of ToolMatch objects, sorted by confidence (highest first).
            Empty list if no matches found.
            
        Example:
            >>> matcher.match("How does calculate_importance work?")
            [ToolMatch(tool_name='codebase', confidence=0.92, ...)]
        """
        matches = []
        
        for pattern_group in self.patterns:
            tool_name = pattern_group["tool_name"]
            
            # Check negative patterns first (exclusions)
            if self._matches_negative_pattern(query, pattern_group):
                continue
            
            # Try each activation pattern
            for pattern in pattern_group["activation_patterns"]:
                match = re.search(pattern["regex"], query, re.IGNORECASE)
                if match:
                    params = self._extract_params(match, pattern.get("param_extraction", {}))
                    confidence = self._calculate_confidence(query, pattern, match)
                    
                    matches.append(ToolMatch(
                        tool_name=tool_name,
                        confidence=confidence,
                        extracted_params=params,
                        pattern_matched=pattern["regex"]
                    ))
        
        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def _matches_negative_pattern(self, query: str, pattern_group: dict) -> bool:
        """Check if query matches exclusion patterns.
        
        Args:
            query: User query to check.
            pattern_group: Pattern group with potential negative_patterns.
            
        Returns:
            True if query matches a negative pattern (should NOT activate).
        """
        for neg_pattern in pattern_group.get("negative_patterns", []):
            if re.search(neg_pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _extract_params(self, match: re.Match, extraction_rules: dict) -> dict:
        """Extract parameters from regex match groups.
        
        Args:
            match: Regex match object.
            extraction_rules: Dict mapping param names to group references.
                            e.g., {"query": "group1"} extracts group 1 as "query" param.
            
        Returns:
            Dict of extracted parameters.
        """
        params = {}
        for param_name, group_ref in extraction_rules.items():
            if group_ref.startswith("group"):
                group_num = int(group_ref.replace("group", ""))
                params[param_name] = match.group(group_num)
        return params
    
    def _calculate_confidence(self, query: str, pattern: dict, match: re.Match) -> float:
        """Calculate confidence score for match.
        
        Adjusts base confidence based on:
        - Query length (shorter = more ambiguous)
        - Match coverage (how much of query matched)
        
        Args:
            query: Original query string.
            pattern: Pattern definition with confidence_base.
            match: Regex match object.
            
        Returns:
            Confidence score between 0.0 and 1.0.
        """
        base_confidence = pattern.get("confidence_base", 0.5)
        
        # Adjust for query clarity
        if len(query.split()) < 5:  # Short query = ambiguous
            base_confidence *= 0.7
        
        # Adjust for match coverage
        match_coverage = len(match.group(0)) / len(query)
        confidence = base_confidence * (0.7 + 0.3 * match_coverage)
        
        return min(confidence, 1.0)
