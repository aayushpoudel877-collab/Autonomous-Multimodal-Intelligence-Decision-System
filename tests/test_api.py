import time
from io import BytesIO
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.chunking import chunk_text,chunk_document_pages
from app.document_intelligence import script_signal
from app.schemas import Source

c=TestClient(app)

def test_health():
    data=c.get("/health").json()
    assert data["status"]=="ok"
    assert data["storage_backend"] in {"sqlite","postgres"}
    assert data["retrieval_ready"] in (True,False)

def test_pipeline():
    response=c.post("/api/ingest/text",json={"title":"Policy","text":"AegisMind supports trustworthy decisions.","metadata":{}})
    assert response.status_code==200
    results=c.post("/api/retrieve",json={"query":"trustworthy","top_k":3}).json()["results"]
    assert results and "semantic_score" in results[0]

def test_chunking():
    chunks=chunk_text("Sentence one. Sentence two. "*100,size=80,overlap=10)
    assert len(chunks)>1 and all(chunks)

def test_page_aware_chunking_does_not_rechunk():
    source=Source(id="doc-1",title="Report",content="",metadata={"type":"pdf"})
    chunks=chunk_document_pages(source,[{"page":2,"text":"Revenue increased. Risk remains.","script":"latin","extracted_by":"text","table_count":1}])
    assert len(chunks)==1 and chunks[0].metadata["page"]==2 and chunks[0].metadata["indexed_chunk"] is True

def test_script_signal():
    assert script_signal("This is English.")=="latin"
    assert script_signal("यो नेपाली पाठ हो।")=="devanagari"
    assert script_signal("Nepali नेपाली")=="devanagari+latin"

def test_image_ingestion():
    image=Image.new("RGB",(32,32),(200,200,200)); buffer=BytesIO(); image.save(buffer,format="PNG")
    response=c.post("/api/ingest/image",files={"file":("test.png",buffer.getvalue(),"image/png")})
    assert response.status_code==200
    analysis=response.json()["analysis"]
    assert analysis["sha256"] and analysis["ocr"]["enabled"] and "available" in analysis["ocr"]

def test_invalid_document_type():
    response=c.post("/api/ingest/document",files={"file":("bad.txt",b"hello","text/plain")})
    assert response.status_code==415

def test_async_text_job_and_idempotency():
    payload={"job_type":"text","title":"Async policy","text":"Asynchronous trusted processing.","metadata":{}}
    first=c.post("/api/jobs/text",json=payload,headers={"Idempotency-Key":"test-idempotency-1"})
    second=c.post("/api/jobs/text",json=payload,headers={"Idempotency-Key":"test-idempotency-1"})
    assert first.status_code==200 and second.status_code==200
    assert first.json()["id"]==second.json()["id"]
    job_id=first.json()["id"]
    deadline=time.time()+5
    status=None
    while time.time()<deadline:
        status=c.get(f"/api/jobs/{job_id}").json()["status"]
        if status in {"completed","failed"}: break
        time.sleep(.05)
    assert status=="completed"

def test_metrics():
    data=c.get("/metrics").json()
    assert "jobs" in data and "sources" in data

def test_audit():
    assert isinstance(c.get("/api/audit?limit=10").json()["events"],list)
