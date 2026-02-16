"""Recreate Pinecone index with 384 dimensions for free embeddings (sentence-transformers)."""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

def recreate_index():
    """Delete existing index and create new one with 384 dimensions."""
    
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "agrilink-rag-index")
    
    if not api_key:
        raise ValueError("PINECONE_API_KEY not set in .env")
    
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name in existing_indexes:
        print(f"⚠️  Index '{index_name}' already exists with dimension 1536 (OpenAI)")
        response = input(f"Delete and recreate with dimension 384 for free embeddings? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Cancelled. Keeping existing index.")
            return
        
        print(f"🗑️  Deleting index '{index_name}'...")
        pc.delete_index(index_name)
        print("✅ Index deleted")
    
    # Create new index with 384 dimensions (for sentence-transformers/all-MiniLM-L6-v2)
    print(f"🔨 Creating new index '{index_name}' with dimension 384...")
    
    pc.create_index(
        name=index_name,
        dimension=384,  # For sentence-transformers/all-MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    
    print(f"✅ Index '{index_name}' created successfully!")
    print("\n📋 Index details:")
    print(f"  - Dimension: 384")
    print(f"  - Metric: cosine")
    print(f"  - Embedding model: sentence-transformers/all-MiniLM-L6-v2 (FREE)")
    print(f"  - Cloud: AWS us-east-1")
    print("\n🚀 Next steps:")
    print("  1. Update embeddings.py to use HuggingFace embeddings")
    print("  2. Run: python scripts/ingest_knowledge.py")
    print("  3. Start server: python -m uvicorn agrilink.main:app --host 0.0.0.0 --port 8001 --reload")

if __name__ == "__main__":
    recreate_index()
