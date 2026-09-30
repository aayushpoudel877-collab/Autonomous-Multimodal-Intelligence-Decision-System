from threading import RLock
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .chunking import chunk_source
from .embeddings import embedding_model
from .store import store
from .vector_store import build_vector_repository

class Retriever:
    def __init__(self):
        self.v=TfidfVectorizer(ngram_range=(1,2),max_features=20000,sublinear_tf=True)
        self.tfidf=None; self.embeddings=None; self.s=[]; self.vector_repo=None; self.lock=RLock()
    @property
    def ready(self):
        with self.lock:return bool(self.s and self.tfidf is not None and self.embeddings is not None and self.vector_repo is not None)
    @property
    def model_name(self): return embedding_model.name
    def _prepare(self,sources):
        return [x for source in sources for x in ([source] if source.metadata.get("indexed_chunk") else chunk_source(source))]
    def rebuild(self,sources):
        with self.lock:
            self.s=self._prepare(sources); texts=[x.content for x in self.s]
            self.tfidf=self.v.fit_transform(texts) if texts else None
            self.embeddings=embedding_model.encode(texts) if texts else None
            if self.s:
                if self.vector_repo is None:self.vector_repo=build_vector_repository(store.db)
                self.vector_repo.save([x.id for x in self.s],self.embeddings)
            elif self.vector_repo and hasattr(self.vector_repo,"close"):
                self.vector_repo.close(); self.vector_repo=None
    def search(self,q,k=5):
        with self.lock:
            if not self.ready or not q.strip(): return []
            lexical=cosine_similarity(self.v.transform([q]),self.tfidf)[0]
            semantic=self.vector_repo.search(embedding_model.encode([q])[0],[x.id for x in self.s],k=k)
            combined=.55*lexical+.45*semantic
            ranked=combined.argsort()[::-1]
            return [{"source":self.s[i],"score":round(float(combined[i]),4),"lexical_score":round(float(lexical[i]),4),"semantic_score":round(float(semantic[i]),4)} for i in ranked[:k] if combined[i]>0]
    def close(self):
        with self.lock:
            if self.vector_repo and hasattr(self.vector_repo,"close"): self.vector_repo.close()
            self.vector_repo=None

retriever=Retriever()
