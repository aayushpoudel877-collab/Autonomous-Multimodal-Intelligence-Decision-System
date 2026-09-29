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
- [ ] Redis/distributed task queue
- [ ] object storage abstraction with S3-compatible backend
- [ ] production multilingual embeddings
- [ ] authentication/RBAC
- [ ] distributed observability

## Phase 6 — Asynchronous Intelligence Orchestration
- [x] durable job state
- [x] bounded background worker pool
- [x] text/PDF/image job handlers
- [x] retry policy with persisted attempt counts
- [x] idempotency-key support
- [x] startup recovery for queued jobs
- [x] local object storage for uploaded artifacts
- [x] job status/list APIs
- [x] operational job metrics
- [ ] distributed workers via Redis
- [ ] S3-compatible object storage
- [ ] scheduled/batched processing
- [ ] dead-letter queue
- [ ] distributed tracing

## Research
- [ ] Nepali/English benchmark
- [ ] cross-modal evidence benchmark
- [ ] calibrated confidence
- [ ] adversarial retrieval evaluation
- [ ] causal reasoning
- [ ] human feedback learning
