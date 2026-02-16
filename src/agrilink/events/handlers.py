"""Event handlers that trigger agent workflows."""

import logging
import uuid
from typing import Any, Dict

from agrilink.events.bus import get_event_bus
from agrilink.events.router import get_event_router
from agrilink.events.schema import (
    AgentResponseEvent,
    BaseEvent,
    EventPriority,
    EventType,
)

logger = logging.getLogger(__name__)


class EventHandlers:
    """Collection of event handlers."""

    def __init__(self):
        """Initialize event handlers."""
        self.router = get_event_router()

    async def handle_user_query(self, event: BaseEvent) -> None:
        """Handle user query events."""
        logger.info(f"Handling user query: {event.event_id}")
        
        # Route to agents and get orchestrated response
        response = await self.router.route_and_orchestrate(event)
        
        if response:
            # Publish agent response event
            response_event = AgentResponseEvent(
                event_id=str(uuid.uuid4()),
                source="orchestrator",
                user_id=event.user_id,
                agent_name=response.agent_name,
                recommendation=response.recommendation,
                confidence=response.confidence,
                reasoning=response.reasoning,
                sources=response.sources,
                original_event_id=event.event_id,
                metadata=response.metadata,
            )
            
            bus = await get_event_bus()
            await bus.publish(response_event)

    async def handle_weather_alert(self, event: BaseEvent) -> None:
        """Handle high-priority weather alerts."""
        logger.warning(f"Weather alert received: {event.event_id}")
        
        # Route to weather agent
        response = await self.router.route_and_orchestrate(event)
        
        if response and response.confidence > 0.7:
            # Publish high-priority response
            response_event = AgentResponseEvent(
                event_id=str(uuid.uuid4()),
                source="weather_agent",
                priority=EventPriority.HIGH,
                user_id=event.user_id,
                agent_name=response.agent_name,
                recommendation=response.recommendation,
                confidence=response.confidence,
                reasoning=response.reasoning,
                sources=response.sources,
                original_event_id=event.event_id,
                metadata=response.metadata,
            )
            
            bus = await get_event_bus()
            await bus.publish(response_event)

    async def handle_price_update(self, event: BaseEvent) -> None:
        """Handle market price updates."""
        logger.info(f"Price update received: {event.event_id}")
        
        # Route to market intelligence agent
        response = await self.router.route_and_orchestrate(event)
        
        if response:
            response_event = AgentResponseEvent(
                event_id=str(uuid.uuid4()),
                source="market_agent",
                user_id=event.user_id,
                agent_name=response.agent_name,
                recommendation=response.recommendation,
                confidence=response.confidence,
                reasoning=response.reasoning,
                sources=response.sources,
                original_event_id=event.event_id,
                metadata=response.metadata,
            )
            
            bus = await get_event_bus()
            await bus.publish(response_event)

    async def handle_logistics_issue(self, event: BaseEvent) -> None:
        """Handle logistics issues."""
        logger.warning(f"Logistics issue: {event.event_id}")
        
        response = await self.router.route_and_orchestrate(event)
        
        if response:
            response_event = AgentResponseEvent(
                event_id=str(uuid.uuid4()),
                source="logistics_agent",
                priority=EventPriority.HIGH,
                user_id=event.user_id,
                agent_name=response.agent_name,
                recommendation=response.recommendation,
                confidence=response.confidence,
                reasoning=response.reasoning,
                sources=response.sources,
                original_event_id=event.event_id,
                metadata=response.metadata,
            )
            
            bus = await get_event_bus()
            await bus.publish(response_event)


async def setup_event_handlers() -> None:
    """Set up event handlers by subscribing to event types."""
    bus = await get_event_bus()
    handlers = EventHandlers()
    
    # Subscribe to event types
    await bus.subscribe(EventType.USER_QUERY, handlers.handle_user_query)
    await bus.subscribe(EventType.FARMER_QUERY, handlers.handle_user_query)
    await bus.subscribe(EventType.WEATHER_ALERT, handlers.handle_weather_alert)
    await bus.subscribe(EventType.PRICE_UPDATE, handlers.handle_price_update)
    await bus.subscribe(EventType.LOGISTICS_ISSUE, handlers.handle_logistics_issue)
    await bus.subscribe(EventType.DELIVERY_DELAY, handlers.handle_logistics_issue)
    
    logger.info("Event handlers configured and subscribed")
