"""Event routing logic to activate appropriate agents."""

import logging
from typing import Any, Dict, List, Optional

from agrilink.agents.buyer_strategy import BuyerStrategyAgent
from agrilink.agents.farmer_advisory import FarmerAdvisoryAgent
from agrilink.agents.logistics import LogisticsAgent
from agrilink.agents.market_intelligence import MarketIntelligenceAgent
from agrilink.agents.orchestrator import OrchestratorAgent
from agrilink.agents.weather_risk import WeatherRiskAgent
from agrilink.events.schema import BaseEvent, EventType

logger = logging.getLogger(__name__)


class EventRouter:
    """Routes events to appropriate agents."""

    def __init__(self):
        """Initialize event router with agent instances."""
        self.market_agent = MarketIntelligenceAgent()
        self.weather_agent = WeatherRiskAgent()
        self.farmer_agent = FarmerAdvisoryAgent()
        self.buyer_agent = BuyerStrategyAgent()
        self.logistics_agent = LogisticsAgent()
        self.orchestrator = OrchestratorAgent()
        
        # Event type to agent mapping
        self.routing_table = {
            EventType.PRICE_UPDATE: [self.market_agent],
            EventType.MARKET_UPDATE: [self.market_agent],
            EventType.WEATHER_UPDATE: [self.weather_agent],
            EventType.WEATHER_ALERT: [self.weather_agent],
            EventType.FARMER_QUERY: [self.farmer_agent],
            EventType.PURCHASE_REQUEST: [self.buyer_agent, self.market_agent],
            EventType.ORDER_PLACED: [self.logistics_agent],
            EventType.DELIVERY_DELAY: [self.logistics_agent],
            EventType.LOGISTICS_ISSUE: [self.logistics_agent],
            EventType.ORDER_UPDATE: [self.logistics_agent],
            
            # Complex events that may need multiple agents
            EventType.USER_QUERY: [
                self.farmer_agent,
                self.market_agent,
                self.weather_agent,
            ],
        }

    async def route_event(self, event: BaseEvent) -> List[Any]:
        """
        Route an event to appropriate agents and collect responses.
        
        Args:
            event: Event to route
            
        Returns:
            List of agent responses
        """
        logger.info(f"Routing event: {event.event_type} (ID: {event.event_id})")
        
        # Get agents for this event type
        agents = self.routing_table.get(event.event_type, [])
        
        if not agents:
            logger.warning(f"No agents configured for event type: {event.event_type}")
            return []
        
        # Collect agent responses
        responses = []
        for agent in agents:
            try:
                response = await agent.handle_event(event.model_dump())
                if response:
                    responses.append(response)
                    logger.info(
                        f"Agent {agent.agent_name} responded with confidence {response.confidence}"
                    )
            except Exception as e:
                logger.error(
                    f"Error in agent {agent.agent_name} handling event: {e}",
                    exc_info=True,
                )
        
        return responses

    async def route_and_orchestrate(self, event: BaseEvent) -> Optional[Any]:
        """
        Route event to agents and orchestrate final response.
        
        Args:
            event: Event to process
            
        Returns:
            Orchestrated final response
        """
        # Get agent responses
        agent_responses = await self.route_event(event)
        
        if not agent_responses:
            logger.warning(f"No agent responses for event {event.event_id}")
            return None
        
        # If only one response, return it directly
        if len(agent_responses) == 1:
            return agent_responses[0]
        
        # Multiple responses - orchestrate
        try:
            final_response = await self.orchestrator.orchestrate(
                agent_responses=agent_responses,
                context=event.model_dump(),
            )
            logger.info(
                f"Orchestrated final response with confidence {final_response.confidence}"
            )
            return final_response
        except Exception as e:
            logger.error(f"Error orchestrating responses: {e}", exc_info=True)
            return None

    def add_agent_for_event(self, event_type: EventType, agent: Any) -> None:
        """
        Add an agent to handle a specific event type.
        
        Args:
            event_type: Event type
            agent: Agent instance
        """
        if event_type not in self.routing_table:
            self.routing_table[event_type] = []
        
        self.routing_table[event_type].append(agent)
        logger.info(f"Added {agent.agent_name} for {event_type} events")


# Global router instance
_router: Optional[EventRouter] = None


def get_event_router() -> EventRouter:
    """Get or create the global event router instance."""
    global _router
    
    if _router is None:
        _router = EventRouter()
    
    return _router
