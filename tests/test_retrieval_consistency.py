"""
Test-driven development for parametrized retrieval methods.

Tests that retrieve_memories, retrieve_turns, retrieve_faqs follow
a parametrizable template pattern for easier ML analysis.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from brain.rag_store import RagStore


class TestRetrievalMethodConsistency:
    """Test that retrieval methods follow consistent patterns."""

    @pytest.fixture
    def mock_store(self):
        """Mock RagStore instance."""
        store = RagStore.__new__(RagStore)
        store.use_http = False
        store.embedding_fn = Mock()
        store.col = MagicMock()
        store._query_collection = MagicMock()
        return store

    def test_retrieve_memories_uses_query_collection(self, mock_store):
        """retrieve_memories should use _query_collection helper."""
        mock_store._query_collection.return_value = {
            "documents": [],
            "metadatas": [],
            "distances": [],
        }

        # Should call _query_collection with type=memory filter
        mock_store.retrieve_memories("test query", k=3)

        # Verify _query_collection was called
        assert mock_store._query_collection.called

    def test_retrieve_turns_uses_query_collection(self, mock_store):
        """retrieve_turns should use _query_collection helper."""
        mock_store._query_collection.return_value = {
            "documents": [],
            "metadatas": [],
            "distances": [],
        }
        mock_store.col.get = Mock(return_value={"documents": [], "metadatas": []})

        # Should call _query_collection
        mock_store.retrieve_turns("test query", k=2, conversation_id="conv-1")

        # Verify _query_collection was called
        assert mock_store._query_collection.called

    def test_retrieve_faqs_uses_query_collection(self, mock_store):
        """retrieve_faqs should use _query_collection helper."""
        mock_store._query_collection.return_value = {
            "documents": ["FAQ 1"],
            "metadatas": [{"type": "faq"}],
            "distances": [0.1],
        }

        result = mock_store.retrieve_faqs("test query", k=2)

        # Verify _query_collection was called
        assert mock_store._query_collection.called
        # Should return list of tuples
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], tuple)
            assert len(result[0]) == 2  # (doc, meta)

    def test_retrieve_memories_returns_tuples(self, mock_store):
        """All retrieve methods should return List[Tuple[str, dict]]."""
        mock_store._query_collection.return_value = {
            "documents": ["doc1", "doc2"],
            "metadatas": [{"imp": 3}, {"imp": 2}],
            "distances": [0.1, 0.2],
        }
        mock_store.col.get = Mock(return_value={"documents": [], "metadatas": []})

        result = mock_store.retrieve_memories("test", k=2)

        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], dict)

    def test_retrieve_uses_where_filters(self, mock_store):
        """All retrieve methods should pass where filters to _query_collection."""
        mock_store._query_collection.return_value = {
            "documents": [],
            "metadatas": [],
            "distances": [],
        }
        mock_store.col.get = Mock(return_value={"documents": [], "metadatas": []})

        # Test memories with entity scope
        mock_store.retrieve_memories("test", k=3, entity="user")
        call_args = mock_store._query_collection.call_args_list

        # Should have called _query_collection at least once
        assert len(call_args) >= 1
        # Should pass where filter
        for call in call_args:
            where_arg = call.kwargs.get("where")
            assert where_arg is not None or "$and" in str(call)

    def test_retrieve_uses_k_parameter(self, mock_store):
        """All retrieve methods should respect k parameter."""
        mock_store._query_collection.return_value = {
            "documents": ["doc"] * 20,
            "metadatas": [{"id": i} for i in range(20)],
            "distances": [0.1] * 20,
        }
        mock_store.col.get = Mock(return_value={"documents": [], "metadatas": []})

        # Test with different k values
        for k in [1, 5, 10]:
            mock_store._query_collection.reset_mock()
            result = mock_store.retrieve_memories("test", k=k)
            
            # Verify it returns at most k items (or respects k in call)
            assert len(result) <= k

    def test_retrieve_methods_handle_empty_results(self, mock_store):
        """Should handle empty result gracefully."""
        mock_store._query_collection.return_value = {
            "documents": [],
            "metadatas": [],
            "distances": [],
        }
        mock_store.col.get = Mock(return_value={"documents": [], "metadatas": []})

        result_mem = mock_store.retrieve_memories("test", k=3)
        result_faq = mock_store.retrieve_faqs("test", k=2)

        assert result_mem == []
        assert result_faq == []

    def test_retrieve_methods_consistent_error_handling(self, mock_store):
        """All retrieve methods should handle exceptions gracefully."""
        # Make _query_collection raise exception
        mock_store._query_collection.side_effect = Exception("Query failed")
        mock_store.col.get = Mock(side_effect=Exception("Get failed"))

        # Should not crash, should return empty list
        result_mem = mock_store.retrieve_memories("test", k=3)
        assert isinstance(result_mem, list)

        mock_store._query_collection.reset_mock()
        mock_store._query_collection.side_effect = None
        mock_store._query_collection.return_value = {
            "documents": [],
            "metadatas": [],
            "distances": [],
        }

        result_faq = mock_store.retrieve_faqs("test", k=2)
        assert isinstance(result_faq, list)
