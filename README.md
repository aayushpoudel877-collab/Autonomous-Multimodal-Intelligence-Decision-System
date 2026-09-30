# AegisMind — Autonomous Multimodal Intelligence & Decision System

A modular AI/ML platform combining multimodal ingestion, grounded retrieval, predictive ML, anomaly detection, knowledge graphs, agent orchestration, and explainable human-reviewed decisions.

## Current capabilities

- Page-aware PDF ingestion with OCR and table extraction
- Image OCR and media metadata
- Devanagari/Latin script signals
- Hybrid TF-IDF + learned multilingual 384-dimensional embedding retrieval with deterministic fallback
- Persisted vector representations
- SQLite development backend
- PostgreSQL + pgvector production-style backend
- Evidence provenance with content hashes and retrieval scores
- Isolation Forest anomaly detection
- Forecasting baseline
- NetworkX knowledge graph
- Human-review-gated agent workflow
- Durable asynchronous text/PDF/image jobs
- Redis-backed distributed workers
- Atomic job claiming and bounded retries
- Dead-letter queue for exhausted Redis jobs
- Local filesystem and S3-compatible object storage
- Optional API-key protection for write APIs
- Docker Compose stack with PostgreSQL, Redis, MinIO, API, and workers
- Retrieval evaluation with Recall@K, MRR, and nDCG\n- Deterministic cross-modal evidence fusion\n- Temperature-scaling confidence calibration primitive\n- Automated tests and CI

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The local default uses SQLite, a local object store, and the in-process worker pool.

## Run the distributed stack

```bash
docker compose up --build
```

The distributed profile starts:

- AegisMind API
- PostgreSQL + pgvector
- Redis
- dedicated AegisMind worker
- MinIO S3-compatible object storage

The API and worker share PostgreSQL, Redis, and object storage so jobs can move between processes without depending on local container state.

## Configuration

Set `AEGISMIND_QUEUE_BACKEND=redis` and `AEGISMIND_REDIS_URL` to enable distributed jobs.

Set `AEGISMIND_OBJECT_STORAGE_BACKEND=s3` together with `AEGISMIND_S3_BUCKET` and optional `AEGISMIND_S3_ENDPOINT_URL` for S3-compatible storage.

Set `AEGISMIND_EMBEDDING_PROVIDER=sentence-transformers` to enable the learned multilingual encoder. The default hash provider remains suitable for offline tests.\n\nSet `AEGISMIND_API_KEYS` to a comma-separated list such as `admin-secret:admin,reader-secret:reader`. When configured, non-GET APIs require a valid `X-API-Key`.

Do not use the development credentials in `docker-compose.yml` for an internet-exposed deployment; move credentials to a secret manager or deployment secret store.

## API

`POST /api/ingest/text` · `POST /api/ingest/document` · `POST /api/ingest/image`

`POST /api/jobs/text` · `POST /api/jobs/document` · `POST /api/jobs/image`

`GET /api/jobs` · `GET /api/jobs/{job_id}` · `GET /metrics` · `GET /health`

`POST /api/retrieve` · `POST /api/ask` · `POST /api/evaluate/retrieval` · `POST /api/anomaly` · `POST /api/forecast` · `POST /api/decision` · `POST /api/agent/run`

## Architecture

`Client → API → durable job state → Redis queue → workers → multimodal ingestion → PostgreSQL/pgvector + object storage → hybrid retrieval → evidence → reasoning → decision`

The deterministic hash embedding remains a baseline; pgvector provides scalable vector storage/indexing but does not make that embedding a learned semantic model.

See `docs/ARCHITECTURE.md` and `docs/ROADMAP.md`.
