"""Quick test to demonstrate AgriLink working with Groq API."""

import requests
import json

BASE_URL = "http://localhost:8001"

print("="*60)
print("AgriLink API Test - Groq Integration")
print("="*60 + "\n")

# Test 1: Health Check
print("1. Testing Health Endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: Root endpoint
print("2. Testing Root Endpoint...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
data = response.json()
print(f"   Service: {data.get('service')}")
print(f"   Version: {data.get('version')}")
print(f"   Description: {data.get('description')}\n")

# Test 3: Farmer Query
print("3. Testing Farmer Query (RAG + Groq LLM)...")
print("   Question: 'When should I plant wheat in Punjab?'\n")

query_data = {
    "query": "When should I plant wheat in Punjab?",
    "user_id": "demo_farmer_001",
    "crop": "wheat",
    "region": "punjab"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/farmer/query",
        json=query_data,
        timeout=60  # Groq is fast but first query might take longer
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success!")
        print(f"   Query ID: {result.get('query_id')}")
        print(f"   Agent: {result.get('agent_name')}")
        print(f"   Confidence: {result.get('confidence'):.2f}")
        print(f"\n   Answer:\n   {result.get('answer')}\n")
        
        sources = result.get('sources', [])
        if sources:
            print(f"   Sources ({len(sources)}):")
            for i, source in enumerate(sources[:3], 1):
                print(f"   {i}. {source.get('source')} (score: {source.get('score'):.2f})")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
