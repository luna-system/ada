"""Tests for response caching layer."""
import pytest
from datetime import datetime, timezone, timedelta
from brain.response_cache import ResponseCache, CachedResponse, ResponseCacheStats


class TestCachedResponse:
    """Test CachedResponse dataclass."""
    
    def test_is_expired_fresh_entry(self):
        """Fresh entries should not be expired."""
        entry = CachedResponse(
            key="test_key",
            response_text="response",
            request_type="chat",
            model="qwen2.5-coder:7b",
            created_at=datetime.now(timezone.utc),
            ttl_seconds=3600,
        )
        assert entry.is_expired() is False
    
    def test_is_expired_old_entry(self):
        """Old entries should be expired."""
        entry = CachedResponse(
            key="test_key",
            response_text="response",
            request_type="chat",
            model="qwen2.5-coder:7b",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            ttl_seconds=3600,  # 1 hour TTL, but entry is 2 hours old
        )
        assert entry.is_expired() is True
    
    def test_age_seconds(self):
        """Should calculate age correctly."""
        created = datetime.now(timezone.utc) - timedelta(seconds=30)
        entry = CachedResponse(
            key="test_key",
            response_text="response",
            request_type="chat",
            model="qwen2.5-coder:7b",
            created_at=created,
            ttl_seconds=3600,
        )
        age = entry.age_seconds()
        assert 29 <= age <= 31  # Allow 1 second tolerance


class TestResponseCache:
    """Test ResponseCache class."""
    
    def test_cache_miss(self):
        """Should return None on cache miss."""
        cache = ResponseCache(max_size=100)
        result = cache.get("nonexistent_key")
        assert result is None
        
        stats = cache.get_stats()
        assert stats.misses == 1
        assert stats.hits == 0
    
    def test_cache_hit(self):
        """Should return cached response on hit."""
        cache = ResponseCache(max_size=100)
        
        # Store response
        cache.set(
            cache_key="test_key",
            response_text="cached response",
            request_type="quick_query",
            model="qwen2.5-coder:7b",
            ttl_seconds=3600,
        )
        
        # Retrieve response
        result = cache.get("test_key")
        assert result == "cached response"
        
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 0
    
    def test_cache_expiration(self):
        """Should not return expired entries."""
        cache = ResponseCache(max_size=100)
        
        # Create entry with past timestamp
        entry = CachedResponse(
            key="old_key",
            response_text="old response",
            request_type="quick_query",
            model="qwen2.5-coder:7b",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            ttl_seconds=3600,  # 1 hour TTL
        )
        cache._cache["old_key"] = entry
        
        # Try to retrieve expired entry
        result = cache.get("old_key")
        assert result is None
        
        # Should count as miss
        stats = cache.get_stats()
        assert stats.misses == 1
        assert stats.expired == 1
        
        # Entry should be removed
        assert "old_key" not in cache._cache
    
    def test_lru_eviction(self):
        """Should evict least recently used entry when full."""
        cache = ResponseCache(max_size=3)
        
        # Fill cache
        cache.set("key1", "response1", "chat", "model", 3600)
        cache.set("key2", "response2", "chat", "model", 3600)
        cache.set("key3", "response3", "chat", "model", 3600)
        
        # Access key1 (moves to end)
        cache.get("key1")
        
        # Add key4 (should evict key2, the oldest unaccessed)
        cache.set("key4", "response4", "chat", "model", 3600)
        
        # key2 should be evicted
        assert cache.get("key2") is None
        assert cache.get("key1") == "response1"
        assert cache.get("key4") == "response4"
        
        stats = cache.get_stats()
        assert stats.evictions == 1
    
    def test_hit_count_tracking(self):
        """Should track hit counts correctly."""
        cache = ResponseCache(max_size=100)
        
        cache.set("key", "response", "chat", "model", 3600)
        
        # Hit multiple times
        cache.get("key")
        cache.get("key")
        cache.get("key")
        
        entry = cache._cache["key"]
        assert entry.hit_count == 3
    
    def test_invalidate_single(self):
        """Should invalidate specific key."""
        cache = ResponseCache(max_size=100)
        
        cache.set("key1", "response1", "chat", "model", 3600)
        cache.set("key2", "response2", "chat", "model", 3600)
        
        # Invalidate key1
        result = cache.invalidate("key1")
        assert result is True
        assert cache.get("key1") is None
        assert cache.get("key2") == "response2"
        
        # Try to invalidate again
        result = cache.invalidate("key1")
        assert result is False
    
    def test_invalidate_pattern(self):
        """Should invalidate all keys matching pattern."""
        cache = ResponseCache(max_size=100)
        
        cache.set("user:123:query1", "response1", "chat", "model", 3600)
        cache.set("user:123:query2", "response2", "chat", "model", 3600)
        cache.set("user:456:query1", "response3", "chat", "model", 3600)
        
        # Invalidate all user:123 entries
        count = cache.invalidate_pattern("user:123")
        assert count == 2
        
        assert cache.get("user:123:query1") is None
        assert cache.get("user:123:query2") is None
        assert cache.get("user:456:query1") == "response3"
    
    def test_cleanup_expired(self):
        """Should remove all expired entries."""
        cache = ResponseCache(max_size=100)
        
        # Add fresh entry
        cache.set("fresh", "response", "chat", "model", 3600)
        
        # Add expired entries manually
        for i in range(3):
            entry = CachedResponse(
                key=f"old_{i}",
                response_text=f"response_{i}",
                request_type="chat",
                model="model",
                created_at=datetime.now(timezone.utc) - timedelta(hours=2),
                ttl_seconds=3600,
            )
            cache._cache[f"old_{i}"] = entry
        
        # Cleanup
        removed = cache.cleanup_expired()
        assert removed == 3
        
        # Fresh entry should remain
        assert cache.get("fresh") == "response"
        
        stats = cache.get_stats()
        assert stats.expired == 3
        assert stats.total_entries == 1
    
    def test_get_entries_by_type(self):
        """Should filter entries by request type."""
        cache = ResponseCache(max_size=100)
        
        cache.set("code1", "response1", "code_completion", "qwen", 3600)
        cache.set("code2", "response2", "code_completion", "qwen", 3600)
        cache.set("query1", "response3", "quick_query", "qwen", 3600)
        
        code_entries = cache.get_entries_by_type("code_completion")
        assert len(code_entries) == 2
        
        query_entries = cache.get_entries_by_type("quick_query")
        assert len(query_entries) == 1
    
    def test_get_top_hits(self):
        """Should return most accessed entries."""
        cache = ResponseCache(max_size=100)
        
        # Add entries with different hit counts
        cache.set("key1", "response1", "chat", "model", 3600)
        cache.set("key2", "response2", "chat", "model", 3600)
        cache.set("key3", "response3", "chat", "model", 3600)
        
        # Hit different amounts
        for _ in range(5):
            cache.get("key1")
        for _ in range(2):
            cache.get("key2")
        cache.get("key3")
        
        top = cache.get_top_hits(limit=2)
        assert len(top) == 2
        assert top[0].key == "key1"  # 5 hits
        assert top[1].key == "key2"  # 2 hits
    
    def test_clear(self):
        """Should remove all entries."""
        cache = ResponseCache(max_size=100)
        
        cache.set("key1", "response1", "chat", "model", 3600)
        cache.set("key2", "response2", "chat", "model", 3600)
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        
        stats = cache.get_stats()
        assert stats.total_entries == 0
    
    def test_reset_stats(self):
        """Should reset statistics but keep entries."""
        cache = ResponseCache(max_size=100)
        
        cache.set("key", "response", "chat", "model", 3600)
        cache.get("key")
        cache.get("nonexistent")
        
        stats = cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        
        cache.reset_stats()
        
        stats = cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.total_entries == 1  # Entry still there


class TestCacheStats:
    """Test cache statistics."""
    
    def test_hit_rate_calculation(self):
        """Should calculate hit rate correctly."""
        cache = ResponseCache(max_size=100)
        
        cache.set("key1", "response1", "chat", "model", 3600)
        
        # 3 hits, 2 misses
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")
        cache.get("nonexistent1")
        cache.get("nonexistent2")
        
        stats = cache.get_stats()
        assert stats.hits == 3
        assert stats.misses == 2
        assert stats.hit_rate == 0.6  # 3 / (3 + 2)
    
    def test_avg_age_calculation(self):
        """Should calculate average entry age."""
        cache = ResponseCache(max_size=100)
        
        # Add entries with different ages
        now = datetime.now(timezone.utc)
        entry1 = CachedResponse(
            key="key1",
            response_text="response1",
            request_type="chat",
            model="model",
            created_at=now - timedelta(seconds=10),
            ttl_seconds=3600,
        )
        entry2 = CachedResponse(
            key="key2",
            response_text="response2",
            request_type="chat",
            model="model",
            created_at=now - timedelta(seconds=20),
            ttl_seconds=3600,
        )
        cache._cache["key1"] = entry1
        cache._cache["key2"] = entry2
        
        stats = cache.get_stats()
        # Average should be around 15 seconds
        assert 14 <= stats.avg_age_seconds <= 16


class TestCacheIntegration:
    """Integration tests for cache with router."""
    
    def test_code_completion_caching(self):
        """Should cache code completions with 1 hour TTL."""
        cache = ResponseCache(max_size=100)
        
        # Simulate router cache key
        cache_key = "code_completion:python:def_hello"
        
        cache.set(
            cache_key=cache_key,
            response_text="    print('Hello, World!')",
            request_type="code_completion",
            model="qwen2.5-coder:7b",
            ttl_seconds=3600,  # 1 hour
        )
        
        # Should be cached
        result = cache.get(cache_key)
        assert result == "    print('Hello, World!')"
        
        stats = cache.get_stats()
        assert stats.hits == 1
    
    def test_quick_query_caching(self):
        """Should cache quick queries with 24 hour TTL."""
        cache = ResponseCache(max_size=100)
        
        # Simulate router cache key
        cache_key = "quick_query:what_is_python"
        
        cache.set(
            cache_key=cache_key,
            response_text="Python is a high-level programming language...",
            request_type="quick_query",
            model="qwen2.5-coder:7b",
            ttl_seconds=86400,  # 24 hours
        )
        
        # Should be cached
        result = cache.get(cache_key)
        assert result == "Python is a high-level programming language..."
        
        entry = cache._cache[cache_key]
        assert entry.ttl_seconds == 86400
