# Project Workflow

## 1. Daily development workflow

This project should be built in small, testable steps. The safest workflow is:

1. Update config or environment variables
2. Implement the smallest module change
3. Run the relevant test or smoke check
4. Move to the next phase only after the step passes

---

## 2. Local setup

### Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Use environment variables

- Copy `.env.example` to `.env`
- Fill in the model/provider settings
- Set `LLM_PROVIDER` to either `azure` or `gemini`
- Keep secrets out of version control

---

## 3. Recommended execution flow

## Step 1 — Build the data foundation

Create or update the raw support documents and source registry:

```bash
# if web scraping is added
python -m ingestion.web_scraper
```

Then validate the raw content and metadata structure.

---

## Step 2 — Build the vector index

```bash
python -m ingestion.build_index
```

Expected outcome:
- documents are cleaned and loaded
- chunks are created
- FAISS index is built and written to `vectorstore/`

If this fails, check:
- missing file paths
- import issues
- invalid embeddings provider setup
- wrong environment variables

---

## Step 3 — Validate retrieval

Run a quick retrieval smoke test through Python:

```bash
python - <<'PY'
from app.rag.retriever import retrieve
results = retrieve('How can I track my order?', 'shipping')
print(type(results), len(results))
for item in results[:3]:
    print(item['document'].metadata.get('category'))
    print(item['document'].page_content[:200])
PY
```

This confirms the index loads and the vector search works before you add more RAG logic.

---

## Step 4 — Validate generation

Once retrieval works, test the generator against a known question:

```bash
python - <<'PY'
from app.rag.query_router import detect_category
from app.rag.retriever import retrieve
from app.rag.reranker import rerank
from app.rag.generator import generate_answer

question = 'Can I return a damaged product?'
category = detect_category(question)
results = retrieve(question, category)
print('category:', category)
print('retrieved:', len(results))
results = rerank(results)[:4]
answer = generate_answer(question, results)
print(answer)
PY
```

This should produce a grounded answer using context from the retrieved documents.

---

## Step 5 — Run the API locally

```bash
uvicorn app.main:app --reload
```

Then open:

- http://localhost:8000/docs
- POST `/api/v1/chat`

Example request:

```json
{
  "question": "Can I return a damaged product?"
}
```

---

## Step 6 — Test the app

```bash
pytest
```

Add or update tests for:
- health endpoint
- retrieval returns a list
- category detection results
- generation fallback logic

---

## Step 7 — Run evaluation

```bash
python scripts/evaluate.py
```

Checklist:
- the benchmark questions run successfully
- categories match expected values
- answers are grounded and concise
- unsupported questions fail gracefully

---

## Step 8 — Build and containerize

```bash
docker build -t shopassist-rag .
```

Run it locally:

```bash
docker run -p 8000:8000 --env-file .env shopassist-rag
```

---

## 4. Working principles for this repo

### Keep modules single-purpose
- `ingestion/` handles document processing
- `app/rag/` handles retrieval and generation logic
- `app/api/` handles HTTP requests
- `tests/` validates behavior

### Validate early
Do not add a new abstraction without testing it with a smoke check.

### Prefer simple working implementations first
The default flow should be:
- retrieval from FAISS
- rerank by score
- prompt with context
- answer

### Treat unsupported answers as a feature
If the context is missing, the app should say so clearly instead of guessing.

---

## 5. Typical failure points

### Import errors
Check package installation and whether the environment is activated.

### Embedding model errors
Verify that the selected provider and deployment names are valid.

### Vectorstore missing
Build the index before running retrieval.

### LLM call errors
Confirm the API key, endpoint, and deployment are set correctly.

### Unstable answers
Reduce prompt complexity and ensure context is short and relevant.

---

## 6. Recommended phased execution checklist

## Phase 1
- [ ] Setup environment
- [ ] Install dependencies
- [ ] Build ingestion utilities
- [ ] Build initial FAISS index
- [ ] Run retrieval smoke test

## Phase 2
- [ ] Add provider abstraction
- [ ] Add prompt template
- [ ] Add generator and pipeline
- [ ] Validate answer generation

## Phase 3
- [ ] Create FastAPI app and route file
- [ ] Validate `/health`
- [ ] Validate `/api/v1/chat`

## Phase 4
- [ ] Add tests
- [ ] Add evaluation questions
- [ ] Run `pytest` and benchmark script

## Phase 5
- [ ] Add Dockerfile and Makefile
- [ ] Build and run container
- [ ] Document final workflow in the project README

---

## 7. Suggested command summary

```bash
# install
pip install -r requirements.txt

# index
python -m ingestion.build_index

# api
uvicorn app.main:app --reload

# tests
pytest

# evaluation
python scripts/evaluate.py

# docker
docker build -t shopassist-rag .
docker run -p 8000:8000 --env-file .env shopassist-rag
```

This is the main local workflow for the project from setup to validation and deployment.
