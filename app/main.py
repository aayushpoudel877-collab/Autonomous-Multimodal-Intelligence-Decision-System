import os,tempfile,uuid
from fastapi import FastAPI,File,UploadFile
from fastapi.responses import FileResponse
from .config import settings
from .schemas import *
from .store import store
from .retrieval import retriever
from .multimodal import text_from_pdf,image_analysis
from .ml import detect_anomalies,forecast
from .graph import knowledge_graph
from .decision import make_decision
from .agent import run_agent
app=FastAPI(title=settings.app_name,version="1.0.0")
@app.get("/",include_in_schema=False)
def root():return FileResponse("static/index.html")
@app.get("/health")
def health():return {"status":"ok","service":settings.app_name}
@app.post("/api/ingest/text")
def ingest(req:IngestTextRequest):
    s=Source(id=str(uuid.uuid4()),title=req.title,content=req.text,metadata=req.metadata);store.add(s);retriever.rebuild(store.all());knowledge_graph.add_text(s.id,s.content);return s
@app.post("/api/ingest/document")
async def document(file:UploadFile=File(...)):
    suffix=os.path.splitext(file.filename or "")[1].lower()
    if suffix!=".pdf":return {"error":"Baseline supports PDF documents."}
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:f.write(await file.read());path=f.name
    text=text_from_pdf(path);s=Source(id=str(uuid.uuid4()),title=file.filename or "document.pdf",content=text,metadata={"type":"pdf"});store.add(s);retriever.rebuild(store.all());knowledge_graph.add_text(s.id,text);return s
@app.post("/api/ingest/image")
async def image(file:UploadFile=File(...)):
    suffix=os.path.splitext(file.filename or "")[1] or ".png"
    with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as f:f.write(await file.read());path=f.name
    return {"filename":file.filename,"analysis":image_analysis(path)}
@app.post("/api/retrieve")
def retrieve(req:RetrieveRequest):return {"results":[{"source":x["source"].model_dump(),"score":x["score"]} for x in retriever.search(req.query,req.top_k)]}
@app.post("/api/ask")
def ask(req:AskRequest):
    rs=retriever.search(req.question,req.top_k)
    return {"answer":" ".join(x["source"].content[:500] for x in rs) if rs else "No grounded knowledge found. Ingest trusted material first.","sources":[x["source"].id for x in rs]}
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