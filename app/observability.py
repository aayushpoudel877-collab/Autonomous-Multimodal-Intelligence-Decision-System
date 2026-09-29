import logging,time
from contextlib import contextmanager
from .store import store

logger=logging.getLogger("aegismind")
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s %(message)s")

@contextmanager
def timed_operation(name:str,**fields):
    started=time.perf_counter()
    try: yield
    finally:
        elapsed=round(time.perf_counter()-started,4)
        logger.info("operation=%s duration_seconds=%s fields=%s",name,elapsed,fields)

def metrics():
    jobs=store.db.list_jobs(1000)
    counts={}
    for job in jobs: counts[job["status"]]=counts.get(job["status"],0)+1
    return {"jobs":counts,"sources":len(store.all())}
