# AgriLink Knowledge Base

This directory contains agricultural knowledge that powers the RAG (Retrieval-Augmented Generation) system.

## Structure

```
knowledge/
├── crops/          # Crop-specific guides and best practices
├── market/         # Market rules, pricing trends, trading information
└── policies/       # Government policies and regulations
```

## Document Format

All knowledge documents should be in Markdown format (`.md`) with the following metadata structure:

```markdown
---
category: crops
crop: wheat
region: punjab
tags: [planting, irrigation, pest-control]
---

# Document Title

Content goes here...
```

## Ingestion

To ingest knowledge into the vector database:

```bash
python scripts/ingest_knowledge.py
```

## Adding New Knowledge

1. Create a new `.md` file in the appropriate category directory
2. Add proper frontmatter metadata
3. Write clear, factual content
4. Run the ingestion script to update the vector database

## Quality Guidelines

- **Factual**: All information must be accurate and verifiable
- **Specific**: Include region-specific and crop-specific details
- **Actionable**: Provide practical, implementable advice
- **Cited**: Reference sources where applicable
- **Updated**: Keep information current with latest practices
