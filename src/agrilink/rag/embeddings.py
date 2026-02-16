"""Embedding generation service with caching."""

import logging
from functools import lru_cache
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from agrilink.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_embeddings() -> Embeddings:
    """
    Get the configured embeddings model.
    
    This function is cached to ensure we only load the model once,
    preventing memory issues and redundant downloads.
    
    Returns:
        Embeddings instance (OpenAI or HuggingFace)
    """
    settings = get_settings()
    
    # Use HuggingFace embeddings for Groq (free, 384 dimensions)
    # Groq provides LLM but not embeddings
    if settings.default_llm_provider == "groq":
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            
            logger.info("Loading HuggingFace embeddings (all-MiniLM-L6-v2, 384-dim)...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("Successfully loaded HuggingFace embeddings")
            return embeddings
            
        except ImportError:
            error_msg = (
                "HuggingFace dependencies not installed. "
                "Install with: pip install sentence-transformers langchain-huggingface"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)
            
    else:
        logger.info(f"Using OpenAI embeddings ({settings.embedding_model})")
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
