# AgriLink

**Real-time, sensor-less agricultural intelligence platform powered by RAG-grounded, multi-agent AI**

## Overview

AgriLink is an advanced agricultural intelligence system that provides real-time insights, recommendations, and alerts **without relying on physical sensors**. Instead, it uses:

- **Retrieval-Augmented Generation (RAG)** for grounded, factual advice
- **Multi-agent AI systems** with specialized expertise
- **Event-driven architecture** for real-time responsiveness
- **LangChain orchestration** for complex reasoning workflows

## Core Principles

1. ✅ **No Physical Sensors** - All intelligence from human inputs and external APIs
2. ✅ **RAG-Grounded** - Every recommendation backed by retrieved knowledge
3. ✅ **Multi-Agent** - Specialized agents for different agricultural domains
4. ✅ **Event-Driven** - Real-time reactions to changes and updates
5. ✅ **Safety First** - Cautious recommendations with confidence scoring

## Architecture

### Specialized Agents

- **Market Intelligence Agent** - Price monitoring, supply/demand analysis, timing advice
- **Weather Risk Agent** - Weather-based risk assessment and mitigation strategies
- **Farmer Advisory Agent** - Personalized farming advice and Q&A
- **Buyer Strategy Agent** - Pricing, negotiation, and fair value assessment
- **Logistics & Fulfillment Agent** - Order tracking, delay detection, routing optimization
- **System Orchestrator** - Coordinates all agents and makes final decisions

### Technology Stack

- **Backend**: Python 3.11+, FastAPI, LangChain
- **LLM**: Groq (Llama 3 70B/8B) - Ultra-fast inference
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`) - 384 dimensions
- **Vector DB**: Pinecone (Serverless)
- **Frontend**: React + Vite + TailwindCSS
- **Event Bus**: Redis Pub/Sub (optional) / In-memory (default)
- **Real-time**: WebSockets

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- Pinecone Account (Free Tier works)
- Groq API Key (Free Tier works)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agri_ai
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```ini
   # Required
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=agri
   
   # RAG Settings (Tuned for Pinecone + HuggingFace)
   RAG_SIMILARITY_THRESHOLD=0.3
   ```

5. **Knowledge Ingestion**
   Before running the app, ingest the knowledge base into Pinecone:
   ```bash
   python scripts/ingest_knowledge.py
   ```

6. **Start the Application**
   
   **Terminal 1 (Backend):**
   ```bash
   python -m uvicorn agrilink.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   
   **Terminal 2 (Frontend):**
   ```bash
   cd frontend
   npm run dev
   ```

   The app will be available at: **http://localhost:5173/**
   The API docs will be at: **http://localhost:8001/docs**

## Configuration

### Vector Database (Pinecone)
Ensure your Pinecone index is created with:
- **Dimensions**: 384
- **Metric**: Cosine
- **Region**: Any (e.g., us-east-1)

### RAG Tuning
If retrieval confidence is too low or high, adjust `RAG_SIMILARITY_THRESHOLD` in `.env`.
- Default: `0.3` (works best for `all-MiniLM-L6-v2`)

## Usage

### REST API

```bash
# Ask a farming question
curl -X POST http://localhost:8001/api/farmer/query \
  -H "Content-Type: application/json" \
  -d '{"query": "When should I plant wheat in Punjab?", "user_id": "farmer123"}'
```

### Frontend
Navigate to `http://localhost:5173/` to access the Farmer Advisory Portal.
- Select your crop (Wheat/Rice) and region (Punjab).
- Ask detailed questions like "What fertilizer should I use?".
- View AI recommendations grounded in official agricultural guides.

## Project Structure

```
agri_ai/
├── src/agrilink/
│   ├── agents/          # Multi-agent system
│   ├── api/             # REST API endpoints
│   ├── events/          # Event-driven architecture
│   ├── rag/             # RAG (Pinecone + Groq)
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI application
├── frontend/            # React Application
│   ├── src/
│   │   ├── pages/       # React components
│   │   └── services/    # API integration
├── knowledge/           # Knowledge base markdown files
├── scripts/             # Ingestion scripts
└── docs/                # Additional documentation
```

## Development

### Run Tests

```bash
python -m pytest tests/
```

### Safety & Guardrails

AgriLink implements multiple safety mechanisms:

- **RAG Validation**: All advice must be grounded in retrieved documents
- **Confidence Scoring**: Recommendations include confidence levels
- **Cautious Mode**: Incomplete data triggers conservative advice
- **Citations**: Sources are cited in the response

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
\"# Agrilink_ai\"  
