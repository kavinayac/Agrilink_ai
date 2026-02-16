"""Vector store implementations for RAG system."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from agrilink.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreBase(ABC):
    """Base class for vector store implementations."""

    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with relevance scores."""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by IDs."""
        pass


class PineconeVectorStore(VectorStoreBase):
    """Pinecone vector store implementation (v5 compatible)."""

    def __init__(self, embeddings: Embeddings):
        settings = get_settings()

        try:
            from pinecone import Pinecone
            from langchain_pinecone import PineconeVectorStore as LangChainPinecone

            if not settings.pinecone_api_key:
                raise ValueError("PINECONE_API_KEY not set")

            if not settings.pinecone_index_name:
                raise ValueError("PINECONE_INDEX_NAME not set")

            # Initialize Pinecone client (v5 style)
            pc = Pinecone(api_key=settings.pinecone_api_key)

            # Connect to existing index
            self.store = LangChainPinecone.from_existing_index(
                index_name=settings.pinecone_index_name,
                embedding=embeddings,
            )

            logger.info(
                f"Initialized Pinecone vector store: {settings.pinecone_index_name}"
            )

        except ImportError as e:
            logger.error(f"Failed to import Pinecone dependencies: {e}")
            raise ImportError(
                f"Install with: pip install pinecone langchain-pinecone. Error: {e}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize Pinecone: {e}") from e

    async def add_documents(self, documents: List[Document]) -> List[str]:
        return self.store.add_documents(documents)

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return self.store.similarity_search(
            query=query,
            k=k,
            filter=filter,
        )

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        return self.store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )

    async def delete(self, ids: List[str]) -> None:
        self.store.delete(ids=ids)


class ChromaVectorStore(VectorStoreBase):
    """Chroma vector store implementation."""

    def __init__(self, embeddings: Embeddings):
        settings = get_settings()

        try:
            from langchain_community.vectorstores import Chroma

            self.store = Chroma(
                collection_name="agrilink_knowledge",
                embedding_function=embeddings,
                persist_directory=str(settings.data_dir / "chroma"),
            )

            logger.info("Initialized Chroma vector store")

        except ImportError as e:
            logger.error(f"Failed to import Chroma: {e}")
            raise ImportError("Install with: pip install chromadb")

        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {e}")
            raise e

    async def add_documents(self, documents: List[Document]) -> List[str]:
        return self.store.add_documents(documents)

    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return self.store.similarity_search(
            query=query,
            k=k,
            filter=filter,
        )

    async def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[Document, float]]:
        return self.store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )

    async def delete(self, ids: List[str]) -> None:
        self.store.delete(ids=ids)


def get_vector_store(embeddings: Embeddings) -> VectorStoreBase:
    """Factory function to get the configured vector store."""
    settings = get_settings()

    if settings.vector_db_type == "pinecone":
        return PineconeVectorStore(embeddings)
    elif settings.vector_db_type == "chroma":
        return ChromaVectorStore(embeddings)
    else:
        raise ValueError(f"Unsupported vector store type: {settings.vector_db_type}")
