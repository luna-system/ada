"""Multi-timescale context caching system.

Phase 1: Persona caching with 24-hour TTL
Future phases: FAQ, memories, conversation caching
"""
import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    value: str
    timestamp: datetime
    ttl_seconds: int
    hits: int = 0
    token_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has exceeded TTL."""
        age = (datetime.now(timezone.utc) - self.timestamp).total_seconds()
        return age > self.ttl_seconds
    
    def increment_hit(self):
        """Record a cache hit."""
        self.hits += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int
    misses: int
    hit_rate: float
    tokens_saved: int
    entries: int


class MultiTimescaleCache:
    """Time-aware caching with TTL and LRU eviction.
    
    Caches context at different timescales based on update frequency:
    - Persona: 24 hours (rarely changes)
    - FAQ: 24 hours (rarely changes)
    - Memories: 5 minutes (more dynamic)
    - Conversation: 1 hour (session-based)
    """
    
    def __init__(self, config):
        """Initialize cache with configuration.
        
        Args:
            config: Config object with cache settings (TTLs, max entries)
        """
        self.config = config
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        
        logger.info(
            f"Cache initialized: max_entries={config.CACHE_MAX_ENTRIES}, "
            f"persona_ttl={config.CACHE_PERSONA_TTL}s"
        )
    
    def get(self, key: str) -> Optional[str]:
        """Get cached value if still valid.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if valid, None if expired/missing
        """
        if key not in self._cache:
            self._misses += 1
            logger.debug(f"Cache miss: {key}")
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if entry.is_expired():
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            del self._cache[key]
            return None
        
        # Cache hit!
        self._hits += 1
        entry.increment_hit()
        
        # Move to end (LRU)
        self._cache.move_to_end(key)
        
        logger.debug(
            f"Cache hit: {key}, hits={entry.hits}, "
            f"tokens={entry.token_count}"
        )
        
        return entry.value
    
    def set(
        self, 
        key: str, 
        value: str, 
        ttl_seconds: int,
        token_count: int = 0
    ):
        """Cache value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            token_count: Optional token count for metrics
        """
        # Check if we need to evict
        if len(self._cache) >= self.config.CACHE_MAX_ENTRIES:
            if key not in self._cache:
                # Evict oldest (first in OrderedDict)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"Evicted oldest entry: {oldest_key}")
        
        # Store entry
        entry = CacheEntry(
            value=value,
            timestamp=datetime.now(timezone.utc),
            ttl_seconds=ttl_seconds,
            token_count=token_count
        )
        
        self._cache[key] = entry
        logger.debug(
            f"Cached: {key}, ttl={ttl_seconds}s, "
            f"tokens={token_count}"
        )
    
    def invalidate(self, key: str):
        """Manually invalidate cache entry.
        
        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Invalidated: {key}")
    
    def cleanup_expired(self):
        """Remove all expired entries.
        
        Should be called periodically (e.g., every 5 minutes).
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> CacheStats:
        """Return cache performance statistics.
        
        Returns:
            CacheStats with hits, misses, hit rate, tokens saved
        """
        total_accesses = self._hits + self._misses
        hit_rate = self._hits / total_accesses if total_accesses > 0 else 0.0
        
        # Calculate tokens saved (hits * token_count, minus first access)
        tokens_saved = sum(
            entry.token_count * (entry.hits - 1)
            for entry in self._cache.values()
            if entry.hits > 0
        )
        
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            hit_rate=hit_rate,
            tokens_saved=tokens_saved,
            entries=len(self._cache)
        )
