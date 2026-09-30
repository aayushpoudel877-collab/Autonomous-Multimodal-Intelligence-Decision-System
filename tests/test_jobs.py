from pathlib import Path
from app.persistence import SQLiteStore

def test_job_claim_is_single_owner(tmp_path:Path):
    db=SQLiteStore(str(tmp_path/"jobs.db"))
    job=db.create_job("job-1","text",{"title":"x","text":"y"},None,3)
    first=db.claim_job(job["id"])
    second=db.claim_job(job["id"])
    assert first is not None
    assert first["status"]=="running"
    assert second is None
    assert first["attempts"]==1

def test_idempotency_returns_existing_job(tmp_path:Path):
    db=SQLiteStore(str(tmp_path/"jobs.db"))
    first=db.create_job("job-1","text",{"x":1},"same-key",3)
    second=db.create_job("job-2","text",{"x":2},"same-key",3)
    assert first["id"]==second["id"]
    assert second["payload"]==first["payload"]
