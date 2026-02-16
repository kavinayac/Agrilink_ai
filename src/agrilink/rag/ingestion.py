"""Document ingestion pipeline for agricultural knowledge."""

import logging
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agrilink.rag.embeddings import get_embeddings
from agrilink.rag.vector_store import VectorStoreBase, get_vector_store

logger = logging.getLogger(__name__)


class KnowledgeIngestionPipeline:
    """Pipeline for ingesting agricultural knowledge into the vector store."""

    def __init__(self, vector_store: Optional[VectorStoreBase] = None):
        """Initialize ingestion pipeline."""
        if vector_store is None:
            embeddings = get_embeddings()
            self.vector_store = get_vector_store(embeddings)
        else:
            self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def ingest_directory(
        self,
        directory_path: str,
        category: str,
        glob_pattern: str = "**/*.md",
        metadata: Optional[dict] = None,
    ) -> int:
        """
        Ingest all documents from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            category: Document category (e.g., "crops", "market", "policies")
            glob_pattern: File pattern to match
            metadata: Additional metadata to add to all documents
            
        Returns:
            Number of documents ingested
        """
        logger.info(f"Ingesting documents from {directory_path} (category: {category})")
        
        # Load documents
        loader = DirectoryLoader(
            directory_path,
            glob=glob_pattern,
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True,
        )
        documents = loader.load()
        
        # Add category and custom metadata
        base_metadata = {"category": category}
        if metadata:
            base_metadata.update(metadata)
        
        for doc in documents:
            doc.metadata.update(base_metadata)
            # Add source filename
            if "source" not in doc.metadata:
                doc.metadata["source"] = Path(doc.metadata.get("file_path", "")).name
        
        # Split documents
        split_docs = self.text_splitter.split_documents(documents)
        
        # Add to vector store
        await self.vector_store.add_documents(split_docs)
        
        logger.info(
            f"Ingested {len(documents)} documents ({len(split_docs)} chunks) "
            f"from {directory_path}"
        )
        
        return len(split_docs)

    async def ingest_file(
        self,
        file_path: str,
        category: str,
        metadata: Optional[dict] = None,
    ) -> int:
        """
        Ingest a single file.
        
        Args:
            file_path: Path to file
            category: Document category
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        logger.info(f"Ingesting file: {file_path}")
        
        # Load document
        if file_path.endswith(".md"):
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        
        # Add metadata
        base_metadata = {
            "category": category,
            "source": Path(file_path).name,
        }
        if metadata:
            base_metadata.update(metadata)
        
        for doc in documents:
            doc.metadata.update(base_metadata)
        
        # Split and ingest
        split_docs = self.text_splitter.split_documents(documents)
        await self.vector_store.add_documents(split_docs)
        
        logger.info(f"Ingested {len(split_docs)} chunks from {file_path}")
        return len(split_docs)

    async def ingest_text(
        self,
        text: str,
        category: str,
        source: str,
        metadata: Optional[dict] = None,
    ) -> int:
        """
        Ingest raw text content.
        
        Args:
            text: Text content to ingest
            category: Document category
            source: Source identifier
            metadata: Additional metadata
            
        Returns:
            Number of chunks created
        """
        # Create document
        doc_metadata = {
            "category": category,
            "source": source,
        }
        if metadata:
            doc_metadata.update(metadata)
        
        document = Document(page_content=text, metadata=doc_metadata)
        
        # Split and ingest
        split_docs = self.text_splitter.split_documents([document])
        await self.vector_store.add_documents(split_docs)
        
        logger.info(f"Ingested {len(split_docs)} chunks from text source: {source}")
        return len(split_docs)

    async def ingest_crop_knowledge(self, crops_dir: str = "./knowledge/crops") -> int:
        """Ingest crop-specific knowledge."""
        return await self.ingest_directory(
            directory_path=crops_dir,
            category="crops",
            metadata={"type": "agricultural_guide"},
        )

    async def ingest_market_knowledge(self, market_dir: str = "./knowledge/market") -> int:
        """Ingest market and pricing knowledge."""
        return await self.ingest_directory(
            directory_path=market_dir,
            category="market",
            metadata={"type": "market_intelligence"},
        )

    async def ingest_policy_knowledge(self, policy_dir: str = "./knowledge/policies") -> int:
        """Ingest government policies and regulations."""
        return await self.ingest_directory(
            directory_path=policy_dir,
            category="policies",
            metadata={"type": "regulatory"},
        )

    async def ingest_all_knowledge(self, knowledge_base_dir: str = "./knowledge") -> dict:
        """
        Ingest all knowledge from the knowledge base directory.
        
        Returns:
            Dictionary with ingestion statistics
        """
        base_path = Path(knowledge_base_dir)
        stats = {}
        
        # Ingest crops
        crops_path = base_path / "crops"
        if crops_path.exists():
            stats["crops"] = await self.ingest_crop_knowledge(str(crops_path))
        
        # Ingest market data
        market_path = base_path / "market"
        if market_path.exists():
            stats["market"] = await self.ingest_market_knowledge(str(market_path))
        
        # Ingest policies
        policy_path = base_path / "policies"
        if policy_path.exists():
            stats["policies"] = await self.ingest_policy_knowledge(str(policy_path))
        
        total = sum(stats.values())
        logger.info(f"Total ingestion complete: {total} chunks across {len(stats)} categories")
        
        return stats
