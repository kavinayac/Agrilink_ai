"""Simple script to test knowledge ingestion with minimal dependencies."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.documents import Document
from agrilink.rag.vector_store import get_vector_store

async def main():
    """Add sample knowledge directly to vector store."""
    print("Creating sample agricultural knowledge...")
    
    # Create sample documents
    documents = [
        Document(
            page_content="""
            Wheat Planting in Punjab:
            - Best planting time: Mid-October to mid-November (Rabi season)
            - Soil temperature should be 18-22°C
            - Recommended varieties: PBW 725, HD 3086, DBW 187
            - Seed rate: 100 kg per hectare
            - Row spacing: 20-22.5 cm
            - Irrigation: First irrigation 20-25 days after sowing
            """,
            metadata={
                "source": "wheat_punjab.md",
                "category": "crops",
                "crop": "wheat",
                "region": "punjab",
            }
        ),
        Document(
            page_content="""
            Rice Cultivation in Punjab:
            - Nursery sowing: Mid-May to early June
            - Transplanting: Mid-June to early July
            - Recommended varieties: PR 126, Pusa 44, PR 121
            - Water requirement: 1500-2000 mm
            - Fertilizer: 120 kg N, 60 kg P2O5, 30 kg K2O per hectare
            """,
            metadata={
                "source": "rice_punjab.md",
                "category": "crops",
                "crop": "rice",
                "region": "punjab",
            }
        ),
        Document(
            page_content="""
            Minimum Support Price (MSP) India:
            - MSP is announced by Government of India
            - Wheat MSP 2023-24: ₹2125 per quintal
            - Rice (Paddy) MSP 2023-24: ₹2183 per quintal
            - MSP ensures farmers get fair prices
            - Procurement done through FCI and state agencies
            """,
            metadata={
                "source": "pricing_guide.md",
                "category": "market",
                "region": "india",
            }
        ),
    ]
    
    print(f"Adding {len(documents)} documents to vector store...")
    
    # Get vector store and add documents
    vector_store = get_vector_store()
    await vector_store.add_documents(documents)
    
    print("✅ Knowledge ingestion complete!")
    print(f"Added {len(documents)} documents successfully")

if __name__ == "__main__":
    asyncio.run(main())
