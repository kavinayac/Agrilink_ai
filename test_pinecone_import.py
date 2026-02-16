import sys
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print(f"Python executable: {sys.executable}")
print(f"Path: {sys.path}")

try:
    from pinecone import Pinecone
    print("Successfully imported Pinecone class")

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        print("PINECONE_API_KEY not set")
    else:
        print("PINECONE_API_KEY loaded successfully")
        pc = Pinecone(api_key=api_key)
        print("Pinecone client initialized")
        print("Indexes:", pc.list_indexes())

except Exception as e:
    print(f"Pinecone error: {e}")

try:
    from langchain_pinecone import PineconeVectorStore
    print("Successfully imported PineconeVectorStore")
except Exception as e:
    print(f"Failed to import langchain_pinecone: {e}")
