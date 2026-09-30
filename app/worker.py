import logging,time
from .jobs import job_manager
from .queue import RedisQueue
from .store import store
from .config import settings

log=logging.getLogger("aegismind.worker")

def run():
    if settings.queue_backend!="redis": raise RuntimeError("Worker service requires AEGISMIND_QUEUE_BACKEND=redis")
    queue=RedisQueue()
    log.info("AegisMind distributed worker started")
    while True:
        job_id=queue.receive(timeout=10)
        if not job_id: continue
        try: job_manager.run_job(job_id)
        except Exception:
            log.exception("Worker crashed while processing %s",job_id)

if __name__=="__main__": run()
