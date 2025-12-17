"""Integration tests for cache with ContextRetriever."""
import pytest
from unittest.mock import Mock
from brain.context_cache import MultiTimescaleCache
from brain.prompt_builder.context_retriever import ContextRetriever


class TestPersonaCaching:
    """Test persona caching integration."""
    
    def test_first_persona_request_queries_rag(self, mock_config, mock_rag_store, sample_persona_text):
        """First persona request should query RAG store."""
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        result = retriever.get_persona()
        
        # Should have called RAG store
        mock_rag_store.load_persona_block.assert_called_once()
        assert result[0] == sample_persona_text
    
    def test_second_persona_request_uses_cache(self, mock_config, mock_rag_store, sample_persona_text):
        """Second persona request should use cached value."""
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        # First request
        retriever.get_persona()
        
        # Second request
        result = retriever.get_persona()
        
        # Should only call RAG once (first time)
        assert mock_rag_store.load_persona_block.call_count == 1
        assert result[0] == sample_persona_text
    
    def test_persona_cache_respects_ttl(self, mock_config, mock_rag_store):
        """Persona cache should respect TTL configuration."""
        # Set very short TTL for testing
        mock_config.CACHE_PERSONA_TTL = 1
        
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        # First request
        retriever.get_persona()
        
        # Wait for TTL to expire
        import time
        time.sleep(1.1)
        
        # Second request should query RAG again
        retriever.get_persona()
        
        assert mock_rag_store.load_persona_block.call_count == 2
    
    def test_invalidating_persona_clears_cache(self, mock_config, mock_rag_store):
        """Invalidating persona should force RAG query."""
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        # First request
        retriever.get_persona()
        
        # Invalidate cache
        cache.invalidate("persona")
        
        # Second request should query RAG again
        retriever.get_persona()
        
        assert mock_rag_store.load_persona_block.call_count == 2


class TestCacheMetrics:
    """Test cache metrics tracking."""
    
    def test_tracks_cache_hit_rate(self, mock_config, mock_rag_store):
        """Cache should track hit rate across requests."""
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        # First request (miss)
        retriever.get_persona()
        
        # Three more requests (hits)
        retriever.get_persona()
        retriever.get_persona()
        retriever.get_persona()
        
        stats = cache.get_stats()
        assert stats.hits == 3
        assert stats.misses == 1
        assert stats.hit_rate == 0.75
    
    def test_logs_cache_performance(self, mock_config, mock_rag_store, caplog):
        """Cache should log performance metrics."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        cache = MultiTimescaleCache(mock_config)
        retriever = ContextRetriever(mock_rag_store, mock_config, cache)
        
        # Trigger cache hit
        retriever.get_persona()
        retriever.get_persona()
        
        # Check for log messages about cache hits
        log_messages = [record.message.lower() for record in caplog.records]
        assert any("cache" in msg for msg in log_messages), f"No cache logs found in: {log_messages}"


class TestCacheWithoutInjection:
    """Test that ContextRetriever works without cache."""
    
    def test_retriever_works_without_cache(self, mock_config, mock_rag_store, sample_persona_text):
        """ContextRetriever should work if cache is None."""
        # Don't inject cache
        retriever = ContextRetriever(mock_rag_store, mock_config, cache=None)
        
        result = retriever.get_persona()
        
        # Should still query RAG and return result
        mock_rag_store.load_persona_block.assert_called_once()
        assert result[0] == sample_persona_text
    
    def test_without_cache_queries_every_time(self, mock_config, mock_rag_store):
        """Without cache, should query RAG every time."""
        retriever = ContextRetriever(mock_rag_store, mock_config, cache=None)
        
        retriever.get_persona()
        retriever.get_persona()
        retriever.get_persona()
        
        # Should query RAG every time
        assert mock_rag_store.load_persona_block.call_count == 3
