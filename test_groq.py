import os
import asyncio
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"Testing Groq with key: {api_key[:10]}...")
    
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant", 
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama3-70b-8192"
    ]
    
    with open("groq_result.txt", "w") as f:
        for model in models:
            print(f"\nTesting model: {model}")
            try:
                llm = ChatGroq(
                    api_key=api_key,
                    model=model
                )
                print("Invoking Groq...")
                response = await llm.ainvoke("Hello")
                print(f"Response: {response.content}")
                print(f"Groq Test: SUCCESS with {model}")
                f.write(f"SUCCESS: {model}\n")
                return
            except Exception as e:
                print(f"Groq Test: FAILED with {model}: {e}")
                f.write(f"FAILED: {model} - {e}\n")

if __name__ == "__main__":
    asyncio.run(test_groq())
