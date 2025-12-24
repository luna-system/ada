"""Context caching for reasoning loop with LRU eviction and semantic hashing.

Caches high-importance tool results to avoid redundant computation. Uses:
- Semantic hashing (MD5 of normalized content) for cache keys
- LRU eviction when cache is full
- TTL-based expiration for freshness
- Importance threshold filtering (only cache high-value results)
"""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class CachedResult:
    """A cached tool result with metadata."""
    content: str
    tool_name: str
    importance: float
    timestamp: float
    access_count: int = 0
    
    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if this entry has exceeded its TTL."""
        return time.time() - self.timestamp > ttl_seconds


class ContextCache:
    """LRU cache for high-importance tool results with semantic hashing.
    
    Design principles:
    - Only cache results with importance ≥ threshold (default 0.75)
    - Use semantic hashing to detect similar content
    - LRU eviction when max_size is reached
    - TTL-based expiration for time-sensitive data
    - Track hit/miss rates for optimization
    
    Example:
        cache = ContextCache(max_size=100, ttl_seconds=300, min_importance=0.75)
        
        # Try to get from cache
        if cached := cache.get("brain_read_file", {"file": "test.py"}):
            logger.info("Cache HIT!")
            return cached
        
        # Cache miss, execute tool
        result = execute_tool(...)
        cache.set("brain_read_file", {"file": "test.py"}, result, importance=0.85)
    """
    
    def __init__(
        self,
        max_size: int = 100,
        ttl_seconds: float = 300.0,  # 5 minutes default
        min_importance: float = 0.75,  # Only cache high-importance results
    ):
        """Initialize context cache.
        
        Args:
            max_size: Maximum number of entries before LRU eviction
            ttl_seconds: Time-to-live for cached entries
            min_importance: Minimum importance score to cache (0.0-1.0)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.min_importance = min_importance
        
        # OrderedDict maintains insertion order for LRU
        self._cache: OrderedDict[str, CachedResult] = OrderedDict()
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        
        logger.info(
            f"🗄️ Context cache initialized: "
            f"max_size={max_size}, ttl={ttl_seconds}s, min_importance={min_importance}"
        )
    
    def _make_cache_key(self, tool_name: str, params: dict) -> str:
        """Generate semantic hash from tool name + params.
        
        Uses MD5 for fast hashing. The key format is:
        {tool_name}:{md5_of_normalized_params}
        
        Args:
            tool_name: Name of the tool (e.g., "brain_read_file")
            params: Tool parameters dict
            
        Returns:
            Cache key string
        """
        # Normalize params to consistent string representation
        # Sort keys to ensure same dict with different order = same hash
        normalized = str(sorted(params.items()))
        param_hash = hashlib.md5(normalized.encode()).hexdigest()[:12]  # First 12 chars
        return f"{tool_name}:{param_hash}"
    
    def get(self, tool_name: str, params: dict) -> Optional[str]:
        """Retrieve cached result if available and fresh.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Cached content string if hit, None if miss
        """
        cache_key = self._make_cache_key(tool_name, params)
        
        if cache_key not in self._cache:
            self.misses += 1
            logger.debug(f"💨 Cache MISS: {cache_key}")
            return None
        
        entry = self._cache[cache_key]
        
        # Check if expired
        if entry.is_expired(self.ttl_seconds):
            logger.debug(f"⏰ Cache entry expired: {cache_key}")
            del self._cache[cache_key]
            self.expirations += 1
            self.misses += 1
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(cache_key)
        entry.access_count += 1
        self.hits += 1
        
        hit_rate = self.hits / (self.hits + self.misses) * 100 if (self.hits + self.misses) > 0 else 0
        logger.info(
            f"✨ Cache HIT: {cache_key} "
            f"(accessed {entry.access_count}x, importance={entry.importance:.2f}, "
            f"hit_rate={hit_rate:.1f}%)"
        )
        
        return entry.content
    
    def set(
        self,
        tool_name: str,
        params: dict,
        content: str,
        importance: float,
    ) -> bool:
        """Cache a tool result if it meets importance threshold.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            content: Result content to cache
            importance: Importance score (0.0-1.0)
            
        Returns:
            True if cached, False if below threshold or other reason
        """
        # Don't cache low-importance results
        if importance < self.min_importance:
            logger.debug(
                f"🚫 Not caching (low importance): {tool_name} "
                f"(importance={importance:.2f} < {self.min_importance})"
            )
            return False
        
        cache_key = self._make_cache_key(tool_name, params)
        
        # Create cache entry
        entry = CachedResult(
            content=content,
            tool_name=tool_name,
            importance=importance,
            timestamp=time.time(),
            access_count=0,
        )
        
        # Check if we need to evict (LRU)
        if len(self._cache) >= self.max_size and cache_key not in self._cache:
            # Remove least recently used (first item)
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            self.evictions += 1
            logger.debug(
                f"🗑️ LRU eviction: {evicted_key} "
                f"(accessed {evicted_entry.access_count}x, importance={evicted_entry.importance:.2f})"
            )
        
        # Add to cache (or update if exists)
        self._cache[cache_key] = entry
        self._cache.move_to_end(cache_key)  # Mark as most recently used
        
        logger.info(
            f"💾 Cached result: {cache_key} "
            f"(importance={importance:.2f}, size={len(self._cache)}/{self.max_size})"
        )
        
        return True
    
    def invalidate(self, tool_name: Optional[str] = None) -> int:
        """Invalidate cache entries.
        
        Args:
            tool_name: If provided, only invalidate entries for this tool.
                      If None, invalidate entire cache.
        
        Returns:
            Number of entries invalidated
        """
        if tool_name is None:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Cache cleared: {count} entries invalidated")
            return count
        
        # Invalidate specific tool
        keys_to_remove = [
            key for key, entry in self._cache.items()
            if entry.tool_name == tool_name
        ]
        
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"🧹 Invalidated {len(keys_to_remove)} entries for tool: {tool_name}")
        return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired(self.ttl_seconds)
        ]
        
        for key in expired_keys:
            del self._cache[key]
            self.expirations += 1
        
        if expired_keys:
            logger.info(f"⏰ Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate, evictions, etc.
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "evictions": self.evictions,
            "expirations": self.expirations,
            "ttl_seconds": self.ttl_seconds,
            "min_importance": self.min_importance,
        }
    
    def __len__(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"ContextCache("
            f"size={stats['size']}/{stats['max_size']}, "
            f"hits={stats['hits']}, "
            f"misses={stats['misses']}, "
            f"hit_rate={stats['hit_rate_percent']:.1f}%"
            f")"
        )
