"""Core data structures for ada-logs."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class LogEntry:
    """A single log entry with metadata."""

    timestamp: datetime
    level: str  # DEBUG, INFO, WARN, ERROR, FATAL
    message: str
    source: str  # File/module that logged it

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level}: {self.message[:100]}"


@dataclass
class LogAnalysis:
    """Structured analysis result from parsing a log."""

    error_type: str
    """Type of error detected (e.g., 'mod_conflict', 'out_of_memory')"""

    confidence: float
    """Confidence score 0.0-1.0"""

    kid_explanation: str
    """Kid-friendly explanation of what went wrong"""

    fix: str
    """Actionable fix instructions"""

    difficulty: str = "easy"
    """Difficulty: easy, medium, hard"""

    conflicting_mods: List[str] = field(default_factory=list)
    """List of mods involved (for Minecraft)"""

    stack_trace: Optional[str] = None
    """Full stack trace if available"""

    common_causes: List[str] = field(default_factory=list)
    """Common causes of this error"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'error_type': self.error_type,
            'confidence': self.confidence,
            'kid_explanation': self.kid_explanation,
            'fix': self.fix,
            'difficulty': self.difficulty,
            'conflicting_mods': self.conflicting_mods,
            'stack_trace': self.stack_trace,
            'common_causes': self.common_causes,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        return f"LogAnalysis(error_type={self.error_type}, confidence={self.confidence:.2f})"
