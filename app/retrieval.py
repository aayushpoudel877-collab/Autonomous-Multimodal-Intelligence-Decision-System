from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .chunking import chunk_source
from .embeddings import embedding_model
from .store import store
from .vector_store import build_vector_repository

class Retriever:
    def __init__(self):
        self.v=TfidfVectorizer(ngram_range=(1,2),max_features=20000,sublinear_tf=True)
        self.tfidf=None; self.embeddings=None; self.s=[]; self.vector_repo=None
    @property
    def ready(self): return bool(self.s and self.tfidf is not None and self.embeddings is not None and self.vector_repo is not None)
    def _prepare(self,sources):
        chunks=[]
        for source in sources:
            if source.metadata.get("indexed_chunk"): chunks.append(source)
            else: chunks.extend(chunk_source(source))
        return chunks
    def rebuild(self,sources):
        self.s=self._prepare(sources)
        texts=[x.content for x in self.s]
        self.tfidf=self.v.fit_transform(texts) if texts else None
        self.embeddings=embedding_model.encode(texts) if texts else None
        if self.s:
            if self.vector_repo is None:
                self.vector_repo=build_vector_repository(store.db)
            self.vector_repo.save([x.id for x in self.s],self.embeddings)
        else:
            self.vector_repo=None
    def search(self,q,k=5):
        if not self.ready or not q.strip(): return []
        lexical=cosine_similarity(self.v.transform([q]),self.tfidf)[0]
        qvec=embedding_model.encode([q])[0]
        semantic=self.vector_repo.search(qvec,[x.id for x in self.s],k=k)
        combined=.55*lexical+.45*semantic
        ranked=combined.argsort()[::-1]
        return [{"source":self.s[i],"score":round(float(combined[i]),4),"lexical_score":round(float(lexical[i]),4),"semantic_score":round(float(semantic[i]),4)} for i in ranked[:k] if combined[i]>0]
    def close(self):
        if self.vector_repo and hasattr(self.vector_repo,"close"): self.vector_repo.close()
        self.vector_repo=None

retriever=Retriever()
