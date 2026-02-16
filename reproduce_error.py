import asyncio
import logging
import sys
import os
import json

# Set up logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add src to python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agrilink.events.schema import UserQueryEvent, EventType
from agrilink.events.router import get_event_router
from agrilink.agents.market_intelligence import MarketIntelligenceAgent

async def reproduce():
    try:
        logger.info("Initializing reproduction script...")
        router = get_event_router()
        logger.info("Router created successfully")
        
        event = UserQueryEvent(
            event_id="test-123",
            source="repro",
            user_id="user-1",
            query="What is the price of wheat in Punjab?",
            crop="Wheat",
            region="Punjab",
            context={}
        )
        
        event_dict = event.model_dump()
        logger.info(f"Event dict: {json.dumps(event_dict, default=str)}")
        logger.info(f"Event type: {event_dict.get('event_type')}")
        logger.info(f"Event type (key 'type'): {event_dict.get('type')}")
         
        # Test Market agent directly to see if handle_event works
        market_agent = router.market_agent
        logger.info(f"Testing MarketAgent directly with event type: {event.event_type}")
        response = await market_agent.handle_event(event_dict)
        logger.info(f"Direct MarketAgent response: {response}")
        
        logger.info(f"Routing event via router: {event}")
        response = await router.route_and_orchestrate(event)
        
        if response:
            logger.info(f"Success! Response: {response.recommendation}")
        else:
            logger.error("Failed: No response returned from router")
            
    except Exception as e:
        logger.error(f"Caught exception: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(reproduce())
