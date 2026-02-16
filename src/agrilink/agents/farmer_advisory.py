"""Farmer Advisory Agent - provides personalized farming advice."""

import logging
from typing import Any, Dict, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class FarmerAdvisoryAgent(BaseAgent):
    """Agent for answering farming questions and providing personalized advice."""

    def __init__(self, **kwargs):
        """Initialize Farmer Advisory Agent."""
        super().__init__(agent_name="FarmerAdvisoryAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for farmer advisory."""
        return get_agent_prompt("farmer_advisory")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process farmer advisory request.
        
        Expected context keys:
            - question: Farmer's question
            - crop: Crop type (optional)
            - region: Geographic region (optional)
            - season: Current season (optional)
            - farm_size: Farm size (optional)
        """
        question = context.get("question", "")
        crop = context.get("crop", "")
        region = context.get("region", "")
        season = context.get("season", "")
        
        if not question:
            return self.create_response(
                recommendation="Please provide a specific question.",
                confidence=0.0,
                reasoning="No question provided",
                sources=[],
            )
        
        # Build context-aware query
        query_parts = [question]
        if crop:
            query_parts.append(f"for {crop}")
        if region:
            query_parts.append(f"in {region}")
        if season:
            query_parts.append(f"during {season}")
        
        query = " ".join(query_parts)
        
        # Retrieve relevant agricultural knowledge using semantic similarity
        # Note: We don't use metadata filters because documents are ingested with
        # minimal metadata (only 'category'). Semantic search is sufficient.
        knowledge = await self.retrieve_knowledge(
            query=query,
            filter=None,
        )
        
        if not knowledge.get("grounded", False):
            return self.create_response(
                recommendation="I don't have enough information in my knowledge base to answer this question accurately. "
                              "Please consult with a local agricultural expert or extension service.",
                confidence=0.0,
                reasoning="No relevant agricultural knowledge found.",
                sources=[],
                metadata={"needs_expert_consultation": True},
            )
        
        # Generate personalized advice
        advice_prompt = f"""Based on the retrieved agricultural knowledge, provide practical advice for the farmer's question.

Question: {question}
Context: Crop={crop}, Region={region}, Season={season}

Retrieved Knowledge:
{knowledge['answer']}

Provide:
1. Direct answer to the question
2. Step-by-step instructions (if applicable)
3. Important warnings or precautions
4. Best practices
5. Common mistakes to avoid

Be specific, practical, and cite sources using [Citation X] format.
"""
        
        advice = await self.reason(advice_prompt, context)
        
        # Add disclaimer if confidence is low
        final_advice = advice
        if knowledge.get("confidence", 1.0) < 0.7:
            final_advice += "\n\n⚠️ Note: This advice is based on limited information. " \
                           "Please verify with local agricultural experts before implementation."
        
        return self.create_response(
            recommendation=final_advice,
            confidence=knowledge.get("confidence", 0.5),
            reasoning="Based on agricultural best practices and knowledge base",
            sources=knowledge.get("sources", []),
            metadata={
                "question": question,
                "crop": crop,
                "region": region,
                "season": season,
            },
        )

    async def handle_event(self, event: Dict[str, Any]) -> Optional[AgentResponse]:
        """Handle farmer query events."""
        event_type = event.get("event_type", "")
        
        if event_type == "farmer_query":
            return await self.process({
                "question": event.get("question", ""),
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
                "season": event.get("season", ""),
            })
            
        elif event_type == "user_query":
            # Treat generic user query as farmer question
            return await self.process({
                "question": event.get("query", ""),
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
            })
        
        return None
