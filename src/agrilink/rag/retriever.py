"""Document retrieval with hybrid search and re-ranking."""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

from agrilink.config import get_settings
from agrilink.rag.embeddings import get_embeddings
from agrilink.rag.vector_store import VectorStoreBase, get_vector_store

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Advanced document retriever with filtering and re-ranking."""

    def __init__(self, vector_store: Optional[VectorStoreBase] = None):
        """Initialize document retriever."""
        self.settings = get_settings()
        if vector_store is None:
            embeddings = get_embeddings()
            self.vector_store = get_vector_store(embeddings)
        else:
            self.vector_store = vector_store

    async def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve (default from settings)
            filter: Metadata filters (e.g., {"category": "crops", "region": "punjab"})
            min_score: Minimum similarity score threshold
            
        Returns:
            List of relevant documents
        """
        k = k or self.settings.rag_top_k
        min_score = min_score or self.settings.rag_similarity_threshold
        
        # Perform similarity search with scores
        results = await self.vector_store.similarity_search_with_score(
            query=query,
            k=k * 2,  # Retrieve more for filtering
            filter=filter,
        )
        
        # Filter by minimum score
        filtered_results = [
            (doc, score) for doc, score in results if score >= min_score
        ]
        
        # Sort by score (descending) and take top k
        filtered_results.sort(key=lambda x: x[1], reverse=True)
        documents = [doc for doc, _ in filtered_results[:k]]
        
        logger.info(
            f"Retrieved {len(documents)} documents for query: '{query[:50]}...' "
            f"(filtered from {len(results)} results)"
        )
        
        return documents

    async def retrieve_with_metadata(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with metadata and scores.
        
        Returns:
            List of dicts with 'document', 'score', and 'metadata' keys
        """
        k = k or self.settings.rag_top_k
        min_score = min_score or self.settings.rag_similarity_threshold
        
        results = await self.vector_store.similarity_search_with_score(
            query=query,
            k=k * 2,
            filter=filter,
        )
        
        # Filter and format results
        formatted_results = []
        for doc, score in results:
            if score >= min_score:
                formatted_results.append({
                    "document": doc,
                    "content": doc.page_content,
                    "score": score,
                    "metadata": doc.metadata,
                })
        
        # Sort by score and take top k
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        return formatted_results[:k]

    async def retrieve_by_category(
        self,
        query: str,
        category: str,
        k: Optional[int] = None,
    ) -> List[Document]:
        """
        Retrieve documents filtered by category.
        
        Args:
            query: Search query
            category: Document category (e.g., "crops", "market", "policies")
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents from the specified category
        """
        return await self.retrieve(
            query=query,
            k=k,
            filter={"category": category},
        )

    async def retrieve_by_region(
        self,
        query: str,
        region: str,
        k: Optional[int] = None,
    ) -> List[Document]:
        """
        Retrieve documents filtered by region.
        
        Args:
            query: Search query
            region: Geographic region (e.g., "punjab", "maharashtra")
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents for the specified region
        """
        return await self.retrieve(
            query=query,
            k=k,
            filter={"region": region},
        )

    async def retrieve_by_crop(
        self,
        query: str,
        crop: str,
        k: Optional[int] = None,
    ) -> List[Document]:
        """
        Retrieve documents filtered by crop type.
        
        Args:
            query: Search query
            crop: Crop type (e.g., "wheat", "rice", "cotton")
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents for the specified crop
        """
        return await self.retrieve(
            query=query,
            k=k,
            filter={"crop": crop},
        )

    def format_context(self, documents: List[Document]) -> str:
        """
        Format retrieved documents into a context string for LLM.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string with citations
        """
        if not documents:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            category = doc.metadata.get("category", "general")
            
            context_parts.append(
                f"[Source {i}: {source} ({category})]\n{doc.page_content}\n"
            )
        
        return "\n".join(context_parts)

    async def get_context_for_query(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve and format context for a query.
        
        This is a convenience method that combines retrieval and formatting.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filter: Metadata filters
            
        Returns:
            Formatted context string ready for LLM consumption
        """
        documents = await self.retrieve(query=query, k=k, filter=filter)
        return self.format_context(documents)
