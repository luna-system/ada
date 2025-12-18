"""
Test-driven development for TimestampUtils class.

This class consolidates timestamp parsing, sorting, and recency scoring
which appears in 4+ different locations with slight variations.
"""

import pytest
import datetime
from unittest.mock import patch


class TestTimestampUtils:
    """Test the TimestampUtils helper class."""

    @pytest.fixture(autouse=True)
    def import_utils(self):
        """Import TimestampUtils - will fail until created."""
        try:
            from brain.timestamp_utils import TimestampUtils
            self.TimestampUtils = TimestampUtils
        except ImportError:
            pytest.skip("TimestampUtils not yet implemented")

    def test_parse_iso_valid_timestamp(self):
        """Should parse valid ISO format timestamps."""
        ts_str = "2025-12-18T10:30:45+00:00"
        result = self.TimestampUtils.parse_iso(ts_str)
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 18

    def test_parse_iso_invalid_timestamp_returns_none(self):
        """Should return None for invalid timestamps instead of raising."""
        invalid_inputs = ["invalid", "2025-13-45", "", None, 12345]
        for invalid in invalid_inputs:
            result = self.TimestampUtils.parse_iso(invalid)
            assert result is None

    def test_parse_iso_naive_datetime(self):
        """Should handle naive (no timezone) ISO strings."""
        ts_str = "2025-12-18T10:30:45"
        result = self.TimestampUtils.parse_iso(ts_str)
        assert result is not None
        assert result.year == 2025

    def test_timestamp_to_float_converts_to_unix(self):
        """Should convert datetime to Unix timestamp float."""
        ts = datetime.datetime(2025, 12, 18, 10, 30, 45, tzinfo=datetime.timezone.utc)
        result = self.TimestampUtils.timestamp_to_float(ts)
        assert isinstance(result, float)
        assert result > 0  # Should be positive Unix timestamp

    def test_timestamp_to_float_none_returns_zero(self):
        """Should return 0.0 for None timestamp."""
        result = self.TimestampUtils.timestamp_to_float(None)
        assert result == 0.0

    def test_recency_score_exponential_decay(self):
        """Should compute exponential decay score: 0.5^(age / half_life)."""
        now = datetime.datetime.now(datetime.timezone.utc)
        half_life = 3600  # 1 hour

        # At age=0, score should be 1.0
        score_at_zero = self.TimestampUtils.recency_score(now, now, half_life)
        assert score_at_zero == pytest.approx(1.0, abs=0.01)

        # At age=half_life, score should be ~0.5
        past = now - datetime.timedelta(seconds=half_life)
        score_at_half = self.TimestampUtils.recency_score(past, now, half_life)
        assert score_at_half == pytest.approx(0.5, abs=0.01)

        # At age=2*half_life, score should be ~0.25
        older = now - datetime.timedelta(seconds=2 * half_life)
        score_at_double = self.TimestampUtils.recency_score(older, now, half_life)
        assert score_at_double == pytest.approx(0.25, abs=0.01)

    def test_recency_score_from_iso_string(self):
        """Should accept ISO timestamp string as input."""
        now = datetime.datetime.now(datetime.timezone.utc)
        now_iso = now.isoformat()
        half_life = 3600

        # Current timestamp should give score ~1.0
        score = self.TimestampUtils.recency_score(now_iso, now, half_life)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_recency_score_negative_age_handled(self):
        """Should handle future timestamps (negative age) gracefully."""
        now = datetime.datetime.now(datetime.timezone.utc)
        future = now + datetime.timedelta(seconds=100)
        half_life = 3600

        # Future timestamp should not crash, should be clamped to ~1.0
        score = self.TimestampUtils.recency_score(future, now, half_life)
        assert 0.0 <= score <= 1.0

    def test_recency_score_zero_half_life(self):
        """Should handle zero half_life gracefully."""
        now = datetime.datetime.now(datetime.timezone.utc)
        past = now - datetime.timedelta(seconds=100)
        half_life = 0

        # Should not crash with division by zero
        score = self.TimestampUtils.recency_score(past, now, half_life)
        assert score == 0.0

    def test_recency_score_invalid_timestamp_returns_zero(self):
        """Should return 0.0 for invalid timestamps."""
        now = datetime.datetime.now(datetime.timezone.utc)
        half_life = 3600

        invalid_inputs = ["invalid", "", None, "2025-13-45"]
        for invalid in invalid_inputs:
            score = self.TimestampUtils.recency_score(invalid, now, half_life)
            assert score == 0.0

    def test_sort_by_timestamp_descending(self):
        """Should sort list of metadata dicts by timestamp descending."""
        now = datetime.datetime.now(datetime.timezone.utc)
        metas = [
            {"timestamp": (now - datetime.timedelta(seconds=100)).isoformat(), "id": 1},
            {"timestamp": (now - datetime.timedelta(seconds=50)).isoformat(), "id": 2},
            {"timestamp": now.isoformat(), "id": 3},
            {"id": 4},  # No timestamp
        ]

        sorted_metas = self.TimestampUtils.sort_by_timestamp(metas, reverse=True)

        # Should be: id=3 (latest), id=2, id=1, id=4 (no ts goes to end)
        assert sorted_metas[0]["id"] == 3
        assert sorted_metas[1]["id"] == 2
        assert sorted_metas[2]["id"] == 1
        assert sorted_metas[3]["id"] == 4

    def test_sort_by_timestamp_ascending(self):
        """Should sort ascending when reverse=False."""
        now = datetime.datetime.now(datetime.timezone.utc)
        metas = [
            {"timestamp": now.isoformat(), "id": 1},
            {"timestamp": (now - datetime.timedelta(seconds=100)).isoformat(), "id": 2},
        ]

        sorted_metas = self.TimestampUtils.sort_by_timestamp(metas, reverse=False)
        assert sorted_metas[0]["id"] == 2  # Older first
        assert sorted_metas[1]["id"] == 1  # Newer second

    def test_sort_by_timestamp_empty_list(self):
        """Should handle empty list."""
        result = self.TimestampUtils.sort_by_timestamp([], reverse=True)
        assert result == []

    def test_sort_by_timestamp_none_values(self):
        """Should handle None metadata values gracefully."""
        now = datetime.datetime.now(datetime.timezone.utc)
        metas = [
            {"timestamp": now.isoformat(), "id": 1},
            None,
            {"timestamp": (now - datetime.timedelta(seconds=100)).isoformat(), "id": 2},
            {},
        ]

        sorted_metas = self.TimestampUtils.sort_by_timestamp(metas, reverse=True)
        # Should not crash, should keep None/empty at end
        assert len(sorted_metas) == 4
        assert sorted_metas[0]["id"] == 1  # Latest first

    def test_timestamp_from_iso_string_or_dict(self):
        """Should extract timestamp from either string or dict.get()."""
        now = datetime.datetime.now(datetime.timezone.utc)
        now_iso = now.isoformat()

        # From string
        ts1 = self.TimestampUtils.get_timestamp_value(now_iso)
        assert isinstance(ts1, datetime.datetime)

        # From dict
        ts2 = self.TimestampUtils.get_timestamp_value({"timestamp": now_iso})
        assert isinstance(ts2, datetime.datetime)

        # From None
        ts3 = self.TimestampUtils.get_timestamp_value(None)
        assert ts3 is None
