"""Simple test script to verify AgriLink API."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_root():
    """Test root endpoint."""
    print("Testing / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_query():
    """Test query endpoint."""
    print("Testing /api/query endpoint...")
    data = {
        "query": "When should I plant wheat in Punjab?",
        "user_id": "test_user_123",
        "crop": "wheat",
        "region": "punjab"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json=data,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Query ID: {result.get('query_id')}")
            print(f"Answer: {result.get('answer')[:200]}...")
            print(f"Confidence: {result.get('confidence')}")
            print(f"Agent: {result.get('agent_name')}")
            print(f"Sources: {len(result.get('sources', []))} sources\n")
        else:
            print(f"Error: {response.text}\n")
    except Exception as e:
        print(f"Error: {e}\n")

if __name__ == "__main__":
    print("="*60)
    print("AgriLink API Test")
    print("="*60 + "\n")
    
    test_health()
    test_root()
    test_query()
    
    print("="*60)
    print("Tests Complete")
    print("="*60)
