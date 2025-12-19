"""Pattern matching engine for log analysis.

Loads patterns from JSON and matches them against log content.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


class PatternMatcher:
    """Matches log content against known error patterns.

    Patterns are loaded from minecraft_patterns.json and matched using regex.
    """

    def __init__(self, patterns_file: Optional[Path] = None):
        """Initialize pattern matcher.

        Args:
            patterns_file: Optional path to patterns JSON file.
                          Defaults to minecraft_patterns.json in this package.
        """
        if patterns_file is None:
            # Default to minecraft_patterns.json in the same directory
            patterns_file = Path(__file__).parent / "minecraft_patterns.json"

        self.patterns = self._load_patterns(patterns_file)

    def _load_patterns(self, patterns_file: Path) -> List[Dict[str, Any]]:
        """Load patterns from JSON file.

        Args:
            patterns_file: Path to JSON file

        Returns:
            List of pattern dictionaries
        """
        with open(patterns_file, 'r') as f:
            data = json.load(f)

        return data.get('patterns', [])

    def match(self, log_content: str) -> List[Dict[str, Any]]:
        """Find all patterns that match the log content.

        Args:
            log_content: Raw log file content

        Returns:
            List of matching patterns (empty if no matches)
        """
        matches = []

        for pattern in self.patterns:
            regex = pattern.get('regex', '')

            try:
                # Case-insensitive, multiline, dotall matching
                if re.search(regex, log_content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                    matches.append(pattern)
            except re.error:
                # Skip invalid regex patterns
                continue

        return matches

    def best_match(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Find the best (highest confidence) matching pattern.

        Args:
            log_content: Raw log file content

        Returns:
            Best matching pattern, or None if no matches
        """
        matches = self.match(log_content)

        if not matches:
            return None

        # Sort by confidence_boost (highest first)
        sorted_matches = sorted(
            matches,
            key=lambda p: p.get('confidence_boost', 0.5),
            reverse=True
        )

        return sorted_matches[0]

    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID.

        Args:
            pattern_id: Pattern ID (e.g., 'out_of_memory')

        Returns:
            Pattern dictionary or None if not found
        """
        for pattern in self.patterns:
            if pattern.get('id') == pattern_id:
                return pattern

        return None
