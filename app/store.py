from threading import Lock
from .schemas import Source
from .config import settings
from .persistence import SQLiteStore
class KnowledgeStore:
    def __init__(self):
        self.db=SQLiteStore(settings.db_path)
        self.items={s.id:s for s in self.db.all()}
        self.lock=Lock()
    def add(self,s):
        with self.lock:
            self.items[s.id]=s
            self.db.upsert(s)
        return s
    def all(self):
        with self.lock:return list(self.items.values())
    def audit(self,limit=100):return self.db.audit(limit)
store=KnowledgeStore()
