import numpy as np
from .config import settings

class VectorRepository:
    model_name="hash-384-v1"
    def save(self,ids,vectors): raise NotImplementedError
    def search(self,query,ids,k=5): raise NotImplementedError

class SQLiteVectorRepository(VectorRepository):
    def __init__(self,db):
        self.db=db; self.vectors={}
    def save(self,ids,vectors):
        self.vectors={sid:np.asarray(vec,dtype=np.float32) for sid,vec in zip(ids,vectors)}
        self.db.save_embeddings(ids,vectors,self.model_name)
    def search(self,query,ids,k=5):
        q=np.asarray(query,dtype=np.float32)
        scores=np.asarray([float(np.dot(q,self.vectors.get(sid,np.zeros_like(q)))) for sid in ids],dtype=np.float32)
        return scores

def build_vector_repository(db):
    if settings.storage_backend=="postgres":
        from .postgres import PostgresVectorRepository
        return PostgresVectorRepository(settings.postgres_url)
    return SQLiteVectorRepository(db)
