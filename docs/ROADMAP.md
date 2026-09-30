# Roadmap

## Foundation
- [x] API and dashboard
- [x] multimodal ingestion
- [x] retrieval
- [x] forecasting
- [x] anomaly detection
- [x] knowledge graph
- [x] agent workflow
- [x] tests and CI

## Phase 3 — Semantic Intelligence
- [x] hybrid lexical + semantic ranking
- [x] evidence provenance
- [x] deterministic local embedding fallback
- [x] retrieval score decomposition

## Phase 4 — Multimodal Document Intelligence
- [x] page-aware PDF parsing
- [x] scanned-page OCR adapter
- [x] image OCR adapter
- [x] PDF table extraction adapter
- [x] script detection
- [x] page-level provenance metadata
- [ ] document layout/schema extraction
- [ ] vision-language model integration
- [ ] multimodal evidence fusion

## Phase 5 — Production Intelligence Infrastructure
- [x] storage backend configuration
- [x] persistent vector representation
- [x] SQLite vector reload on startup
- [x] PostgreSQL + pgvector backend
- [x] Docker Compose production-style database stack
- [x] retrieval compatibility for pre-indexed document pages
- [x] backend/capability health reporting
- [x] PostgreSQL connection reuse
- [ ] production multilingual embeddings

## Phase 6 — Asynchronous Intelligence Orchestration
- [x] durable job state
- [x] bounded background worker pool
- [x] text/PDF/image job handlers
- [x] retry policy with persisted attempt counts
- [x] idempotency-key support
- [x] startup recovery
- [x] local object storage
- [x] job status/list APIs
- [x] operational job metrics

## Phase 7 — Distributed Production Orchestration
- [x] Redis-backed distributed job queue
- [x] dedicated worker process
- [x] atomic job claiming to prevent duplicate execution
- [x] persisted retry/dead-letter flow
- [x] S3-compatible object-storage adapter
- [x] MinIO development deployment
- [x] optional API-key authentication for write APIs
- [x] distributed Docker Compose stack
- [x] worker-safe startup recovery
- [ ] scheduled/batched processing
- [ ] distributed tracing/OpenTelemetry
- [ ] production secret manager integration
- [ ] horizontal autoscaling policy
- [ ] rate limiting and per-tenant quotas

## Research
- [ ] Nepali/English benchmark
- [ ] cross-modal evidence benchmark
- [ ] calibrated confidence
- [ ] adversarial retrieval evaluation
- [ ] causal reasoning
- [ ] human feedback learning
