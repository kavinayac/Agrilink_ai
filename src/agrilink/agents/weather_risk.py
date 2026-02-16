"""Weather Risk Agent - assesses weather risks and recommends mitigation."""

import logging
from typing import Any, Dict, Optional

from agrilink.agents.base import AgentResponse, BaseAgent
from agrilink.agents.prompts import get_agent_prompt

logger = logging.getLogger(__name__)


class WeatherRiskAgent(BaseAgent):
    """Agent for weather risk assessment and mitigation strategies."""

    def __init__(self, **kwargs):
        """Initialize Weather Risk Agent."""
        super().__init__(agent_name="WeatherRiskAgent", **kwargs)

    def get_system_prompt(self) -> str:
        """Get system prompt for weather risk assessment."""
        return get_agent_prompt("weather_risk")

    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Process weather risk assessment request.
        
        Expected context keys:
            - crop: Crop type
            - region: Geographic region
            - growth_stage: Current growth stage (e.g., "seedling", "flowering")
            - weather_forecast: Weather forecast data
            - timeframe: Assessment timeframe (e.g., "7_days", "14_days")
        """
        crop = context.get("crop", "")
        region = context.get("region", "")
        growth_stage = context.get("growth_stage", "unknown")
        weather_forecast = context.get("weather_forecast", {})
        
        # Retrieve crop-specific weather vulnerability knowledge
        query = f"Weather risks and vulnerabilities for {crop} at {growth_stage} stage. Mitigation strategies."
        knowledge = await self.retrieve_knowledge(
            query=query,
            filter={"category": "crops"},
        )
        
        if not knowledge.get("grounded", False):
            return self.create_response(
                recommendation="Insufficient crop-specific weather risk data available.",
                confidence=0.0,
                reasoning="No weather vulnerability data found for this crop.",
                sources=[],
                metadata={"requires_weather_api": True},
            )
        
        # Assess risk based on forecast and crop knowledge
        risk_prompt = f"""Based on the crop knowledge and weather forecast, assess weather risks for {crop} in {region}.

Crop Knowledge:
{knowledge['answer']}

Current Growth Stage: {growth_stage}
Weather Forecast: {weather_forecast}

Provide:
1. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
2. Specific threats identified
3. Mitigation actions (prioritized)
4. Timeline for action
5. Confidence in assessment

Format your response as:
RISK_LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
THREATS: [specific weather threats]
MITIGATION: [specific actionable steps]
TIMELINE: [when to act]
CONFIDENCE: [0.0 to 1.0]
"""
        
        assessment = await self.reason(risk_prompt, context)
        
        # Parse assessment
        risk_level = self._extract_section(assessment, "RISK_LEVEL") or "MEDIUM"
        threats = self._extract_section(assessment, "THREATS")
        mitigation = self._extract_section(assessment, "MITIGATION")
        timeline = self._extract_section(assessment, "TIMELINE")
        confidence_str = self._extract_section(assessment, "CONFIDENCE")
        
        try:
            confidence = float(confidence_str) if confidence_str else 0.7
        except ValueError:
            confidence = 0.7
        
        # Adjust confidence based on knowledge grounding
        final_confidence = min(confidence, knowledge.get("confidence", 1.0))
        
        recommendation = f"Risk Level: {risk_level}\n\nMitigation Actions:\n{mitigation}\n\nTimeline: {timeline}"
        
        return self.create_response(
            recommendation=recommendation,
            confidence=final_confidence,
            reasoning=f"Threats: {threats}",
            sources=knowledge.get("sources", []),
            metadata={
                "crop": crop,
                "region": region,
                "growth_stage": growth_stage,
                "risk_level": risk_level,
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
        """Handle weather-related events."""
        event_type = event.get("event_type", "")
        
        if event_type == "weather_update":
            # Process weather update event
            return await self.process({
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
                "growth_stage": event.get("growth_stage", "unknown"),
                "weather_forecast": event.get("forecast", {}),
            })
        
        elif event_type == "weather_alert":
            # High priority weather alert
            logger.warning(f"Weather alert received: {event.get('alert_type', 'unknown')}")
            return await self.process(event)
            
        elif event_type == "user_query":
            # Process general user query as weather risk assessment
            # Only if it asks about weather/risk
            return await self.process({
                "crop": event.get("crop", ""),
                "region": event.get("region", ""),
                "growth_stage": "unknown",  # We might need to extract this from context
                "weather_forecast": {"note": "No forecast in query"},
            })
        
        return None
