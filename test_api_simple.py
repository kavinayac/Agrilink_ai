"""Test AgriLink API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8001"

print("="*60)
print("Testing AgriLink API")
print("="*60 + "\n")

# Test farmer query
print("Testing Farmer Query...")
response = requests.post(
    f"{BASE_URL}/api/farmer/query",
    json={
        "query": "When should I plant wheat in Punjab?",
        "user_id": "test_farmer",
        "crop": "wheat",
        "region": "punjab",
        "season": "rabi"
    },
    timeout=30
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"Answer: {data['answer'][:200]}...")
    print(f"Confidence: {data['confidence']}")
    print(f"Sources: {len(data.get('sources', []))}")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60)
