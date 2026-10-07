# ShopEase Enterprise RAG Customer Support Assistant

ShopEase is a lightweight retrieval-augmented generation (RAG) application for customer support queries across shipping, returns, refunds, and cancellations.

It ingests policy documents, chunks them into retrievable units, stores them in a FAISS vector index, and answers user questions with grounded support responses plus source metadata.

## Features

- Policy ingestion and cleaning from support documents
- Chunking with metadata for source and category
- FAISS-based semantic retrieval
- Category-aware reranking and routing
- Grounded support answer generation
- FastAPI chat API with Swagger docs
- Local fallback LLM support for offline development
- Docker-ready setup

## Architecture overview

The app follows a standard RAG pipeline:

1. Load and clean support policy documents
2. Split content into chunks
3. Embed chunks and store them in FAISS
4. Retrieve top relevant passages
5. Re-rank and filter by category
6. Build a grounded answer using the retrieved context
7. Return answer, sources, confidence, and escalation signal

## Project structure

```text
ShopEase_Enterprise_RAG_Customer_Support_Assistant/
├── app/
│   ├── api/
│   ├── core/
│   ├── evaluation/
│   ├── generation/
│   ├── ingestion/
│   ├── rag/
│   ├── retrieval/
│   ├── schemas/
│   └── main.py
├── data/
│   ├── raw/
│   └── evaluation/
├── ingestion/
├── tests/
├── vectorstore/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── workflow.md
```

## Prerequisites

- Python 3.11+
- pip
- Optional: Docker / Docker Compose

## Quick start

### 1) Create a virtual environment

```bash
cd /path/to/ShopEase_Enterprise_RAG_Customer_Support_Assistant
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Build the vector index

```bash
python -m ingestion.build_index
```

This creates or refreshes the FAISS index used by retrieval.

### 4) Run the app

```bash
uvicorn app.main:app --reload
```

Open the API docs here:

- http://localhost:8000/docs
- http://localhost:8000/health

The root route redirects to Swagger UI.

## API usage

### Chat endpoint

- Method: POST
- Path: /api/v1/chat

Example request body:

```json
{
  "question": "Can I return a damaged product?",
  "history": []
}
```

Example response:

```json
{
  "answer": "Returns are generally allowed within 30 days for eligible unused items. Damaged or incorrect products should be reported within 48 hours of delivery, and photographic evidence may be required.",
  "sources": [
    {
      "document": "return_policy.md",
      "category": "returns",
      "url": null
    }
  ],
  "category": "returns",
  "confidence": 0.88,
  "escalation_required": false
}
```

## Environment configuration

Copy the sample environment file and adjust values as needed:

```bash
cp .env.example .env
```

Supported settings include:

- APP_NAME / APP_ENV / LOG_LEVEL
- LLM_PROVIDER = local, azure, or google
- Azure settings for OpenAI deployments
- Google Gemini settings
- Retrieval tuning values such as TOP_K, FINAL_K, CHUNK_SIZE, and SIMILARITY_THRESHOLD
- API_PREFIX and optional API_KEY

The default configuration uses the local provider for development and testing.

## Local model behavior

When LLM_PROVIDER is set to local, the app uses a lightweight fallback generator instead of calling external cloud APIs. This is useful for local demos and development where credentials are not available.

## Running with Docker

```bash
docker-compose up --build
```

Then access:

- http://localhost:8000/docs

## Testing

Run the project test suite with:

```bash
pytest -q
```

## Common commands

```bash
python -m ingestion.build_index
uvicorn app.main:app --reload
pytest -q
```

## Troubleshooting

### FAISS index missing

If the vector store is not initialized yet, rebuild it:

```bash
python -m ingestion.build_index
```

### App not reachable

Confirm the server is running and the port is open:

```bash
curl http://localhost:8000/health
```

### Wrong answer quality

Check that:

- the index has been rebuilt after policy edits
- the question matches the supported policy categories
- the retrieval settings are tuned for your use case

## Notes

This project is intentionally designed as a practical demo of a customer-support RAG workflow. It is a strong foundation for further enhancements such as production LLM integration, authentication, monitoring, and richer evaluation pipelines.
