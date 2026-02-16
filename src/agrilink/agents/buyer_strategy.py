"""Buyer Strategy Agent - assists with pricing and negotiation."""

import logging
from typing import Any, Dict, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class BuyerStrategyAgent(BaseAgent):
    """Agent for buyer pricing strategy and negotiation assistance."""

    def __init__(self, **kwargs):
        """Initialize Buyer Strategy Agent."""
        super().__init__(agent_name="BuyerStrategyAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for buyer strategy."""
        return get_agent_prompt("buyer_strategy")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process buyer strategy request.
        
        Expected context keys:
            - crop: Crop type
            - quantity: Quantity to purchase
            - quality_grade: Quality grade (e.g., "A", "B", "premium")
            - region: Geographic region
            - current_offer: Current price offer (optional)
            - seller_asking_price: Seller's asking price (optional)
        """
        crop = context.get("crop", "")
        quantity = context.get("quantity", 0)
        quality_grade = context.get("quality_grade", "standard")
        region = context.get("region", "")
        current_offer = context.get("current_offer")
        seller_asking = context.get("seller_asking_price")
        
        # Retrieve market pricing knowledge
        query = f"Fair market price and pricing trends for {crop} quality grade {quality_grade} in {region}"
        # Removed 'crop' filter as it's not present in document metadata
        knowledge = await self.retrieve_knowledge(
            query=query,
            filter={"category": "market"},
        )
        
        if not knowledge.get("grounded", False):
            return self.create_response(
                recommendation="Insufficient market pricing data for accurate valuation.",
                confidence=0.0,
                reasoning="No market pricing data found.",
                sources=[],
                metadata={"requires_market_data": True},
            )
        
        # Generate pricing strategy
        strategy_prompt = f"""Based on market data, provide buyer pricing strategy for {crop}.

Market Knowledge:
{knowledge['answer']}

Purchase Details:
- Crop: {crop}
- Quantity: {quantity}
- Quality Grade: {quality_grade}
- Region: {region}
- Current Offer: {current_offer if current_offer else 'Not set'}
- Seller Asking: {seller_asking if seller_asking else 'Unknown'}

Provide:
1. Fair market value range
2. Recommended offer price
3. Negotiation strategy
4. Key factors affecting price
5. Risk assessment

Format your response as:
FAIR_VALUE_RANGE: [min - max]
RECOMMENDED_OFFER: [specific price]
STRATEGY: [negotiation approach]
FACTORS: [price-affecting factors]
CONFIDENCE: [0.0 to 1.0]
"""
        
        strategy = await self.reason(strategy_prompt, context)
        
        # Parse strategy
        fair_value = self._extract_section(strategy, "FAIR_VALUE_RANGE")
        recommended_offer = self._extract_section(strategy, "RECOMMENDED_OFFER")
        negotiation_strategy = self._extract_section(strategy, "STRATEGY")
        factors = self._extract_section(strategy, "FACTORS")
        confidence_str = self._extract_section(strategy, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else 0.6
        except ValueError:
            confidence = 0.6
        
        # Build recommendation
        recommendation = f"""Fair Market Value: {fair_value}
Recommended Offer: {recommended_offer}

Negotiation Strategy:
{negotiation_strategy}

Key Price Factors:
{factors}
"""
        
        # Add warning if asking price is significantly above fair value
        if seller_asking and fair_value:
            recommendation += "\n\n⚠️ Compare seller's asking price against the fair value range before proceeding."
        
        return self.create_response(
            recommendation=recommendation,
            confidence=min(confidence, knowledge.get("confidence", 1.0)),
            reasoning="Based on market data and pricing trends",
            sources=knowledge.get("sources", []),
            metadata={
                "crop": crop,
                "quantity": quantity,
                "quality_grade": quality_grade,
                "fair_value_range": fair_value,
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
        """Handle buyer-related events."""
        event_type = event.get("event_type", "")
        
        if event_type == "purchase_request":
            return await self.process({
                "crop": event.get("crop", ""),
                "quantity": event.get("quantity", 0),
                "quality_grade": event.get("quality_grade", "standard"),
                "region": event.get("region", ""),
                "seller_asking_price": event.get("asking_price"),
            })
        
        return None
