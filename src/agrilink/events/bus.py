"""Event bus implementation using Redis Pub/Sub with in-memory fallback."""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as aioredis
from pydantic import ValidationError

from agrilink.config import get_settings
from agrilink.events.schema import BaseEvent, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """Redis-based event bus with in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize event bus.
        
        Args:
            redis_url: Redis connection URL (uses settings if not provided)
        """
        self.settings = get_settings()
        self.redis_url = redis_url or self.settings.redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self._listening = False
        self._listen_task: Optional[asyncio.Task] = None
        
        # In-memory fallback
        self.use_memory = False
        self._memory_queue: Optional[asyncio.Queue] = None

    async def connect(self) -> None:
        """Connect to Redis or fallback to in-memory."""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2.0,  # Fail fast
            )
            await self.redis.ping()
            logger.info(f"Connected to Redis event bus: {self.redis_url}")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}. Falling back to in-memory event bus.")
            self.use_memory = True
            self._memory_queue = asyncio.Queue()

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self.pubsub:
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from event bus")

    async def publish(self, event: BaseEvent) -> None:
        """
        Publish an event to the bus.
        
        Args:
            event: Event to publish
        """
        if self.redis is None and not self.use_memory:
            await self.connect()
        
        channel = f"agrilink:events:{event.event_type}"
        event_data = event.model_dump_json()

        if self.use_memory:
            # In-memory publish
            if self._memory_queue:
                await self._memory_queue.put({"channel": channel, "data": event_data})
                
                # Global channel
                await self._memory_queue.put({"channel": "agrilink:events:all", "data": event_data})
        else:
            # Redis publish
            if self.redis:
                await self.redis.publish(channel, event_data)
                # Global channel
                await self.redis.publish("agrilink:events:all", event_data)
        
        logger.info(
            f"Published event: {event.event_type} (ID: {event.event_id}, "
            f"Priority: {event.priority})"
        )

    async def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[BaseEvent], Any],
    ) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Async function to handle events
        """
        channel = f"agrilink:events:{event_type}"
        
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(handler)
        logger.info(f"Subscribed to {event_type} events")
        
        if not self._listening:
            await self._start_listening()

    async def subscribe_all(self, handler: Callable[[BaseEvent], Any]) -> None:
        """
        Subscribe to all events.
        
        Args:
            handler: Async function to handle events
        """
        channel = "agrilink:events:all"
        
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(handler)
        logger.info("Subscribed to all events")
        
        if not self._listening:
            await self._start_listening()

    async def _start_listening(self) -> None:
        """Start listening for events."""
        if self.redis is None and not self.use_memory:
            await self.connect()
        
        if self.use_memory:
            self._listening = True
            self._listen_task = asyncio.create_task(self._listen_memory())
            logger.info("Started listening for in-memory events")
        else:
            if self.redis:
                self.pubsub = self.redis.pubsub()
                for channel in self.subscribers.keys():
                    await self.pubsub.subscribe(channel)
                
                self._listening = True
                self._listen_task = asyncio.create_task(self._listen_redis())
                logger.info("Started listening for Redis events")

    async def _listen_redis(self) -> None:
        """Listen for incoming Redis events."""
        try:
            if self.pubsub:
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        await self._handle_message(message["channel"], message["data"])
        except asyncio.CancelledError:
            logger.info("Redis event listener cancelled")
        except Exception as e:
            logger.error(f"Error in Redis event listener: {e}", exc_info=True)

    async def _listen_memory(self) -> None:
        """Listen for incoming in-memory events."""
        try:
            while True and self._memory_queue:
                message = await self._memory_queue.get()
                await self._handle_message(message["channel"], message["data"])
                self._memory_queue.task_done()
        except asyncio.CancelledError:
            logger.info("In-memory event listener cancelled")
        except Exception as e:
            logger.error(f"Error in in-memory event listener: {e}", exc_info=True)

    async def _handle_message(self, channel: str, data: str) -> None:
        """
        Handle incoming message.
        
        Args:
            channel: Channel name
            data: Event data (JSON string)
        """
        try:
            # Parse event
            event_dict = json.loads(data)
            event = BaseEvent(**event_dict)
            
            # Get handlers for this channel
            handlers = self.subscribers.get(channel, [])
            
            # Execute handlers
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(
                        f"Error in event handler for {event.event_type}: {e}",
                        exc_info=True,
                    )
        
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error parsing event: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)


# Global event bus instance
_event_bus: Optional[EventBus] = None


async def get_event_bus() -> EventBus:
    """Get or create the global event bus instance."""
    global _event_bus
    
    if _event_bus is None:
        _event_bus = EventBus()
        await _event_bus.connect()
    
    return _event_bus


async def publish_event(event: BaseEvent) -> None:
    """
    Convenience function to publish an event.
    
    Args:
        event: Event to publish
    """
    bus = await get_event_bus()
    await bus.publish(event)

