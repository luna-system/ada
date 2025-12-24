"""Tests for context cache with LRU eviction and semantic hashing."""

import time
import pytest
from brain.reasoning.context_cache import ContextCache, CachedResult


class TestContextCache:
    """Test context caching functionality."""
    
    def test_cache_initialization(self):
        """Test cache initializes with correct parameters."""
        cache = ContextCache(max_size=50, ttl_seconds=120.0, min_importance=0.8)
        
        assert cache.max_size == 50
        assert cache.ttl_seconds == 120.0
        assert cache.min_importance == 0.8
        assert len(cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = ContextCache()
        
        result = cache.get("brain_read_file", {"file": "test.py"})
        
        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0
    
    def test_cache_hit(self):
        """Test cache hit returns stored content."""
        cache = ContextCache()
        
        # Store result
        cache.set("brain_read_file", {"file": "test.py"}, "content here", importance=0.85)
        
        # Retrieve result
        result = cache.get("brain_read_file", {"file": "test.py"})
        
        assert result == "content here"
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_importance_threshold(self):
        """Test that low-importance results are not cached."""
        cache = ContextCache(min_importance=0.75)
        
        # Try to cache low-importance result
        cached = cache.set("brain_grep", {"pattern": "test"}, "result", importance=0.5)
        
        assert not cached  # Should reject
        assert len(cache) == 0
        
        # Cache high-importance result
        cached = cache.set("brain_read_file", {"file": "important.py"}, "result", importance=0.9)
        
        assert cached
        assert len(cache) == 1
    
    def test_semantic_hashing(self):
        """Test that semantically identical params generate same cache key."""
        cache = ContextCache()
        
        # Store with one param order
        cache.set("brain_grep", {"pattern": "test", "file": "main.py"}, "result1", importance=0.8)
        
        # Retrieve with different param order (should still hit!)
        result = cache.get("brain_grep", {"file": "main.py", "pattern": "test"})
        
        assert result == "result1"  # Same semantic key
        assert cache.hits == 1
    
    def test_lru_eviction(self):
        """Test LRU eviction when max_size is reached."""
        cache = ContextCache(max_size=3, min_importance=0.5)
        
        # Fill cache
        cache.set("tool1", {"a": 1}, "result1", importance=0.8)
        cache.set("tool2", {"b": 2}, "result2", importance=0.8)
        cache.set("tool3", {"c": 3}, "result3", importance=0.8)
        
        assert len(cache) == 3
        assert cache.evictions == 0
        
        # Add 4th item (should evict tool1)
        cache.set("tool4", {"d": 4}, "result4", importance=0.8)
        
        assert len(cache) == 3  # Still at max
        assert cache.evictions == 1
        
        # tool1 should be evicted (least recently used)
        result = cache.get("tool1", {"a": 1})
        assert result is None
        
        # tool2 should still be there
        result = cache.get("tool2", {"b": 2})
        assert result == "result2"
    
    def test_lru_access_updates_order(self):
        """Test that accessing an entry makes it most recent."""
        cache = ContextCache(max_size=3, min_importance=0.5)
        
        # Fill cache
        cache.set("tool1", {"a": 1}, "result1", importance=0.8)
        cache.set("tool2", {"b": 2}, "result2", importance=0.8)
        cache.set("tool3", {"c": 3}, "result3", importance=0.8)
        
        # Access tool1 (makes it most recent)
        cache.get("tool1", {"a": 1})
        
        # Add tool4 (should evict tool2, not tool1)
        cache.set("tool4", {"d": 4}, "result4", importance=0.8)
        
        # tool1 should still be there
        assert cache.get("tool1", {"a": 1}) == "result1"
        
        # tool2 should be evicted
        assert cache.get("tool2", {"b": 2}) is None
    
    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = ContextCache(ttl_seconds=0.1)  # 100ms TTL
        
        # Store result
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        
        # Immediate retrieval works
        assert cache.get("tool1", {"a": 1}) == "result1"
        
        # Wait for expiration
        time.sleep(0.15)
        
        # Should be expired now
        result = cache.get("tool1", {"a": 1})
        assert result is None
        assert cache.expirations == 1
    
    def test_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        cache = ContextCache(ttl_seconds=0.1)
        
        # Add multiple entries
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        cache.set("tool2", {"b": 2}, "result2", importance=0.9)
        cache.set("tool3", {"c": 3}, "result3", importance=0.9)
        
        assert len(cache) == 3
        
        # Wait for expiration
        time.sleep(0.15)
        
        # Clean up expired
        removed = cache.cleanup_expired()
        
        assert removed == 3
        assert len(cache) == 0
    
    def test_invalidate_all(self):
        """Test clearing entire cache."""
        cache = ContextCache()
        
        # Add entries
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        cache.set("tool2", {"b": 2}, "result2", importance=0.9)
        
        assert len(cache) == 2
        
        # Clear all
        removed = cache.invalidate()
        
        assert removed == 2
        assert len(cache) == 0
    
    def test_invalidate_by_tool(self):
        """Test invalidating entries for specific tool."""
        cache = ContextCache()
        
        # Add entries for different tools
        cache.set("brain_read_file", {"file": "a.py"}, "result1", importance=0.9)
        cache.set("brain_read_file", {"file": "b.py"}, "result2", importance=0.9)
        cache.set("brain_grep", {"pattern": "test"}, "result3", importance=0.9)
        
        assert len(cache) == 3
        
        # Invalidate only brain_read_file entries
        removed = cache.invalidate("brain_read_file")
        
        assert removed == 2
        assert len(cache) == 1
        
        # brain_grep should still be there
        assert cache.get("brain_grep", {"pattern": "test"}) == "result3"
    
    def test_access_count_tracking(self):
        """Test that access count is tracked correctly."""
        cache = ContextCache()
        
        # Store result
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        
        # Access multiple times
        cache.get("tool1", {"a": 1})
        cache.get("tool1", {"a": 1})
        cache.get("tool1", {"a": 1})
        
        # Check access count via cache internals
        cache_key = cache._make_cache_key("tool1", {"a": 1})
        entry = cache._cache[cache_key]
        
        assert entry.access_count == 3
    
    def test_statistics(self):
        """Test cache statistics reporting."""
        cache = ContextCache(max_size=10, ttl_seconds=300, min_importance=0.75)
        
        # Generate some activity
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        cache.get("tool1", {"a": 1})  # Hit
        cache.get("tool2", {"b": 2})  # Miss
        
        stats = cache.get_stats()
        
        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == 50.0
        assert stats["ttl_seconds"] == 300
        assert stats["min_importance"] == 0.75
    
    def test_repr(self):
        """Test string representation."""
        cache = ContextCache(max_size=100)
        cache.set("tool1", {"a": 1}, "result1", importance=0.9)
        cache.get("tool1", {"a": 1})
        
        repr_str = repr(cache)
        
        assert "ContextCache" in repr_str
        assert "size=1/100" in repr_str
        assert "hits=1" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
