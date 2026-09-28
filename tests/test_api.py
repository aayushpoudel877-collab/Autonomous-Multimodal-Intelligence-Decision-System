from fastapi.testclient import TestClient
from app.main import app
from app.chunking import chunk_text
c=TestClient(app)

def test_health():
    data=c.get("/health").json()
    assert data["status"]=="ok"
    assert "sources" in data

def test_pipeline():
    c.post("/api/ingest/text",json={"title":"Policy","text":"AegisMind supports trustworthy decisions.","metadata":{}})
    assert c.post("/api/retrieve",json={"query":"trustworthy","top_k":3}).json()["results"]

def test_anomaly():assert 6 in c.post("/api/anomaly",json={"values":[1,1,1,1,1,1,50]}).json()["anomaly_indices"]
def test_forecast():assert len(c.post("/api/forecast",json={"values":[1,2,3,4,5],"horizon":2}).json()["forecast"])==2
def test_chunking():
    chunks=chunk_text("Sentence one. Sentence two. "*100,size=80,overlap=10)
    assert len(chunks)>1 and all(chunks)
def test_audit():
    data=c.get("/api/audit?limit=10").json()
    assert isinstance(data["events"],list)


def test_hybrid_retrieval_exposes_scores_and_provenance():
    response=c.post("/api/retrieve",json={"query":"trustworthy decisions","top_k":3})
    assert response.status_code==200
    if response.json()["results"]:
        item=response.json()["results"][0]
        assert "semantic_score" in item and "lexical_score" in item
        assert "evidence" in item and "content_hash" in item["evidence"]
