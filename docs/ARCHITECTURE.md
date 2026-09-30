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


## Phase 7 — Distributed production orchestration

Phase 6's process-local executor is retained for zero-configuration development, but scalable deployments can use Redis as the durable work queue. The API persists jobs in PostgreSQL, stores uploaded artifacts in shared S3-compatible object storage, and pushes only job identifiers into Redis.

A dedicated worker process consumes the queue. Before processing, the worker atomically changes a queued/retrying job to running. This prevents two workers from executing the same attempt concurrently. Failed attempts are persisted; retryable failures return to the queue, while exhausted failures are also written to the Redis dead-letter queue.

The distributed Docker stack provides PostgreSQL/pgvector, Redis, MinIO, the API, and a dedicated worker. MinIO is used as a local S3-compatible development service; production deployments should replace development credentials with managed secrets and use managed/object-storage infrastructure where appropriate.

Optional API-key authentication can protect write APIs. This is intentionally a lightweight deployment guard rather than a complete identity/RBAC system; tenant isolation, OAuth/OIDC, rate limits, and fine-grained permissions remain future work.
