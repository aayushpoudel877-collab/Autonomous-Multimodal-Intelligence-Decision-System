import os,tempfile
from fastapi import FastAPI,File,UploadFile,HTTPException,Header
from fastapi.responses import FileResponse,JSONResponse
from fastapi import Request
from fastapi import Request
from .security import verify_api_key
from .config import settings
from .schemas import *
from .store import store
from .retrieval import retriever
from .ingestion import ingest_text,ingest_document,ingest_image
from .object_storage import object_storage
from .jobs import job_manager
from .ml import detect_anomalies,forecast
from .graph import knowledge_graph
from .decision import make_decision
from .agent import run_agent
from .provenance import evidence_record
from .observability import metrics

app=FastAPI(title=settings.app_name,version="1.5.0")

@app.middleware("http")
async def api_security(request:Request,call_next):
    if settings.api_keys and request.method not in {"GET","HEAD","OPTIONS"} and request.url.path!="/health":
        try:
            verify_api_key(request.headers.get("X-API-Key"))
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code,content={"detail":exc.detail})
    return await call_next(request)

@app.middleware("http")
async def api_security(request:Request,call_next):
    if settings.api_keys and request.method not in {"GET","HEAD","OPTIONS"} and request.url.path not in {"/health"}:
        verify_api_key(request.headers.get("X-API-Key"))
    return await call_next(request)

@app.on_event("startup")
def startup():
    retriever.rebuild(store.all())
    if settings.queue_backend=="local": job_manager.recover()

@app.get("/",include_in_schema=False)
def root(): return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status":"ok","service":settings.app_name,"sources":len(store.all()),"retrieval_ready":retriever.ready,"storage_backend":settings.storage_backend,"embedding_model":"hash-384-v1","workers":settings.worker_count,"object_storage":"local"}

@app.get("/metrics")
def health_metrics(): return metrics()

@app.post("/api/ingest/text")
def ingest(req:IngestTextRequest):
    return ingest_text(req.title,req.text,req.metadata)

@app.post("/api/ingest/document")
async def document(file:UploadFile=File(...),ocr_language:str="eng"):
    suffix=os.path.splitext(file.filename or "")[1].lower()
    if suffix!=".pdf": raise HTTPException(415,"Only PDF documents are supported by this ingestion endpoint.")
    data=await file.read()
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:
        f.write(data); path=f.name
    try:return ingest_document(path,file.filename or "document.pdf",ocr_language)
    finally:
        try:os.unlink(path)
        except OSError:pass

@app.post("/api/ingest/image")
async def image(file:UploadFile=File(...),ocr_language:str="eng"):
    suffix=os.path.splitext(file.filename or "")[1] or ".png"; data=await file.read()
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:
        f.write(data);path=f.name
    try:return ingest_image(path,file.filename or "image",ocr_language)
    finally:
        try:os.unlink(path)
        except OSError:pass

@app.post("/api/jobs/text")
def submit_text_job(req:JobSubmitRequest,idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    return job_manager.submit("text",{"title":req.title,"text":req.text,"metadata":req.metadata},idempotency_key)

@app.post("/api/jobs/document")
async def submit_document_job(file:UploadFile=File(...),ocr_language:str="eng",idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    suffix=os.path.splitext(file.filename or "")[1].lower()
    if suffix!=".pdf": raise HTTPException(415,"Only PDF documents are supported by this job endpoint.")
    stored=object_storage.put(await file.read(),file.filename or "document.pdf")
    return job_manager.submit("document",{"object_key":stored["key"],"filename":file.filename or "document.pdf","suffix":suffix,"ocr_language":ocr_language},idempotency_key)

@app.post("/api/jobs/image")
async def submit_image_job(file:UploadFile=File(...),ocr_language:str="eng",idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    filename=file.filename or "image.png"; suffix=os.path.splitext(filename)[1] or ".png"
    stored=object_storage.put(await file.read(),filename)
    return job_manager.submit("image",{"object_key":stored["key"],"filename":filename,"suffix":suffix,"ocr_language":ocr_language},idempotency_key)

@app.get("/api/jobs/{job_id}")
def get_job(job_id:str):
    job=job_manager.get(job_id)
    if not job: raise HTTPException(404,"Job not found")
    return job

@app.get("/api/jobs")
def list_jobs(limit:int=50):
    return {"jobs":job_manager.list(max(1,min(limit,200)))}

@app.post("/api/retrieve")
def retrieve(req:RetrieveRequest):
    return {"results":[{"source":x["source"].model_dump(),"score":x["score"],"lexical_score":x["lexical_score"],"semantic_score":x["semantic_score"],"evidence":evidence_record(x["source"],x["score"])} for x in retriever.search(req.query,req.top_k)]}

@app.post("/api/ask")
def ask(req:AskRequest):
    rs=retriever.search(req.question,req.top_k)
    return {"answer":" ".join(x["source"].content[:700] for x in rs) if rs else "No grounded knowledge found. Ingest trusted material first.","sources":[evidence_record(x["source"],x["score"]) for x in rs]}

@app.post("/api/anomaly")
def anomaly(req:AnomalyRequest):return detect_anomalies(req.values,req.contamination)
@app.post("/api/forecast")
def forecast_api(req:ForecastRequest):return forecast(req.values,req.horizon)
@app.post("/api/decision")
def decision(req:DecisionRequest):return make_decision(req.question,req.signals,req.evidence)
@app.post("/api/agent/run")
def agent_api(req:AgentRequest):return run_agent(req.goal,req.context)
@app.get("/api/knowledge/graph")
def graph():return knowledge_graph.export()
@app.get("/api/audit")
def audit(limit:int=100):return {"events":store.audit(limit)}
