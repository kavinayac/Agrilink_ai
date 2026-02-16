import requests
import json
import asyncio
import sys

# Add src to path if needed, but we are testing via API so requests is enough

def test_weather_api():
    url = "http://localhost:8001/api/weather/risk"
    
    payload = {
        "user_id": "test_user_weather",
        "region": "Punjab",
        "crop": "Wheat",
        "growth_stage": "sowing"
    }
    
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Check if actual weather data is present (not placeholder)
            # Placeholder had "note": "Fetch from weather API..."
            # Real data has "risk_assessment" and likely "current" in sources or similar
            # Actually, routes.py puts forecast in event. The response is from agent.
            # Agent uses forecast to generate recomm.
            
            # But we can check if response implies real data
            print("\nAssessment:")
            print(data.get("risk_assessment", "")[:200] + "...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_weather_api()
