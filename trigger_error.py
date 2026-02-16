import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trigger_market_insights_error():
    url = "http://localhost:8001/api/market/insights"
    payload = {
        "user_id": "debug_user",
        "crop": "Wheat",
        "region": "Punjab",
        "action": "analyze"
    }
    
    try:
        logger.info(f"Sending POST request to {url}")
        response = requests.post(url, json=payload)
        
        logger.info(f"Status Code: {response.status_code}")
        try:
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            logger.info(f"Response Text: {response.text}")
            
    except Exception as e:
        logger.error(f"Request failed: {e}")

if __name__ == "__main__":
    trigger_market_insights_error()
