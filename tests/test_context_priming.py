"""Tests for context priming system (Phase 3 biomimetic features)."""

import pytest
from datetime import datetime, timezone, timedelta
from brain.context_priming import (
    ContextPrimer,
    SemanticNetwork,
    PrimingContext
)


class TestSemanticNetwork:
    """Test semantic network for priming relationships."""
    
    def test_add_relationship(self):
        """Test adding bidirectional relationships."""
        network = SemanticNetwork()
        network.add_relationship("specialist", "protocol", 0.9)
        
        # Both directions should exist
        specialist_related = network.get_related("specialist")
        protocol_related = network.get_related("protocol")
        
        assert "protocol" in specialist_related
        assert "specialist" in protocol_related
    
    def test_get_related_with_threshold(self):
        """Test filtering by strength threshold."""
        network = SemanticNetwork()
        network.add_relationship("topic", "strong", 0.9)
        network.add_relationship("topic", "weak", 0.3)
        
        # High threshold excludes weak
        strong_only = network.get_related("topic", threshold=0.5)
        assert "strong" in strong_only
        assert "weak" not in strong_only
        
        # Low threshold includes both
        all_related = network.get_related("topic", threshold=0.1)
        assert "strong" in all_related
        assert "weak" in all_related
    
    def test_default_network_has_ada_concepts(self):
        """Test default network includes Ada-specific concepts."""
        network = SemanticNetwork.load_default()
        
        # Check key Ada relationships
        specialist_related = network.get_related("specialist")
        assert "protocol" in specialist_related
        assert "activation" in specialist_related
        
        memory_related = network.get_related("memory")
        assert "rag" in memory_related
        assert "chroma" in memory_related
    
    def test_learn_from_cooccurrence(self):
        """Test learning relationships from memory co-occurrence."""
        network = SemanticNetwork()
        
        # Sample memories with topic co-occurrence
        memories = [
            {'metadata': {'topics': ['python', 'testing', 'pytest']}},
            {'metadata': {'topics': ['python', 'testing', 'unittest']}},
            {'metadata': {'topics': ['python', 'web', 'fastapi']}},
            {'metadata': {'topics': ['testing', 'pytest', 'fixtures']}},
        ]
        
        network.learn_from_cooccurrence(memories, min_cooccurrence=2)
        
        # Python and testing co-occur frequently
        python_related = network.get_related("python", threshold=0.0)
        assert "testing" in python_related
        
        # Testing and pytest co-occur
        testing_related = network.get_related("testing", threshold=0.0)
        assert "pytest" in testing_related


class TestContextPrimer:
    """Test context priming system."""
    
    def test_initialization_default_network(self):
        """Test primer initializes with default network."""
        primer = ContextPrimer()
        
        assert primer.network is not None
        assert primer.priming_enabled
        assert len(primer.primed_contexts) == 0
    
    def test_initialization_custom_network(self):
        """Test primer accepts custom semantic network."""
        custom_network = SemanticNetwork()
        custom_network.add_relationship("a", "b", 0.8)
        
        primer = ContextPrimer(semantic_network=custom_network)
        
        assert primer.network is custom_network
        assert "b" in primer.network.get_related("a")
    
    def test_prime_from_message_basic(self):
        """Test basic priming from current topics."""
        primer = ContextPrimer()
        
        # Prime based on "specialist" topic
        primed = primer.prime_from_message(
            message="Tell me about specialists",
            current_topics=["specialist"]
        )
        
        # Should prime related topics
        assert len(primed) > 0
        primed_topics = [ctx.topic for ctx in primed]
        
        # These should be primed (from default network)
        assert "protocol" in primed_topics or "activation" in primed_topics
    
    def test_prime_from_multiple_topics(self):
        """Test priming from multiple active topics."""
        primer = ContextPrimer()
        
        primed = primer.prime_from_message(
            message="How does memory and RAG work?",
            current_topics=["memory", "rag"]
        )
        
        # Should prime topics related to both memory and rag
        assert len(primed) > 0
        primed_topics = [ctx.topic for ctx in primed]
        
        # Memory-related priming
        assert any(topic in primed_topics for topic in ["chroma", "vector", "embedding"])
    
    def test_priming_disabled(self):
        """Test priming can be disabled."""
        primer = ContextPrimer()
        primer.priming_enabled = False
        
        primed = primer.prime_from_message(
            message="Test message",
            current_topics=["specialist"]
        )
        
        # Should return empty list when disabled
        assert len(primed) == 0
        assert len(primer.primed_contexts) == 0
    
    def test_is_primed(self):
        """Test checking if topic is primed."""
        primer = ContextPrimer()
        
        # Prime some topics
        primer.prime_from_message(
            message="Tell me about specialists",
            current_topics=["specialist"]
        )
        
        # Check primed state
        # Protocol should be primed (related to specialist)
        assert primer.is_primed("protocol")
        
        # Random topic should not be primed
        assert not primer.is_primed("random_topic_xyz")
    
    def test_get_priming_benefit(self):
        """Test getting priming benefit (for metrics)."""
        primer = ContextPrimer()
        
        # Prime topics
        primed = primer.prime_from_message(
            message="Test",
            current_topics=["specialist"]
        )
        
        # Get benefit for primed topic
        if len(primed) > 0:
            primed_topic = primed[0].topic
            benefit = primer.get_priming_benefit(primed_topic)
            
            # Should return non-zero benefit
            assert benefit > 0.0
            assert benefit <= 1.0
            
            # Should mark as accessed
            assert primer.primed_contexts[primed_topic].accessed
        
        # Unprimed topic returns zero benefit
        assert primer.get_priming_benefit("not_primed") == 0.0
    
    def test_priming_stats(self):
        """Test priming statistics tracking."""
        primer = ContextPrimer()
        
        # Prime topics
        primed = primer.prime_from_message(
            message="Test",
            current_topics=["specialist"]
        )
        
        # Access some primed topics
        if len(primed) > 0:
            primer.get_priming_benefit(primed[0].topic)
        
        # Get stats
        stats = primer.get_priming_stats()
        
        assert 'total_primed' in stats
        assert 'accessed' in stats
        assert 'hit_rate' in stats
        assert 'priming_enabled' in stats
        
        assert stats['total_primed'] == len(primed)
        assert stats['accessed'] >= 0
        assert 0.0 <= stats['hit_rate'] <= 1.0
    
    def test_clear_priming(self):
        """Test clearing primed contexts."""
        primer = ContextPrimer()
        
        # Prime topics
        primer.prime_from_message(
            message="Test",
            current_topics=["specialist"]
        )
        
        assert len(primer.primed_contexts) > 0
        
        # Clear
        primer.clear_priming()
        
        assert len(primer.primed_contexts) == 0
    
    def test_priming_context_dataclass(self):
        """Test PrimingContext dataclass."""
        now = datetime.now(timezone.utc)
        
        context = PrimingContext(
            topic="protocol",
            related_topics=["specialist", "interface"],
            priming_strength=0.9,
            primed_at=now
        )
        
        assert context.topic == "protocol"
        assert len(context.related_topics) == 2
        assert context.priming_strength == 0.9
        assert context.primed_at == now
        assert not context.accessed  # Default False
    
    def test_priming_strength_calculation(self):
        """Test priming strength is correctly calculated from network."""
        network = SemanticNetwork()
        network.add_relationship("a", "b", 0.9)
        network.add_relationship("a", "c", 0.3)
        
        primer = ContextPrimer(semantic_network=network)
        
        # Prime from topic "a"
        primed = primer.prime_from_message(
            message="Test",
            current_topics=["a"]
        )
        
        # Find primed contexts
        primed_dict = {ctx.topic: ctx for ctx in primed}
        
        # Stronger relationship should have higher priming strength
        if "b" in primed_dict and "c" in primed_dict:
            assert primed_dict["b"].priming_strength > primed_dict["c"].priming_strength
    
    def test_no_duplicate_priming(self):
        """Test topics aren't primed multiple times."""
        network = SemanticNetwork()
        # Both a and b relate to c
        network.add_relationship("a", "c", 0.8)
        network.add_relationship("b", "c", 0.8)
        
        primer = ContextPrimer(semantic_network=network)
        
        # Prime from both a and b
        primed = primer.prime_from_message(
            message="Test",
            current_topics=["a", "b"]
        )
        
        # Topic "c" should only appear once
        primed_topics = [ctx.topic for ctx in primed]
        assert primed_topics.count("c") == 1
