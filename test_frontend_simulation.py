import requests
import json
import sys

def test_frontend_request():
    url = "http://localhost:8001/api/farmer/query"
    
    # Exact payload structure from api.js
    payload = {
        "query": "When should I plant wheat?",
        "user_id": "test_user_123",
        "crop": "Wheat",  # Frontend likely sends capitalized
        "region": "Punjab",
        "season": "Rabi"
    }
    
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(f"Confidence: {data.get('confidence')}")
            print(f"Answer: {data.get('recommendation', data.get('answer', 'No answer key found'))[:200]}...")
            print(f"Grounded: {data.get('grounded', 'Unknown')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_frontend_request()
