# AegisMind Architecture

AegisMind is organized as a modular intelligence pipeline:

**Ingestion → document intelligence → normalization → hybrid retrieval/knowledge → ML analytics → reasoning → decision → human review**

### Current implementation
- FastAPI service
- page-aware PDF ingestion with per-page provenance
- optional scanned-page OCR using Tesseract + PyMuPDF
- PDF table extraction adapter
- Devanagari/Latin/mixed-script detection signals
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
- script signal
- table count and extracted table cells when available
- parent document ID and page-aware chunk metadata

OCR language is configurable per ingestion request. The default Docker image installs Tesseract's standard English data; additional language packs can be installed when required. Script detection is intentionally heuristic and does not claim full language identification.

### Production extension points
Replace baseline components with PostgreSQL/pgvector, object storage, production OCR/layout models, multilingual embedding models, vision-language models, model registry, RBAC, distributed audit logging and GPU inference.

### Research directions
Multilingual low-resource retrieval, multimodal evidence fusion, uncertainty calibration, poisoned-document robustness, causal forecasting, continual learning and agent trajectory evaluation.
