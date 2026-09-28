# AegisMind Architecture

AegisMind is organized as a modular intelligence pipeline:

**Ingestion → document intelligence → normalization → hybrid retrieval/knowledge → ML analytics → reasoning → decision → human review**

### Current implementation
- FastAPI service
- page-aware PDF ingestion with per-page provenance
- optional OCR adapter for scanned PDF/image content
- PDF table extraction adapter
- English/Nepali/mixed-script language detection signals
- image metadata and optional OCR
- hybrid TF-IDF + deterministic embedding retrieval
- evidence provenance with content hashes and retrieval scores
- Isolation Forest anomaly detection
- Linear regression forecasting
- NetworkX knowledge graph
- deterministic agent orchestration
- structured confidence/evidence/risk output
- Docker and CI

### Multimodal document contract

Each document manifest contains:
- document hash and media type
- page count
- page-level text
- extraction method: text, OCR, or none
- language signal
- table count and extracted table cells when available
- parent document ID and page-aware chunk metadata

This keeps OCR, layout parsing, table extraction, and future vision-language models replaceable without changing retrieval or decision APIs.

### Production extension points
Replace baseline components with PostgreSQL/pgvector, object storage, production OCR/layout models, multilingual embedding models, vision-language models, model registry, RBAC, distributed audit logging and GPU inference.

### Research directions
Multilingual low-resource retrieval, multimodal evidence fusion, uncertainty calibration, poisoned-document robustness, causal forecasting, continual learning and agent trajectory evaluation.
