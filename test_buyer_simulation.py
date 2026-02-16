import requests
import json

def test_buyer_pricing():
    url = "http://localhost:8001/api/buyer/pricing"
    
    # Payload from user request
    payload = {
        "crop": "Wheat",
        "quantity": 100,
        "region": "Punjab",
        "quality_grade": "Standard",
        "asking_price": None,
        "user_id": "test_user_buyer"
    }
    
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nSuccess response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_buyer_pricing()
