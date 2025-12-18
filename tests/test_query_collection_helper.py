"""
Test-driven development for _query_collection() helper method.

This test suite validates that the extracted helper correctly handles:
1. HTTP vs embedded mode branching (unified)
2. Embedding generation for HTTP mode
3. Query parameter passing
4. Result parsing and distance annotation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from brain.rag_store import RagStore


class TestQueryCollectionHelper:
    """Test the extracted _query_collection() helper method."""

    @pytest.fixture
    def rag_store_http(self):
        """RagStore instance in HTTP mode (mocked)."""
        store = RagStore.__new__(RagStore)
        store.use_http = True
        store.embedding_fn = Mock()
        store.col = MagicMock()
        return store

    @pytest.fixture
    def rag_store_embedded(self):
        """RagStore instance in embedded mode (mocked)."""
        store = RagStore.__new__(RagStore)
        store.use_http = False
        store.embedding_fn = Mock()
        store.col = MagicMock()
        return store

    def test_query_http_mode_generates_embeddings(self, rag_store_http):
        """In HTTP mode, _query_collection() should generate embeddings and pass them."""
        rag_store_http.use_http = True
        rag_store_http.embedding_fn = Mock(return_value=[[0.1, 0.2, 0.3]])
        rag_store_http.col.query = Mock(
            return_value={
                "documents": [["doc1", "doc2"]],
                "metadatas": [[{"key": "val1"}, {"key": "val2"}]],
                "distances": [[0.1, 0.2]],
            }
        )

        query_text = "test query"
        k = 2
        where_filter = {"type": "memory"}

        result = rag_store_http._query_collection(query_text, k, where_filter)

        # Verify embeddings were generated
        rag_store_http.embedding_fn.assert_called_once_with([query_text])

        # Verify query was called with embeddings (not texts)
        rag_store_http.col.query.assert_called_once()
        call_kwargs = rag_store_http.col.query.call_args.kwargs
        assert "query_embeddings" in call_kwargs
        assert call_kwargs["query_embeddings"] == [[0.1, 0.2, 0.3]]
        assert "query_texts" not in call_kwargs

        # Verify result structure
        assert result["documents"] == ["doc1", "doc2"]
        assert len(result["metadatas"]) == 2
        assert result["metadatas"][0]["distance"] == 0.1
        assert result["metadatas"][1]["distance"] == 0.2

    def test_query_embedded_mode_uses_text(self, rag_store_embedded):
        """In embedded mode, _query_collection() should pass query text directly."""
        rag_store_embedded.use_http = False
        rag_store_embedded.col.query = Mock(
            return_value={
                "documents": [["doc1"]],
                "metadatas": [[{"key": "val"}]],
                "distances": [[0.15]],
            }
        )

        query_text = "test query"
        k = 1
        where_filter = {"type": "memory"}

        result = rag_store_embedded._query_collection(query_text, k, where_filter)

        # Verify query was called with text (not embeddings)
        rag_store_embedded.col.query.assert_called_once()
        call_kwargs = rag_store_embedded.col.query.call_args.kwargs
        assert "query_texts" in call_kwargs
        assert call_kwargs["query_texts"] == [query_text]
        assert "query_embeddings" not in call_kwargs

        # Verify result
        assert result["documents"] == ["doc1"]
        assert result["metadatas"][0]["distance"] == 0.15

    def test_query_adds_distance_to_metadata(self, rag_store_http):
        """Distance values should be added to metadata for each result."""
        rag_store_http.use_http = True
        rag_store_http.embedding_fn = Mock(return_value=[[0.1]])
        rag_store_http.col.query = Mock(
            return_value={
                "documents": [["doc1", "doc2", "doc3"]],
                "metadatas": [[{}, {"x": "y"}, {"z": "w"}]],
                "distances": [[0.1, 0.2, 0.3]],
            }
        )

        result = rag_store_http._query_collection("query", 3, {"type": "test"})

        # All metadata entries should have distance added
        assert result["metadatas"][0]["distance"] == 0.1
        assert result["metadatas"][1]["distance"] == 0.2
        assert result["metadatas"][1]["x"] == "y"  # Original data preserved
        assert result["metadatas"][2]["distance"] == 0.3
        assert result["metadatas"][2]["z"] == "w"  # Original data preserved

    def test_query_passes_where_filter(self, rag_store_embedded):
        """Where filters should be passed through to query call."""
        rag_store_embedded.use_http = False
        rag_store_embedded.col.query = Mock(
            return_value={
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }
        )

        where = {"$and": [{"type": "memory"}, {"scope": {"$eq": "global"}}]}
        rag_store_embedded._query_collection("query", 5, where)

        call_kwargs = rag_store_embedded.col.query.call_args.kwargs
        assert call_kwargs["where"] == where

    def test_query_passes_n_results(self, rag_store_http):
        """n_results parameter should be passed correctly."""
        rag_store_http.use_http = True
        rag_store_http.embedding_fn = Mock(return_value=[[0.1]])
        rag_store_http.col.query = Mock(
            return_value={
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }
        )

        for k in [1, 5, 10, 20]:
            rag_store_http._query_collection("query", k, {})
            call_kwargs = rag_store_http.col.query.call_args.kwargs
            assert call_kwargs["n_results"] == k

    def test_query_handles_empty_results(self, rag_store_http):
        """Should handle empty result sets gracefully."""
        rag_store_http.use_http = True
        rag_store_http.embedding_fn = Mock(return_value=[[0.1]])
        rag_store_http.col.query = Mock(
            return_value={
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }
        )

        result = rag_store_http._query_collection("query", 5, {})

        assert result["documents"] == []
        assert result["metadatas"] == []

    def test_query_handles_mismatched_lengths(self, rag_store_http):
        """Should handle cases where metadata/distance lengths don't match docs."""
        rag_store_http.use_http = True
        rag_store_http.embedding_fn = Mock(return_value=[[0.1]])
        # Chroma might return mismatched lengths in edge cases
        rag_store_http.col.query = Mock(
            return_value={
                "documents": [["doc1", "doc2", "doc3"]],
                "metadatas": [[{}, {}]],  # Only 2 metadata entries
                "distances": [[0.1]],  # Only 1 distance
            }
        )

        result = rag_store_http._query_collection("query", 3, {})

        # Should not crash and should only annotate what has corresponding distance
        assert result["documents"] == ["doc1", "doc2", "doc3"]
        assert len(result["metadatas"]) == 2
        # First metadata should have distance
        assert result["metadatas"][0].get("distance") == 0.1
        # Second metadata should NOT have distance (no corresponding value)
        assert "distance" not in result["metadatas"][1]
