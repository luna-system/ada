"""Basic cache functionality tests."""
import pytest
import time
from datetime import datetime, timedelta, timezone
from brain.context_cache import MultiTimescaleCache, CacheEntry


class TestCacheBasics:
    """Test basic get/set/invalidate operations."""
    
    def test_set_and_get(self, mock_config):
        """Cache should store and retrieve values."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("test_key", "test_value", ttl_seconds=3600)
        result = cache.get("test_key")
        
        assert result == "test_value"
    
    def test_get_nonexistent_key(self, mock_config):
        """Getting non-existent key should return None."""
        cache = MultiTimescaleCache(mock_config)
        
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_set_overwrites_existing(self, mock_config):
        """Setting same key twice should overwrite."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key", "value1", ttl_seconds=3600)
        cache.set("key", "value2", ttl_seconds=3600)
        
        assert cache.get("key") == "value2"
    
    def test_invalidate_removes_entry(self, mock_config):
        """Invalidating should remove cache entry."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key", "value", ttl_seconds=3600)
        cache.invalidate("key")
        
        assert cache.get("key") is None
    
    def test_invalidate_nonexistent_key(self, mock_config):
        """Invalidating non-existent key should not error."""
        cache = MultiTimescaleCache(mock_config)
        
        # Should not raise
        cache.invalidate("nonexistent")


class TestCacheTTL:
    """Test time-to-live expiration."""
    
    def test_entry_expires_after_ttl(self, mock_config):
        """Cache entry should expire after TTL."""
        cache = MultiTimescaleCache(mock_config)
        
        # Set with 1 second TTL
        cache.set("key", "value", ttl_seconds=1)
        
        # Should exist immediately
        assert cache.get("key") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("key") is None
    
    def test_entry_valid_before_ttl(self, mock_config):
        """Cache entry should remain valid before TTL expires."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key", "value", ttl_seconds=10)
        
        # Should still be valid after 1 second
        time.sleep(1)
        assert cache.get("key") == "value"
    
    def test_cleanup_removes_expired_entries(self, mock_config):
        """Cleanup should remove expired entries."""
        cache = MultiTimescaleCache(mock_config)
        
        # Set entries with different TTLs
        cache.set("short", "value1", ttl_seconds=1)
        cache.set("long", "value2", ttl_seconds=10)
        
        # Wait for short TTL to expire
        time.sleep(1.1)
        
        # Run cleanup
        cache.cleanup_expired()
        
        # Short should be gone, long should remain
        assert "short" not in cache._cache
        assert "long" in cache._cache


class TestCacheStats:
    """Test metrics and statistics."""
    
    def test_tracks_cache_hits(self, mock_config):
        """Cache should track hit count."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key", "value", ttl_seconds=3600)
        
        # Access multiple times
        cache.get("key")
        cache.get("key")
        cache.get("key")
        
        stats = cache.get_stats()
        assert stats.hits == 3
    
    def test_tracks_cache_misses(self, mock_config):
        """Cache should track miss count."""
        cache = MultiTimescaleCache(mock_config)
        
        # Access non-existent keys
        cache.get("key1")
        cache.get("key2")
        
        stats = cache.get_stats()
        assert stats.misses == 2
    
    def test_calculates_hit_rate(self, mock_config):
        """Cache should calculate hit rate correctly."""
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key", "value", ttl_seconds=3600)
        
        # 3 hits, 2 misses = 60% hit rate
        cache.get("key")
        cache.get("key")
        cache.get("key")
        cache.get("nonexistent1")
        cache.get("nonexistent2")
        
        stats = cache.get_stats()
        assert stats.hit_rate == 0.6
    
    def test_hit_rate_zero_with_no_accesses(self, mock_config):
        """Hit rate should be 0 with no cache accesses."""
        cache = MultiTimescaleCache(mock_config)
        
        stats = cache.get_stats()
        assert stats.hit_rate == 0.0
    
    def test_tracks_token_savings(self, mock_config):
        """Cache should track token savings from hits."""
        cache = MultiTimescaleCache(mock_config)
        
        # Set with token count
        cache.set("key", "value", ttl_seconds=3600, token_count=1234)
        
        # Hit twice
        cache.get("key")
        cache.get("key")
        
        stats = cache.get_stats()
        # First access doesn't count as savings (would have been cached anyway)
        # Second access saves tokens
        assert stats.tokens_saved == 1234


class TestCacheEviction:
    """Test LRU eviction when cache is full."""
    
    def test_evicts_oldest_when_full(self, mock_config):
        """Cache should evict least recently used entry when full."""
        # Set small max size for testing
        mock_config.CACHE_MAX_ENTRIES = 3
        cache = MultiTimescaleCache(mock_config)
        
        # Fill cache
        cache.set("key1", "value1", ttl_seconds=3600)
        cache.set("key2", "value2", ttl_seconds=3600)
        cache.set("key3", "value3", ttl_seconds=3600)
        
        # Add one more - should evict key1 (oldest)
        cache.set("key4", "value4", ttl_seconds=3600)
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_accessing_entry_updates_lru(self, mock_config):
        """Accessing an entry should mark it as recently used."""
        mock_config.CACHE_MAX_ENTRIES = 3
        cache = MultiTimescaleCache(mock_config)
        
        cache.set("key1", "value1", ttl_seconds=3600)
        cache.set("key2", "value2", ttl_seconds=3600)
        cache.set("key3", "value3", ttl_seconds=3600)
        
        # Access key1 - makes it recently used
        cache.get("key1")
        
        # Add key4 - should evict key2 (oldest unused)
        cache.set("key4", "value4", ttl_seconds=3600)
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
