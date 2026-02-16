"""Test Groq API connection and model availability."""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_groq import ChatGroq
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("DEFAULT_MODEL", "llama-3.1-70b-versatile")
    
    print(f"Testing Groq API with model: {model}")
    print(f"API Key (first 10 chars): {groq_api_key[:10] if groq_api_key else 'NOT SET'}")
    
    llm = ChatGroq(
        model=model,
        temperature=0.2,
        groq_api_key=groq_api_key,
    )
    
    print("✓ Groq LLM initialized successfully!")
    
    # Test a simple invocation
    response = llm.invoke("Say 'Hello, AgriLink!' if you can hear me.")
    print(f"✓ Test invocation successful: {response.content}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
