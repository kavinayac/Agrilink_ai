"""Script to ingest knowledge base into vector store."""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agrilink.rag.ingestion import KnowledgeIngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Ingest all knowledge from the knowledge directory."""
    # Get knowledge directory
    knowledge_dir = Path(__file__).parent.parent / "knowledge"
    
    if not knowledge_dir.exists():
        logger.error(f"Knowledge directory not found: {knowledge_dir}")
        return
    
    logger.info(f"Starting knowledge ingestion from: {knowledge_dir}")
    
    # Initialize pipeline
    pipeline = KnowledgeIngestionPipeline()
    
    # Ingest crops knowledge
    crops_dir = knowledge_dir / "crops"
    if crops_dir.exists():
        logger.info(f"Ingesting crops knowledge from: {crops_dir}")
        await pipeline.ingest_crop_knowledge(str(crops_dir))
    
    # Ingest market knowledge
    market_dir = knowledge_dir / "market"
    if market_dir.exists():
        logger.info(f"Ingesting market knowledge from: {market_dir}")
        await pipeline.ingest_market_knowledge(str(market_dir))
    
    # Ingest policy knowledge
    policy_dir = knowledge_dir / "policy"
    if policy_dir.exists():
        logger.info(f"Ingesting policy knowledge from: {policy_dir}")
        await pipeline.ingest_policy_knowledge(str(policy_dir))
    
    logger.info("Knowledge ingestion complete!")


if __name__ == "__main__":
    asyncio.run(main())
