"""Response caching layer for router-optimized requests.

Caches complete LLM responses for quick queries and code completions.
Separate from context_cache.py which caches RAG context assembly.

This cache stores:
- Code completion responses (1 hour TTL)
- Quick query responses (24 hour TTL)
- Reasoning responses (disabled - too dynamic)
- Chat responses (disabled - conversation context changes)
"""
# @ai-indexable: core-service
# @ai-purpose: Response-level caching for router-optimized requests
# @ai-dependencies: collections, dataclasses, datetime, logging, hashlib
# @ai-related: brain/router.py, brain/context_cache.py

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """A cached LLM response with metadata."""
    key: str
    response_text: str
    request_type: str
    model: str
    created_at: datetime
    ttl_seconds: int
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > self.ttl_seconds
    
    def age_seconds(self) -> float:
        """Get age of this entry in seconds."""
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds()


@dataclass
class ResponseCacheStats:
    """Statistics for response cache performance."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0
    total_entries: int = 0
    hit_rate: float = 0.0
    avg_age_seconds: float = 0.0
    
    def calculate_hit_rate(self):
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total) if total > 0 else 0.0


class ResponseCache:
    """LRU cache with TTL for LLM responses.
    
    Design decisions:
    - In-memory (fast, simple, no Redis dependency)
    - LRU eviction (max_size limit)
    - Per-entry TTL (from router config)
    - Thread-safe (OrderedDict operations are atomic in CPython)
    
    Performance targets:
    - Cache lookup: < 1ms
    - Cache store: < 5ms
    - Memory: < 100MB for 1000 entries
    """
    
    def __init__(self, max_size: int = 1000):
        """Initialize response cache.
        
        Args:
            max_size: Maximum number of cached responses (LRU eviction)
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, CachedResponse] = OrderedDict()
        self._stats = ResponseCacheStats()
        logger.info(f"ResponseCache initialized with max_size={max_size}")
    
    def get(self, cache_key: str) -> Optional[str]:
        """Get cached response if available and not expired.
        
        Args:
            cache_key: Cache key (from router.generate_cache_key)
            
        Returns:
            Cached response text if hit, None if miss
        """
        entry = self._cache.get(cache_key)
        
        if entry is None:
            self._stats.misses += 1
            logger.debug(f"Cache MISS: {cache_key[:16]}...")
            return None
        
        # Check expiration
        if entry.is_expired():
            self._stats.expired += 1
            self._stats.misses += 1
            del self._cache[cache_key]
            logger.debug(f"Cache EXPIRED: {cache_key[:16]}... (age={entry.age_seconds():.1f}s)")
            return None
        
        # Cache hit!
        self._stats.hits += 1
        entry.hit_count += 1
        
        # Move to end (LRU)
        self._cache.move_to_end(cache_key)
        
        logger.debug(
            f"Cache HIT: {cache_key[:16]}... "
            f"(age={entry.age_seconds():.1f}s, hits={entry.hit_count})"
        )
        return entry.response_text
    
    def set(
        self,
        cache_key: str,
        response_text: str,
        request_type: str,
        model: str,
        ttl_seconds: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store response in cache with TTL.
        
        Args:
            cache_key: Cache key (from router.generate_cache_key)
            response_text: Complete LLM response
            request_type: Request type (for debugging)
            model: Model used (for debugging)
            ttl_seconds: Time to live in seconds
            metadata: Optional metadata dict
        """
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size:
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            self._stats.evictions += 1
            logger.debug(f"Cache EVICT: {evicted_key[:16]}... (age={evicted_entry.age_seconds():.1f}s)")
        
        # Create cache entry
        entry = CachedResponse(
            key=cache_key,
            response_text=response_text,
            request_type=request_type,
            model=model,
            created_at=datetime.now(timezone.utc),
            ttl_seconds=ttl_seconds,
            metadata=metadata or {}
        )
        
        self._cache[cache_key] = entry
        logger.debug(
            f"Cache SET: {cache_key[:16]}... "
            f"(type={request_type}, ttl={ttl_seconds}s, size={len(response_text)} chars)"
        )
    
    def invalidate(self, cache_key: str) -> bool:
        """Remove entry from cache.
        
        Args:
            cache_key: Cache key to invalidate
            
        Returns:
            True if entry was removed, False if not found
        """
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"Cache INVALIDATE: {cache_key[:16]}...")
            return True
        return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (simple substring match).
        
        Args:
            pattern: Substring to match in keys
            
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]
        
        if keys_to_remove:
            logger.info(f"Cache INVALIDATE_PATTERN: '{pattern}' removed {len(keys_to_remove)} entries")
        
        return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
            self._stats.expired += 1
        
        if expired_keys:
            logger.info(f"Cache CLEANUP: Removed {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> ResponseCacheStats:
        """Get current cache statistics.
        
        Returns:
            ResponseCacheStats with current metrics
        """
        stats = ResponseCacheStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            expired=self._stats.expired,
            total_entries=len(self._cache),
        )
        stats.calculate_hit_rate()
        
        # Calculate average age
        if self._cache:
            total_age = sum(e.age_seconds() for e in self._cache.values())
            stats.avg_age_seconds = total_age / len(self._cache)
        
        return stats
    
    def get_entries_by_type(self, request_type: str) -> List[CachedResponse]:
        """Get all cached entries for a specific request type.
        
        Args:
            request_type: Request type to filter by
            
        Returns:
            List of matching cache entries
        """
        return [
            entry for entry in self._cache.values()
            if entry.request_type == request_type
        ]
    
    def get_top_hits(self, limit: int = 10) -> List[CachedResponse]:
        """Get most frequently accessed cache entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of cache entries sorted by hit count (descending)
        """
        entries = sorted(
            self._cache.values(),
            key=lambda e: e.hit_count,
            reverse=True
        )
        return entries[:limit]
    
    def clear(self):
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEAR: Removed {count} entries")
    
    def reset_stats(self):
        """Reset statistics counters (keeps cache entries)."""
        self._stats = ResponseCacheStats()
        logger.info("Cache stats reset")


# Global response cache instance (initialized in app.py)
response_cache: Optional[ResponseCache] = None


def get_response_cache() -> ResponseCache:
    """Get or create global response cache instance."""
    global response_cache
    if response_cache is None:
        response_cache = ResponseCache(max_size=1000)
    return response_cache
