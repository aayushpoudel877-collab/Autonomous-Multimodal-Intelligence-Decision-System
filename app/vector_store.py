import numpy as np
from .config import settings
from .embeddings import embedding_model

class VectorRepository:
    model_name=embedding_model.name
    def save(self,ids,vectors): raise NotImplementedError
    def search(self,query,ids,k=5): raise NotImplementedError

class SQLiteVectorRepository(VectorRepository):
    def __init__(self,db):
        self.db=db; self.vectors={}
        for sid,vec in db.load_embeddings(self.model_name).items():
            self.vectors[sid]=np.asarray(vec,dtype=np.float32)
    def save(self,ids,vectors):
        for sid,vec in zip(ids,vectors): self.vectors[sid]=np.asarray(vec,dtype=np.float32)
        self.db.save_embeddings(ids,vectors,self.model_name)
    def search(self,query,ids,k=5):
        q=np.asarray(query,dtype=np.float32)
        return np.asarray([float(np.dot(q,self.vectors.get(sid,np.zeros_like(q)))) for sid in ids],dtype=np.float32)

def build_vector_repository(db):
    if settings.storage_backend=="postgres":
        from .postgres import PostgresVectorRepository
        return PostgresVectorRepository(settings.postgres_url,model_name=embedding_model.name)
    return SQLiteVectorRepository(db)
