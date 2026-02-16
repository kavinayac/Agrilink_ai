"""Test RAGChain initialization to diagnose the error."""

import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

try:
    print("1. Importing modules...")
    from agrilink.config import get_settings
    from langchain_groq import ChatGroq
    from agrilink.rag.chains import RAGChain
    
    print("2. Getting settings...")
    settings = get_settings()
    
    print("3. Initializing Groq LLM...")
    llm = ChatGroq(
        model=settings.default_model,
        temperature=0.2,
        groq_api_key=settings.groq_api_key,
    )
    print(f"✓ LLM initialized: {llm}")
    
    print("4. Initializing RAGChain...")
    rag_chain = RAGChain(llm=llm)
    print(f"✓ RAGChain initialized: {rag_chain}")
    
    print("\n✓ All components initialized successfully!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
