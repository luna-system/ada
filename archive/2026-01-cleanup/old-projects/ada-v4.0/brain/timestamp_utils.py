# @ai-indexable: utility
# @ai-purpose: Consolidated timestamp parsing, sorting, and recency scoring utilities
# @ai-dependencies: datetime
# @ai-related: brain/rag_store.py, brain/prompt_builder/context_retriever.py

import datetime
from typing import Optional, List, Dict, Any, Union


class TimestampUtils:
    """
    Utility class consolidating timestamp operations used throughout RAG system.

    Centralizes timestamp parsing, recency scoring, and sorting logic that was
    previously duplicated across retrieve_memories, retrieve_turns, and other modules.
    This improves ML-friendliness by reducing pattern duplication.
    """

    @staticmethod
    def parse_iso(value: Any) -> Optional[datetime.datetime]:
        """
        Parse ISO 8601 timestamp string to datetime object.

        Args:
            value: ISO timestamp string or any other value

        Returns:
            datetime.datetime if parsing succeeds, None otherwise (no exceptions raised)
        """
        if value is None or not isinstance(value, str):
            return None
        try:
            return datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError, AttributeError):
            return None

    @staticmethod
    def timestamp_to_float(dt: Optional[datetime.datetime]) -> float:
        """
        Convert datetime to Unix timestamp float.

        Args:
            dt: datetime object or None

        Returns:
            Unix timestamp (seconds since epoch) or 0.0 if dt is None
        """
        if dt is None:
            return 0.0
        try:
            return dt.timestamp()
        except (AttributeError, TypeError):
            return 0.0

    @staticmethod
    def recency_score(
        timestamp_value: Union[str, datetime.datetime, None],
        now: datetime.datetime,
        half_life: float,
    ) -> float:
        """
        Compute exponential decay score based on age: 0.5^(age / half_life).

        Args:
            timestamp_value: ISO string, datetime object, or None
            now: Current time (usually datetime.now(timezone.utc))
            half_life: Half-life in seconds (time for score to reach 0.5)

        Returns:
            Score between 0.0 and 1.0 (1.0 = current, 0.0 = very old or invalid)
        """
        # Parse timestamp if string
        if isinstance(timestamp_value, str):
            ts = TimestampUtils.parse_iso(timestamp_value)
            if ts is None:
                return 0.0
        elif isinstance(timestamp_value, datetime.datetime):
            ts = timestamp_value
        else:
            return 0.0

        # Calculate age
        try:
            age = (now - ts).total_seconds()
            # Clamp negative age (future timestamps) to 0
            if age < 0:
                age = 0
            # Exponential decay
            if half_life <= 0:
                return 0.0
            return 0.5 ** (age / half_life)
        except (TypeError, AttributeError):
            return 0.0

    @staticmethod
    def sort_by_timestamp(
        metadata_list: List[Dict[str, Any]],
        reverse: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Sort list of metadata dicts by timestamp field.

        Args:
            metadata_list: List of dicts with optional "timestamp" key
            reverse: If True, sort descending (newest first); if False, ascending

        Returns:
            Sorted list (preserves dicts with no timestamp at the end)
        """
        def ts_of(meta: Optional[Dict[str, Any]]) -> float:
            """Extract timestamp float from metadata dict."""
            if meta is None or not isinstance(meta, dict):
                return 0.0
            ts = meta.get("timestamp")
            if ts is None:
                return 0.0
            dt = TimestampUtils.parse_iso(ts)
            return TimestampUtils.timestamp_to_float(dt)

        try:
            return sorted(metadata_list, key=ts_of, reverse=reverse)
        except TypeError:
            # If sorting fails for any reason, return original list
            return metadata_list

    @staticmethod
    def get_timestamp_value(
        value: Union[str, Dict[str, Any], None],
    ) -> Optional[datetime.datetime]:
        """
        Extract and parse timestamp from various input formats.

        Args:
            value: ISO string, dict with "timestamp" key, or None

        Returns:
            Parsed datetime or None
        """
        if isinstance(value, str):
            return TimestampUtils.parse_iso(value)
        elif isinstance(value, dict):
            return TimestampUtils.parse_iso(value.get("timestamp"))
        else:
            return None
