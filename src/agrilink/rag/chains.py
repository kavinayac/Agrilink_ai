"""LangChain retrieval chains with citation tracking."""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from agrilink.config import get_settings
from agrilink.rag.retriever import DocumentRetriever

logger = logging.getLogger(__name__)


class RAGChain:
    """RAG chain with citation tracking and confidence scoring."""

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        retriever: Optional[DocumentRetriever] = None,
    ):
        """Initialize RAG chain."""
        self.settings = get_settings()
        self.llm = llm or self._get_default_llm()
        self.retriever = retriever or DocumentRetriever()

    def _get_default_llm(self) -> BaseLLM:
        """Get default LLM based on settings."""
        if self.settings.default_llm_provider == "groq":
            try:
                from langchain_groq import ChatGroq
                return ChatGroq(
                    model=self.settings.default_model,
                    temperature=0.1,  # Low temperature for factual responses
                    groq_api_key=self.settings.groq_api_key,
                )
            except ImportError:
                raise ImportError(
                    "Groq dependencies not installed. "
                    "Install with: pip install langchain-groq groq"
                )
        elif self.settings.default_llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.settings.default_model,
                temperature=0.1,
                anthropic_api_key=self.settings.anthropic_api_key,
            )
        else:  # openai
            return ChatOpenAI(
                model=self.settings.default_model,
                temperature=0.1,
                openai_api_key=self.settings.openai_api_key,
            )

    async def query(
        self,
        question: str,
        filter: Optional[Dict[str, Any]] = None,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User question
            filter: Metadata filters for retrieval
            include_sources: Whether to include source documents in response
            
        Returns:
            Dictionary with 'answer', 'sources', and 'confidence' keys
        """
        # Retrieve relevant documents
        docs_with_metadata = await self.retriever.retrieve_with_metadata(
            query=question,
            filter=filter,
        )
        
        if not docs_with_metadata:
            return {
                "answer": "I don't have enough information in my knowledge base to answer this question accurately.",
                "sources": [],
                "confidence": 0.0,
                "grounded": False,
            }
        
        # Format context
        context = self._format_context_with_citations(docs_with_metadata)
        
        # Create prompt
        prompt = self._create_rag_prompt(question, context)
        
        # Get LLM response
        response = await self.llm.ainvoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)
        
        # Calculate confidence based on retrieval scores
        avg_score = sum(d["score"] for d in docs_with_metadata) / len(docs_with_metadata)
        confidence = min(avg_score, 1.0)
        
        # Format sources
        sources = []
        if include_sources:
            sources = [
                {
                    "source": doc["metadata"].get("source", "Unknown"),
                    "category": doc["metadata"].get("category", "general"),
                    "score": doc["score"],
                    "excerpt": doc["content"][:200] + "...",
                }
                for doc in docs_with_metadata
            ]
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "grounded": True,
        }

    def _format_context_with_citations(self, docs_with_metadata: List[Dict[str, Any]]) -> str:
        """Format documents with citation markers."""
        context_parts = []
        for i, doc in enumerate(docs_with_metadata, 1):
            source = doc["metadata"].get("source", "Unknown")
            category = doc["metadata"].get("category", "general")
            content = doc["content"]
            
            context_parts.append(
                f"[Citation {i} - Source: {source}, Category: {category}]\n{content}\n"
            )
        
        return "\n".join(context_parts)

    def _create_rag_prompt(self, question: str, context: str) -> str:
        """Create RAG prompt with strict grounding requirements."""
        template = """You are an agricultural expert assistant. Answer the question based ONLY on the provided context.

CRITICAL RULES:
1. Only use information from the context provided below
2. If the context doesn't contain enough information, say so explicitly
3. Cite sources using [Citation X] format when referencing information
4. Do not make assumptions or add information not in the context
5. Be specific and practical in your advice

Context:
{context}

Question: {question}

Answer (remember to cite sources):"""
        
        return template.format(context=context, question=question)

    async def query_with_category(
        self,
        question: str,
        category: str,
    ) -> Dict[str, Any]:
        """Query with category filter."""
        return await self.query(question, filter={"category": category})

    async def query_for_crop(
        self,
        question: str,
        crop: str,
    ) -> Dict[str, Any]:
        """Query with crop-specific filter."""
        return await self.query(question, filter={"crop": crop})

    async def query_for_region(
        self,
        question: str,
        region: str,
    ) -> Dict[str, Any]:
        """Query with region-specific filter."""
        return await self.query(question, filter={"region": region})


class ConversationalRAGChain(RAGChain):
    """RAG chain with conversation history support."""

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        retriever: Optional[DocumentRetriever] = None,
    ):
        """Initialize conversational RAG chain."""
        super().__init__(llm, retriever)
        self.conversation_history: List[Dict[str, str]] = []

    async def query_with_history(
        self,
        question: str,
        filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query with conversation history context."""
        # Add conversation history to the question context
        if self.conversation_history:
            history_context = "\n".join([
                f"User: {turn['question']}\nAssistant: {turn['answer']}"
                for turn in self.conversation_history[-3:]  # Last 3 turns
            ])
            enhanced_question = f"Previous conversation:\n{history_context}\n\nCurrent question: {question}"
        else:
            enhanced_question = question
        
        # Get response
        response = await self.query(enhanced_question, filter)
        
        # Store in history
        self.conversation_history.append({
            "question": question,
            "answer": response["answer"],
        })
        
        return response

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
