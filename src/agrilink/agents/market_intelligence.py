"""Market Intelligence Agent - monitors prices and advises on timing."""

import logging
from typing import Any, Dict, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class MarketIntelligenceAgent(BaseAgent):
    """Agent for market price monitoring and buy/sell timing advice."""

    def __init__(self, **kwargs):
        """Initialize Market Intelligence Agent."""
        super().__init__(agent_name="MarketIntelligenceAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for market intelligence."""
        return get_agent_prompt("market_intelligence")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process market intelligence request.
        
        Expected context keys:
            - crop: Crop type (e.g., "wheat", "rice")
            - region: Geographic region
            - action: "buy" or "sell"
            - quantity: Optional quantity
            - current_price: Optional current market price
        """
        crop = context.get("crop", "")
        region = context.get("region", "")
        action = context.get("action", "analyze")
        
        # Prepare filter
        filter_dict = {"category": "market"}
        if crop:
            filter_dict["crop"] = crop
        if region:
            filter_dict["region"] = region

        # Retrieve market knowledge
        query = f"Market prices and trends for {crop} in {region}. Supply and demand analysis."
        knowledge = await self.retrieve_knowledge(
            query=query,
            filter=filter_dict,
        )
        
        if not knowledge.get("grounded", False):
            return self.create_response(
                recommendation="Insufficient market data available for this crop and region.",
                confidence=0.0,
                reasoning="No market data found in knowledge base.",
                sources=[],
                metadata={"requires_external_api": True},
            )
        
        # Analyze market conditions
        analysis_prompt = f"""Based on the retrieved market knowledge, analyze the market for {crop} in {region}.

Retrieved Knowledge:
{knowledge['answer']}

Provide:
1. Current market assessment
2. Price trend analysis
3. Recommendation for {action} action
4. Risk factors
5. Optimal timing advice

Format your response as:
RECOMMENDATION: [clear buy/sell/hold/wait recommendation]
REASONING: [detailed explanation]
CONFIDENCE: [0.0 to 1.0]
RISKS: [key risk factors]
"""
        
        analysis = await self.reason(analysis_prompt, context)
        
        # Parse analysis (simplified - in production, use structured output)
        recommendation = self._extract_section(analysis, "RECOMMENDATION")
        reasoning = self._extract_section(analysis, "REASONING")
        confidence_str = self._extract_section(analysis, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else knowledge.get("confidence", 0.5)
        except ValueError:
            confidence = knowledge.get("confidence", 0.5)
        
        return self.create_response(
            recommendation=recommendation or analysis,
            confidence=min(confidence, knowledge.get("confidence", 1.0)),
            reasoning=reasoning or "Based on market data analysis",
            sources=knowledge.get("sources", []),
            metadata={
                "crop": crop,
                "region": region,
                "action": action,
            },
        )

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted text."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{section_name}:"):
                return line.split(":", 1)[1].strip()
        return ""

    async def handle_event(self, event: Dict[str, Any]) -> Optional[AgentResponse]:
        """Handle market-related events."""
        event_type = event.get("event_type", "")
        
        if event_type == "price_update":
            # Process price update event
            return await self.process({
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
                "current_price": event.get("price", 0),
                "action": "analyze",
            })
            
        elif event_type == "user_query":
            # Process general user query as market analysis
            # Only if it seems relevant to markets (simple heuristic or just always try)
            # For now, we'll try to process it if crop/region are present
            return await self.process({
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
                "action": "analyze",
                "question": event.get("query", ""),
            })
        
        return None
