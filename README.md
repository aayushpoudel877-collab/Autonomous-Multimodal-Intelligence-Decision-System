# AegisMind — Autonomous Multimodal Intelligence & Decision System

A modular AI/ML platform combining multimodal ingestion, grounded retrieval, predictive ML, anomaly detection, knowledge graphs, agent orchestration, and explainable human-reviewed decisions.

## Implemented
- PDF ingestion and image analysis
- TF-IDF grounded retrieval / RAG baseline
- Isolation Forest anomaly detection
- Transparent forecasting baseline
- NetworkX knowledge graph
- Agent workflow with mandatory human-review gate
- Evidence, confidence and risk in decision outputs
- FastAPI API + browser dashboard
- Docker / Docker Compose
- Automated tests and CI

## Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://localhost:8000` and `/docs`.

## API
`POST /api/ingest/text` · `POST /api/ingest/document` · `POST /api/ingest/image` · `POST /api/retrieve` · `POST /api/ask` · `POST /api/anomaly` · `POST /api/forecast` · `POST /api/decision` · `POST /api/agent/run` · `GET /api/knowledge/graph` · `GET /health`

## Architecture
**Data → Ingestion → Retrieval/Knowledge → ML Analytics → Reasoning → Decision → Human Review**

See `docs/ARCHITECTURE.md` and `docs/ROADMAP.md` for the production and research extension plan.

> AegisMind is advisory software; consequential actions remain behind human review.
