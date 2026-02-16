"""Base agent class with RAG integration and tool support."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI

from agrilink.config import get_settings
from agrilink.rag.chains import RAGChain
from agrilink.rag.retriever import DocumentRetriever

logger = logging.getLogger(__name__)


class AgentResponse:
    """Structured agent response."""

    def __init__(
        self,
        agent_name: str,
        recommendation: str,
        confidence: float,
        reasoning: str,
        sources: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize agent response."""
        self.agent_name = agent_name
        self.recommendation = recommendation
        self.confidence = confidence
        self.reasoning = reasoning
        self.sources = sources
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "sources": self.sources,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Base class for all AgriLink agents."""

    def __init__(
        self,
        agent_name: str,
        llm: Optional[BaseLLM] = None,
        rag_chain: Optional[RAGChain] = None,
    ):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent
            llm: Language model (uses default if not provided)
            rag_chain: RAG chain for knowledge retrieval
        """
        self.agent_name = agent_name
        self.settings = get_settings()
        self.llm = llm or self._get_default_llm()
        self.rag_chain = rag_chain or RAGChain(llm=self.llm)
        
        logger.info(f"Initialized {self.agent_name}")

    def _get_default_llm(self) -> BaseLLM:
        """Get default LLM from settings."""
        if self.settings.default_llm_provider == "groq":
            try:
                from langchain_groq import ChatGroq
                return ChatGroq(
                    model=self.settings.default_model,
                    temperature=0.2,
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
                temperature=0.2,
                anthropic_api_key=self.settings.anthropic_api_key,
            )
        else:  # openai
            return ChatOpenAI(
                model=self.settings.default_model,
                temperature=0.2,
                openai_api_key=self.settings.openai_api_key,
            )

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process input and generate response.
        
        Args:
            context: Input context with relevant information
            
        Returns:
            AgentResponse with recommendation and reasoning
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    async def retrieve_knowledge(
        self,
        query: str,
        filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge using RAG.
        
        This is the MANDATORY method for all agents to access knowledge.
        Agents MUST use this before making recommendations.
        
        Args:
            query: Query for knowledge retrieval
            filter: Optional metadata filters
            
        Returns:
            RAG response with answer, sources, and confidence
        """
        logger.info(f"[{self.agent_name}] Retrieving knowledge for: {query[:100]}...")
        response = await self.rag_chain.query(query, filter=filter)
        
        if not response.get("grounded", False):
            logger.warning(f"[{self.agent_name}] No grounded knowledge found for query")
        
        return response

    async def reason(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Use LLM for reasoning with the agent's system prompt.
        
        Args:
            prompt: Reasoning prompt
            context: Additional context
            
        Returns:
            LLM response
        """
        system_prompt = self.get_system_prompt()
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt += f"\n\nContext:\n{context_str}"
        
        response = await self.llm.ainvoke(full_prompt)
        return response.content if hasattr(response, "content") else str(response)

    def validate_response(self, response: AgentResponse) -> bool:
        """
        Validate agent response meets safety requirements.
        
        Args:
            response: Agent response to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if response has sources (RAG grounding)
        if self.settings.enable_rag_validation and not response.sources:
            logger.warning(f"[{self.agent_name}] Response lacks RAG grounding")
            return False
        
        # Check confidence threshold
        if response.confidence < self.settings.minimum_confidence_for_action:
            logger.warning(
                f"[{self.agent_name}] Confidence {response.confidence} "
                f"below threshold {self.settings.minimum_confidence_for_action}"
            )
            return False
        
        return True

    def create_response(
        self,
        recommendation: str,
        confidence: float,
        reasoning: str,
        sources: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Create a structured agent response.
        
        Args:
            recommendation: The agent's recommendation
            confidence: Confidence score (0.0 to 1.0)
            reasoning: Explanation of the reasoning
            sources: Source documents used
            metadata: Additional metadata
            
        Returns:
            AgentResponse object
        """
        return AgentResponse(
            agent_name=self.agent_name,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            sources=sources,
            metadata=metadata,
        )

    async def handle_event(self, event: Dict[str, Any]) -> Optional[AgentResponse]:
        """
        Handle an event and potentially generate a response.
        
        Args:
            event: Event data
            
        Returns:
            AgentResponse if the agent has a recommendation, None otherwise
        """
        # Default implementation - subclasses can override
        logger.info(f"[{self.agent_name}] Received event: {event.get('type', 'unknown')}")
        return None
