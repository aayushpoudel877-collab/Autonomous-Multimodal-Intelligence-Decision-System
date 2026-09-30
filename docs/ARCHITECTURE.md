# AegisMind Architecture

AegisMind follows:

Ingestion → document intelligence → persistent sources → vector indexing → hybrid retrieval → evidence fusion → analytics/reasoning → decision → human review

## Phase 5 infrastructure

SQLite supports zero-configuration local development. PostgreSQL + pgvector provides the production-style persistent backend with HNSW cosine indexing.

## Phase 4 document intelligence

PDFs are processed page-by-page with native text extraction, optional OCR, PDF table extraction, Devanagari/Latin script signals, and page-level provenance. Images support metadata extraction and OCR.

## Phase 6 — asynchronous intelligence orchestration

Uploaded artifacts are persisted before durable jobs are created. Workers process text, PDF, and image jobs, persist retries and completion state, and recover queued work after startup.

## Phase 7 — distributed production orchestration

Scalable deployments use Redis for work distribution, PostgreSQL for durable job state, and shared S3-compatible storage for artifacts. Workers atomically claim queued/retrying jobs before execution. Exhausted jobs are also written to a Redis dead-letter queue. API-key protection is intentionally lightweight and is not a full identity/RBAC system.

## Phase 8 — multilingual retrieval and evidence intelligence

The embedding layer supports a deterministic hash fallback and a learned sentence-transformers provider. The configured learned model is a 384-dimensional multilingual encoder by default, loaded lazily. Strict mode can force startup/runtime failure instead of fallback when the learned dependency is unavailable.

Persistent vector representations are model-aware. Retrieval therefore identifies which embedding model generated a vector and avoids mixing representations from different configured models. PostgreSQL remains fixed at 384 dimensions so the current schema is predictable.

Hybrid retrieval combines TF-IDF lexical similarity with vector similarity. The evaluation module reports Recall@K, MRR, and nDCG from explicit relevance labels, enabling reproducible Nepali/English benchmark work without pretending that a benchmark exists before labels are collected.

Evidence fusion groups repeated evidence by source, applies bounded modality priors, and adds a small cross-modal corroboration bonus when multiple modalities support the same source. This is a deterministic evidence layer, not a learned vision-language model.

Confidence calibration implements temperature scaling over labeled confidence samples. It must be fitted on representative validation data before being used for operational decisions.

## Current limitations

- learned embeddings require model weights and may need network access on first use;
- learned reranking and vision-language reasoning are not yet integrated;
- deterministic modality fusion requires empirical benchmarking;
- confidence calibration is only a primitive until fitted on representative data;
- distributed tracing, secret management, tenant isolation, queue visibility leases, autoscaling, and model rollout controls remain future work.
