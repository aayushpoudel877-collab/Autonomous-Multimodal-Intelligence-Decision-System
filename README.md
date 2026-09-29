# AegisMind — Autonomous Multimodal Intelligence & Decision System

A modular AI/ML platform combining multimodal ingestion, grounded retrieval, predictive ML, anomaly detection, knowledge graphs, agent orchestration, and explainable human-reviewed decisions.

## Current capabilities
- Page-aware PDF ingestion with OCR and table extraction
- Image OCR and media metadata
- Devanagari/Latin script signals
- Hybrid TF-IDF + deterministic 384-dimensional embedding retrieval
- Persisted vector representations
- SQLite zero-configuration backend
- PostgreSQL + pgvector production backend
- Evidence provenance with content hashes and retrieval scores
- Isolation Forest anomaly detection
- Forecasting baseline
- NetworkX knowledge graph
- Human-review-gated agent workflow
- FastAPI dashboard/API
- Docker Compose production-style stack
- Automated tests and CI

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run scalable stack
```bash
docker compose up --build
```
This starts AegisMind with PostgreSQL + pgvector. SQLite remains available by setting `AEGISMIND_STORAGE_BACKEND=sqlite`.

## API
`POST /api/ingest/text` · `POST /api/ingest/document` · `POST /api/ingest/image` · `POST /api/retrieve` · `POST /api/ask` · `POST /api/anomaly` · `POST /api/forecast` · `POST /api/decision` · `POST /api/agent/run` · `GET /api/knowledge/graph` · `GET /api/audit` · `GET /health`

## Phase 5 architecture
`Ingestion → persistent sources → vector repository → hybrid retrieval → evidence → reasoning → decision`

The default development path uses SQLite. The containerized path uses PostgreSQL/pgvector. The embedding model is still a deterministic local baseline; pgvector provides scalable vector storage/indexing, not a learned semantic model.

See `docs/ARCHITECTURE.md` and `docs/ROADMAP.md`.
