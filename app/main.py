import os,tempfile,uuid
from fastapi import FastAPI,File,UploadFile
from fastapi.responses import FileResponse
from .config import settings
from .schemas import *
from .store import store
from .retrieval import retriever
from .document_intelligence import pdf_document,image_document
from .chunking import chunk_document_pages
from .ml import detect_anomalies,forecast
from .graph import knowledge_graph
from .decision import make_decision
from .agent import run_agent
from .provenance import evidence_record

app=FastAPI(title=settings.app_name,version="1.2.0")

@app.on_event("startup")
def startup(): retriever.rebuild(store.all())

@app.get("/",include_in_schema=False)
def root(): return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status":"ok","service":settings.app_name,"sources":len(store.all()),"retrieval_ready":retriever.m is not None}

@app.post("/api/ingest/text")
def ingest(req:IngestTextRequest):
    s=Source(id=str(uuid.uuid4()),title=req.title,content=req.text,metadata=req.metadata)
    store.add(s); retriever.rebuild(store.all()); knowledge_graph.add_text(s.id,s.content)
    return s

@app.post("/api/ingest/document")
async def document(file:UploadFile=File(...)):
    suffix=os.path.splitext(file.filename or "")[1].lower()
    if suffix!=".pdf": return {"error":"Phase 4 document ingestion currently accepts PDF files."}
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:
        f.write(await file.read()); path=f.name
    try:
        manifest=pdf_document(path,ocr=True)
        parent=Source(id=str(uuid.uuid4()),title=file.filename or "document.pdf",content="",metadata={"type":"pdf","media_type":"application/pdf","sha256":manifest["sha256"],"page_count":manifest["page_count"],"language":manifest["language"],"modality":"document"})
        page_sources=chunk_document_pages(parent,manifest["pages"])
        for source in page_sources:
            store.add(source); knowledge_graph.add_text(source.id,source.content)
        retriever.rebuild(store.all())
        return {"document":parent,"manifest":manifest,"indexed_chunks":len(page_sources)}
    finally:
        try: os.unlink(path)
        except OSError: pass

@app.post("/api/ingest/image")
async def image(file:UploadFile=File(...)):
    suffix=os.path.splitext(file.filename or "")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:
        f.write(await file.read()); path=f.name
    try:
        analysis=image_document(path,ocr=True)
        text=analysis["ocr"]["text"]
        indexed=None
        if text:
            indexed=Source(id=str(uuid.uuid4()),title=file.filename or "image",content=text,metadata={"type":"image","modality":"image","sha256":analysis["sha256"],"language":analysis["ocr"]["language"],"extracted_by":"ocr"})
            store.add(indexed); retriever.rebuild(store.all()); knowledge_graph.add_text(indexed.id,text)
        return {"filename":file.filename,"analysis":analysis,"indexed_source":indexed}
    finally:
        try: os.unlink(path)
        except OSError: pass

@app.post("/api/retrieve")
def retrieve(req:RetrieveRequest):
    return {"results":[{"source":x["source"].model_dump(),"score":x["score"],"lexical_score":x["lexical_score"],"semantic_score":x["semantic_score"],"evidence":evidence_record(x["source"],x["score"])} for x in retriever.search(req.query,req.top_k)]}

@app.post("/api/ask")
def ask(req:AskRequest):
    rs=retriever.search(req.question,req.top_k)
    return {"answer":" ".join(x["source"].content[:700] for x in rs) if rs else "No grounded knowledge found. Ingest trusted material first.","sources":[evidence_record(x["source"],x["score"]) for x in rs]}

@app.post("/api/anomaly")
def anomaly(req:AnomalyRequest): return detect_anomalies(req.values,req.contamination)

@app.post("/api/forecast")
def forecast_api(req:ForecastRequest): return forecast(req.values,req.horizon)

@app.post("/api/decision")
def decision(req:DecisionRequest): return make_decision(req.question,req.signals,req.evidence)

@app.post("/api/agent/run")
def agent_api(req:AgentRequest): return run_agent(req.goal,req.context)

@app.get("/api/knowledge/graph")
def graph(): return knowledge_graph.export()

@app.get("/api/audit")
def audit(limit:int=100): return {"events":store.audit(limit)}
