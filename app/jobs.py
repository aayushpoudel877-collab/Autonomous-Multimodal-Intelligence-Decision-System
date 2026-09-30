import json,logging,uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from .config import settings
from .object_storage import object_storage
from .store import store
from .ingestion import ingest_text,ingest_document,ingest_image
from .queue import build_queue

log=logging.getLogger(__name__)

class JobManager:
    def __init__(self):
        self.executor=ThreadPoolExecutor(max_workers=settings.worker_count,thread_name_prefix="aegismind") if settings.queue_backend=="local" else None
        self.queue=build_queue()
        self.handlers={"text":self._text,"document":self._document,"image":self._image}
    def submit(self,job_type,payload,idempotency_key=None,max_attempts=None):
        job=self._create(job_type,payload,idempotency_key,max_attempts or settings.job_max_attempts)
        if job["status"] in {"queued","retrying"}:
                if settings.queue_backend=="redis": self.queue.enqueue(job["id"])
                else: self.executor.submit(self._run,job["id"])
        return self.public(job)
    def _create(self,job_type,payload,idempotency_key,max_attempts):
        return store.db.create_job(str(uuid.uuid4()),job_type,payload,idempotency_key,max_attempts)
    def run_job(self,job_id):
        return self._run(job_id)
    def run_job(self,job_id):
        return self._run(job_id)
    def _run(self,job_id):
        job=store.db.claim_job(job_id)
        if not job:return
        attempts=int(job["attempts"])
        try:
            result=self.handlers[job["type"]](job["payload"])
            store.db.update_job(job_id,status="completed",result=result,finished_at=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            log.exception("AegisMind job %s failed",job_id)
            if attempts < int(job["max_attempts"]):
                store.db.update_job(job_id,status="retrying",error=str(exc))
                if settings.queue_backend=="redis": self.queue.enqueue(job_id)
                else: self.executor.submit(self._run,job_id)
            else:
                store.db.update_job(job_id,status="failed",error=str(exc),finished_at=datetime.now(timezone.utc).isoformat())
                if settings.queue_backend=="redis" and hasattr(self.queue,"dead_letter_job"): self.queue.dead_letter_job(job_id)

    def _text(self,p):
        return ingest_text(p["title"],p["text"],p.get("metadata"))
    def _file(self,p,kind):
        data=object_storage.get(p["object_key"])
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False,suffix=p.get("suffix","")) as f:
            f.write(data); path=f.name
        try:
            if kind=="document": return ingest_document(path,p.get("filename","document.pdf"),p.get("ocr_language","eng"))
            return ingest_image(path,p.get("filename","image"),p.get("ocr_language","eng"))
        finally:
            import os
            try:os.unlink(path)
            except OSError:pass
    def _document(self,p): return self._file(p,"document")
    def _image(self,p): return self._file(p,"image")
    def recover(self):
        for job in store.db.list_jobs(200):
            if job["status"] == "running":
                store.db.update_job(job["id"],status="queued",error="Recovered after worker interruption")
            if job["status"] in {"queued","retrying"}:
                if settings.queue_backend=="redis": self.queue.enqueue(job["id"])
                else: self.executor.submit(self._run,job["id"])
    def get(self,job_id): return self.public(store.db.get_job(job_id))
    def list(self,limit=50): return [self.public(x) for x in store.db.list_jobs(limit)]
    @staticmethod
    def public(job):
        if not job:return None
        return {**job,"payload":job.get("payload") or {}, "result":job.get("result")}

job_manager=JobManager()
