# AegisMind Architecture

AegisMind follows:

**Ingestion → document intelligence → persistent sources → vector indexing → hybrid retrieval → evidence → analytics/reasoning → decision → human review**

## Phase 5 infrastructure

Two persistence modes are supported:

- **SQLite**: zero-configuration local development; sources, audit events, and vector representations are persisted in the local database.
- **PostgreSQL + pgvector**: containerized production-style mode; sources, JSON metadata, audit events, and 384-dimensional vector representations are persisted in PostgreSQL, with an HNSW cosine index for vector candidate retrieval.

The embedding implementation remains a deterministic local baseline. pgvector provides storage and indexing; it does not turn the hash embedding into a learned semantic model.

## Document intelligence

PDFs are processed page-by-page with:
- native text extraction
- optional OCR for scanned pages
- PDF table extraction
- Devanagari/Latin script signals
- page-level hashes/provenance metadata

Images support metadata extraction and optional OCR.

Page-level document records are marked as pre-indexed so the retrieval layer does not accidentally chunk them a second time.

## Retrieval

Hybrid retrieval combines:
- TF-IDF lexical similarity
- deterministic 384-dimensional vector similarity

The vector repository is selected from configuration without changing the retrieval API.

## Production extension points

Next infrastructure work includes Redis-backed asynchronous jobs, object storage, multilingual learned embeddings, authentication/RBAC, observability, model registry, and multimodal evidence fusion.
