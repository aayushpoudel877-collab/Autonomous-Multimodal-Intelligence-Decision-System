import json
from .config import settings

class LocalQueue:
    def __init__(self): self.name="local"
    def enqueue(self,job_id): return None
    def close(self): pass

class RedisQueue:
    def __init__(self,url=None):
        import redis
        self.client=redis.Redis.from_url(url or settings.redis_url,decode_responses=True)
        self.queue=settings.redis_queue_name
        self.dead_letter=settings.redis_dead_letter_queue
        self.client.ping()
    def enqueue(self,job_id):
        self.client.rpush(self.queue,job_id)
    def receive(self,timeout=5):
        item=self.client.blpop(self.queue,timeout=timeout)
        return item[1] if item else None
    def dead_letter_job(self,job_id):
        self.client.rpush(self.dead_letter,job_id)
    def close(self): self.client.close()

def build_queue():
    if settings.queue_backend=="redis": return RedisQueue()
    return LocalQueue()
