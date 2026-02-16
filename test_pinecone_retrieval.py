"""Test Pinecone retrieval directly."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from agrilink.rag.embeddings import get_embeddings
from agrilink.rag.vector_store import get_vector_store

async def test_retrieval():
    print("1. Initializing embeddings...")
    embeddings = get_embeddings()
    
    print("2. Initializing vector store...")
    vector_store = get_vector_store(embeddings)
    
    print("3. Testing similarity search...")
    query = "When should I plant wheat in Punjab?"
    
    results = await vector_store.similarity_search(
        query=query,
        k=5,
        filter=None
    )
    
    print(f"\n✅ Found {len(results)} documents")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Document {i} ---")
        print(f"Content: {doc.page_content[:200]}...")
        print(f"Metadata: {doc.metadata}")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
