"""Logistics & Fulfillment Agent - optimizes delivery and routing."""

import logging
from typing import Any, Dict, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class LogisticsAgent(BaseAgent):
    """Agent for logistics optimization and fulfillment tracking."""

    def __init__(self, **kwargs):
        """Initialize Logistics Agent."""
        super().__init__(agent_name="LogisticsAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for logistics."""
        return get_agent_prompt("logistics")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process logistics optimization request.
        
        Expected context keys:
            - order_id: Order identifier
            - origin: Origin location
            - destination: Destination location
            - crop: Crop type (for perishability assessment)
            - quantity: Quantity to transport
            - current_status: Current delivery status
            - issues: Any reported issues
        """
        order_id = context.get("order_id", "")
        origin = context.get("origin", "")
        destination = context.get("destination", "")
        crop = context.get("crop", "")
        quantity = context.get("quantity", 0)
        current_status = context.get("current_status", "pending")
        issues = context.get("issues", "")
        
        # Retrieve logistics best practices
        query = f"Logistics and transportation best practices for {crop}. Storage and handling requirements."
        knowledge = await self.retrieve_knowledge(
            query=query,
            filter={"category": "crops", "crop": crop} if crop else None,
        )
        
        # Generate logistics recommendation
        logistics_prompt = f"""Based on logistics best practices, provide recommendations for this delivery.

Logistics Knowledge:
{knowledge.get('answer', 'No specific knowledge available')}

Delivery Details:
- Order ID: {order_id}
- Route: {origin} → {destination}
- Crop: {crop}
- Quantity: {quantity}
- Current Status: {current_status}
- Issues: {issues if issues else 'None reported'}

Provide:
1. Routing recommendation
2. Timeline estimate
3. Storage/handling requirements
4. Risk factors
5. Issue resolution (if applicable)

Format your response as:
ROUTING: [recommended route/method]
TIMELINE: [estimated delivery time]
REQUIREMENTS: [handling requirements]
RISKS: [potential risks]
RESOLUTION: [steps to resolve issues]
CONFIDENCE: [0.0 to 1.0]
"""
        
        recommendation_text = await self.reason(logistics_prompt, context)
        
        # Parse recommendation
        routing = self._extract_section(recommendation_text, "ROUTING")
        timeline = self._extract_section(recommendation_text, "TIMELINE")
        requirements = self._extract_section(recommendation_text, "REQUIREMENTS")
        risks = self._extract_section(recommendation_text, "RISKS")
        resolution = self._extract_section(recommendation_text, "RESOLUTION")
        confidence_str = self._extract_section(recommendation_text, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else 0.7
        except ValueError:
            confidence = 0.7
        
        # Build recommendation
        recommendation = f"""Routing: {routing}
Estimated Timeline: {timeline}

Handling Requirements:
{requirements}

Risk Factors:
{risks}
"""
        
        if resolution and issues:
            recommendation += f"\n\nIssue Resolution:\n{resolution}"
        
        # Add urgency flag for perishable crops
        metadata = {
            "order_id": order_id,
            "origin": origin,
            "destination": destination,
            "crop": crop,
        }
        
        if crop and any(perishable in crop.lower() for perishable in ["tomato", "lettuce", "strawberry", "milk"]):
            metadata["urgency"] = "high"
            recommendation += "\n\n⚠️ High Priority: Perishable cargo requires expedited handling."
        
        return self.create_response(
            recommendation=recommendation,
            confidence=confidence,
            reasoning="Based on logistics best practices and crop requirements",
            sources=knowledge.get("sources", []),
            metadata=metadata,
        )

    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted text."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{section_name}:"):
                return line.split(":", 1)[1].strip()
        return ""

    async def handle_event(self, event: Dict[str, Any]) -> Optional[AgentResponse]:
        """Handle logistics-related events."""
        event_type = event.get("event_type", "")
        
        if event_type in ["order_placed", "delivery_delay", "logistics_issue", "order_update"]:
            return await self.process({
                "order_id": event.get("order_id", ""),
                "origin": event.get("origin", ""),
                "destination": event.get("destination", ""),
                "crop": event.get("crop", ""),
                "quantity": event.get("quantity", 0),
                "current_status": event.get("status", event.get("current_status", "unknown")),
                "issues": event.get("issue_description", ""),
            })
        
        return None
