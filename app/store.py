from threading import Lock
from .schemas import Source
class KnowledgeStore:
    def __init__(self): self.items={}; self.lock=Lock()
    def add(self,s):
        with self.lock:self.items[s.id]=s
        return s
    def all(self):
        with self.lock:return list(self.items.values())
store=KnowledgeStore()