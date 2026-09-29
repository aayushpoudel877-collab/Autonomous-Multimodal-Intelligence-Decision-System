# AegisMind Architecture

AegisMind follows:

**Ingestion → document intelligence → persistent sources → vector indexing → hybrid retrieval → evidence → analytics/reasoning → decision → human review**

## Phase 5 infrastructure

Two persistence modes are supported:

- **SQLite**: zero-configuration local development; sources, audit events, vector representations, and job state are persisted locally.
- **PostgreSQL + pgvector**: containerized production-style mode; sources, JSON metadata, audit events, job state, and vector representations are persisted in PostgreSQL, with an HNSW cosine index for vector candidate retrieval.

The embedding implementation remains a deterministic local baseline. pgvector provides storage and indexing; it does not turn the hash embedding into a learned semantic model.

## Phase 4 document intelligence

PDFs are processed page-by-page with native text extraction, optional OCR for scanned pages, PDF table extraction, Devanagari/Latin script signals, and page-level provenance metadata. Images support metadata extraction and optional OCR.

Page-level document records are marked as pre-indexed so retrieval does not accidentally chunk them a second time.

## Phase 6 — asynchronous intelligence orchestration

The API now separates **acceptance** from **processing** for longer multimodal workloads:

1. uploaded bytes are written to object storage before a job is created;
2. a durable job record is created with type, payload, attempts, status, and optional idempotency key;
3. a bounded worker pool processes text, PDF, and image jobs through the same ingestion services used by synchronous endpoints;
4. failures are retried until the configured attempt limit;
5. completed or failed state is persisted and queryable through the jobs API;
6. queued jobs are recovered when the service starts again;
7. basic operational metrics expose job-state counts.

The current object-storage implementation is local filesystem storage. Its interface is deliberately isolated so an S3-compatible backend can be introduced without changing job payloads or API contracts.

## Retrieval

Hybrid retrieval combines TF-IDF lexical similarity with deterministic 384-dimensional vector similarity. SQLite vector representations are now reloaded from persistence at startup, while PostgreSQL vector connections are reused across retrieval rebuilds.

## Current limitations

- The asynchronous worker pool is process-local; Redis/Celery-style distributed execution is not yet implemented.
- The object-storage backend is local filesystem only.
- The semantic embedding is still a deterministic hash baseline rather than a learned multilingual model.
- Authentication/RBAC, distributed tracing, model registry, VLM integration, and multimodal evidence fusion remain future work.
