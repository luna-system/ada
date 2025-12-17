"""Context retrieval from RAG store and configuration.

@ai-indexable: core-refactor
@ai-purpose: Retrieves context data from various sources (RAG, filesystem, config)
@ai-dependencies: brain.rag_store, brain.config
"""
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging

from brain import rag_store, config

logger = logging.getLogger(__name__)


class ContextRetriever:
    """Retrieves context from RAG store and configuration files.
    
    This class handles all data retrieval operations needed for prompt building,
    separating retrieval logic from formatting and assembly.
    """

    def __init__(self):
        """Initialize the context retriever."""
        self.rag_store = rag_store
        self.config = config

    def get_persona(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Retrieve persona content from RAG store.
        
        Returns:
            (text, metadata) tuple or None if not found
        """
        try:
            return self.rag_store.load_persona_block()
        except Exception as e:
            logger.error(f"Error reading persona: {e}")
            return None

    def get_memories(
        self, 
        query: str, 
        k: int = 5, 
        entity: Optional[str] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve relevant memories from RAG store.
        
        Args:
            query: Search query for semantic similarity
            k: Maximum number of memories to return
            entity: Optional entity scope filter
            
        Returns:
            List of (text, metadata) tuples
        """
        try:
            return self.rag_store.retrieve_memories(query=query, k=k, entity=entity)
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    def get_faqs(
        self, 
        query: str, 
        k: int = 3
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve relevant FAQs from RAG store.
        
        Args:
            query: Search query for semantic similarity
            k: Maximum number of FAQs to return
            
        Returns:
            List of (text, metadata) tuples
        """
        try:
            return self.rag_store.retrieve_faqs(query=query, k=k)
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {e}")
            return []

    def get_turns(
        self, 
        query: str,
        k: int = 5,
        conversation_id: Optional[str] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve conversation turns.
        
        Args:
            query: Search query for semantic similarity  
            k: Maximum number of turns to return
            conversation_id: Optional conversation ID filter
            
        Returns:
            List of (text, metadata) tuples
        """
        if not conversation_id:
            return []
        
        try:
            return self.rag_store.retrieve_turns(
                query=query,
                k=k,
                conversation_id=conversation_id
            )
        except Exception as e:
            logger.error(f"Error retrieving conversation turns: {e}")
            return []
    
    def get_summaries(
        self,
        conversation_id: str,
        k: int = 3
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve conversation summaries.
        
        Args:
            conversation_id: Conversation ID to retrieve summaries for
            k: Maximum number of summaries to return
            
        Returns:
            List of (text, metadata) tuples
        """
        try:
            return self.rag_store.retrieve_summaries(
                conversation_id=conversation_id,
                k=k
            )
        except Exception as e:
            logger.error(f"Error retrieving summaries: {e}")
            return []
