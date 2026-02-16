import asyncio
import logging
import sys
import os
import random
import json
from datetime import datetime

# Set up logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add src to python path
sys.path.append(os.path.join(os.getcwd(), "src"))

from agrilink.events.schema import PriceUpdateEvent, EventType
from agrilink.events.bus import get_event_bus

async def simulate_market_activity():
    try:
        logger.info("Initializing market simulation...")
        bus = await get_event_bus()
        logger.info("Connected to event bus")
        
        crops = ["Wheat", "Rice", "Cotton", "Sugarcane"]
        regions = ["Punjab", "Haryana", "UP", "Maharashtra"]
        base_prices = {"Wheat": 2300, "Rice": 3100, "Cotton": 6200, "Sugarcane": 380}
        
        logger.info("Starting price updates... Press Ctrl+C to stop.")
        
        while True:
            crop = random.choice(crops)
            region = random.choice(regions)
            base = base_prices[crop]
            
            # Fluctuate price by +/- 5%
            fluctuation = random.uniform(-0.05, 0.05)
            new_price = round(base * (1 + fluctuation), 2)
            
            event = PriceUpdateEvent(
                event_id=f"price-{datetime.now().timestamp()}",
                crop=crop,
                region=region,
                price=new_price,
                unit="per_quintal",
                change_percent=round(fluctuation * 100, 2),
                market_name=f"{region} Mandi",
                source="market_simulator"
            )
            
            await bus.publish(event)
            logger.info(f"Published update: {crop} in {region} @ ₹{new_price}")
            
            # Wait for random interval
            await asyncio.sleep(random.uniform(2, 5))
            
    except asyncio.CancelledError:
        logger.info("Simulation stopped")
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(simulate_market_activity())
    except KeyboardInterrupt:
        pass
